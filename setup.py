from setuptools import setup

setup(
    name='Herd',
    version='0.1.0',
    author='Nathan House',
    author_email='nathan.house@rackspace.com',
    packages=['herd', 'herd.BitTornado', 'herd.BitTornado.BT1'],
    scripts=[],
    url='http://github.com/naterh/Herd',
    description='Torrent distribution.',
    long_description=open('README.md').read(),
    install_requires=["argparse"],
    entry_points={
        'console_scripts': [
            'herd = herd.herd:entry_point',
            ],
        },
    #include_package_data = True,
    #package_data = {
     #   '': ['*.tar.gz'],
    #},
    #zip_safe=True,
    data_files=[('herd', ['herd/bittornado.tar.gz'])]
)
