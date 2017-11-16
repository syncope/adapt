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

# generate points according to fitted model for the given fit results

from adapt import iProcess


class gendatafromfunctiondef(iProcess.IProcessDefinition):

    def __init__(self):
        super(gendatafromfunctiondef, self).__init__()
        self._ptype = "gendatafromfunction"
        self.createParameter("fitresult", "STRING")
        self.createParameter("xdata", "STRING")
        self.createParameter("output", "STRING")

class gendatafromfunction(iProcess.IProcess):

    def __init__(self, procDef):
        super(gendatafromfunction, self).__init__(procDef)
        self._fitresult = self._parameters["fitresult"]
        self._xdata = self._parameters["xdata"]
        self._output = self._parameters["output"]

    def initialize(self, data):
        pass

    def execute(self, data):
        fitresult = data.getData(self._fitresult)
        xdata = data.getData(self._xdata)
        data.addData(self._output, fitresult.eval(x=xdata))
        
    def finalize(self, data):
        pass

    def check(self, data):
        pass
