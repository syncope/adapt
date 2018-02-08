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
        
        self._specReader = specfilereader.specfilereader()
        self._specReaderDict = {}
        self._observableDict = iintdefinition.iintdefinition().getProcessParameters()
        self._procConfig = processingConfiguration.ProcessingConfiguration()
        
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
        self._useAttenuationFactor=False
        self.observableAttFaccheck.stateChanged.connect(self.toggleAttFac)
        self.observableAttFacCB.setDisabled(True)
        self.observableAttFacCB.activated.connect(self.setAttFac)
        # background section

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
        self.data = self._specReader.getSelectedData()
        self.observableMotorLabel.setText(self.data[0].getStartIdentifier(2))
        self.observableDetectorCB.clear()
        self.observableMonitorCB.clear()
        self.observableTimeCB.clear()
        self.observableAttFacCB.clear()
        self.observableDetectorCB.addItems(self.data[0].getLabels())
        self.observableMonitorCB.addItems(self.data[0].getLabels())
        self.observableTimeCB.addItems(self.data[0].getLabels())
        self.observableAttFacCB.addItems(self.data[0].getLabels())

    def defineOutput(self):
        self._outfile = QtGui.QFileDialog.getOpenFileName(self, 'Select output file', '.')

    def setObservable(self, obsname):
        self._obsname = obsname

    def setMonitor(self, monname):
        self._monname = monname

    def setTime(self, timename):
        self._timename = timename

    def toggleAttFac(self):
        self.observableAttFacCB.setDisabled(self._useAttenuationFactor)
        self._useAttenuationFactor = not self._useAttenuationFactor

    def setAttFac(self, attfacname):
        if(self._useAttenuationFactor):
            self._attenfname = attfacname

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())

