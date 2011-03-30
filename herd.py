import tempfile, sys, os, time
from os import path
from greenlet import GreenletExit
import eventlet
from eventlet.green import socket
from eventlet.green import subprocess
murder_client = eventlet.import_patched('murder_client')
bttrack = eventlet.import_patched('BitTornado.BT1.track')
makemetafile = eventlet.import_patched('BitTornado.BT1.makemetafile')

PORT = 8998
REMOTE_PATH = '/tmp/herd'
DATA_FILE = './data'

def run(local_file, remote_file, hosts):
    start = time.time()
    print "Spawning tracker..."
    tracker = eventlet.spawn(track)
    eventlet.sleep(1)
    local_host = (local_ip(), PORT)
    print "Creating torrent (host %s:%s)..." % local_host
    torrent_file = mktorrent(local_file, '%s:%s' % local_host)
    print "Seeding"
    seeder = eventlet.spawn(seed, torrent_file, local_file)
    print "Transferring"
    if not os.path.isfile('./bittornado.tar.gz'):
        subprocess.call("tar cfz ./bittornado.tar.gz ./BitTornado".split(' '))
    pool = eventlet.GreenPool(100)
    threads = []
    for host in hosts:
        threads.append(pool.spawn(transfer, host, torrent_file, remote_file))
    for thread in threads:
        thread.wait()
    os.unlink(torrent_file)
    try:
        os.unlink(DATA_FILE)
    except OSError:
        pass
    print "Finished, took %.2f seconds." % (time.time() - start)

def transfer(host, local_file, remote_target):
    file_name = path.basename(local_file)
    remote_file = '%s/%s' % (REMOTE_PATH, file_name)
    scp(host, local_file, remote_file)
    if ssh(host, 'test -d %s/BitTornado' % REMOTE_PATH) != 0:
        ssh(host, "mkdir %s" % REMOTE_PATH)
        scp(host, 'bittornado.tar.gz', '%s/bittornado.tar.gz' % REMOTE_PATH)
        ssh(host, "cd %s; tar zxvf bittornado.tar.gz > /dev/null" % REMOTE_PATH)
        scp(host, 'murder_client.py', '%s/murder_client.py' % REMOTE_PATH)
    result = ssh(host, 'python %s/murder_client.py peer %s %s' % (REMOTE_PATH, remote_file, remote_target))
    ssh(host, 'rm %s' % remote_file)
    if result == 0:
        print "%s complete" % host
    else:
        print "%s FAILED with code %s" % (host, result)

def ssh(host, command):
    return subprocess.call(['ssh', host, command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def scp(host, local_file, remote_file):
    return subprocess.call(['scp', local_file, '%s:%s' % (host, remote_file)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def mktorrent(file_name, tracker):
    torrent_file = tempfile.mkstemp('.torrent')
    makemetafile.make_meta_file(file_name, "http://%s/announce" % tracker,
                                        {'target': torrent_file[1]})
    return torrent_file[1]

def track():
       bttrack.track(["--dfile", DATA_FILE,
                  "--port", PORT])

def seed(torrent, local_file):
        murder_client.run(["--responsefile", torrent,
                        "--saveas", local_file])

def local_ip():
     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     s.connect(("10.1.0.0", 0))
     return s.getsockname()[0]

if __name__ == '__main__':
    hosts = [line.strip() for line in open(sys.argv[3], 'r') if line[0] != '#']
    run(sys.argv[1], sys.argv[2], hosts)
