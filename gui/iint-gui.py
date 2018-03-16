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

from adapt.utilities import interactiveP09ProcessingControl
from adapt.processes import specfilereader
from adapt.processes import iintdefinition
from adapt.processes import filter1d
#~ from adapt.processes import subsequenceselection
#~ from adapt.processes import curvefitting
#~ from adapt.processes import gendatafromfunction
#~ from adapt.processes import backgroundsubtraction
#~ from adapt.processes import trapezoidintegration
#~ from adapt import processData
#~ from adapt.utilities import iintData

__version__ ="0.0.2alpha"

class iintGUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(iintGUI, self).__init__(parent)
        uic.loadUi("iint_main.ui", self)

        # the steering helper object
        self._control = interactiveP09ProcessingControl.InteractiveP09ProcessingControl()

        # the core independent variable in iint:
        self._motorname = ""
        self._rawdataobject = None
        
        self._chooseConfig = chooseConfiguration()
        self._sfrGUI = specfilereader.specfilereaderGUI()
        self._obsDef = observableDefinition()
        self._bkgHandling = backgroundHandling()

        self._tasklist = [ self._chooseConfig,
                           self._sfrGUI,
                           self._obsDef,
                           self._bkgHandling]
        for task in self._tasklist:
            self.listWidget.addItem(task.windowTitle())
            self.stackedWidget.addWidget(task)

        # workaround for now: pass info to observable ... (always at change!)
        self.listWidget.currentRowChanged.connect(self._distributeInfo)

        self._chooseConfig.choice.connect(print)
        self._sfrGUI.pDict.connect(self.runFileReader)
        self._obsDef.observableDicts.connect(self.runObservable)

    def nextWidget(self):
        ci = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(ci+1)
        cr = self.listWidget.currentRow()
        self.listWidget.setCurrentRow(cr+1)

    def runFileReader(self, pDict):
        sfr = self._control.createAndInitialize(pDict)
        self._control.convertToDataList(sfr.getData(),"rawdata")
        # to set the displayed columns etc. one element of the selected data is needed
        self._rawdataobject = self._control.getDataList()[0].getData("rawdata")
        self._motorname = self._rawdataobject.getStartIdentifier(2)
        self._control.setMotorName(self._motorname)
        self.nextWidget()

    def runObservable(self, obsDict, despDict):
        self._control.createAndBulkExecute(obsDict)
        if despDict != {}:
            self._control.createAndBulkExecute(despDict)
        self.plotit()
        self.nextWidget()

    def plotit(self):
        # pyqt helper stuff
        self._simpleImageView = simpleDataPlot(parent=self)
        self._simpleImageView.passData(self._control.getDataList(), self._control.getNames())
        self._simpleImageView.plot()
        self._simpleImageView.show()


        #~ self._fitPanel = firstFitPanel(parent=self, dataview=self._simpleImageView)

        #~ # background section
        #~ self.subtractBkgCheckBox.stateChanged.connect(self.toggleBKGsubtraction)
        #~ self.bkgStartPointsSB.setKeyboardTracking(False)
        #~ self.bkgStartPointsSB.valueChanged.connect(self.selectStartBKG)
        #~ self.bkgEndPointsSB.setKeyboardTracking(False)
        #~ self.bkgEndPointsSB.valueChanged.connect(self.selectEndBKG)
        #~ self.fitBKGbtn.clicked.connect(self.selectAndFitBackground)
        #~ self.subtractBkgCheckBox.stateChanged.connect(self.subtractBackground)

        #~ # signal section
        #~ self.openFitPanelPushBtn.clicked.connect(self.showFitPanel)

    def _distributeInfo(self):
        self._obsDef.passInfo(self._rawdataobject)

    def getAndOpenFile(self):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose spec file', '.', "SPEC files (*.spc *.spe *.spec)")
        self.inputFileLE.setText(self._file)

    def defineOutput(self):
        self._outfile = QtGui.QFileDialog.getOpenFileName(self, 'Select output file', '.')

    def toggleBKGsubtraction(self):
        self._subtractBackground = not self._subtractBackground

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
        self._bkgSelector.initialize()
        self._bkgFitter.initialize()
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
        self._bkgValues.initialize()
        self._bkgSubtractor.initialize()
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
    mouseposition = QtCore.pyqtSignal(float,float)

    def __init__(self, parent=None):
        super(simpleDataPlot, self).__init__(parent)
        uic.loadUi("iint_simplePlot.ui", self)
        self.showPreviousBtn.clicked.connect(self.decrementCurrentScanID)
        self.showNextBtn.clicked.connect(self.incrementCurrentScanID)
        self.viewPart.scene().sigMouseClicked.connect(self.mouse_click)
        self._control = None
        self._currentIndex = 0
        
    def passData(self, datalist, names):
        self._dataList = datalist
        self._names = names

    def plot(self):
        datum = self._dataList[self._currentIndex]
    
        self.showID.setText(str(datum.getData("scannumber")))
        xdata = datum.getData(self._names["motorName"])
        ydata = datum.getData(self._names["observableName"])
        self.viewPart.clear()
        self.viewPart.plot(xdata, ydata, pen=None, symbolPen='w', symbolBrush='w', symbol='+')

    def incrementCurrentScanID(self):
        self._currentIndex += 1
        if ( self._currentIndex >= len(self._dataList) ):
            self._currentIndex -= len(self._dataList)
        self.plot()

    def decrementCurrentScanID(self):
        self._currentIndex -= 1
        if ( self._currentIndex < (-1)*len(self._dataList) ):
            self._currentIndex += len(self._dataList)
        self.plot()

    #~ def addDespike(self, xdata, despikeData):
        #~ self.viewPart.plot(xdata, despikeData, pen=None, symbolPen='y', symbolBrush='y', symbol='o')

    def mouse_click(self, mouseclick):
        mousepos = self._plot.mapFromScene(mouseclick.pos())
        xdata = mousepos.x()
        ydata = mousepos.y()
        self.mouseposition.emit(xdata, ydata)

