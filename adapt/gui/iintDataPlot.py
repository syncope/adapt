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
import numpy as np

from adapt.utilities import getUIFile



class iintDataPlot(QtGui.QDialog):
    #~ mouseposition = QtCore.pyqtSignal(float,float)
    currentIndex = QtCore.pyqtSignal(int)
    blacklist = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(iintDataPlot, self).__init__(parent)
        uic.loadUi(getUIFile("iintSimplePlot.ui"), self)
        self.showPreviousBtn.clicked.connect(self.decrementCurrentScanID)
        self.showNextBtn.clicked.connect(self.incrementCurrentScanID)
        self.showRAW.stateChanged.connect(self._toggleRAW)
        self.showDES.stateChanged.connect(self._toggleDES)
        self.showBKG.stateChanged.connect(self._toggleBKG)
        self.showSIG.stateChanged.connect(self._toggleSIG)
        self.showFIT.stateChanged.connect(self._toggleFIT)
        self.logScale.stateChanged.connect(self._toggleLOG)
        self.showRAW.stateChanged.connect(self.plot)
        self.showDES.stateChanged.connect(self.plot)
        self.showBKG.stateChanged.connect(self.plot)
        self.showSIG.stateChanged.connect(self.plot)
        self.showFIT.stateChanged.connect(self.plot)
        self.logScale.stateChanged.connect(self.plot)
        self.viewPart.scene().sigMouseClicked.connect(self.mouse_click)
        self.blacklistButton.clicked.connect(self._blacklisting)
        self._setBLB2Add()
        self._blacklist = []
        self._currentIndex = 0
        self.currentIndex.emit(self._currentIndex)
        self._showraw = True
        self._showdespike = False
        self._showbkg = False
        self._showbkgsubtracted = False
        self._tmpFit = None
        self._logScale = False
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
        self.hide()

    def update(self, action=None):
        self._checkDataAvailability()
        if(action == "plotfit"):
            self.showFIT.setChecked(True)
        self.plot()

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
        if( self._currentIndex in self._blacklist):
            self._setBLB2Rm()
        else:
            self._setBLB2Add()
        
        self.showID.setText(str(datum.getData("scannumber")))
        xdata = datum.getData(self._motorName)
        ydata = datum.getData(self._observableName)
        if ( self._logScale ):
            ydata = np.log10(np.clip(ydata, 10e-3, np.inf))
        self.viewPart.clear()
        if( self._showraw):
            self._theDrawItem = self.viewPart.plot(xdata, ydata, pen=None, symbolPen='w', symbolBrush='w', symbol='+')
        if( self._showdespike ):
            despikeData = datum.getData(self._despObservableName)
            if ( self._logScale ):
                despikeData = np.log10(np.clip(despikeData, 10e-3, np.inf))
            self.viewPart.plot(xdata, despikeData, pen=None, symbolPen='y', symbolBrush='y', symbol='o')
        if( self._showbkg ):
            bkg = datum.getData(self._backgroundPointsName)
            if ( self._logScale ):
                bkg = np.log10(np.clip(bkg, 10e-3, np.inf))
            self.viewPart.plot(xdata, bkg, pen=None, symbolPen='r', symbolBrush='r', symbol='+')
        if( self._showbkgsubtracted ):
            signal = datum.getData(self._signalName)
            if ( self._logScale ):
                signal = np.log10(np.clip(signal, 10e-3, np.inf))
            self.viewPart.plot(xdata, signal, pen=None, symbolPen='b', symbolBrush='b', symbol='o')
        if( self._showsigfit ):
            fitdata = datum.getData(self._fittedSignalName)
            if ( self._logScale ):
                fitdata = np.log10(np.clip(fitdata, 10e-3, np.inf))
            self.viewPart.plot(xdata, fitdata, pen='r')

    def plotFit(self, ydata):
        datum = self._dataList[self._currentIndex]
        xdata = datum.getData(self._motorName)
        if self._tmpFit != None:
            self._tmpFit.clear()
        self.viewPart.disableAutoRange()
        if ( self._logScale ):
            ydata = np.log10(np.clip(ydata, 10e-3, np.inf))
        self._tmpFit = self.viewPart.plot(xdata, ydata, pen='g') #, symbol='+')

    def removeGuess(self):
        self._tmpFit.clear()
        self.viewPart.enableAutoRange()

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

    def _toggleLOG(self):
        self._logScale = not self._logScale

    def incrementCurrentScanID(self):
        self._currentIndex += 1
        if ( self._currentIndex >= len(self._dataList) ):
            self._currentIndex -= len(self._dataList)
        self.currentIndex.emit(self._currentIndex)
        self.plot()

    def decrementCurrentScanID(self):
        self._currentIndex -= 1
        if ( self._currentIndex < 0  ):
            self._currentIndex += len(self._dataList)
        self.currentIndex.emit(self._currentIndex)
        self.plot()

    def mouse_click(self, event):
        position = self._theDrawItem.mapFromScene(event.pos())
        self.xPosition.setText("%.3f" % position.x())
        self.yPosition.setText("%.3f" % position.y())
        #~ self.mouseposition.emit(x, y)

    def getCurrentIndex(self):
        return self._currentIndex

    def setCurrentIndex(self, index):
        self._currentIndex = index
        self.plot()

    def getCurrentSignal(self):
        datum = self._dataList[self._currentIndex]
        return datum.getData(self._motorName), datum.getData(self._signalName)

    def _blacklisting(self):
        ci = self._currentIndex
        if ci < 0:
            ci = len(self._dataList) + ci
        elif ci > len(self._dataList):
            ci -= len(self._dataList)
        if ci in self._blacklist:
            i = self._blacklist.index(ci)
            del self._blacklist[i]
            self._setBLB2Add()
        else:
            self._blacklist.append(ci)
            self._setBLB2Rm()
        self.blacklist.emit(self._blacklist)

    def _setBLB2Add(self):
        self.blacklistButton.setStyleSheet("color: white;background-color: green;")
        self.blacklistButton.setText("Add to blacklist")

    def _setBLB2Rm(self):
        self.blacklistButton.setStyleSheet("color: yellow;background-color: red;")
        self.blacklistButton.setText("Remove from blacklist")

