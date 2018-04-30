# Copyright (C) 2016  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# this is the standard reader process
# it uses the psio library
# it is an implementation of the iProcess

try:
    from psio import dataHandler
except ImportError:
    print("[proc:stdreader] library psio not found; it will not be available!")
    pass

from adapt.iProcess import *


class stdreader(IProcess):

    def __init__(self, ptype="stdreader"):
        super(stdreader, self).__init__(ptype)
        self._inputPar = ProcessParameter("input", list)
        self._datanamePar = ProcessParameter("output", str)
        self._pathPar = ProcessParameter("path", str, None, optional=True)
        self._attributePar = ProcessParameter("attribute", str, None, optional=True)
        self._parameters.add(self._inputPar)
        self._parameters.add(self._datanamePar)
        self._parameters.add(self._pathPar)
        self._parameters.add(self._attributePar)

    def initialize(self):
        self._input = self._inputPar.get()
        self._dataname = self._datanamePar.get()
        self._path = self._pathPar.get()
        self._attribute = self._attributePar.get()

        if(self.parameter("path")):
            try:
                self.dataIterator = dataHandler.DataHandler(
                    self.parameter("input"), self.parameter("path"),
                    self.parameter("attribute"))
            except:
                raise("Can't open file, maybe a path is set, but it's not needed?!")
        else:
            self.dataIterator = dataHandler.DataHandler(self.parameter("input"))

    def execute(self, data):
        try:
            data.addData(self.parameter("output"), next(self.dataIterator))
        except StopIteration:
            print("---End of procesing ---")
            raise StopIteration

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

if __name__ == "__main__":
    sd = stdreaderdef()
    sd.setParameterValue("input", "BLBLA")
    sd.setParameterValue("output", "LALALA")
    print(" parameters of sd are: " + repr(sd.getParameters()))
    s = stdreader(sd)
    for p, k in s._parameters.items():
        print(p + " with name " + k._name + " and value: " + str(k._value))
