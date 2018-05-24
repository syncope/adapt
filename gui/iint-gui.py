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
import pyqtgraph as pg

from adapt.utilities import interactiveP09ProcessingControl
from adapt.processes import specfilereader

__version__ ="0.0.5alpha"

class iintGUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(iintGUI, self).__init__(parent)
        uic.loadUi("iint_main3.ui", self)

        self.actionNew.triggered.connect(self._askReset)
        self.actionOpen_file.triggered.connect(self.choosefile)
        self.actionSave_file.triggered.connect(self._saveConfig)
        self.actionExit.triggered.connect(self._closeApp)

        # the steering helper object
        self._control = interactiveP09ProcessingControl.InteractiveP09ProcessingControl()

        # the quit dialog
        self._quit = quitDialog()
        self._quit.quitandsave.clicked.connect(self._saveConfig)
        self._quit.justquit.clicked.connect(exit)

        # the core independent variable in iint:
        self._motorname = ""
        self._rawdataobject = None

        self._simpleImageView = simpleDataPlot(parent=self)
        #~ self.horizontalLayout.addWidget(self._simpleImageView)
        self.imageWidget = self._simpleImageView

        self._resetQuestion = resetDialog()
        self._resetQuestion.resetOK.connect(self._resetAll)
        self._fileDisplay = fileDisplay()
        self._sfrGUI = specfilereader.specfilereaderGUI()
        self._obsDef = observableDefinition()
        self._obsDef.doDespike.connect(self._control.useDespike)
        self._obsDef.doTrapint.connect(self._control.useTrapInt)
        self._bkgHandling = backgroundHandling(self._control.getBKGDicts())
        self._signalHandling = signalHandling(self._control.getSIGDict())
        self._signalHandling.passModels(self._control.getFitModels())
        self._signalHandling.modelcfg.connect(self.openFitDialog)
        self._signalHandling.performFitPushBtn.clicked.connect(self._prepareSignalFitting)
        self._fitList = []
        self._inspectAnalyze = inspectAnalyze()
        self._inspectAnalyze.trackData.clicked.connect(self._dataToTrack)
        self._inspectAnalyze.polAnalysis.clicked.connect(self._polarizationAnalysis)

        self._loggingBox = loggerBox()

        self.verticalLayout.addWidget(self._fileDisplay)
        self.verticalLayout.addWidget(self._obsDef)
        self.verticalLayout.addWidget(self._bkgHandling)
        self.verticalLayout.addWidget(self._signalHandling)
        self.verticalLayout.addWidget(self._inspectAnalyze)
        self.verticalLayout.addWidget(self._loggingBox)

        self._fileDisplay.newspecfile.connect(self.showSFRGUI)
        self._sfrGUI.valuesSet.connect(self.runFileReader)
        self._obsDef.observableDicts.connect(self.runObservable)
        self._bkgHandling.bkgDicts.connect(self.runBkgProcessing)
        
        self.setGeometry(0,0,600,840)


    def message(self, text):
        self._loggingBox.addText(text)

    def _resetAll(self):
        self._simpleImageView.reset()
        self._fileDisplay.reset()
        self._obsDef.reset()
        self._bkgHandling.reset()
        self._signalHandling.reset()
        self._control.resetAll()

    def _closeApp(self):
        for i in self._trackedDataWidgets:
            i.close()
        self._quit.show()

    def _saveConfig(self, num=None):
        tempfilename = self._control.proposeConfigfileName()
        savename = QtGui.QFileDialog.getSaveFileName(self, 'Choose iint config file to save', tempfilename, "iint cfg files (*.iint)")
        if savename != '':
            self._control.saveConfig(savename)
            self.message("Saving config file " + str(savename) + ".")
        return

    def _askReset(self):
        if self._control.getSFRDict()["filename"] == None:
            self._resetAll()
        else:
            self._resetQuestion.show()
            self.message("Cleared all data and processing configuration.")

    def showSFRGUI(self):
        self._sfrGUI.show()

    def choosefile(self):
        try:
            prev = self._file
        except:
            prev = None
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose iint config file', '.', "iint cfg files (*.iint)")
        if self._file != "":
            if prev != None:
                self._resetAll()
            from adapt import configurationHandler
            handler = configurationHandler.ConfigurationHandler()
            self._procconf = handler.loadConfig(self._file)
            self._initializeFromConfig()

    def _initializeFromConfig(self):
        self._control.loadConfig(self._procconf)
        self._sfrGUI.setParameterDict(self._control.getSFRDict())
        self.runFileReader()
        self._obsDef.setParameterDicts(self._control.getOBSDict(), self._control.getDESDict(), self._control.getTrapIntDict())
        self._obsDef.emittit()
        self._bkgHandling.setParameterDicts( self._control.getBKGDicts())
        self._bkgHandling.emittem()

    def runFileReader(self):
        filereaderdict = self._sfrGUI.getParameterDict()
        self._fileDisplay.setNames(filereaderdict["filename"], filereaderdict["scanlist"])
        self.message("Reading spec file: " + str(filereaderdict["filename"]))

        sfr = self._control.createAndInitialize(filereaderdict)
        self._control.createDataList(sfr.getData(), self._control.getRawDataName())
        # to set the displayed columns etc. one element of the selected data is needed
        self._rawdataobject = self._control.getDataList()[0].getData(self._control.getRawDataName())
        self._motorname = self._rawdataobject.getMotorName()
        self._control.setMotorName(self._motorname)
        # pass info to the observable definition part
        self._obsDef.passInfo(self._rawdataobject)
        self.message("... done.\n")

    def runObservable(self, obsDict, despDict):
        self.message("Computing the observable...")
        self._control.createAndBulkExecute(obsDict)
        # check whether despiking is activated, otherwise unset names
        if despDict != {}:
            self._control.useDespike(True)
            self._control.createAndBulkExecute(despDict)
        else:
            self._control.noDespiking()
        self.message(" and plotting ...")
        self.plotit()
        self.message(" done.\n")

    def runBkgProcessing(self, selDict, fitDict, calcDict, subtractDict):
        self.message("Fitting background ...")
        if selDict == {}:
            self._control.useBKG(False)
            self.message("... nothing to be done.\n")
            return
        self._control.useBKG(True)
        self._control.createAndBulkExecute(selDict)
        self._control.createAndBulkExecute(fitDict)
        self._control.createAndBulkExecute(calcDict)
        self._control.createAndBulkExecute(subtractDict)
        if( self._simpleImageView != None):
            self._simpleImageView.update()
        if self._obsDef._dotrapint:
            self._control.createAndBulkExecute(self._control.getTrapIntDict())
        self.message(" ... done.\n")

    def plotit(self):
        # pyqt helper stuff
        self._simpleImageView.passData( self._control.getDataList(), 
                                        self._control.getMotorName(),
                                        self._control.getObservableName(),
                                        self._control.getDespikedObservableName(),
                                        self._control.getBackgroundName(),
                                        self._control.getSignalName(),
                                        self._control.getFittedSignalName(),
                                        )
        self._simpleImageView.plot()
        self._simpleImageView.show()

    def openFitDialog(self, modelname, index):
        self._fitWidget = self._control.getFitModel(modelname, self._simpleImageView.getCurrentSignal(), index=index)
        self._fitWidget.updateFit.connect(self._updateCurrentImage)
        self._fitWidget.guessingDone.connect(self._simpleImageView.removeGuess)
        self._fitWidget.show()
        self._fitWidget.update()
        self._keepFitList(self._fitWidget)

    def _prepareSignalFitting(self):
        fitDict =  {}
        for fit in self._fitList:
            fitDict.update(fit.getCurrentParameterDict())
        self.runSignalFitting(fitDict)

    def runSignalFitting(self, fitDict):
        self.message("Fitting the signal, this can take a while ...")
        rundict = self._control.getSIGDict()
        rundict['model'] = fitDict
        self._control.createAndBulkExecute(rundict)
        self._control.createAndBulkExecute(self._control.getSignalFitDict())
        if( self._simpleImageView != None):
            self._simpleImageView.update("plotfit")
        self.message(" ... done.\n")

    def _updateCurrentImage(self):
        ydata = self._fitWidget.getCurrentFitData()
        self._simpleImageView.plotFit(ydata)

    def _keepFitList(self, fitwidget):
        # remove if index is already there
        for fit in self._fitList:
            if fitwidget.getIndex() == fit.getIndex():
                self._fitList.remove(fit)
        self._fitList.append(fitwidget)

    def _dataToTrack(self):
        rawScanData = self._control.getDataList()[0].getData(self._control.getRawDataName())
        self._trackedDataChoice = chooseTrackedData(rawScanData)
        self._trackedDataChoice.trackedData.connect(self._showTracked)
        
    def _polarizationAnalysis(self):
        pass

    def _showTracked(self, namelist):
        self._trackedDataWidgets = []
        for name in namelist:
            trackinfo = self._control.getTrackInformation(name)
            self._trackedDataWidgets.append(multiTrackedDataView(trackinfo))



