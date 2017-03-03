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

import dataHandler
from core import iProcess


class stdreaderdef(iProcess.IProcessDefinition):

    def __init__(self):
        super(stdreaderdef, self).__init__()
        self._ptype = "stdreader"
        self.createParameter("input", "STRINGLIST")
        self.createParameter("output", "STRING")
        self.createParameter("path", "STRING", optional=True)
        self.createParameter("attribute", "STRING", optional=True)

class stdreader(iProcess.IProcess):

    def __init__(self, procDef):
        super(stdreader, self).__init__(procDef)

    def initialize(self, data):
        dHandler = dataHandler.DataHandler()
        if(self.parameter("path")):
            try:
                self.dataIterator = dHandler.create_reader(
                    self.parameter("input"), self.parameter("path"),
                    self.parameter("attribute"))
            except:
                raise("Can't open file, maybe a path is set, but it's not needed?!")
        else:
            self.dataIterator = dHandler.create_reader(self.parameter("input"))

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

if __name__ == "__main__":
    sd = stdreaderdef()
    sd.setParameterValue("input", "BLBLA")
    sd.setParameterValue("output", "LALALA")
    print(" parameters of sd are: " + repr(sd.getParameters()))
    s = stdreader(sd)
    for p, k in s._parameters.items():
        print(p + " with name " + k._name + " and value: " + str(k._value))
