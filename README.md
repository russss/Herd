## About

Herd is a torrent-based file distribution system based on [Murder](https://github.com/lg/murder).
It allows for quick and easy transfer of small and large files. You can probably use
it for other things too.

Herd requires no extra Python modules and includes everything needed for destinations including
its own (lightly modified) copy of BitTornado.

Herd has been updated from its fork [Horde](https://github.com/naterh/Horde) which removed limitations
around large file transfers, peer seeding, and python integration.  Herd now has the same capabilities
as Horde in that regard.

## Differences from Murder

[Murder](https://github.com/lg/murder) was Twitter's original BitTorrent-based file
distribution system. It's pretty dependent on Capistrano and requires that a separate
tracker process is started before you run the deploy task.

Herd spawns its own tracker in the background which makes it really trivial to integrate into whatever
deployment system you like.

## Requirements

Herd needs Python > 2.5 and argparse.  If you're using python 2.7+ nothing else is needed as argparse
was added to the standard library.

Argparse, if needed, can be installed with `easy_install` or `pip`:

    pip install argparse
    easy_install argparse

Herd also requires that key based passwordless authentication is enabled on all of your target
destinations.

## Install

    git clone https://github.com/russss/Herd
    cd Herd && sudo python setup.py install

Herd also supports `pypi_server` hosting.

## Usage

With a hosts file that includes a list of the hosts you want to copy to:

    herd myfile.tar.gz /path/to/destination.tar.gz hosts_file

Using a hosts list that is a single string comma separated:

    herd myfile.tar.gz /path/to/destination.tar.gz --hostlist "host1,host2,host3"

Reading the host list from stdin.

    cat /tmp/hosts_file | herd myfile.tar.gz /path/to/destination.tar.gz hosts_file

More options:

    herd --help

## Python Integration

Herd can also be imported as a python module.  This makes integration into existing projects
easy.  One would simply need to:

    import herd.herd as herd
    herd.run_with_opts('localfile', 'remotefile', hostlist='server1,server2')

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
