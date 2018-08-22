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
from adapt.utilities import getUIFile


class iintSignalHandling(QtGui.QWidget):
    modelcfg = QtCore.pyqtSignal(str, int)

    def __init__(self, pDict, parent=None):
        super(iintSignalHandling, self).__init__(parent)
        uic.loadUi(getUIFile("fitpanel.ui"), self)
        self.setParameterDict(pDict)
        self.configureFirst.clicked.connect(self.emitfirstmodelconfig)
        self.configureSecond.clicked.connect(self.emitsecondmodelconfig)
        self.configureThird.clicked.connect(self.emitthirdmodelconfig)
        self.configureFourth.clicked.connect(self.emitfourthmodelconfig)
        self._inactive = [ True, True, True, True ]
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
        self.performFitPushBtn.setDisabled(True)
        self.configureFirst.setDisabled(True)

    def activate(self):
        self.activateConfiguration()
        self.activateFitting()

    def activateConfiguration(self):
        self.firstModelCB.setDisabled(False)
        self.configureFirst.setDisabled(False)

    def activateFitting(self):
        self.performFitPushBtn.setDisabled(False)

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
        self.activateFitting()

    def emitsecondmodelconfig(self):
        index = self.secondModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 1)

    def emitthirdmodelconfig(self):
        index = self.thirdModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 2)

    def emitfourthmodelconfig(self):
        index = self.fourthModelCB.currentIndex()
        self.modelcfg.emit(self._modelnames[index], 3)
