#!/usr/bin/env python
import argparse
import eventlet
import logging
import os
import random
import re
import socket
import sys
import tempfile
import time
from eventlet.green import socket
from eventlet.green import subprocess

 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('local-file',
                        help='Local file to upload')

    parser.add_argument('remote-file',
                        help="Remote file destination")

    parser.add_argument('hosts',
                        help="File containing list of hosts",
                        default='',
                        nargs='?')

    parser.add_argument('--retry',
                        default=0,
                        type=int,
                        help="Number of times to retry in case of failure. " +
                        "Use -1 to make it retry forever (not recommended)")

    parser.add_argument('--port',
                        default=8998,
                        help="Port number to run the tracker on. Port range " +
                        "for random port selection also allowed (e.g. 8000-9000).")

    parser.add_argument('--remote-path',
                        default='/tmp/herd',
                        help="Temporary path to store uploads")

    parser.add_argument('--data-file',
                        default='./data',
                        help="Temporary file to store for bittornado.")

    parser.add_argument('--log-dir',
                        default='/tmp/herd',
                        help="Path to the directory for murder logs")

    parser.add_argument('--hostlist',
                        default=False,
                        help="Comma separated list of hosts")

    parser.add_argument('--torrent',
                        default=False,
                        help="Location of the torrent file you want to seed")

    parser.add_argument('--keep-torrent',
                        default=False,
                        help="Don't remove the torrent file on exit",
                        action='store_true')

    opts = vars(parser.parse_args())


    murder_client = eventlet.import_patched('murder_client')
    bttrack = eventlet.import_patched('BitTornado.BT1.track')
    makemetafile = eventlet.import_patched('BitTornado.BT1.makemetafile')

    log = logging.getLogger('herd')
    log.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    # add the handlers to the log
    log.addHandler(ch)

    herd_root = os.path.dirname(os.path.realpath(__file__))
    bittornado_tgz = os.path.join(herd_root, 'bittornado.tar.gz')
    murderclient_py = os.path.join(herd_root, 'murder_client.py')


def get_random_open_port(port,interface=""):
    """
        Arguments:
            port - can be a single number or a number range with a hyphen as a string
            interface - a string representing either a hostname in Internet domain notation or IP
                address to test binding.  By default a blank value means test a binding for all
                interfaces.
        Returns:
            returns an int between 1 and 65535 based on input port

        If a single port is given as input then it simply returns the port

        If a port range is input then a random port will be returned if there is no
        Listening socket for that port.
    """
    regex=re.compile(r'[0-9]+-{0,1}[0-9]*')
    #if port is an integer then convert to string
    if isinstance(port,int):
        port=str(port)
    #Do some error checking on the input.
    if not isinstance(port, str):
        raise TypeError("port not of type str.")
    if not regex.match(port):
        raise ValueError("port str must be a number or a range of numbers between 1 and 65535.")
    ports = sorted(map(lambda x: int(x), port.split('-')))
    #Do range checking on the input.
    if len(ports) == 2 and ( ports[1] > 65535 ):
        raise ValueError("port range is between 1 and 65535.")
    elif ports[0] < 1 or ports[0] > 65535:
        raise ValueError("port range is between 1 and 65535.")
    #Return a port or a random range.
    if len(ports) == 1:
        #Since we're given a single port don't even try to test it.  Just return the value.
        return ports[0]
    else:
        port=random.randrange(ports[0],ports[1]+1)
        count=0
        found=False
        while not found:
            try:
                #test the socket for a listening service
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((interface, port))
                found=True
            except socket.error,e:
                #Generate another port to be tested because the last one had a listening socket.
                port=random.randrange(ports[0],ports[1]+1)
            s.close()
            count+=1
            #avoid an infinite loop
            if count > 10000:
                break
        if not found:
            raise socket.error("could not obtain socket from port or port range.")
        return port


