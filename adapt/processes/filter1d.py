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

# 1d filtering process -- signal shaping

from adapt import iProcess
import scipy.signal

def medianfilter1d(data):
    return scipy.signal.medfilt(data,kernel_size=3)


class filter1ddef(iProcess.IProcessDefinition):

    def __init__(self):
        super(filter1ddef, self).__init__()
        self._ptype = "filter1d"
        self.createParameter("method", "STRING")
        self.createParameter("input", "STRING")
        self.createParameter("output", "STRING")

class filter1d(iProcess.IProcess):

    def __init__(self, procDef):
        super(filter1d, self).__init__(procDef)
        self._input = self._parameters["input"]
        self._output = self._parameters["output"]
        self._methods = ["medianFilter",]
        self._method = self._parameters["method"]

    def initialize(self, data):
        if self._method in self._methods:
            return True
        else:
            raise NameError("Unknown method in filter1d process.")

    def execute(self, data):
        if self._method == "medianFilter":
            data.addData(self._output, medianfilter1d(data.getData(self._input)))
        else:
            raise NameError("Some wrong method is used in filtering.")

    def finalize(self, data):
        pass

    def check(self, data):
        pass
