## About

Herd is a single-command Bittorrent-based file distribution system, based on Twitter's Murder.
It was designed for pushing code out to a number of production systems. You can probably use
it for other things.

Herd requires no extra Python modules on the destination system as it ships around
its own (lightly modified) copy of BitTornado.

## Differences from Murder

[Murder](https://github.com/lg/murder) was Twitter's original BitTorrent-based file
distribution system. It's pretty dependent on Capistrano and requires that a separate
tracker process is started before you run the deploy task.

Herd is run by a single command, which spawns its own tracker in the background. This
makes it really trivial to integrate into whatever deployment system you like.

## Requirements

Herd needs Python > 2.5, argparse,  and eventlet (on the source system only). All other libraries
are shipped with it. To install eventlet, you can just do:

    easy_install eventlet

On CentOS:

    yum install python-eventlet

Argparse can be found with easy_install as well:

    easy_install argparse

## Usage

Herd assumes that you're running as a user which has passwordless SSH access,
with the same account, to all the machines you need to copy to.

Create a file hosts.dat with a list of the hosts you want to copy to, and:

    /path/to/herd.py ./myfile.tar.gz /path/to/destination.tar.gz hosts.dat

## Python Integration

Herd can now be imported as a python module.  This makes integration into existing projects
much more bueno.  One would simply need to:

    import herd
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
