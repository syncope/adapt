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
from adapt.utilities import getUIFile
from adapt.processes import specfilereader

from . import iintDataPlot
from . import fileInfo
from . import iintObservableDefinition
from . import iintBackgroundHandling
from . import iintSignalHandling
from . import iintTrackedDataChoice
from . import quitDialog
from . import loggerBox
from . import resetDialog
from . import showFileContents
from . import iintMultiTrackedDataView
from . import iintInspectAnalyze
from . import selectResultOutput



class iintGUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(iintGUI, self).__init__(parent)
        uic.loadUi(getUIFile("iintMain.ui"), self)

        self.actionNew.triggered.connect(self._askReset)
        self.actionOpen_file.triggered.connect(self.choosefile)
        self.actionSave_file.triggered.connect(self._saveConfig)
        self.actionExit.triggered.connect(self._closeApp)
        self.action_Config_File.triggered.connect(self._showConfig)
        self.action_Spec_File.triggered.connect(self._showSpecFile)
        self.action_Fit_Results.triggered.connect(self._showFitResults)
        self.action_Results_File.triggered.connect(self._showResultsFile)

        # the steering helper object
        self._control = interactiveP09ProcessingControl.InteractiveP09ProcessingControl()

        # the quit dialog
        self._quit = quitDialog.QuitDialog()
        self._quit.quitandsave.clicked.connect(self._saveConfig)
        self._quit.quitandsave.clicked.connect(exit)
        self._quit.justquit.clicked.connect(exit)

        # the core independent variable in iint:
        self._motorname = ""
        self._rawdataobject = None

        self.imageTabs.removeTab(1)
        self.imageTabs.removeTab(0)
        self.imageTabs.hide()
        self.imageTabs.tabCloseRequested.connect(self.imageTabs.removeTab)
        self._simpleImageView = iintDataPlot.iintDataPlot(parent=self)
        self._simpleImageView.blacklist.connect(self._retrackDataDisplay)
        self._blacklist = []

        self._resetQuestion = resetDialog.ResetDialog()
        self._resetQuestion.resetOK.connect(self._resetAll)
        self._fileInfo = fileInfo.FileInfo()
        self._sfrGUI = specfilereader.specfilereaderGUI()
        self._obsDef = iintObservableDefinition.iintObservableDefinition()
        self._obsDef.doDespike.connect(self._control.useDespike)
        self._bkgHandling = iintBackgroundHandling.iintBackgroundHandling(self._control.getBKGDicts())
        self._bkgHandling.bkgmodel.connect(self._control.setBkgModel)
        self._signalHandling = iintSignalHandling.iintSignalHandling(self._control.getSIGDict())
        self._signalHandling.passModels(self._control.getFitModels())
        self._signalHandling.modelcfg.connect(self.openFitDialog)
        self._signalHandling.performFitPushBtn.clicked.connect(self._prepareSignalFitting)
        self._fitList = []

        self._inspectAnalyze = iintInspectAnalyze.iintInspectAnalyze()
        self._inspectAnalyze.trackData.clicked.connect(self._dataToTrack)
        self._inspectAnalyze.polAnalysis.clicked.connect(self._runPolarizationAnalysis)
        self._inspectAnalyze.saveResults.clicked.connect(self._saveResultsFile)
        self._inspectAnalyze.inspectionPlots.clicked.connect(self._showInspectionPlots)

        self._saveResultsDialog = selectResultOutput.SelectResultOutput()
        self._saveResultsDialog.accept.connect(self._control.setResultFilename)
        self._saveResultsDialog.accept.connect(self.runOutputSaving)

        self._loggingBox = loggerBox.LoggerBox()

        self.verticalLayout.addWidget(self._fileInfo)
        self.verticalLayout.addWidget(self._obsDef)
        self.verticalLayout.addWidget(self._bkgHandling)
        self.verticalLayout.addWidget(self._signalHandling)
        self.verticalLayout.addWidget(self._inspectAnalyze)
        self.verticalLayout.addWidget(self._loggingBox)

        self._fileInfo.newspecfile.connect(self.showSFRGUI)
        self._sfrGUI.valuesSet.connect(self.runFileReader)
        self._obsDef.observableDicts.connect(self.runObservable)
        self._bkgHandling.bkgDicts.connect(self.runBkgProcessing)
        
        self.setGeometry(0,0,600,840)
        self._widgetList = []
        self._trackedDataDict = {}
        self._resultFileName = None

    def _resetInternals(self):
        self._motorname = ""
        del self._widgetList[:]
        self._trackedDataDict.clear()
        self._rawdataobject = None
        del self._blacklist[:]
        del self._fitList[:]
        self._resultFileName = None

    def _resetAll(self):
        self._resetInternals()
        self._simpleImageView.reset()
        self._fileInfo.reset()
        self._obsDef.reset()
        self._bkgHandling.reset()
        self._bkgHandling.setParameterDicts(self._control.getBKGDicts())
        self._signalHandling.reset()
        self._signalHandling.setParameterDict(self._control.getSIGDict())
        self._control.resetAll()
        self._sfrGUI.reset()
        self.resetTabs()
        self._inspectAnalyze.reset()

    def resetTabs(self, keepSpectra=False):
        self._control.resetTrackedData()
        if keepSpectra:
            ivtab = self.imageTabs.indexOf(self._simpleImageView)
            while self.imageTabs.count() > 1:
                for tab in range(self.imageTabs.count()):
                    if tab != ivtab:
                        self.imageTabs.removeTab(tab)
                        continue
        else:
            while self.imageTabs.count() >= 1:
                for tab in range(self.imageTabs.count()):
                    self.imageTabs.removeTab(tab)
            self.imageTabs.hide()

    def closeEvent(self, event):
        event.ignore()
        self._closeApp()

    def _showConfig(self):
        try:
            if self._file != "":
                self._widgetList.append(showFileContents.ShowFileContents(open(self._file).read()))
            else:
                return
        except AttributeError:
            self.message("Can't show config file, since none is present.\n")

    def _showSpecFile(self):
        try:
            self._widgetList.append(showFileContents.ShowFileContents(open(self._sfrGUI.getParameterDict()["filename"]).read()))
        except TypeError:
            self.message("Can't show spec file, since none has been selected yet.\n")
        return

    def _showResultsFile(self):
        try:
            self._widgetList.append(showFileContents.ShowFileContents(open(self._resultFileName).read()))
        except TypeError:
            self.message("Can't show results file, there is none yet.\n")

    def _showFitResults(self):
        self._widgetList.append(showFileContents.ShowFileContents(''.join(self._control.getSignalFitResults())))
        
    def message(self, text):
        self._loggingBox.addText(text)

    def warning(self, text):
        self._loggingBox.addRedText(text)

    def _closeApp(self):
        for i in self._widgetList:
            i.close()
        del self._widgetList[:]
        self._quit.show()

    def _saveConfig(self, num=None):
        savename, timesuffix  = self._control.proposeSaveFileName('')
        self._control.saveConfig(savename+".icfg")
        self._control.saveConfig(savename+timesuffix+".icfg")
        self.message("Saved config file " + str(savename) + ".\n")
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
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose iint config file', '.', "iint cfg files (*.icfg)")
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
        self._obsDef.setParameterDicts(self._control.getOBSDict(), self._control.getDESDict())
        self._obsDef.emittit()
        self._bkgHandling.setParameterDicts(self._control.getBKGDicts())
        self._bkgHandling.emittem()
        if self._control.getDESDict() != {}:
            self._obsDef.activateDespikingBox()

    def runFileReader(self):
        self._resetInternals()
        self._obsDef.reset()
        self._simpleImageView.reset()
        self._fileInfo.reset()
        self._bkgHandling.reset()
        self._bkgHandling.setParameterDicts(self._control.getBKGDicts())
        self._control.resetSIGdata()
        self._signalHandling.reset()
        self._signalHandling.setParameterDict(self._control.getSIGDict())
        self.resetTabs()
        self._inspectAnalyze.reset()
        self._control.resetAll()

        filereaderdict = self._sfrGUI.getParameterDict()
        self._fileInfo.setNames(filereaderdict["filename"], filereaderdict["scanlist"])
        self._control.setSpecFile(filereaderdict["filename"],filereaderdict["scanlist"])
        self.message("Reading spec file: " + str(filereaderdict["filename"]))
       
        sfr = self._control.createAndInitialize(filereaderdict)
        self._control.createDataList(sfr.getData(), self._control.getRawDataName())

        # to set the displayed columns etc. one element of the selected data is needed
        self._rawdataobject = self._control.getDataList()[0].getData(self._control.getRawDataName())
        self._motorname = self._rawdataobject.getMotorName()
        check = self._control.checkDataIntegrity(self._motorname)
        if check:
            self.warning("There are different motor names in the selection!\n Can't continue, please correct!")
            return

        self._control.setMotorName(self._motorname)
        # pass info to the observable definition part
        self._obsDef.passInfo(self._rawdataobject)
        self.message("... done.\n")

    def runObservable(self, obsDict, despDict, trapIntDict):
        self._simpleImageView.reset()
        self.resetTabs(keepSpectra=True)
        self._inspectAnalyze.reset()
        self._control.resetBKGdata()
        self._bkgHandling.setParameterDicts(self._control.getBKGDicts())
        self._control.resetSIGdata()
        self._signalHandling.setParameterDict(self._control.getSIGDict())
        self._control.resetFITdata()
        self._control.resetTrackedData()

        self.message("Computing the observable...")
        self._control.createAndBulkExecute(obsDict)
        self.message(" and plotting ...")
        self.plotit()

        # check whether despiking is activated, otherwise unset names
        if despDict != {}:
            self._control.useDespike(True)
            self._control.createAndBulkExecute(despDict)
            if( self._simpleImageView != None):
                self._simpleImageView.update("des")
        self._bkgHandling.activate()
        self._signalHandling.activate()
        self.message(" done.\n")

    def runBkgProcessing(self, selDict, fitDict, calcDict, subtractDict):
        self._inspectAnalyze.reset()
        self._control.resetSIGdata()
        self._signalHandling.setParameterDict(self._control.getSIGDict())
        self._control.resetFITdata()
        self._control.resetBKGdata()
        self._bkgHandling.setParameterDicts(self._control.getBKGDicts())

        self._control.resetTrackedData()
        self.resetTabs(keepSpectra=True)

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
            self._simpleImageView.update("bkg")

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
        self.imageTabs.addTab(self._simpleImageView,"Image Display")
        self.imageTabs.show()
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
        self.runSignalProcessing(fitDict)

    def runSignalProcessing(self, fitDict):
        self.message("Signal processing: first trapezoidal integration ...")
        self._control.createAndBulkExecute(self._control.getTrapIntDict())
        self.message(" ... done.")
        self.runSignalFitting(fitDict)

    def runSignalFitting(self, fitDict):
        self._inspectAnalyze.reset()
        self._control.resetTrackedData()
        self.resetTabs(keepSpectra=True)
        
        self.message("Fitting the signal, this can take a while ...")
        rundict = self._control.getSIGDict()
        rundict['model'] = fitDict
        self._control.createAndBulkExecute(rundict)
        self._control.createAndBulkExecute(self._control.getSignalFitDict())
        if( self._simpleImageView != None):
            self._simpleImageView.update("plotfit")
        trackinfo = self._control.getDefaultTrackInformation()
        tdv = iintMultiTrackedDataView.iintMultiTrackedDataView(trackinfo)
        self._trackedDataDict[trackinfo.getName()] = trackinfo
        self.imageTabs.addTab(tdv, trackinfo.getName())
        tdv.pickedTrackedDataPoint.connect(self._setFocusToSpectrum)
        self.message(" ... done.\n")
        self._inspectAnalyze.activate()

    def _runPolarizationAnalysis(self):
        self.message("Running the polarization analysis ...")
        polanadict = self._control.getPOLANADict()
        filename = polanadict["outputname"] + "_polarizationAnalysis.pdf"
        self._control.processAll(polanadict)
        self.message(" ... done.\n")
        from subprocess import call
        call(["evince", filename])

    def _setFocusToSpectrum(self, title, name, xpos, ypos):
        # very special function; lots of assumptions
        import math
        import numpy as np
        xvallist = self._trackedDataDict[title].getTrackedValues()
        yvallist = [i[0] for i in self._trackedDataDict[title].getFitParameterValue(name)]
        xindices = []
        yindices = []
        # since numpy does not provide a approximate 'where', iterate manually
        for xval in xvallist:
            if math.fabs(xval - xpos) < 0.00001:
                xindices.append(xvallist.index(xval))
        for yval in yvallist:
            if math.fabs(yval - ypos) < 0.00001:
                yindices.append(yvallist.index(yval))
        if len(xindices) == 1 and len(yindices) == 1:
            if xindices[0] == yindices[0]:
                self._simpleImageView.setCurrentIndex(xindices[0])
                self.imageTabs.setCurrentIndex(self.imageTabs.indexOf(self._simpleImageView))

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
        self._trackedDataChoice = iintTrackedDataChoice.iintTrackedDataChoice(rawScanData,self._control.getTrackedData() )
        self._trackedDataChoice.trackedData.connect(self._showTracked)
        self._trackedDataChoice.trackedData.connect(self._control.setTrackedData)

    def _showTracked(self, namelist):
        for name in namelist:
            trackinfo = self._control.getTrackInformation(name)
            tdv = iintMultiTrackedDataView.iintMultiTrackedDataView(trackinfo, self._blacklist)
            self._trackedDataDict[trackinfo.getName()] = trackinfo
            self.imageTabs.addTab(tdv, trackinfo.getName())
            tdv.pickedTrackedDataPoint.connect(self._setFocusToSpectrum)

    def _saveResultsFile(self):
        name, timesuffix = self._control.proposeSaveFileName()
        self._saveResultsDialog.setName(name+timesuffix)
        self._saveResultsDialog.show()

    def runOutputSaving(self):
        finalDict = self._control.getFinalizingDict()

        self.message("Saving results file ...")
        self._control.processAll(finalDict)
        self._resultFileName = finalDict["outfilename"]
        self.message(" ... done.\n")

    def _retrackDataDisplay(self, blacklist):
        self._blacklist = blacklist
        # if the blacklist has been changed, re-display the tracked data
        ivtab = self.imageTabs.indexOf(self._simpleImageView)

        while self.imageTabs.count() > 1:
            for tab in range(self.imageTabs.count()):
                if tab != ivtab:
                    self.imageTabs.removeTab(tab)
                    continue

        for k,v  in self._trackedDataDict.items():
            tdv = iintMultiTrackedDataView.iintMultiTrackedDataView(v, blacklist)
            tdv.pickedTrackedDataPoint.connect(self._setFocusToSpectrum)
            self.imageTabs.addTab(tdv, k)

    def _showInspectionPlots(self):
        tempDict = self._control.getInspectionDict()
        filename = tempDict["outputname"] + '_controlPlots.pdf'
        self.message("Generating temporary control plots ...")
        self._control.processAll(tempDict)
        self.message(" ... done.\n")
        from subprocess import call
        call(["evince", filename])
