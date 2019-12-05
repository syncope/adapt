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

from adapt.iProcess import *


class iintfinalization(IProcess):

    def __init__(self, ptype="iintfinalization"):
        super(iintfinalization, self).__init__(ptype)
        self._trackedheaderPar = ProcessParameter("trackedHeaders", list)
        self._trackedcolumnPar = ProcessParameter("trackedColumns", list)
        self._rawdataPar = ProcessParameter("specdataname", str)
        self._outfilenamePar = ProcessParameter("outfilename", str)
        self._pdfmotorPar = ProcessParameter("motor", str)
        self._pdfobservablePar = ProcessParameter("observable", str)
        self._pdffitresultPar = ProcessParameter("fitresult", str)
        self._parameters.add(self._trackedheaderPar)
        self._parameters.add(self._trackedcolumnPar)
        self._parameters.add(self._rawdataPar)
        self._parameters.add(self._outfilenamePar)
        self._parameters.add(self._pdfmotorPar)
        self._parameters.add(self._pdfobservablePar)
        self._parameters.add(self._pdffitresultPar)

    def initialize(self):
        self._trackedHeaders = self._trackedheaderPar.get()
        self._trackedColumns = self._trackedcolumnPar.get()
        self._rawdata = self._rawdataPar.get()
        self._outfilename = self._outfilenamePar.get()
        self._pdfmotor = self._pdfmotorPar.get()
        self._pdfobservable = self._pdfobservablePar.get()
        self._pdffitresult = self._pdffitresultPar.get()
        self._trackedDataNames = []
        self._values = []

    def execute(self, data):
        skip = False
        tmpValues = []
        # check whether the name/s have already been set
        # if they already have been set, then simply skip the addition
        if len(self._trackedDataNames) > 0:
            skip = True

        # go through header data
        for header in self._trackedHeaders:
            try:
                datum = data.getData(header)
            except KeyError:
                try:
                    datum = data.getData(self._rawdata).getCustomVar(header)
                except:
                    print("Could not retrieve the data to track. Name: " + str(header))
                    continue
            tmpValues.append(float(datum))
            if not skip:
                self._trackedDataNames.append(header)

        # go through column data
        for column in self._trackedColumns:
            try:
                datum = data.getData(self._rawdata).getArray(column)
            except KeyError:
                try:
                    datum = data.getData(self._rawdata).getCustomVar(column)
                except:
                    print("Could not retrieve the data to track. Name: " + str(column))
                    continue
            tmpValues.append(np.mean(datum))
            tmpValues.append(np.std(datum))
            if not skip:
                self._trackedData.append("mean_"+column)
                self._trackedData.append("stderr_"+column)

        # finally go through the fit result
        pars = self._pdffitresult.params
        for parameter in pars:
            pname = pars[parameter].column
            pval = pars[parameter].value
            perr = pars[parameter].stderr
            tmpValues.append(pval)
            tmpValues.append(perr)
            if not skip:
                self._trackedData.append(pname)
                self._trackedData.append(pname + "_stderr")

        self._values.append(tmpValues)

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
        data.clearCurrent(self._trackedHeaders)
        data.clearCurrent(self._trackedColumns)
        data.clearCurrent(self._pdffitresult)