class simpleDataPlot(QtGui.QDialog):
    mouseposition = QtCore.pyqtSignal(float,float)
    currentIndex = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(simpleDataPlot, self).__init__(parent)
        uic.loadUi("iint_simplePlot.ui", self)
        self.showPreviousBtn.clicked.connect(self.decrementCurrentScanID)
        self.showNextBtn.clicked.connect(self.incrementCurrentScanID)
        self.showRAW.stateChanged.connect(self._toggleRAW)
        self.showDES.stateChanged.connect(self._toggleDES)
        self.showBKG.stateChanged.connect(self._toggleBKG)
        self.showSIG.stateChanged.connect(self._toggleSIG)
        self.showFIT.stateChanged.connect(self._toggleFIT)
        self.showRAW.stateChanged.connect(self.plot)
        self.showDES.stateChanged.connect(self.plot)
        self.showBKG.stateChanged.connect(self.plot)
        self.showSIG.stateChanged.connect(self.plot)
        self.showFIT.stateChanged.connect(self.plot)
        self.viewPart.scene().sigMouseClicked.connect(self.mouse_click)
        self._currentIndex = 0
        self.currentIndex.emit(self._currentIndex)
        self._showraw = True
        self._showdespike = False
        self._showbkg = False
        self._showbkgsubtracted = False
        self._tmpFit = None
        self._showsigfit = False
        self.setGeometry(640,1,840,840)

    def reset(self):
        self.showDES.setChecked(False)
        self.showBKG.setChecked(False)
        self.showSIG.setChecked(False)
        self.showFIT.setChecked(False)
        self.showDES.setDisabled(True)
        self.showBKG.setDisabled(True)
        self.showSIG.setDisabled(True)
        self.showFIT.setDisabled(True)
        self._currentIndex = 0
        self._showraw = True
        self._showdespike = False
        self._showbkg = False
        self._showbkgsubtracted = False
        self._showsigfit = False
        
        self.viewPart.clear()

    def update(self, action=None):
        self._checkDataAvailability()
        if(action == "plotfit"):
            self.showFIT.setChecked(True)

    def passData(self, datalist, motorname, obsname, despobsname, bkgname, signalname, fittedsignalname):
        self._dataList = datalist
        self._motorName = motorname
        self._observableName = obsname
        self._despObservableName = despobsname
        self._backgroundPointsName = bkgname
        self._signalName = signalname
        self._fittedSignalName = fittedsignalname
        self.update()

    def _checkDataAvailability(self):
        datum = self._dataList[0]
        
        try:
            datum.getData(self._observableName)
            self.showRAW.setDisabled(False)
        except KeyError:
            self.showRAW.setDisabled(True)
        try:
            if(self._despObservableName == self._observableName):
                self.showDES.setDisabled(True)
            else:
                datum.getData(self._despObservableName)
                self.showDES.setDisabled(False)
        except KeyError:
            self.showDES.setDisabled(True)
        try:
            datum.getData(self._backgroundPointsName)
            self.showBKG.setDisabled(False)
        except KeyError:
            self.showBKG.setDisabled(True)
        try:
            datum.getData(self._signalName)
            self.showSIG.setDisabled(False)
        except KeyError:
            self.showSIG.setDisabled(True)
        try:
            datum.getData(self._fittedSignalName)
            self.showFIT.setDisabled(False)
        except KeyError:
            self.showFIT.setDisabled(True)

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
        if( self._showsigfit ):
            fitdata = datum.getData(self._fittedSignalName)
            self.viewPart.plot(xdata, fitdata, pen='r')

    def plotFit(self, ydata):
        datum = self._dataList[self._currentIndex]
        xdata = datum.getData(self._motorName)
        if self._tmpFit != None:
            self._tmpFit.clear()
        self._tmpFit = self.viewPart.plot(xdata, ydata, pen='g') #, symbol='+')

    def removeGuess(self):
        self._tmpFit.clear()

    def _toggleRAW(self):
        self._showraw = not self._showraw 

    def _toggleDES(self):
        self._showdespike = not self._showdespike 

    def _toggleBKG(self):
        self._showbkg = not self._showbkg

    def _toggleSIG(self):
        self._showbkgsubtracted = not self._showbkgsubtracted 

    def _toggleFIT(self):
        self._showsigfit = not self._showsigfit

    def incrementCurrentScanID(self):
        self._currentIndex += 1
        if ( self._currentIndex >= len(self._dataList) ):
            self._currentIndex -= len(self._dataList)
        self.currentIndex.emit(self._currentIndex)
        self.plot()

    def decrementCurrentScanID(self):
        self._currentIndex -= 1
        if ( self._currentIndex < (-1)*len(self._dataList) ):
            self._currentIndex += len(self._dataList)
        self.currentIndex.emit(self._currentIndex)
        self.plot()

    def mouse_click(self, event):
        try:
            mousepos = self.viewPart.mapFromScene(event)
            xdata = mousepos.x()
            ydata = mousepos.y()
            self.mouseposition.emit(xdata, ydata)
        except:
            pass

    def getCurrentIndex(self):
        return self._currentIndex

    def getCurrentSignal(self):
        datum = self._dataList[self._currentIndex]
        return datum.getData(self._motorName), datum.getData(self._signalName)



