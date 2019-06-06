# Copyright (C) 2018  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# collect and print all scans with their fits into a pdf file

import numpy as np
try:
    import pensant.plmfit
except ImportError:
    print("lmfit package is not available, please install.")
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintscanplot(IProcess):

    def __init__(self, ptype="iintscanplot"):
        super(iintscanplot, self).__init__(ptype)
        self._rawdataPar = ProcessParameter("specdataname", str)
        self._pdfoutfilenamePar = ProcessParameter("outfilename", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdffitresultPar = ProcessParameter("fitresult", str)
        self._parameters.add(self._rawdataPar)
        self._parameters.add(self._pdfoutfilenamePar)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._pdfobservablePar)
        self._parameters.add(self._pdffitresultPar)

    def initialize(self):
        self._rawdata = self._rawdataPar.get()
        self._pdfoutfilename = self._pdfoutfilenamePar.get()
        self._pdfmotor = self._pdfmotorPar.get()
        self._pdfobservable = self._pdfobservablePar.get()
        self._pdffitresult = self._pdffitresultPar.get()
        self._values = []
        self._plotstuff = []
        self._pdfoutfile = PdfPages(self._pdfoutfilename)

    def execute(self, data):
        scannumber = int(data.getData("scannumber"))
        observable = data.getData(self._pdfobservable)
        motor = data.getData(self._pdfmotor)
        fitresult = data.getData(self._pdffitresult)
        self._plotstuff.append((scannumber, motor, observable, fitresult.best_fit))

    def finalize(self, data):
        import math as m
        fig_size = plt.rcParams["figure.figsize"]
        # print "Current size:", fig_size
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        # plotstuff -- this must be the worst way to do it
        # determine number of figures
        nof = m.ceil(len(self._plotstuff)/9)
        for n in range(len(self._plotstuff)):
            scannumber, motor, observable, fitresult = self._plotstuff[n]
            fn, index, check = m.floor(n/9), int(n % 9) + 1, n/9.
            if check > fn*nof:
                fn += 1
            if index == 1:
                if fn > 0:
                    self._pdfoutfile.savefig()
                figure = plt.figure(fn)
                figure.suptitle('Fit data with peak function & Integrated intensities', fontsize=14, fontweight='bold')

            figure.add_subplot(3, 3, index)
            plt.axis([motor[0], motor[-1], 0, 1.2 * np.amax(observable)])
            plt.plot(motor, observable, 'b+')
            plt.plot(motor, fitresult, 'r-')
            plt.title("Scan: #" + str(scannumber))

        self._pdfoutfile.savefig()
        self._pdfoutfile.close()
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)
