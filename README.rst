ADAPT: A DAta Processing Toolkit
--------------------------------

Formally it is a library that can be used to execute pre-defined processes by providing a yaml-style configuration file.
Processes follow a prototype.
The processing is strictly sequential for the time being.

The main purpose is to allow automated data processing in batch mode.
That is: run the same procedure with identical configuration over large amounts of data files.

The implemented processes focus on data processing at PETRA III at DESY.
Data reading and parameter estimation are incorporated by external libraries.

The library can be used to build applications as well.
The first example is iint-gui, built specifically for the beamline P09 at PETRA III.
It consists of a graphical user interface that can be used to set and run a particular configuration.
In addition, several data views are implmented.


The package is for python3.

To generate the documentation:
python3 setup.py build_sphinx