class fileDisplay(QtGui.QWidget):
    newspecfile = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(fileDisplay, self).__init__(parent)
        self.setWindowTitle("File Display")
        uic.loadUi("fileDisplay.ui", self)
        self.changeFile.clicked.connect(self.emitNew)

    def reset(self):
        self.fileLabel.setText("No File")
        self.fileLabel.setToolTip("No File")
        self.scanSelectionDisplay.setText("No selection")

    def setNames(self, f, s):
        import os.path
        self.fileLabel.setText(os.path.basename(f))
        self.fileLabel.setToolTip(f)
        self.scanSelectionDisplay.setText(s)

    def emitNew(self):
        self.newspecfile.emit()



class observableDefinition(QtGui.QWidget):
    observableDicts = QtCore.pyqtSignal(dict, dict, dict)
    doDespike = QtCore.pyqtSignal(int)
    doTrapint = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(observableDefinition, self).__init__(parent)
        self.setWindowTitle("Observable definition")
        uic.loadUi("iintobservable.ui", self)
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
        self.trapintCheckBox.stateChanged.connect(self.toggleTrapint)
        self._despike = False
        self._dotrapint = False
        self._notEnabled(True)
        self.obsNextBtn.clicked.connect(self.emittit)
        self._observableName = 'observable'

    def _defaultSettings(self):
        self._obsDict = {}
        self._despikeDict = {}
        self._trapintDict = {}
        self._useAttenuationFactor = False
        self.observableAttFacCB.setDisabled(True)
        self.despikeCheckBox.setChecked(False)
        self.trapintCheckBox.setChecked(False)
        self._despike = False
        self._dotrapint = False
        self._notEnabled(True)
        self._observableName = 'observable'

    def reset(self):
        self._defaultSettings()

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
        self.trapintCheckBox.setDisabled(state)
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

    def toggleTrapint(self):
        self._dotrapint = not self._dotrapint
        self.doTrapint.emit(self._dotrapint)

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
        if(self._dotrapint):
            self._trapintDict["type"] = "trapezoidintegration"
            self._trapintDict["motor"] = self._motorname
            self._trapintDict["observable"] = "signalObservable"
            self._trapintDict["output"] = "trapint"
        
        self.observableDicts.emit(self._obsDict, self._despikeDict, self._trapintDict)

    def setParameterDicts(self, obsDict, despDict, trapintDict):
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

        if ( trapintDict != {} ):
            self.trapintCheckBox.setChecked(True)



