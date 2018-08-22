# Copyright (C) 2017-8  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# adapt is a programmable data processing toolkit
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

from PyQt4 import QtCore, QtGui, uic
from adapt.utilities import getUIFile


class iintObservableDefinition(QtGui.QWidget):
    observableDicts = QtCore.pyqtSignal(dict, dict, dict)
    doDespike = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(iintObservableDefinition, self).__init__(parent)
        self.setWindowTitle("Observable definition")
        uic.loadUi(getUIFile("iintobservable.ui"), self)
        self._obsDict = {}
        self._despikeDict = {}
        self._trapintDict = {}
        self.observableDetectorCB.currentIndexChanged.connect(self.setObservable)
        self.observableMonitorCB.currentIndexChanged.connect(self.setMonitor)
        self.observableTimeCB.currentIndexChanged.connect(self.setTime)
        self._useAttenuationFactor = False
        self.observableAttFaccheck.stateChanged.connect(self.toggleAttFac)
        self.observableAttFacCB.setDisabled(True)
        self.observableAttFacCB.currentIndexChanged.connect(self.setAttFac)
        self.despikeCheckBox.stateChanged.connect(self.toggleDespiking)
        self._despike = False
        self._notEnabled(True)
        self.obsNextBtn.clicked.connect(self.emittit)
        self._observableName = 'observable'
        self.observableMotorLabel.setToolTip("The motor taken from the scan command for the chosen series of scans.")
        self.label.setToolTip("The shorthand notation for the used formula to calculate the number of counts at the given motor position.")
        self.observableDetectorCB.setToolTip("Chose the correct detector entry from the scan file information.")
        self.observableMonitorCB.setToolTip("Chose the correct monitor name from the scan file information.")
        self.observableTimeCB.setToolTip("Chose the correct time entry from the scan file information.")
        self.observableAttFaccheck.setToolTip("Chose the correct entry from the scan file information for an attenuation factor.")
        self.observableAttFacCB.setToolTip("Check the box to enable the choice of an attenuation factor entry.")
        self.despikeCheckBox.setToolTip("Check the box to run a despiking/filtering algorithm on the scan data to dampen spikes/noise fluctuation.")
        self.obsNextBtn.setToolTip("Once everything is set, click this button to perform the calculaion of the observable data and open a display." )

    def _defaultSettings(self):
        self._obsDict = {}
        self._despikeDict = {}
        self._trapintDict = {}
        self._useAttenuationFactor = False
        self.observableAttFacCB.setDisabled(True)
        self.despikeCheckBox.setChecked(False)
        self._despike = False
        self._notEnabled(True)
        self._observableName = 'observable'

    def reset(self):
        self._defaultSettings()

    def activate(self):
        self._notEnabled(False)

    def passInfo(self, dataobject):
        if dataobject == None:
            self._notEnabled(True)
            return
        else:
            self._notEnabled(False)

        self._currentdataLabels = dataobject.getLabels()
        self.observableMotorLabel.setStyleSheet("color: blue;")
        self._motorname = dataobject.getMotorName()

        # now set the texts and labels
        self.observableMotorLabel.setText(self._motorname)
        self.observableDetectorCB.clear()
        self.observableMonitorCB.clear()
        self.observableTimeCB.clear()
        self.observableAttFacCB.clear()
        self.observableDetectorCB.addItems(self._currentdataLabels)
        self.observableMonitorCB.addItems(self._currentdataLabels)
        self.observableTimeCB.addItems(self._currentdataLabels)
        self.observableAttFacCB.addItems(self._currentdataLabels)
    
    def _notEnabled(self, state):
        self.observableMotorLabel.setDisabled(state)
        self.observableDetectorCB.setDisabled(state)
        self.observableMonitorCB.setDisabled(state)
        self.observableTimeCB.setDisabled(state)
        self.observableAttFaccheck.setDisabled(state)
        self.despikeCheckBox.setDisabled(state)
        self.obsNextBtn.setDisabled(state)

    def toggleAttFac(self):
        self.observableAttFacCB.setDisabled(self._useAttenuationFactor)
        self._useAttenuationFactor = not self._useAttenuationFactor

    def setObservable(self, obsindex):
        self._detname = self._currentdataLabels[obsindex]

    def setMonitor(self, monindex):
        self._monname = self._currentdataLabels[monindex]

    def setTime(self, timeindex):
        self._timename = self._currentdataLabels[timeindex]

    def setAttFac(self, attfacindex):
        if(self._useAttenuationFactor):
            self._attenfname = self._currentdataLabels[attfacindex]

    def toggleDespiking(self):
        self._despike = not self._despike
        self.doDespike.emit(self._despike)

    def activateDespikingBox(self):
        self.despikeCheckBox.setDisabled(False)

    def emittit(self):
        self._obsDict["type"] = "iintdefinition"
        self._obsDict["input"] = "rawdata"
        self._obsDict["motor_column"] = self._motorname
        self._obsDict["detector_column"] = self._detname
        self._obsDict["monitor_column"] = self._monname
        self._obsDict["exposureTime_column"] = self._timename
        self._obsDict["output"] = self._observableName
        self._obsDict["id"] = "scannumber"
        if(self._useAttenuationFactor):
            self._obsDict["attenuationFactor_column"] = self._attenfname

        if(self._despike):
            self._despikeDict["type"] = "filter1d"
            self._despikeDict["method"] = "p09despiking"
            self._despikeDict["input"] = "observable"
            self._despikeDict["output"] = "despikedObservable"
        self._trapintDict["type"] = "trapezoidintegration"
        self._trapintDict["motor"] = self._motorname
        self._trapintDict["observable"] = "signalObservable"
        self._trapintDict["output"] = "trapezoidIntegral"
        
        self.observableDicts.emit(self._obsDict, self._despikeDict, self._trapintDict)

    def setParameterDicts(self, obsDict, despDict):
        self.observableMotorLabel.setStyleSheet("color: blue;")
        self.observableMotorLabel.setText(obsDict["motor_column"])
        # first get index of element
        index = self.observableDetectorCB.findText(obsDict["detector_column"], QtCore.Qt.MatchExactly) 
        if index >= 0:
            self.observableDetectorCB.setCurrentIndex(index)

        index = self.observableMonitorCB.findText(obsDict["monitor_column"], QtCore.Qt.MatchExactly) 
        if index >= 0:
            self.observableMonitorCB.setCurrentIndex(index)

        index = self.observableTimeCB.findText(obsDict["exposureTime_column"], QtCore.Qt.MatchExactly) 
        if index >= 0:
            self.observableTimeCB.setCurrentIndex(index)

        if ( despDict != {} ):
            self.despikeCheckBox.setChecked(True)
