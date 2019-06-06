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
    import pensant.plmfit
except ImportError:
    print("lmfit package is not available, please install.")
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintcontrolplots(IProcess):

    def __init__(self, ptype="iintcontrolplots"):
        super(iintcontrolplots, self).__init__(ptype)
        self.trackeddataPar = ProcessParameter("trackedData", list)
        self._rawdataPar = ProcessParameter("specdataname", str)
        self._pdfoutfilenamePar = ProcessParameter("outfilename", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdffitresultPar = ProcessParameter("fitresult", str)
        self._trapintPar = ProcessParameter("trapintname", str, optional=True)
        self._parameters.add(self.trackeddataPar)
        self._parameters.add(self._rawdataPar)
        self._parameters.add(self._pdfoutfilenamePar)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._pdfobservablePar)
        self._parameters.add(self._pdffitresultPar)
        self._parameters.add(self._trapintPar)

    def initialize(self):
        self._trackedData = self.trackeddataPar.get()
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
        self._dataKeeper['fitamp'] = []
        self._dataKeeper['fitamperr'] = []
        self._dataKeeper['fitmean'] = []
        self._dataKeeper['fitmeanerr'] = []
        self._dataKeeper['fitsigma'] = []
        self._dataKeeper['fitsigmaerr'] = []
        self._pdfoutfile = PdfPages(self._pdfoutfilename)
        self._names = []

    def execute(self, data):
        if len(self._trackedData) > 0:
            skip = True
        for name in self._trackedData:
            try:
                datum = data.getData(name)
            except KeyError:
                try:
                    datum = data.getData(self._rawdata).getArray(name)
                    try:
                        self._dataKeeper[name]
                    except:
                        self._dataKeeper[name] = []
                        self._dataKeeper[name+"_stderr"] = []
                except KeyError:
                    continue
            if isinstance(datum, np.ndarray):
                self._names.append(name)
                self._dataKeeper[name].append(np.mean(datum))
                self._dataKeeper[name+"_stderr"].append(np.std(datum))

        pars = data.getData(self._pdffitresult).params
        for parameter in pars:
            pname = pars[parameter].name
            val = pars[parameter].value
            err = pars[parameter].stderr
            if pname == "m0_amplitude":
                self._dataKeeper['fitamp'].append(val)
                self._dataKeeper['fitamperr'].append(err)
            elif pname == "m0_center":
                self._dataKeeper['fitmean'].append(val)
                self._dataKeeper['fitmeanerr'].append(err)
            elif pname == "m0_sigma":
                self._dataKeeper['fitsigma'].append(val)
                self._dataKeeper['fitsigmaerr'].append(err)
        try:
            self._dataKeeper[self._trapintname].append(data.getData(self._trapintname))
            self._dataKeeper[self._trapintname + "_stderr"].append(data.getData(self._trapintname + "_stderr"))
        except:
            pass

    def finalize(self, data):
        self._columnNames = list(set(self._names))
        import math as m
        fig_size = plt.rcParams["figure.figsize"]
        # print "Current size:", fig_size
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        # plot the column data vs the fit result data (and trapezoidal integral)
        for n in range(len(self._columnNames)):
            name = self._columnNames[n]
            plt.figure(n+1)
            plt.title('Control plots #'+str(self._pdfoutfilename))
            plt.subplot(3, 1, 1)
            plt.errorbar(self._dataKeeper[name], self._dataKeeper['fitamp'], xerr=self._dataKeeper[name+"_stderr"], yerr=self._dataKeeper['fitamperr'],  fmt='co-', ecolor='cyan', label='gaussfit')
            plt.errorbar(self._dataKeeper[name], self._dataKeeper[self._trapintname], xerr=self._dataKeeper[name+"_stderr"], yerr=self._dataKeeper[self._trapintname + "_stderr"], fmt='bo-', ecolor='blue', label='iint sum')
            plt.legend(loc=3)
            plt.subplot(3, 1, 2)
            plt.errorbar(self._dataKeeper[name], self._dataKeeper['fitmean'], xerr=self._dataKeeper[name+"_stderr"], yerr=self._dataKeeper['fitmeanerr'],  fmt='co-', ecolor='cyan', label='gaussfit')
            plt.legend(loc=3)
            plt.subplot(3, 1, 3)
            plt.errorbar(self._dataKeeper[name], self._dataKeeper['fitsigma'], xerr=self._dataKeeper[name+"_stderr"], yerr=self._dataKeeper['fitsigmaerr'],  fmt='co-', ecolor='cyan', label='gaussfit')
            plt.legend(loc=3)
            plt.xlabel('Values of ' + str(name))
            self._pdfoutfile.savefig()

        figure = plt.figure(len(self._columnNames)+2)
        plt.scatter(self._dataKeeper['fitamp'], self._dataKeeper[self._trapintname])
        plt.xlabel('Integral values of Gauss fit')
        plt.ylabel('Interpolated trapezoid integration values')
        figure.suptitle('Scatter plot of gauss integral result and trapezoid interpolation for integrated intensities', fontsize=14, fontweight='bold')
        self._pdfoutfile.savefig()

        self._pdfoutfile.close()
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)
