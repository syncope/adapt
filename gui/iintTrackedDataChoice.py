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


class iintTrackedDataChoice(QtGui.QWidget):
    trackedData = QtCore.pyqtSignal(list)

    def __init__(self, dataelement=None, parent=None):
        super(iintTrackedDataChoice, self).__init__(parent)
        uic.loadUi(getUIFile("chooseTrackedData.ui"), self)
        self._data = dataelement
        self._initialNames = self._data.getLabels()
        for elem in list(self._data.getCustomKeys()):
            self._initialNames.append(elem)
        self._fillLists()
        self.okBtn.clicked.connect(self._emitTrackedData)
        self.okBtn.clicked.connect(self._reset)
        self.cancel.clicked.connect(self._reset)
        self.addToList.setDisabled(True)
        self.addToList.clicked.connect(self._moveButtonToSelected)
        self.removeFromList.clicked.connect(self._moveButtonToUnselected)
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

    def _moveButtonToSelected(self):
        index = self._untrackedData.index(self._currentUnSelectedItem.text())
        self._trackedData.append(self._untrackedData.pop(index))
        self.listSelected.addItem(self.listAll.takeItem(self.listAll.row(self._currentUnSelectedItem)))
        self.listAll.setCurrentRow(-1)

    def _moveButtonToUnselected(self):
        index = self._trackedData.index(self._currentSelectedItem.text())
        self._untrackedData.append(self._trackedData.pop(index))
        self.listAll.addItem(self.listSelected.takeItem(self.listSelected.row(self._currentSelectedItem)))
        self.listSelected.setCurrentRow(-1)

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

