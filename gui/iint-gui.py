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
from adapt.processes import filter1d
from adapt.processes import subsequenceselection
from adapt.processes import curvefitting
from adapt.processes import gendatafromfunction
from adapt.processes import backgroundsubtraction
from adapt.processes import trapezoidintegration
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
        self._processedObservableName = "_processedobservable"
        self._motorname = ""
        
        # pyqt helper stuff
        self._simpleImageView = simpleDataPlot(parent=self)

        # the adapt processes
        self._specReader = specfilereader.specfilereader()
        self._observableProc = iintdefinition.iintdefinition()
        self._despiker = filter1d.filter1d()
        self._bkgSelector = subsequenceselection.subsequenceselection()
        self._bkgFitter = curvefitting.curvefitting()
        self._bkgValues = gendatafromfunction.gendatafromfunction()
        self._bkgSubtractor = backgroundsubtraction.backgroundsubtraction()
        self._trapezoidIntegrator = trapezoidintegration.trapezoidintegration()
        
        # the internal data pointer -- instance holder
        self.data = processData.ProcessData()

        # define the connections
        # input section:
        self.chooseInputFileBtn.clicked.connect(self.getAndOpenFile)
        self.dataSelectionBtn.clicked.connect(self.readDataFromFile)

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

        self.observableVIEW.clicked.connect(self.viewFirst)

        # background section
        self.subtractBkgCheckBox.stateChanged.connect(self.toggleBKGsubtraction)

        # signal section
        # processing section
        #~ self._simpleImageView.showDespiked.connect(print)

    def getAndOpenFile(self):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose spec file', '.', "SPEC files (*.spc *.spe *.spec)")
        self.inputFileLE.setText(self._file)
        
    def readDataFromFile(self):
        # clear existing all data
        self.data.clearAll()
        
        # steering of the spec reader:
        self.configureSpecReader()
        
        # call the spec reader only to get the data of choice; this is stored as a list!
        self._specReader.initialize(processData.ProcessData())
        self.data.addGlobalData("filteredrawdata", self._specReader.getSelectedData())

        # to set the displayed columns etc. one element of the selected data is needed
        _currentdata = self.data.getData("filteredrawdata")[0]
        self._currentdataLabels = _currentdata.getLabels()
        self.observableMotorLabel.setStyleSheet("color: blue;")
        self._motorname = _currentdata.getStartIdentifier(2)

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

    def defineOutput(self):
        self._outfile = QtGui.QFileDialog.getOpenFileName(self, 'Select output file', '.')

    def setObservable(self, obsindex):
        self._detname = self._currentdataLabels[obsindex]

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

    def viewFirst(self):
        # rethink logic here!
        self.calculateObservable()
        self._obsData.addData("_rawdata", self.data.getData("rawdata")[0])
        self._observableProc.execute(self._obsData)
        self._simpleImageView.show()
        self._simpleImageView.plot(self._obsData.getData(self._motorname), self._obsData.getData(self._observableName), self._obsData.getData("scannumber"))

    def calculateObservable(self):
        self.configureObservable()
        self._obsData = processData.ProcessData()
        self._observableProc.initialize(self._obsData)

    def configureSpecReader(self):
        specReaderDict = { "filename" : self._file,
                           "startScan" : self.processingStartSB.value(),
                           "endScan" : self.processingEndSB.value(),
                           "stride" : self.processingStepSB.value(),
                           "outputdata" : "_specfiledata" }
        self._specReader.setParameterValues(specReaderDict)

    def configureObservable(self):
        observableDict = { "input" : "_rawdata",
                           "motor_column" : self._motorname,
                           "detector_column" : self._detname,
                           "monitor_column" : self._monname,
                           "exposureTime_column" : self._timename,
                           "columns_log" : ["petra_beamcurrent", "lks340_outputchannela", "lks340_outputchannelb"], # CHANGE !
                           "headers_log" : ["pr1chi", "pr2chi", "ptth", "peta"], # CHANGE!
                           "observableoutput" : self._observableName,
                           "motoroutput" : self._motorname,
                           "id" : "scannumber" }
        if(self._useAttenuationFactor):
            observableDict["attenuationFactor_column"] = self._attenfname

        self._observableProc.setParameterValues(observableDict)

    def configureDespiker(self):
        despikeDict = { "input" : self._observableName, 
                        "output" : self._processedObservableName,
                        "method" : "p09despiking"}
        self._despiker.setParameterValues(despikeDict)

    def configureBKGselection(self):
        bkgSelDict = { "input" : [ self._processedObservableName, self._motorname ],
                       "output" : [ "bkgY", "bkgX" ] ,
                       "selectors": [ "selectfromstart" , "selectfromend" ],
                       "startpointnumber" : 3, # CHANGE!
                       "endpointnumber" : 3 } # CHANGE!
        self._bkgSelector.setParameterValues(bkgSelDict)

    #~ def configureBKGFitter(self):
        #~ bkfFitDict = { "model" : "linearModel",
            #~ name: lin_
                #~ xdata: bkgX
    #~ ydata: bkgY
    #~ error: None
    #~ result: bkgfitresult
        #~ self._bkgFitter.setParameterValues(bkfFitDict)

    def configureBKGDataGenerator(self):
        bkgGenDict = { "fitresult" : "bkgfitresult",
                        "xdata" :  "pth", # CHANGE!
                        "output" : "bkg" }
        self._bkgValues.setParameterValues(bkgGenDict)

    def configureBKGSubtractor(self):
        bkgSubtractDict =  { "input" : "despikedObservable",
                             "background" : "bkg",
                             "output" : "despikedSignal" }  # CHANGE!
        self._bkgSubtractor.setParameterValues(bkgSubtractDict)

    def configureTrapezoidIntegrator(self):
        trapintDict = { "motor" : "pth", # CHANGE!
                        "observable" : "observable", # CHANGE!
                        "output" : "trapint" }
        self._trapezoidIntegrator.setParameterValues(trapintDict)

class simpleDataPlot(QtGui.QDialog):
    import pyqtgraph as pg
    showDespiked = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(simpleDataPlot, self).__init__(parent)
        uic.loadUi("iint_simplePlot.ui", self)
        self.showDespikedBtn.clicked.connect(self.showDespiked.emit)

    def plot(self, xdata, ydata, scanid):
        self.scanID.setText(str(scanid))
        self.viewPart.plot(xdata, ydata, pen=None, symbol='+')

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())