class backgroundHandling(QtGui.QWidget):
    bkgDicts = QtCore.pyqtSignal(dict, dict, dict, dict)

    def __init__(self, pDicts, parent=None):
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
        self.nextBtn.clicked.connect(self.emittem)
        self.setParameterDicts(pDicts)

    def reset(self):
        self._selectParDict = {}
        self._fitParDict = {}
        self._calcParDict = {}
        self._subtractParDict = {}
        self.bkgStartPointsSB.setValue(3)
        self.bkgEndPointsSB.setValue(3)

    def setParameterDicts(self, dicts):
        self._selectParDict = dicts[0]
        self.bkgStartPointsSB.setValue(self._selectParDict["startpointnumber"])
        self.bkgEndPointsSB.setValue(self._selectParDict["endpointnumber"])
        self._fitParDict = dicts[1]
        self._calcParDict = dicts[2]
        self._subtractParDict = dicts[3]

    def emittem(self):
        self._selectParDict["startpointnumber"] = self.bkgStartPointsSB.value()
        self._selectParDict["endpointnumber"] = self.bkgEndPointsSB.value()
        self.bkgDicts.emit(  self._selectParDict, self._fitParDict, self._calcParDict, self._subtractParDict )



class signalHandling(QtGui.QWidget):
    modelcfg = QtCore.pyqtSignal(str, int)

    def __init__(self, pDict, parent=None):
        super(signalHandling, self).__init__(parent)
        uic.loadUi("fitpanel.ui", self)
        self.setParameterDict(pDict)
        self.configureFirst.clicked.connect(self.emitfirstmodelconfig)
        self.configureSecond.clicked.connect(self.emitsecondmodelconfig)
        self.configureThird.clicked.connect(self.emitthirdmodelconfig)
        self.configureFourth.clicked.connect(self.emitfourthmodelconfig)
        self._inactive = [ False, True, True, True ]
        self._firstModelDict = {}
        self._secondModelDict = {}
        self._thirdModelDict = {}
        self._fourthModelDict = {}
        self.useFirst.stateChanged.connect(self._toggleFirst)
        self.useSecond.stateChanged.connect(self._toggleSecond)
        self.useThird.stateChanged.connect(self._toggleThird)
        self.useFourth.stateChanged.connect(self._toggleFourth)

    def reset(self):
        self._firstModelDict = {}
        self._secondModelDict = {}
        self._thirdModelDict = {}
        self._fourthModelDict = {}

    def _toggleFirst(self):
        self._inactive[0] = not self._inactive[0]
        self.firstModelCB.setDisabled(self._inactive[0])
        self.configureFirst.setDisabled(self._inactive[0])

    def _toggleSecond(self):
        self._inactive[1] = not self._inactive[1]
        self.secondModelCB.setDisabled(self._inactive[1])
        self.configureSecond.setDisabled(self._inactive[1])

    def _toggleThird(self):
        self._inactive[2] = not self._inactive[2]
        self.thirdModelCB.setDisabled(self._inactive[2])
        self.configureThird.setDisabled(self._inactive[2])

    def _toggleFourth(self):
        self._inactive[3] = not self._inactive[3]
        self.fourthModelCB.setDisabled(self._inactive[3])
        self.configureFourth.setDisabled(self._inactive[3])

    def setParameterDict(self, pDict):
        self._parDict = pDict

    def passModels(self, modelDict):
        self._modelnames = sorted([key for key in modelDict.keys()])
        self.firstModelCB.addItems(self._modelnames)
        self.secondModelCB.addItems(self._modelnames)
        self.thirdModelCB.addItems(self._modelnames)
        self.fourthModelCB.addItems(self._modelnames)

    def emitfirstmodelconfig(self):
        index = self.firstModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 0)

    def emitsecondmodelconfig(self):
        index = self.secondModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 1)

    def emitthirdmodelconfig(self):
        index = self.thirdModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 2)

    def emitfourthmodelconfig(self):
        index = self.fourthModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 3)



