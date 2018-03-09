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

import numpy as np

from adapt.iProcess import *


class iintdefinition(IProcess):

    def __init__(self, ptype="iintdefinition"):
        super(iintdefinition, self).__init__(ptype)
        self._inputPar = ProcessParameter("input", str)
        self._motorPar = ProcessParameter("motor_column", str)
        self._detectorPar = ProcessParameter("detector_column", str)
        self._monitorPar = ProcessParameter("monitor_column", str)
        self._exposure_timePar = ProcessParameter("exposureTime_column", str)
        self._attfacPar = ProcessParameter("attenuationFactor_column", str, optional=True)
        self._trackedstuffPar = ProcessParameter("columns_log", list)
        self._tracked_headersPar = ProcessParameter("headers_log", list)
        self._observableoutputPar = ProcessParameter("observableoutput", str)
        self._motorOutPar = ProcessParameter("motoroutput", str)
        self._idPar = ProcessParameter("id", str)
        self._parameters.add(self._inputPar)
        self._parameters.add(self._motorPar)
        self._parameters.add(self._detectorPar)
        self._parameters.add(self._monitorPar)
        self._parameters.add(self._exposure_timePar)
        self._parameters.add(self._attfacPar)
        self._parameters.add(self._trackedstuffPar)
        self._parameters.add(self._tracked_headersPar)
        self._parameters.add(self._observableoutputPar)
        self._parameters.add(self._motorOutPar)
        self._parameters.add(self._idPar)

    def initialize(self):
        self._input = self._inputPar.get()
        self._motor = self._motorPar.get()
        self._detector = self._detectorPar.get()
        self._monitor =self._monitorPar.get()
        self._exposure_time = self._exposure_timePar.get()
        self._attfac = self._attfacPar.get()
        self._trackedstuff = self._trackedstuffPar.get()
        self._tracked_headers = self._tracked_headersPar.get()
        self._observableoutput = self._observableoutputPar.get()
        self._motorOut = self._motorOutPar.get()
        self._id = self._idPar.get()

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
        if self._id == "scannumber":
            data.addData(self._id, datum.getScanNumber())
        else:
            data.addData(self._id, data.getCustomVar(self._id))

    def finalize(self, data):
        pass

    def check(self, data):
        pass


class iintdefinitionGUI(QtGui.QWidget):
    execute = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(iintdefinitionGUI, self).__init__(parent)
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        formfile = os.path.join(dir_path, "ui/iintdefinition.ui")
        uic.loadUi(formfile, self)
        #~ self.observableDetectorCB.activated.connect(self.setObservable)
        #~ self.observableMonitorCB.activated.connect(self.setMonitor)
        #~ self.observableTimeCB.activated.connect(self.setTime)
        #~ self._useAttenuationFactor = False
        #~ self.observableAttFaccheck.stateChanged.connect(self.toggleAttFac)
        #~ self.observableAttFacCB.setDisabled(True)
        #~ self.observableAttFacCB.activated.connect(self.setAttFac)
        #~ self.observableCalcBtn.clicked.connect(self.calculateObservable)
        #~ self.despikeCheckBox.stateChanged.connect(self.toggleDespiking)
        #~ self.applyDespikeBtn.clicked.connect(self.despike)
        self._iintDefDict = {}

    def getParameterDict(self):
        return self._iintDefDict

    def setParameterDict(self, paramDict):
         self._iintDefDict = paramDict

    def emittit(self):
        #~ self._specReaderDict["filename"] =  self._file
        #~ self._specReaderDict["scanlist"] = self.scanSelectionInput.text()
        #~ self._specReaderDict["outputdata"] = "_specfiledata"
        self.execute.emit(1)
















