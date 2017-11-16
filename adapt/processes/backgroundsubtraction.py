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

# one of the most simple process: subtract two np.ndarrays, store result

from adapt import iProcess


class backgroundsubtractiondef(iProcess.IProcessDefinition):

    def __init__(self):
        super(backgroundsubtractiondef, self).__init__()
        self._ptype = "backgroundsubtraction"
        self.createParameter("input", "STRING")
        self.createParameter("output", "STRING")
        self.createParameter("background", "STRING")

class backgroundsubtraction(iProcess.IProcess):

    def __init__(self, procDef):
        super(backgroundsubtraction, self).__init__(procDef)
        self._input = self._parameters["input"]
        self._output = self._parameters["output"]
        self._background = self._parameters["background"]

    def initialize(self, data):
        pass

    def execute(self, data):
        element = data.getData(self._input)
        background = data.getData(self._background)
        
        data.addData(self._output, (element - background))

    def finalize(self, data):
        pass

    def check(self, data):
        pass
