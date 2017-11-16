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
        self.createParameter("input", "STRING")
        self.createParameter("motor_column", "STRING")
        self.createParameter("detector_column", "STRING")
        self.createParameter("monitor_column", "STRING")
        self.createParameter("exposureTime_column", "STRING")
        self.createParameter("attenuationFactor_column", "STRING", optional=True)
        self.createParameter("columns_log", "STRINGLIST")
        self.createParameter("headers_log", "STRINGLIST")
        self.createParameter("observableoutput", "STRING")
        self.createParameter("motoroutput", "STRING")        

class iintdefinition(iProcess.IProcess):

    def __init__(self, procDef):
        super(iintdefinition, self).__init__(procDef)

    def initialize(self, data):
        self._input = self._parameters["input"]
        self._motor = self._parameters["motor_column"]
        self._detector = self._parameters["detector_column"]
        self._monitor = self._parameters["monitor_column"]
        self._exposure_time = self._parameters["exposureTime_column"]
        self._attfac = self._parameters["attenuationFactor_column"]
        self._trackedstuff = self._parameters["columns_log"]
        self._tracked_headers = self._parameters["headers_log"]
        self._observableoutput = self._parameters["observableoutput"]
        self._motorOut = self._parameters["motoroutput"]

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
        data.addData(self._observableoutput, observable)
        data.addData(self._motorOut, motor)
        trackedcolumns = [ datum.getArray(name) for name in self._trackedstuff ]

        for key in self._trackedstuff:
            data.addData(key, datum.getArray(key))
        for key in self._tracked_headers:
            data.addData(key, datum.getCustomVar(key))

    def finalize(self, data):
        pass

    def check(self, data):
        pass


















