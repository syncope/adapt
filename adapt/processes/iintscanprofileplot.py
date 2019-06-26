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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintscanprofileplot(IProcess):

    def __init__(self, ptype="iintscanprofileplot"):
        super(iintscanprofileplot, self).__init__(ptype)
        self._outfilenamePar = ProcessParameter("outfilename", str)
        self._xaxisPar = ProcessParameter("xaxis", str)
        self._yaxisPar = ProcessParameter("yaxis", str)
        self._zaxisPar = ProcessParameter("zaxis", str)
        self._rawnamePar = ProcessParameter("rawdataname", str)
        self._parameters.add(self._xaxisPar)
        self._parameters.add(self._yaxisPar)
        self._parameters.add(self._zaxisPar)
        self._parameters.add(self._rawnamePar)
        self._parameters.add(self._outfilenamePar)
        self._padded = False

    def initialize(self):
        self._outfilename = self._outfilenamePar.get()
        self._xaxis = self._xaxisPar.get()
        self._yaxis = self._yaxisPar.get()
        self._zaxis = self._zaxisPar.get()
        self._rawdataname = self._rawnamePar.get()
        self._darray = []
        self._values = []
        self._outfile = PdfPages(self._outfilename)

    def execute(self, data):
        xdata = data.getData(self._xaxis)
        ydata = int(data.getData(self._yaxis))
        try:
            zdata = data.getData(self._zaxis)
        except KeyError:
            try:
                zdata = data.getData(self._rawdataname).get(self._zaxis)
            except KeyError:
                return

        self._values.append((ydata, xdata))
        self._darray.append(zdata)

    def finalize(self, data):
        import math as m
        fig_size = plt.rcParams["figure.figsize"]
        # print "Current size:", fig_size
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        # check if the arrays are of different size and correct, if needed
        self._correctArraySize()
        # create 2D array
        # self._mesh = np.stack(self._darray) # numpy v >= 1.10.
        self._mesh = np.row_stack(self._darray)
        val1 = float(self._values[0][1][-1])
        val2 = float(self._values[0][1][0])
        val3 = float(self._values[-1][0])
        val4 = float(self._values[0][0])

        # display it: ( what's the difference between matshow and imshow?)
        plt.imshow(self._mesh, cmap="jet", interpolation='none', aspect="auto", extent=[val1, val2, val3, val4])
        plt.xlabel(self._xaxis)
        plt.ylabel(self._yaxis)
        plt.colorbar()
        figure = plt.figure(1)
        if self._padded:
            figure.suptitle(str(self._xaxis + ' vs. ' + self._yaxis) + '\n with z values: ' + str(self._zaxis) + '\n NOTE: contains padded elements due to different scan commands!', fontsize=14, fontweight='bold')
        else:
            figure.suptitle(str(self._xaxis + ' vs. ' + self._yaxis) + '\n with z values: ' + str(self._zaxis), fontsize=14, fontweight='bold')

        self._outfile.savefig()
        self._outfile.close()
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)

    def _correctArraySize(self):
        import math as m
        # needed if the scans/the arrays have different length
        # first map the sizes:
        testmap = {len(obj) : True for obj in self._darray}
        # if there is more than one length
        if len(testmap) > 1:
            # determine the length of the longest entry
            padlength = max(testmap, key=int)
            for elem in self._darray:
                dl = padlength - len(elem)
                dlfront = m.floor(dl/2)
                dlback = m.ceil(dl/2)
                if dl > 0:
                    self._darray[self._darray.index(elem)] = np.pad(elem, (dlfront, dlback), 'constant', constant_values=(-10))
                    self._padded = True
        else: 
            return