class inspectAnalyze(QtGui.QWidget):

    def __init__(self, parent=None):
        super(inspectAnalyze, self).__init__(parent)
        uic.loadUi("inspectAnalyze.ui", self)



class chooseTrackedData(QtGui.QWidget):
    trackedData = QtCore.pyqtSignal(list)

    def __init__(self, dataelement=None, parent=None):
        super(chooseTrackedData, self).__init__(parent)
        uic.loadUi("chooseTrackedData.ui", self)
        self._data = dataelement
        self._initialNames = self._data.getLabels()
        for elem in list(self._data.getCustomKeys()):
            self._initialNames.append(elem)
        self._fillLists()
        self.okBtn.clicked.connect(self._emitTrackedData)
        self.okBtn.clicked.connect(self._reset)
        self.cancel.clicked.connect(self._reset)
        self.addToList.setDisabled(True)
        self.addToList.clicked.connect(self._moveToSelected)
        self.removeFromList.clicked.connect(self._moveToUnselected)
        self.removeFromList.setDisabled(True)
        self.listAll.itemClicked.connect(self._pickedUnselectedItem)
        self.listAll.itemDoubleClicked.connect(self._moveToSelected)
        self.listSelected.itemClicked.connect(self._pickedSelectedItem)
        self.listSelected.itemDoubleClicked.connect(self._moveToUnselected)
        self._currentUnSelectedItem  = 0
        self._currentSelectedItem  = 0
        self.show()

    def _fillLists(self):
        self._untrackedData = self._initialNames[:]
        self._trackedData = []
        self.listAll.addItems(self._untrackedData)

    def _reset(self):
        self.listAll.clear()
        self.listSelected.clear()
        self._untrackedData.clear()
        self._trackedData.clear()
        #~ self._fillLists()
        self.close()

    def _pickedUnselectedItem(self, item):
        self._currentUnSelectedItem = item
        self.addToList.setDisabled(False)

    def _pickedSelectedItem(self, item):
        self._currentSelectedItem = item
        self.removeFromList.setDisabled(False)

    def _moveToSelected(self, item):
        index = self._untrackedData.index(item.text())
        self._trackedData.append(self._untrackedData.pop(index))
        self.listSelected.addItem(self.listAll.takeItem(self.listAll.row(item)))
        if self.listAll.__len__() == 0:
            self.addToList.setDisabled(True)

    def _moveToUnselected(self, item):
        index = self._trackedData.index(item.text())
        self._untrackedData.append(self._trackedData.pop(index))
        self.listAll.addItem(self.listSelected.takeItem(self.listSelected.row(item)))
        if self.listSelected.__len__() == 0:
            self.removeFromList.setDisabled(True)

    def _addToList(self):
        self._moveToSelected(self.listAll.selectedItems())

    def _removeFromList(self):
        self.listSelected.addItems(self.listSelected.selectedItems())
        for elem in self.listSelected.selectedItems():
            self.listSelected.takeItem(self.listSelected.row(elem))

    def _emitTrackedData(self):
        self.trackedData.emit(self._trackedData)


