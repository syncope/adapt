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

from core import iProcess


class globaldatadef(iProcess.IProcessDefinition):

    def __init__(self):
        super(globaldatadef, self).__init__()
        self._ptype = "globaldata"
        self.createParameter("wavelength", "FLOAT", optional=True)
        self.createParameter("sdd", "FLOAT", optional=True)
        self.createParameter("unit", "STRING", optional=True)


class globaldata(iProcess.IProcess):

    def __init__(self, pparameters):
        super(globaldata, self).__init__(pparameters)

    def initialize(self, data):
        data.addGlobalData("wavelength", self.parameter("wavelength"))
        data.addGlobalData("sdd", self.parameter("sdd"))
        data.addGlobalData("unit", self.parameter("unit"))


if __name__ == "__main__":
    gdd = globaldatadef()
    print(" gdd has parameters: " + repr(gdd.getParameters()))
