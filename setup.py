from setuptools import setup

setup(
    name='Herd',
    version='0.1.1',
    author='Russ Garret',
    author_email='russ@garrett.co.uk',
    packages=['herd', 'herd.BitTornado', 'herd.BitTornado.BT1'],
    scripts=[],
    url='https://github.com/russss/Herd',
    description='A simpler implementation of Twitter Murder in python.  Deploy files distributedly using the Torrent protocol.',
    long_description=open('README.md').read(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'herd = herd.herd:entry_point',
            ],
        },
    data_files=[('herd', ['herd/bittornado.tar.gz'])]
)
