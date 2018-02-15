# Copyright (C) 2017-8  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in version 2
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


# recent re-structuring: use psio library for reading spec files

try:
    from psio import dataHandler
except ImportError:
    print("[proc:stdreader] library psio not found; it will not be available!")
    pass

from adapt.iProcess import *


class specfilereader(IProcess):

    def __init__(self, ptype="specfilereader"):
        super(specfilereader, self).__init__(ptype)

        self._inPar = ProcessParameter("filename", str)
        self._outPar = ProcessParameter("outputdata", str)
        self._startScanPar = ProcessParameter("startScan", int, -1, optional=True)
        self._endScanPar = ProcessParameter("endScan", int, float('inf'), optional=True)
        self._stridePar = ProcessParameter("stride", int, 1, optional=True)
        self._parameters.add(self._inPar)
        self._parameters.add(self._outPar)
        self._parameters.add(self._startScanPar)
        self._parameters.add(self._endScanPar)
        self._parameters.add(self._stridePar)
        self._selectedData = []

    def initialize(self, data):
        self.data = dataHandler.DataHandler(self._inPar.get(), typehint="spec").getFileHandler().getAll()
        self._start = self._startScanPar.get()
        self._end = self._endScanPar.get()
        self._stride = self._stridePar.get()
        self._selectData()
        
        self.dataIterator = iter(self._selectedData)

    def execute(self, data):
        # read next entry from spec file, 
        # put scandata object to common memory
        try:
            data.addData(self._outPar.get(), next(self.dataIterator))
        except StopIteration:
            print("---End of data reading from spec file ---")
            raise StopIteration

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def _selectData(self):
        self._selectedData = []
        for d in self.data:
            if self._start <= d.getScanNumber() <= self._end:
                self._selectedData.append(d)

    def getSelectedData(self):
        return self._selectedData
