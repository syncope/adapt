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

# collect tracked data, spectra and calculated values; plot and save file

import numpy as np
try:
    import lmfit
except ImportError:
    print("lmfit package is not available, please install.")
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintcontrolplots(IProcess):

    def __init__(self, ptype="iintcontrolplots"):
        super(iintcontrolplots, self).__init__(ptype)
        self._trackedcolumnsPar = ProcessParameter("trackedColumns", list)
        self._rawdataPar = ProcessParameter("specdataname", str)
        self._pdfoutfilenamePar = ProcessParameter("outfilename", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdffitresultPar = ProcessParameter("fitresult", str)
        self._trapintPar = ProcessParameter("trapintname", str, optional=True)
        self._parameters.add(self._trackedcolumnsPar)
        self._parameters.add(self._rawdataPar)
        self._parameters.add(self._pdfoutfilenamePar)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._pdfobservablePar)
        self._parameters.add(self._pdffitresultPar)
        self._parameters.add(self._trapintPar)

    def initialize(self):
        self._trackedColumns = self._trackedcolumnsPar.get()
        self._rawdata = self._rawdataPar.get()
        self._pdfoutfilename = self._pdfoutfilenamePar.get()
        self._pdfmotor = self._pdfmotorPar.get()
        self._pdfobservable = self._pdfobservablePar.get()
        self._pdffitresult = self._pdffitresultPar.get()
        try:
            self._trapintname = self._trapintPar.get()
        except:
            self._trapintname = "trapezoidIntegral"
        # keep track of the data values per scan
        self._dataKeeper = {}
        self._dataKeeper[self._trapintname] = []
        self._dataKeeper[self._trapintname + "_stderr"] = []
        self._pdfoutfile = PdfPages(self._pdfoutfilename)

    def execute(self, data):
        if len(self._trackedData) > 0:
            skip = True
        for name in self._trackedColumns:
            try:
                datum = data.getData(name)
            except KeyError:
                try:
                    datum = data.getData(self._rawdata).getArray(name)
                    try:
                        self._dataKeeper[name]
                    except NameError:
                        self._dataKeeper[name] = []
                        self._dataKeeper[name+"_stderr"] = []                       
                except KeyError:
                    continue
            if isinstance(datum, np.ndarray):
                self._dataKeeper[name].append(np.mean(datum))
                self._dataKeeper[name+"_stderr"].append(np.std(datum))
            elif isinstance(datum, lmfit.model.ModelFit):
                pars = datum.params
                for parameter in pars:
                    pname = pars[parameter].name
                    pval = pars[parameter].value
                    perr = pars[parameter].stderr
                    try:
                        self._dataKeeper[pname]
                    except NameError:
                        self._dataKeeper[pname] = []
                        self._dataKeeper[pname + "_stderr"] = []
                    self._dataKeeper[pname].append(pval)
                    self._dataKeeper[pname + "_stderr"].append(perr)
        self._values.append(tmpValues)

        fitresult = data.getData(self._pdffitresult)
        try:
            trapint = data.getData(self._trapintname)
            trapinterr = data.getData(self._trapintname+"_stderr")
        except:
            pass
        self._plotstuff.append((fitresult.best_fit, trapint, trapinterr))

    def finalize(self, data):
        import math as m
        fig_size = plt.rcParams["figure.figsize"]
        # print "Current size:", fig_size
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        # plot the column data vs the fit result data (and trapezoidal integral)
        for n in range(len(self._trackedColumns)):
            plt.figure(0)
            plt.subplot(3, 1, 1)
            #~ plt.errorbar(magneticfield, amplitude, xerr=magneticfielderr, fmt='co-', ecolor='cyan', label='gaussfit')
            #~ plt.errorbar(magneticfield, amplitude, xerr=magneticfielderr, fmt='bo-', ecolor='blue', label='iint sum')
            #~ plt.title('Data analysis #'+str(self._output))
            #~ plt.legend(loc=3)
            #~ plt.subplot(3, 1, 2)
            #~ plt.errorbar(magneticfield, mean, xerr=magneticfielderr, fmt='bo-', ecolor='blue', label='cen')
            #~ plt.legend(loc=3)
            #~ plt.subplot(3, 1, 3)
            #~ plt.errorbar(magneticfield, sigma, xerr=magneticfielderr, fmt='bo-', ecolor='blue', label='cen')
            #~ plt.legend(loc=3)
            #~ plt.xlabel('Magnetic Field (T)')
    

        # plotstuff -- this must be the worst way to do it
        # determine number of figures
        #~ nof = m.ceil(len(self._plotstuff)/9)
        #~ for n in range(len(self._plotstuff)):
            #~ scannumber, motor, observable, fitresult, iint, iinterr = self._plotstuff[n]
            #~ fn, index, check = m.floor(n/9), int(n % 9) + 1, n/9.
            #~ if check > fn*nof:
                #~ fn += 1
            #~ if index == 1:
                #~ if fn > 0:
                    #~ self._pdfoutfile.savefig()
                #~ figure = plt.figure(fn)
                #~ figure.suptitle('Fit data with peak function & Integrated intensities', fontsize=14, fontweight='bold')

            #~ figure.add_subplot(3, 3, index)
            #~ plt.axis([motor[0], motor[-1], 0, 1.2 * np.amax(observable)])
            #~ plt.plot(motor, observable, 'b+')
            #~ plt.plot(motor, fitresult, 'r-')
            #~ plt.title("Scan: #" + str(scannumber))

        self._pdfoutfile.savefig()
        self._pdfoutfile.close()
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)
