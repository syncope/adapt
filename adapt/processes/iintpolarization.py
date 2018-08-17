# Copyright (C) 2017  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

# polarization analysis specific to beamline p09 @ DESY PS

import numpy as np
from scipy.optimize import curve_fit
from math import pi, cos, sin

from adapt.iProcess import *



class iintpolarization(IProcess):

    def __init__(self, ptype="iintpolarization"):
        super(iintpolarization, self).__init__(ptype)
        self._inputPar = ProcessParameter("inputFilename", str)
        self._outputNamePar = ProcessParameter("outputName", str)
        self._pr1chiNamePar = ProcessParameter("pr1chi", str, optional=True)
        self._pr2chiNamePar = ProcessParameter("pr2chi", str, optional=True)
        self._petaNamePar = ProcessParameter("peta", str, optional=True)
        self._ptthNamePar = ProcessParameter("ptth", str, optional=True)
        self._parameters.add(self._inputPar)
        self._parameters.add(self._outputNamePar)
        self._parameters.add(self._pr1chiNamePar)
        self._parameters.add(self._pr2chiNamePar)
        self._parameters.add(self._petaNamePar)
        self._parameters.add(self._ptthNamePar)

    def initialize(self):
        pass

    def execute(self, data):
        pass

    def finalize(self, data):
        # the name of the input file
        infile = self._inputPar.get()

        # first obtain the layout of the file by parsing the header
        with open(infile) as f:
            first_line = f.readline()
            # - remove the leading hash
            line = first_line.split('# ')[1]
            headers = [i for i in line.split('\t')]
            # - remove the trailing newline
            headers.remove('\n')
        # parse the data file
        rawdata = np.loadtxt(infile, unpack=True)
        
        # and finally: build the associative data block
        poldata = { headers[i]: rawdata[i] for i in range(len(headers)) }

        pr1chiana = np.unique(poldata[self._pr1chiNamePar.get()])
        pr2chiana = np.unique(poldata[self._pr2chiNamePar.get()])
        petaana = np.unique(poldata[self._petaNamePar.get()])

        tthana = np.mean(poldata[self._ptthNamePar.get()])


    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def fitfunc(self, x, a0, a1, a2):
        return (a0/2.)*( 1. + ( cos(self.tthana*pi/180.) )**2 + ( (sin(self.tthana*pi/180.))**2 ) * ( a1*np.cos(2*(x)*pi/180.) + a2*np.sin(2*(x)*pi/180.) ))
