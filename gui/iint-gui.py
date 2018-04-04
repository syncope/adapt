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

__version__ ="0.0.4alpha"

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

        self._elementlist = [ self._chooseConfig,
                              self._sfrGUI,
                              self._obsDef,
                              self._bkgHandling]

        for task in self._elementlist:
            self.listWidget.addItem(task.windowTitle())
            self.stackedWidget.addWidget(task)

        self._chooseConfig.choice.connect(self._initializeFromConfig)
        self._chooseConfig.newconfig.connect(self.nextWidget)
        self._sfrGUI.valuesSet.connect(self.runFileReader)
        self._obsDef.observableDicts.connect(self.runObservable)

    def nextWidget(self):
        ci = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(ci+1)
        cr = self.listWidget.currentRow()
        self.listWidget.setCurrentRow(cr+1)

    def _initializeFromConfig(self):
        self._control.loadConfig(self._chooseConfig.getConfig())
        self._sfrGUI.setParameterDict(self._control.getSFRDict())
        self.runFileReader()
        self.nextWidget()
        self._obsDef.setParameterDict(self._control.getOBSDict(), self._control.getDESDict())
        self._obsDef.emittit()
        self._bkgHandling.setParameterDicts( self._control.getBKGDicts())

    def runFileReader(self):
        sfr = self._control.createAndInitialize(self._sfrGUI.getParameterDict())
        self._control.createDataList(sfr.getData(), self._control.getRawDataName())
        # to set the displayed columns etc. one element of the selected data is needed
        self._rawdataobject = self._control.getDataList()[0].getData(self._control.getRawDataName())
        self._motorname = self._rawdataobject.getStartIdentifier(2)
        self._control.setMotorName(self._motorname)
        # pass info to the observable definition part
        self._obsDef.passInfo(self._rawdataobject)
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
        self._simpleImageView.passData( self._control.getDataList(), 
                                        self._control.getMotorName(),
                                        self._control.getObservableName(),
                                        self._control.getDespikedObservableName(),
                                        self._control.getBackgroundName(),
                                        self._control.getSignalName()
                                        )
        self._simpleImageView.plot()
        self._simpleImageView.show()


        #~ self._fitPanel = firstFitPanel(parent=self, dataview=self._simpleImageView)
        #~ # signal section
        #~ self.openFitPanelPushBtn.clicked.connect(self.showFitPanel)

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
        self.showRAW.stateChanged.connect(self._toggleRAW)
        self.showDES.stateChanged.connect(self._toggleDES)
        self.showBKG.stateChanged.connect(self._toggleBKG)
        self.showSIG.stateChanged.connect(self._toggleSIG)
        self.showRAW.stateChanged.connect(self.plot)
        self.showDES.stateChanged.connect(self.plot)
        self.showBKG.stateChanged.connect(self.plot)
        self.showSIG.stateChanged.connect(self.plot)
        self.viewPart.scene().sigMouseClicked.connect(self.mouse_click)
        self._control = None
        self._currentIndex = 0
        self._showraw = True
        self._showdespike = False
        self._showbkg = False
        self._showbkgsubtracted = False
        #~ self._showbkgfit = False

    def passData(self, datalist, motorname, obsname, despobsname, bkgname, signalname):
        self._dataList = datalist
        self._motorName = motorname
        self._observableName = obsname
        self._despObservableName = despobsname
        self._backgroundPointsName = bkgname
        self._signalName = signalname
        self._checkDataAvailability()

    def _checkDataAvailability(self):
        datum = self._dataList[0]
        try:
            datum.getData(self._observableName)
            self.showRAW.setDisabled(False)
        except KeyError:
            self.showRAW.setDisabled(True)
        try:
            datum.getData(self._despObservableName)
            self.showDES.setDisabled(False)
        except KeyError:
            self.showDES.setDisabled(True)
        try:
            datum.getData(self._backgroundPointsName)
        except KeyError:
            self.showBKG.setDisabled(True)
        try:
            datum.getData(self._signalName)
        except KeyError:
            self.showSIG.setDisabled(True)

    def plot(self):
        datum = self._dataList[self._currentIndex]
    
        self.showID.setText(str(datum.getData("scannumber")))
        xdata = datum.getData(self._motorName)
        ydata = datum.getData(self._observableName)
        self.viewPart.clear()
        if( self._showraw):
            self.viewPart.plot(xdata, ydata, pen=None, symbolPen='w', symbolBrush='w', symbol='+')
        if( self._showdespike ):
            despikeData = datum.getData(self._despObservableName)
            self.viewPart.plot(xdata, despikeData, pen=None, symbolPen='y', symbolBrush='y', symbol='o')
        if( self._showbkg ):
            bkg = datum.getData(self._backgroundPointsName)
            self.viewPart.plot(xdata, bkg, pen=None, symbolPen='r', symbolBrush='r', symbol='+')
        if( self._showbkgsubtracted ):
            signal = datum.getData(self._signalName)
            self.viewPart.plot(xdata, signal, pen=None, symbolPen='b', symbolBrush='b', symbol='o')
        #~ if( self._showbkgfit ):
            #~ bkgFit = datum.getData(self._names["bkgFitName"])
            #~ self.viewPart.plot(xdata, despikeData, pen=None, symbolPen='y', symbolBrush='y', symbol='o')

    def _toggleRAW(self):
        self._showraw = not self._showraw 

    def _toggleDES(self):
        self._showdespike = not self._showdespike 

    def _toggleBKG(self):
        self._showbkg = not self._showbkg

    def _toggleSIG(self):
        self._showbkgsubtracted = not self._showbkgsubtracted 


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
    choice = QtCore.pyqtSignal()
    newconfig = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(chooseConfiguration, self).__init__(parent)
        uic.loadUi("configurationChoice.ui", self)
        self.useLast.clicked.connect(self.uselast)
        self.useLast.setDisabled(True)
        self.chooseFile.clicked.connect(self.choosefile)
        self.createNew.clicked.connect(self.createnew)
        self._procconf = None

    def uselast(self, num):
        print("use the last config, still trouble determining where the file should be ")

    def choosefile(self, num):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose iint config file', '.', "iint cfg files (*.iint)")
        
        if self._file != "":
            from adapt import configurationHandler
            handler = configurationHandler.ConfigurationHandler()
            self._procconf = handler.loadConfig(self._file)
            self.choice.emit()

    def getConfig(self):
        return self._procconf

    def createnew(self, num):
        self.newconfig.emit()

