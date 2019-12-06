from setuptools import setup

from codecs import open
from os import path
from sphinx.setup_command import BuildDoc

with open(path.join('.', 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

name = 'adapt'
version = '0'
release = '0.6.10'

setup(
    name='adapt',
    version=release,

    description='ADAPT: a data processing toolkit.',
    long_description=long_description,

    url='https://github.com/syncope/adapt',

    author='Ch.Rosemann',
    author_email='christoph.rosemann@desy.de',

    license='GPLv2',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='photon science data processing analysis',

    packages=['adapt', ],
    package_dir={'adapt': 'adapt', },
    include_package_data=True,

    scripts=['adapt/bin/adapt'],
    cmdclass={'build_sphinx': BuildDoc, },
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release)}},
)