class loggerBox(QtGui.QWidget):

    def __init__(self, parent=None):
        super(loggerBox, self).__init__(parent)
        uic.loadUi("logBOX.ui", self)

    def addText(self,text):
        self.messageWindow.insertPlainText(text)



class quitDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(quitDialog, self).__init__(parent)
        uic.loadUi("quitDialog.ui", self)
        self.cancel.clicked.connect(self.close)



class resetDialog(QtGui.QDialog):
    resetOK = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(resetDialog, self).__init__(parent)
        uic.loadUi("resetDialog.ui", self)
        self.cancelButton.clicked.connect(self.close)
        self.okButton.clicked.connect(self._returnOK)

    def _returnOK(self):
        self.resetOK.emit(0)
        self.close()



class multiTrackedDataView(pg.GraphicsLayoutWidget):

    def __init__(self, trackinfo, parent = None):
        super(multiTrackedDataView, self).__init__(parent)

        # check the number of plots
        trackedDataValues = trackinfo.value
        trackedDataErrors = trackinfo.error
        resultNames = trackinfo.names
        plotnumber = len(resultNames)

        # divide the plotWidget - decision table how many plots per row
        plotsPerRow = 0
        if plotnumber < 4:
            plotsPerRow = 1
        elif plotnumber <= 6:
            plotsPerRow = 2
        elif plotnumber <= 12:
            plotsPerRow = 3
        elif plotnumber <= 20:
            plotsPerRow = 4
        else:
            plotsPerRow = 5

        self.setWindowTitle(trackinfo.name)

        plotcounter = 0
        for paramname in resultNames:
            p = self.addPlot(title=paramname, x=trackedDataValues, y=trackinfo.getValues(paramname), pen=None, symbolPen=None, symbolSize=10, symbolBrush=(0, 0, 255, 90))
            plotcounter += 1
            if ( plotcounter % plotsPerRow ) == 0:
                self.nextRow()
                plotcounter = 0
        self.show()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())
