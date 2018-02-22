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
from adapt.utilities import iintData

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

        # the central data element for the gui; specific to iint!
        self._dataKeeper = {}
        
        # pyqt helper stuff
        self._simpleImageView = simpleDataPlot(parent=self)
        self._simpleImageView.showNext.connect(self.incrementCurrentScanID)
        self._simpleImageView.showPrevious.connect(self.decrementCurrentScanID)
        self._simpleImageView.showNumber.connect(self.setCurrentScanID)
        self._fitPanel = firstFitPanel(parent=self, dataview=self._simpleImageView)


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
        self.observableCalcBtn.clicked.connect(self.calculateObservable)
        self.despikeCheckBox.stateChanged.connect(self.toggleDespiking)
        self.applyDespikeBtn.clicked.connect(self.despike)
        self.observableVIEW.clicked.connect(self.viewSimple)

        # background section
        self.subtractBkgCheckBox.stateChanged.connect(self.toggleBKGsubtraction)
        self.bkgStartPointsSB.setKeyboardTracking(False)
        self.bkgStartPointsSB.valueChanged.connect(self.selectStartBKG)
        self.bkgEndPointsSB.setKeyboardTracking(False)
        self.bkgEndPointsSB.valueChanged.connect(self.selectEndBKG)
        self.fitBKGbtn.clicked.connect(self.selectAndFitBackground)
        self.subtractBkgCheckBox.stateChanged.connect(self.subtractBackground)
        
        # signal section
        self.openFitPanelPushBtn.clicked.connect(self.showFitPanel)
        # processing section

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
        theRawData = self._specReader.getData()

        # to set the displayed columns etc. one element of the selected data is needed
        exampleData = theRawData[0]
        self._currentdataLabels = exampleData.getLabels()
        self.observableMotorLabel.setStyleSheet("color: blue;")
        self._motorname = exampleData.getStartIdentifier(2)
        
        for scan in theRawData:
            scanid = scan.getScanNumber()
            newdata = iintData.IintData(scanid = scanid, 
                                        scantype = scan.getStartIdentifier(1),
                                        motor = self._motorname)
            newdata.setRaw(scan)
            newdata.setMotor(scan.getArray(self._motorname))
            self._dataKeeper[scanid] = newdata

        # create a sorted bookkeeping list of the scan ids  to allow easier handling
        self._dKidlist = list(self._dataKeeper.keys())
        self._dKidlist.sort()
        self.setCurrentScanID(exampleData.getScanNumber())

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
        self.applyDespikeBtn.setEnabled(self._despike)

    def toggleBKGsubtraction(self):
        self._subtractBackground = not self._subtractBackground

    def viewSimple(self):
        self._simpleImageView.setMinimum(self._dKidlist[0])
        self._simpleImageView.setMaximum(self._dKidlist[-1])
        self._simpleImageView.show()
        self._simpleImageView.plot( xdata= self._currentScan.getMotor(), 
                                    ydata = self._currentScan.getObservable(),
                                    scanid= self._currentScan.getScanID())
        despike = self._currentScan.getDespiked()
        if(despike is not None):
            self._simpleImageView.addDespike(self._currentScan.getMotor(),despike )

    def setCurrentScanID(self, identifier):
        self._currentScan = self._dataKeeper[identifier]

    def incrementCurrentScanID(self):
        try:
            self.setCurrentScanID(self._currentScan.getScanID() + 1)
        except KeyError:
            self.setCurrentScanID(self._dKidlist[0])
        self.viewSimple()

    def decrementCurrentScanID(self):
        try:
            self.setCurrentScanID(self._currentScan.getScanID() - 1)
        except KeyError:
            self.setCurrentScanID(self._dKidlist[-1])
        self.viewSimple()

    def configureSpecReader(self):
        specReaderDict = { "filename" : self._file,
                           "scanlist" : self.scanSelectionInput.text(),
                           #~ "stride" : self.processingStepSB.value(),
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

    def calculateObservable(self):
        self.configureObservable()
        obsData = processData.ProcessData()
        self._observableProc.initialize(obsData)
        for scan in self._dataKeeper.values():
            obsData.addData("_rawdata", scan.getRaw())
            self._observableProc.execute(obsData)
            scan.setObservable(obsData.getData(self._observableName))
            scan.setMotor(obsData.getData(self._motorname))
            obsData.clearCurrent()

    def configureDespiker(self):
        despikeDict = { "input" : self._observableName, 
                        "output" : self._processedObservableName,
                        "method" : "p09despiking"}
        self._despiker.setParameterValues(despikeDict)

    def despike(self):
        self.configureDespiker()
        despData = processData.ProcessData()
        self._despiker.initialize(despData)
        for scan in self._dataKeeper.values():
            despData.addData(self._observableName, scan.getObservable())
            self._despiker.execute(despData)
            scan.setDespiked(despData.getData(self._processedObservableName))
            despData.clearCurrent()

    def selectStartBKG(self, value):
        self._bkgStartPoints  = value

    def selectEndBKG(self, value):
        self._bkgEndPoints  = value

    def configureBKGselection(self):
        bkgSelDict = { "input" : [ self._processedObservableName ,self._motorname ],
                       "output" : [ "bkgY", "bkgX" ] ,
                       "selectors": [ "selectfromstart" , "selectfromend" ],
                       "startpointnumber" : self._bkgStartPoints, # CHANGE!
                       "endpointnumber" : self._bkgEndPoints } # CHANGE!
        self._bkgSelector.setParameterValues(bkgSelDict)

    def selectAndFitBackground(self):
        self.configureBKGselection()
        self.configureBKGFitter()
        bkgData = processData.ProcessData()
        self._bkgSelector.initialize(bkgData)
        self._bkgFitter.initialize(bkgData)
        for scan in self._dataKeeper.values():
            bkgData.addData(self._processedObservableName, scan.getDespiked())
            bkgData.addData(self._motorname, scan.getMotor())
            self._bkgSelector.execute(bkgData)
            self._bkgFitter.execute(bkgData)
            scan.setBackground(bkgData.getData("bkgfitresult"))
            bkgData.clearCurrent()
        self.subtractBkgCheckBox.setDisabled(False)

    def configureBKGFitter(self):
        bkfFitDict = { "model" : { "linearModel": { "name" : "lin_"}},
                       "xdata" : "bkgX",
                       "ydata" : "bkgY",
                       "result": "bkgfitresult"}
        self._bkgFitter.setParameterValues(bkfFitDict)

    def configureBKGDataGenerator(self):
        bkgGenDict = { "fitresult" : "bkgfitresult",
                        "xdata" :  "pth", # CHANGE!
                        "output" : "bkg" }
        self._bkgValues.setParameterValues(bkgGenDict)

    def configureBKGSubtractor(self):
        bkgSubtractDict =  { "input" : self._processedObservableName,
                             "background" : "bkg",
                             "output" : "despikedSignal" }  # CHANGE!
        self._bkgSubtractor.setParameterValues(bkgSubtractDict)

    def subtractBackground(self):
        self.configureBKGDataGenerator()
        self.configureBKGSubtractor()
        
        bkgData = processData.ProcessData()
        self._bkgValues.initialize(bkgData)
        self._bkgSubtractor.initialize(bkgData)
        for scan in self._dataKeeper.values():
            bkgData.addData("bkgfitresult", scan.getBackground())
            bkgData.addData(self._motorname, scan.getMotor())
            bkgData.addData(self._processedObservableName, scan.getDespiked())
            self._bkgValues.execute(bkgData)
            self._bkgSubtractor.execute(bkgData)
            scan.setBkgSubtracted(bkgData.getData("despikedSignal"))
            bkgData.clearCurrent()
            
    def configureTrapezoidIntegrator(self):
        trapintDict = { "motor" : "pth", # CHANGE!
                        "observable" : "observable", # CHANGE!
                        "output" : "trapint" }
        self._trapezoidIntegrator.setParameterValues(trapintDict)

    def showFitPanel(self):
        self._fitPanel.show()

class simpleDataPlot(QtGui.QDialog):
    import pyqtgraph as pg
    showNext = QtCore.pyqtSignal(int)
    showPrevious = QtCore.pyqtSignal(int)
    showNumber = QtCore.pyqtSignal(int)
    mouseposition = QtCore.pyqtSignal(float,float)

    def __init__(self, parent=None,minimum=1,maximum=1000):
        super(simpleDataPlot, self).__init__(parent)
        uic.loadUi("iint_simplePlot.ui", self)
        self.scanIDspinbox.setMinimum(minimum)
        self.scanIDspinbox.setMaximum(maximum)
        self.scanIDspinbox.setKeyboardTracking(False)
        self.scanIDspinbox.valueChanged.connect(self.showNumber.emit)
        self.showPreviousBtn.clicked.connect(self.showPrevious.emit)
        self.showNextBtn.clicked.connect(self.showNext.emit)
        self.viewPart.scene().sigMouseClicked.connect(self.mouse_click)
        
    def setMinimum(self, minimum):
        self.scanIDspinbox.setMinimum(minimum)

    def setMaximum(self, maximum):
        self.scanIDspinbox.setMaximum(maximum)

    def plot(self, xdata, ydata, scanid):
        self.scanIDspinbox.setValue(scanid)
        self.viewPart.clear()
        self._plot = self.viewPart.plot(xdata, ydata, pen=None, symbolPen='w', symbolBrush='w', symbol='+')

    def addDespike(self, xdata, despikeData):
        self.viewPart.plot(xdata, despikeData, pen=None, symbolPen='y', symbolBrush='y', symbol='o')

    def mouse_click(self, mouseclick):
        mousepos = self._plot.mapFromScene(mouseclick.pos())
        xdata = mousepos.x()
        ydata = mousepos.y()
        self.mouseposition.emit(xdata, ydata)


class firstFitPanel(QtGui.QDialog):
    def __init__(self, parent=None, dataview=None):
        super(firstFitPanel, self).__init__(parent)
        uic.loadUi("fitpanel.ui", self)
        self._paramDialog = gaussianModelFitParameterDialog()
        self.configureModelPushBtn.clicked.connect(self.showFitParamDialog)
        self.modelCB.addItems(list(curvefitting.FitModels.keys()))
        self.selectModelPushBtn.clicked.connect(self.selectCurrentModel)
        self.reftoplot = dataview
        self.reftoplot.mouseposition.connect(self.useMouseClick)
        #~ self.configDonePushBtn.clicked.connect(self.hideDialog)
        
    def showFitParamDialog(self):
        self._paramDialog.show()


    def selectCurrentModel(self):
        self.currentModelName.setText(self.modelCB.currentText())

    def useMouseClick(self, x, y):
        print( " i have seen the truth at: " + str(x) + " // " + str(y))

class gaussianModelFitParameterDialog(QtGui.QDialog):
    pickPosition = QtCore.pyqtSignal(int)
    parameterValues = QtCore.pyqtSignal(str, float, int, float, float)

    def __init__(self, parent=None):
        super(gaussianModelFitParameterDialog, self).__init__(parent)
        uic.loadUi("gaussModelFitParameters.ui", self)
        #~ self.pickMeanAmplitudeBtn.clicked.connect(self.pickMeanAmplitude)
        #~ self.pickFWHMBtn.clicked.connect(self.pickFWHM)
        self.configDonePushBtn.clicked.connect(self.returnParameterValues)
    
    def pickMeanAmplitude(self):
        pass

    def pickFWHM(self):
        pass

    def returnParameterValues(self):
        pass

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())
