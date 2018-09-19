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

# iintgui processing: collect raw observable spectra and stack them
# create and save 2D plot

import numpy as np
try:
    import lmfit
except ImportError:
    print("lmfit package is not available, please install.")
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintscanprofileplot(IProcess):

    def __init__(self, ptype="iintscanprofileplot"):
        super(iintscanprofileplot, self).__init__(ptype)
        self._outfilenamePar = ProcessParameter("outfilename", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._outfilenamePar)
        self._parameters.add(self._pdfobservablePar)

    def initialize(self):
        self._outfilename = self._outfilenamePar.get()
        self._pdfobservable = self._pdfobservablePar.get()
        self._pdfmotor = self._pdfmotorPar.get()
        self._darray = []
        self._values = []
        self._outfile = PdfPages(self._outfilename)

    def execute(self, data):
        scannumber = int(data.getData("scannumber"))
        observable = data.getData(self._pdfobservable)
        motor = data.getData(self._pdfmotor)

        self._values.append((scannumber, motor))
        self._darray.append(observable)

    def finalize(self, data):
        import math as m
        fig_size = plt.rcParams["figure.figsize"]
        # print "Current size:", fig_size
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        # create 2D array
        self._mesh = np.stack(self._darray)

        # display it:
        plt.matshow(self._mesh, cmap="jet")
        figure = plt.figure(1)
        figure.suptitle('Raw spectra vs. Scan number', fontsize=14, fontweight='bold')

        self._outfile.savefig()
        self._outfile.close()
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)
