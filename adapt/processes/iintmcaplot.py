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


class iintmcaplot(IProcess):

    def __init__(self, ptype="iintmcaplot"):
        super(iintmcaplot, self).__init__(ptype)
        self._inputPar = ProcessParameter("input", str)
        self._outfilenamePar = ProcessParameter("outfilename", str)
        self._parameters.add(self._inputPar)
        self._parameters.add(self._outfilenamePar)

    def initialize(self):
        self._input = self._inputPar.get()
        self._outfilename = self._outfilenamePar.get()
        self._darray = []
        self._values = []
        self._outfile = PdfPages(self._outfilename)

    def execute(self, data):
        try:
            self._name = data.getData("MCAName")
            self._values = data.getData("MCA")
            print("i've got something: " + str(self._name))
        except:
            print("I've got nothing in the MCA department.")


    def finalize(self, data):
        import math as m
        fig_size = plt.rcParams["figure.figsize"]
        # print "Current size:", fig_size
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        nof = m.ceil(len(self._values)/9)
        for n in range(len(self._values)):
            histo = self._values[n]
            fn, index, check = m.floor(n/9), int(n % 9) + 1, n/9.
            if check > fn*nof:
                fn += 1
            if index == 1:
                if fn > 0:
                    self._outfile.savefig()
                figure = plt.figure(fn)
                #~ figure.suptitle('Fit data with peak function & Integrated intensities', fontsize=14, fontweight='bold')

            figure.add_subplot(3, 3, index)
            #~ plt.title("MCA of scanpoint " + str(n))
            #~ plt.axis([0,len(histo), 0, 1.1 * np.amax(histo)])
            plt.plot(self._values[n])


        self._outfile.savefig()
        self._outfile.close()
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)