class observableDefinition(QtGui.QWidget):
    observableDicts = QtCore.pyqtSignal(dict, dict)

    def __init__(self, parent=None):
        super(observableDefinition, self).__init__(parent)
        self.setWindowTitle("Observable definition")
        uic.loadUi("iintobservable.ui", self)
        self._obsDict = {}
        self._despikeDict = {}
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

    def setParameterDict(self, obsDict, despDict):
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
            #~ self.observableDetectorCB.addItem(paramDict["detector_column"])
        #~ self.observableMonitorCB.addItem(paramDict["monitor_column"])
        #~ self.observableTimeCB.addItem(paramDict["exposureTime_column"])
        #~ self.observableAttFaccheck.addItem(
        #~ self.despikeCheckBox.addItem(

class backgroundHandling(QtGui.QWidget):
    bkgDict = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(backgroundHandling, self).__init__(parent)
        uic.loadUi("linearbackground.ui", self)
        self.bkgStartPointsSB.setMinimum(0)
        self.bkgStartPointsSB.setMaximum(5)
        self.bkgEndPointsSB.setMinimum(0)
        self.bkgEndPointsSB.setMaximum(5)
        self._selectParDict = {}
        self._fitParDict = {}
        self._calcParDict = {}
        self._subtractParDict = {}

    def setParameterDicts(self, dicts):
        self._selectParDict = dicts[0]
        self.bkgStartPointsSB.setValue(self._selectParDict["startpointnumber"])
        self.bkgEndPointsSB.setValue(self._selectParDict["endpointnumber"])
        self._fitParDict = dicts[1]
        self._calcParDict = dicts[2]
        self._subtractParDict = dicts[3]


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())