def run(local_file, remote_file, hosts, opts):
    start = time.time()
    log.info("Spawning tracker...")
    eventlet.spawn(track)
    eventlet.sleep(1)

    if opts['torrent'] and os.path.exists(opts['torrent']):
        torrent_file = opts['torrent']
    else:
        local_host = (local_ip(), opts['port'])
        log.info("Creating torrent (host %s:%s)..." % local_host)
        torrent_file = mktorrent(local_file, '%s:%s' % local_host)

    log.info("Seeding %s" % torrent_file)
    eventlet.spawn(seed, torrent_file, local_file)
    log.info("Transferring")
    if not os.path.isfile(bittornado_tgz):
        cwd = os.getcwd()
        os.chdir(herd_root)
        args = ['tar', 'czf', 'bittornado.tar.gz', 'BitTornado']
        log.info("Executing: " + " ".join(args))
        subprocess.call(args)
        os.chdir(cwd)
    pool = eventlet.GreenPool(100)
    threads = []
    remainingHosts = hosts      
    for host in hosts:
        threads.append(pool.spawn(transfer, host, torrent_file, remote_file, opts['retry']))
    for thread in threads:
        host = thread.wait()
        remainingHosts.remove(host)
        log.info("Done: %-6s Remaining: %s" % (host, remainingHosts))

    if opts['keep_torrent'] == False:
        os.unlink(torrent_file)
    try:
        os.unlink(opts['data_file'])
    except OSError:
        pass
    log.info("Finished, took %.2f seconds." % (time.time() - start))


def transfer(host, local_file, remote_target, retry=0):
    rp = opts['remote_path']
    file_name = os.path.basename(local_file)
    remote_file = '%s/%s' % (rp, file_name)
    if ssh(host, 'test -d %s/BitTornado' % rp) != 0:
        ssh(host, "mkdir %s" % rp)
        scp(host, bittornado_tgz, '%s/bittornado.tar.gz' % rp)
        ssh(host, "cd %s; tar zxvf bittornado.tar.gz > /dev/null" % rp)
        scp(host, murderclient_py, '%s/murder_client.py' % rp)
    log.info("Copying %s to %s:%s" % (local_file, host, remote_file))
    scp(host, local_file, remote_file)
    command = 'python %s/murder_client.py peer %s %s' % (rp, remote_file, remote_target)
    log.info("running \"%s\" on %s" %  (command, host))
    result = ssh(host, command)
    ssh(host, 'rm %s' % remote_file)
    if result != 0:
        log.info("%s FAILED with code %s" % (host, result))
        while retry != 0:
            retry = retry - 1
            log.info("retrying on %s" % host)
            transfer(host, local_file, remote_target, 0)
    return host


def ssh(host, command):
    if not os.path.exists(opts['log_dir']):
        os.makedirs(opts['log_dir'])
        
    with open("%s%s%s-ssh.log" % (opts['log_dir'], os.path.sep, host), 'a') as log:
        result = subprocess.call(['ssh', '-o UserKnownHostsFile=/dev/null',
                '-o LogLevel=quiet',
                '-o StrictHostKeyChecking=no',
                host, command], stdout=log,
                stderr=log)
    return result


def scp(host, local_file, remote_file):
    return subprocess.call(['scp', '-o UserKnownHostsFile=/dev/null',
                '-o StrictHostKeyChecking=no',
                local_file, '%s:%s' % (host, remote_file)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def mktorrent(file_name, tracker):
    torrent_file = tempfile.mkstemp('.torrent')
    makemetafile.make_meta_file(file_name, "http://%s/announce" % tracker,
                    {'target': torrent_file[1], 'piece_size_pow2': 0})
    return torrent_file[1]


def track():
    bttrack.track(["--dfile", opts['data_file'], "--port",
                    get_random_open_port(opts['port'])])


def seed(torrent, local_file):
    murder_client.run(["--responsefile", torrent,
                        "--saveas", local_file])


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.1.0.0", 0))
    return s.getsockname()[0]


def  herdmain():
    if not os.path.exists(opts['hosts']) and opts['hostlist'] is False:
        hosts = [line.strip() for line in sys.stdin]
    elif opts['hosts']:
        hosts = [line.strip() for line in open(opts['hosts'], 'r')]
    else:
        hosts = opts['hostlist'].split(',')
    # filter out comments and empty lines
    hosts = [host for host in hosts if not re.match("^#", host) and not host == '']
    if len(hosts) == 0:
      sys.exit('ERROR: No hosts provided.')
    # handles duplicates
    hosts = list(set(hosts))
    log.info("Running with options: %s" % opts)
    log.info("Running for hosts: %s" % hosts)
    run(opts['local-file'], opts['remote-file'], hosts, opts)

if __name__ == '__main__':
    herdmain()
