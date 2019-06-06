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
try:
    import pensant.plmfit as plmfit
except ImportError:
    print("lmfit package is not available, please install.")
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintfinalization(IProcess):

    def __init__(self, ptype="iintfinalization"):
        super(iintfinalization, self).__init__(ptype)
        self._namesPar = ProcessParameter("trackedData", list)
        self._rawdataPar = ProcessParameter("specdataname", str)
        self._outfilenamePar = ProcessParameter("outfilename", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdffitresultPar = ProcessParameter("fitresult", str)
        #~ self._trapintPar = ProcessParameter("trapintname", str, optional=True)
        #~ self._bkgintegralPar = ProcessParameter("bkgintegralname", str, optional=True)
        self._parameters.add(self._namesPar)
        self._parameters.add(self._rawdataPar)
        self._parameters.add(self._outfilenamePar)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._pdfobservablePar)
        self._parameters.add(self._pdffitresultPar)
        #~ self._parameters.add(self._trapintPar)
        #~ self._parameters.add(self._bkgintegralPar)

    def initialize(self):
        self._names = self._namesPar.get()
        self._rawdata = self._rawdataPar.get()
        self._outfilename = self._outfilenamePar.get()
        self._pdfmotor = self._pdfmotorPar.get()
        self._pdfobservable = self._pdfobservablePar.get()
        self._pdffitresult = self._pdffitresultPar.get()
        #~ try:
            #~ self._trapintname = self._trapintPar.get()
        #~ except:
            #~ self._trapintname = "trapezoidIntegral"
        #~ try:
            #~ self._bkgintname = self._bkgintegralPar.get()
        #~ except:
            #~ self._bkgintname = "bkgIntegral"
        self._trackedData = []
        self._values = []

    def execute(self, data):
        skip = False
        tmpValues = []
        scannumber = None
        if len(self._trackedData) > 0:
            skip = True
        for name in self._names:
            try:
                datum = data.getData(name)
            except KeyError:
                try:
                    datum = data.getData(self._rawdata).getArray(name)
                except KeyError:
                    try:
                        datum = data.getData(self._rawdata).getCustomVar(name)
                    except:
                        print("Could not retrieve the data to track. Name: " + str(name))
                        continue
            if isinstance(datum, np.ndarray):
                tmpValues.append(np.mean(datum))
                tmpValues.append(np.std(datum))
                if not skip:
                    self._trackedData.append("mean_"+name)
                    self._trackedData.append("stderr_"+name)
            elif isinstance(datum, plmfit.model.ModelResult):
                pars = datum.params
                for parameter in pars:
                    pname = pars[parameter].name
                    pval = pars[parameter].value
                    perr = pars[parameter].stderr
                    tmpValues.append(pval)
                    tmpValues.append(perr)
                    if not skip:
                        self._trackedData.append(pname)
                        self._trackedData.append(pname + "_stderr")
            else:
                tmpValues.append(float(datum))
                if not skip:
                    self._trackedData.append(name)
        self._values.append(tmpValues)

        #~ scannumber = int(data.getData("scannumber"))
        #~ observable = data.getData(self._pdfobservable)
        #~ motor = data.getData(self._pdfmotor)
        #~ fitresult = data.getData(self._pdffitresult)
        #~ try:
            #~ trapint = data.getData(self._trapintname)
            #~ trapinterr = data.getData(self._trapintname+"_stderr")
        #~ except:
            #~ pass
        #~ try:
            #~ bkgintegral = data.getData(self._bkgintname)
        #~ except:
            #~ pass

    def finalize(self, data):
        # output file stuff
        header = ''
        for elem in self._trackedData:
            header += str(elem)
            header += "\t"
        valuearray = np.asarray(self._values)
        np.savetxt(self._outfilename, valuearray, header=header, fmt='%14.4f')

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._names)
