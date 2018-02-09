# Copyright (C) 2017  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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


import sys
from PyQt4 import QtCore, QtGui, uic

from adapt import processingConfiguration
from adapt.processes import specfilereader
from adapt.processes import iintdefinition
from adapt import processData


__version__ ="0.0.1alpha"

class iintGUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(iintGUI, self).__init__(parent)
        uic.loadUi("iint-gui.ui", self)
        # placeholder objects:
        self._headerlist = []
        self._columnlist = []
        self._despike = False
        self._subtractBackground = False
        self._observableName = "_observable"
        
        self._specReader = specfilereader.specfilereader()
        self._specReaderDict = {}
        self._observableProc = iintdefinition.iintdefinition()
        self._observableDict = {}
        
        # define the connections
        # input section:
        self.chooseInputFileBtn.clicked.connect(self.getAndOpenFile)
        self.dataSelectionBtn.clicked.connect(self.readFile)

        # output section
        self.chooseOutputFileBtn.clicked.connect(self.defineOutput)

        # observable section
        self.observableDetectorCB.activated.connect(self.setObservable)
        self.observableMonitorCB.activated.connect(self.setMonitor)
        self.observableTimeCB.activated.connect(self.setTime)
        self._useAttenuationFactor = False
        self.observableAttFaccheck.stateChanged.connect(self.toggleAttFac)
        self.observableAttFacCB.setDisabled(True)
        self.observableAttFacCB.activated.connect(self.setAttFac)

        self.despikeCheckBox.stateChanged.connect(self.toggleDespiking)

        self.observableVIEW.clicked.connect(self.view)

        # background section
        self.subtractBkgCheckBox.stateChanged.connect(self.toggleBKGsubtraction)

        # signal section
        # processing section

    def getAndOpenFile(self):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose spec file', '.', "SPEC files (*.spc *.spe *.spec)")
        self.inputFileLE.setText(self._file)
        
    def readFile(self):
        self._specReaderDict["filename"] = self._file
        self._specReaderDict["startScan"] = self.processingStartSB.value()
        self._specReaderDict["endScan"] = self.processingEndSB.value()
        self._specReaderDict["stride"] = self.processingStepSB.value()
        self._specReaderDict["outputdata"] = "_specfiledata"
        self._specReader.setParameterValues(self._specReaderDict)
        self._updateDependents()

    def _updateDependents(self):
        # update everything that depends on new available data selection
        self._specReader.initialize(processData.ProcessData())
        self.data = processData.ProcessData()
        self.data.addData("rawdata", self._specReader.getSelectedData())
        self._currentdata = self.data.getData("rawdata")[0]
        self._currentdataLabels = self._currentdata.getLabels()
        self.observableMotorLabel.setStyleSheet("color: blue;")
        self._motorname = self._currentdata.getStartIdentifier(2)
        self.observableMotorLabel.setText(self._motorname)
        self.observableDetectorCB.clear()
        self.observableMonitorCB.clear()
        self.observableTimeCB.clear()
        self.observableAttFacCB.clear()
        self.observableDetectorCB.addItems(self._currentdataLabels)
        self.observableMonitorCB.addItems(self._currentdataLabels)
        self.observableTimeCB.addItems(self._currentdataLabels)
        self.observableAttFacCB.addItems(self._currentdataLabels)
        
    def defineOutput(self):
        self._outfile = QtGui.QFileDialog.getOpenFileName(self, 'Select output file', '.')

    def setObservable(self, obsindex):
        self._obsname = self._currentdataLabels[obsindex]

    def setMonitor(self, monindex):
        self._monname = self._currentdataLabels[monindex]

    def setTime(self, timeindex):
        self._timename = self._currentdataLabels[timeindex]

    def toggleAttFac(self):
        self.observableAttFacCB.setDisabled(self._useAttenuationFactor)
        self._useAttenuationFactor = not self._useAttenuationFactor

    def setAttFac(self, attfacindex):
        if(self._useAttenuationFactor):
            self._attenfname = self._currentdataLabels[attfacindex]

    def toggleDespiking(self):
        self._despike = not self._despike

    def toggleBKGsubtraction(self):
        self._subtractBackground = not self._subtractBackground

    def view(self):
        self.calculateObservable()
        self._obsData.addData("_rawdata", self.data.getData("rawdata")[0])
        self._observableProc.execute(self._obsData)
        gui = simpleDataPlot(parent=self)
        gui.show()
        print(" accessing observable: " + str(self._obsData.getData(self._observableName)))
        print(" accessing motor : " + str(self._obsData.getData(self._motorname))) # THIS IS WHERE IT FAILS.. WHAT'S GOING WRONG??
        gui.plot(self._obsData.getData(self._motorname), self._obsData.getData(self._observableName))

    def calculateObservable(self):
        self._observableDict["input"] = "_rawdata"
        self._observableDict["motor_column"] = self._motorname
        self._observableDict["detector_column"] = self._obsname
        self._observableDict["monitor_column"] = self._monname
        self._observableDict["exposureTime_column"] = self._timename
        if(self._useAttenuationFactor):
            self._observableDict["attenuationFactor_column"] = self._attenfname
        self._observableDict["columns_log"] = [ "petra_beamcurrent", "lks340_outputchannela", "lks340_outputchannelb" ]
        self._observableDict["headers_log"] = [ "pr1chi", "pr2chi", "ptth", "peta" ]
        self._observableDict["observableoutput"] = self._observableName
        self._observableDict["motoroutput"] = "bla"
        self._observableDict["id"] = "scannumber"
        self._observableProc.setParameterValues(self._observableDict)
        self._obsData = processData.ProcessData()
        self._observableProc.initialize(self._obsData)
        print(" types? : motor: " + str(type(self._motorname)) + " and observ: " + str(type(self._obsname)))

class simpleDataPlot(QtGui.QDialog):
    import pyqtgraph as pg
    
    def __init__(self, parent=None):
        super(simpleDataPlot, self).__init__(parent)
        uic.loadUi("iint_simplePlot.ui", self)
        
    def plot(self, xdata, ydata):
        self.viewPart.plot(xdata, ydata, pen=None, symbol='o')


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())