#~ class firstFitPanel(QtGui.QDialog):
    #~ def __init__(self, parent=None, dataview=None):
        #~ super(firstFitPanel, self).__init__(parent)
        #~ uic.loadUi("fitpanel.ui", self)
        #~ self._paramDialog = gaussianModelFitParameterDialog()
        #~ self.configureModelPushBtn.clicked.connect(self.showFitParamDialog)
        #~ self.modelCB.addItems(list(curvefitting.FitModels.keys()))
        #~ self.selectModelPushBtn.clicked.connect(self.selectCurrentModel)
        #~ self.reftoplot = dataview
        #~ self.reftoplot.mouseposition.connect(self.useMouseClick)
        #~ self.configDonePushBtn.clicked.connect(self.hideDialog)
        #~ 
    #~ def showFitParamDialog(self):
        #~ self._paramDialog.show()
#~ 
#~ 
    #~ def selectCurrentModel(self):
        #~ self.currentModelName.setText(self.modelCB.currentText())
#~ 
    #~ def useMouseClick(self, x, y):
        #~ print( " i have seen the truth at: " + str(x) + " // " + str(y))

#~ class gaussianModelFitParameterDialog(QtGui.QDialog):
    #~ pickPosition = QtCore.pyqtSignal(int)
    #~ parameterValues = QtCore.pyqtSignal(str, float, int, float, float)
#~ 
    #~ def __init__(self, parent=None):
        #~ super(gaussianModelFitParameterDialog, self).__init__(parent)
        #~ uic.loadUi("gaussModelFitParameters.ui", self)
        #~ self.pickMeanAmplitudeBtn.clicked.connect(self.pickMeanAmplitude)
        #~ self.pickFWHMBtn.clicked.connect(self.pickFWHM)
        #~ self.configDonePushBtn.clicked.connect(self.returnParameterValues)
    #~ 
    #~ def pickMeanAmplitude(self):
        #~ pass
#~ 
    #~ def pickFWHM(self):
        #~ pass
#~ 
    #~ def returnParameterValues(self):
        #~ pass
#~ 

class chooseConfiguration(QtGui.QWidget):
    choice = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(chooseConfiguration, self).__init__(parent)
        uic.loadUi("configurationChoice.ui", self)
        self.useLast.clicked.connect(self.uselast)
        self.chooseFile.clicked.connect(self.choosefile)
        self.createNew.clicked.connect(self.createnew)

    def uselast(self, num):
        print("use the last config " + str(num))

    def choosefile(self, num):
        print("choose config file " + str(num))

    def createnew(self, num):
        print("new config " + str(num))

class observableDefinition(QtGui.QWidget):
    observableDicts = QtCore.pyqtSignal(dict, dict)

    def __init__(self, parent=None):
        super(observableDefinition, self).__init__(parent)
        self.setWindowTitle("Observable definition")
        uic.loadUi("iintobservable.ui", self)
        self._obsDict = {}
        self._despikeDict = {}
        self.observableDetectorCB.activated.connect(self.setObservable)
        self.observableMonitorCB.activated.connect(self.setMonitor)
        self.observableTimeCB.activated.connect(self.setTime)
        self._useAttenuationFactor = False
        self.observableAttFaccheck.stateChanged.connect(self.toggleAttFac)
        self.observableAttFacCB.setDisabled(True)
        self.observableAttFacCB.activated.connect(self.setAttFac)
        self.despikeCheckBox.stateChanged.connect(self.toggleDespiking)
        self._despike = False
        self._notEnabled(True)
        self.obsNextBtn.clicked.connect(self.emittit)
        self._observableName = 'observable'

    def passInfo(self, dataobject):
        if dataobject == None:
            self._notEnabled(True)
            return
        else:
            self._notEnabled(False)

        self._currentdataLabels = dataobject.getLabels()
        self.observableMotorLabel.setStyleSheet("color: blue;")
        self._motorname = dataobject.getStartIdentifier(2)
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

    def emittit(self):
        self._obsDict["type"] = "iintdefinition"
        self._obsDict["input"] = "rawdata"
        self._obsDict["motor_column"] = self._motorname
        self._obsDict["detector_column"] = self._detname
        self._obsDict["monitor_column"] = self._monname
        self._obsDict["exposureTime_column"] = self._timename
        self._obsDict["observableoutput"] = self._observableName
        self._obsDict["id"] = "scannumber"
        if(self._useAttenuationFactor):
            self._obsDict["attenuationFactor_column"] = self._attenfname

        if(self._despike):
            self._despikeDict["type"] = "filter1d"
            self._despikeDict["method"] = "p09despiking"
            self._despikeDict["input"] = "observable"
            self._despikeDict["output"] = "despikedObservable"
        
        self.observableDicts.emit(self._obsDict, self._despikeDict)

class backgroundHandling(QtGui.QWidget):
    bkgDict = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(backgroundHandling, self).__init__(parent)
        uic.loadUi("linearbackground.ui", self)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())
