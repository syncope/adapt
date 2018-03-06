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

# special for p09: collect and output results

import numpy as np
import lmfit

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintfinalization(IProcess):

    def __init__(self, ptype="iintfinalization"):
        super(iintfinalization, self).__init__(ptype)
        self._namesPar = ProcessParameter("outputs", list)
        self._outfilenamePar = ProcessParameter("outfilename", str)
        self._pdfoutfilenamePar = ProcessParameter("pdffilename", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdffitresultPar = ProcessParameter("fitresult", str)
        self._parameters.add(self._namesPar)
        self._parameters.add(self._outfilenamePar)
        self._parameters.add(self._pdfoutfilenamePar)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._pdfobservablePar)
        self._parameters.add(self._pdffitresultPar)

    def initialize(self):
        self._names = self._namesPar.get()
        self._outfilename = self._outfilenamePar.get()
        self._pdfoutfilename = self._pdfoutfilenamePar.get()
        self._pdfmotor = self._pdfmotorPar.get()
        self._pdfobservable = self._pdfobservablePar.get()
        self._pdffitresult = self._pdffitresultPar.get()
        self._headers = []
        self._values = []
        self._plots = []
        self._pdfoutfile = PdfPages(self._pdfoutfilename + ".pdf")

    def execute(self, data):
        skip = False
        tmpValues = []
        scannumber = None
        if len(self._headers) > 0:
            skip = True
        for name in self._names:
            datum = data.getData(name)
            if name == "scannumber":
                scannumber = int(datum)
            if isinstance(datum, np.ndarray):
                tmpValues.append(np.mean(datum))
                tmpValues.append(np.std(datum))
                if not skip:
                    self._headers.append("mean_"+name)
                    self._headers.append("stderr_"+name)
            elif isinstance(datum, lmfit.model.ModelFit):
                pars = datum.params
                for parameter in pars:
                    pname = pars[parameter].name
                    pval = pars[parameter].value
                    perr = pars[parameter].stderr
                    tmpValues.append(pval)
                    tmpValues.append(perr)
                    if not skip:
                        self._headers.append(pname)
                        self._headers.append(pname + "_stderr")
            else:
                tmpValues.append(datum)
                if not skip:
                    self._headers.append(name)
        self._values.append(tmpValues)

        # plotstuff
        obs = data.getData(self._pdfobservable)
        mot = data.getData(self._pdfmotor)
        fr = data.getData(self._pdffitresult)
        print(fr.fit_report())
        plt.plot(mot,obs,'bo')
        plt.plot(mot, fr.best_fit, 'r-')
        plt.title("Scan: " + str(scannumber))
        self._pdfoutfile.savefig()
        plt.close()

    def finalize(self, data):
        header = ''
        for elem in self._headers:
            header += str(elem)
            header += "\t"
        valuearray = np.asarray(self._values)
        np.savetxt(self._outfilename, valuearray, header=header, fmt='%14.4f')
        self._pdfoutfile.close()

    def check(self, data):
        pass
