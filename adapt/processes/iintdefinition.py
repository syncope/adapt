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

# create the observable for the integrated intensity

from adapt import iProcess
import numpy as np

class iintdefinitiondef(iProcess.IProcessDefinition):

    def __init__(self):
        super(iintdefinitiondef, self).__init__()
        self._ptype = "iintdefinition"
        self.createParameter("motor_colName", "STRING")
        self.createParameter("detector_colName", "STRING")
        self.createParameter("monitor_colName", "STRING")
        self.createParameter("exposureTime_colName", "STRING")
        self.createParameter("attenuationFactor_colName", "STRING", optional=True)
        self.createParameter("input", "STRING")
        self.createParameter("output", "STRING")
        
class iintdefinition(iProcess.IProcess):

    def __init__(self, procDef):
        super(iintdefinition, self).__init__(procDef)

    def initialize(self, data):
        self._input = self._parameters["input"]
        self._output = self._parameters["output"]
        self._motor = self._parameters["motor_colName"]
        self._detector = self._parameters["detector_colName"]
        self._monitor = self._parameters["monitor_colName"]
        self._exposure_time = self._parameters["exposureTime_colName"]
        self._attfac = self._parameters["attenuationFactor_colName"]

    def execute(self, data):
        datum = data.getData(self._input)
        motor = datum.getArray(self._motor)
        detector = datum.getArray(self._detector)
        monitor = datum.getArray(self._monitor)
        time = datum.getArray(self._exposure_time)
        mean_monitor = np.mean(monitor)
        if self._attfac:
            attenfac = datum.getArray(self._attfac) 
        else:
            attenfac = 1.

        observable = detector*mean_monitor*attenfac/monitor/time
        data.addData(self._output, observable)

    def finalize(self, data):
        pass

    def check(self, data):
        pass


















