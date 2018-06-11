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
    mouseposition = QtCore.pyqtSignal(float,float)
    currentIndex = QtCore.pyqtSignal(int)

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
        if ( self._logScale ):
            trimmeddata = np.clip(ydata, 10e-3, np.inf)
            ydata = np.log10(trimmeddata)

        self.viewPart.clear()
        if( self._showraw):
            self._theDrawItem = self.viewPart.plot(xdata, ydata, pen=None, symbolPen='w', symbolBrush='w', symbol='+')
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
        self.viewPart.disableAutoRange()
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
        if ( self._currentIndex < (-1)*len(self._dataList) ):
            self._currentIndex += len(self._dataList)
        self.currentIndex.emit(self._currentIndex)
        self.plot()

    def mouse_click(self, event):
        position = self._theDrawItem.mapFromScene(event.pos())
        x = float("%.3f" % position.x())
        y = float("%.3f" % position.y())
        self.mouseposition.emit(x, y)

    def getCurrentIndex(self):
        return self._currentIndex

    def getCurrentSignal(self):
        datum = self._dataList[self._currentIndex]
        return datum.getData(self._motorName), datum.getData(self._signalName)
