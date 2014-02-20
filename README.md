## About

Horde is a torrent-based file distribution system, forked from [Herd](https://github.com/russss/Herd)
and based on [Murder](https://github.com/lg/murder).
It allows for quick and easy transfer of small and large files. You can probably use
it for other things too.

Horde requires no extra modules on Python and includes everything needed for destinations including
its own (lightly modified) copy of BitTornado.

## Differences from Herd

[Herd](https://github.com/russss/Herd) is a command line python client interface that uses eventlet
and has to be ran from the command line.  This project also has limitations around large file transfers,
peer seeding and python integration.

## Differences from Murder

[Murder](https://github.com/lg/murder) was Twitter's original BitTorrent-based file
distribution system. It's pretty dependent on Capistrano and requires that a separate
tracker process is started before you run the deploy task.

Horde spawns its own tracker in the background which makes it really trivial to integrate into whatever
deployment system you like.

## Requirements

Horde needs Python > 2.5 and argparse.  If your using python 2.7+ nothing else is needed as argparse
was added to the standard library.

Argparse(if needed) can be installed with easy_install or pip:

    pip install argparse
    easy_install argparse

Horde also currently requires that key based passwordless authentication is enabled on all of your
target destinations.

## Install

git clone https://github.com/naterh/Horde
cd Horde && sudo python setup.py install

or

sudo pip install horde

## Usage

With a hosts file that includes a list of the hosts you want to copy to:

    horde myfile.tar.gz /path/to/destination.tar.gz hosts_file

Using a hosts list that is a single string comma separated:

    horde myfile.tar.gz /path/to/destination.tar.gz --hostlist "host1,host2,host3"

More options:

    horde --help

## Python Integration

Horde can also be imported as a python module.  This makes integration into existing projects
much more bueno.  One would simply need to:

    import horde.horde as horde
    horde.run_with_opts('localfile', 'remotefile', hostlist='server1,server2')

## Credits

* [Russ Garrett](https://github.com/russss)
* [Laurie Denness](https://github.com/lozzd)
* [Nate House](https://github.com/naterh)
* [Sam Gleske](https://github.com/samrocketman)
* [Paul Sims](https://github.com/chalupaul)
* [Nandor Sivok](https://github.com/dominis)
* [Mikael Fridh](https://github.com/frimik)
* [Sebastian Borza](https://github.com/sebito91)
* [Patrick Ancillotti](https://github.com/neogenix)
