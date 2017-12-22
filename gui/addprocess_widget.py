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

from PyQt4 import QtCore, QtGui
import sys

from adapt import steering

class addProcess(QtGui.QDialog):
    
    processHeader = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super(addProcess, self).__init__(parent)
        self._defaultname = 'default'
        self._procList = steering.Steering().getProcessTypeList()
        layout = QtGui.QGridLayout()
        namelabel = QtGui.QLabel("Name: ")
        typelabel = QtGui.QLabel("Type: ")
        self.name = QtGui.QLineEdit(self._defaultname)
        self.cb = QtGui.QComboBox()
        self.cb.addItems(self._procList)
        self.add = QtGui.QPushButton("Add")
        self.cancel = QtGui.QPushButton("Cancel")

        layout.addWidget(namelabel, 0, 0)
        layout.addWidget(typelabel, 1, 0)
        layout.addWidget(self.name, 0, 1)
        layout.addWidget(self.cb, 1, 1)
        layout.addWidget(self.add, 2, 0)
        layout.addWidget(self.cancel, 2, 1)

        self.setLayout(layout)
        
        #~ self.name
        self.cancel.clicked.connect(self.close)
        self.add.clicked.connect(self.emitProcessHeader)

    def emitProcessHeader(self):

        if(self.name.text() != self._defaultname):
            self.processHeader.emit(self.name.text(), self.cb.currentText())
            self.close()
        else:
            self.name.setStyleSheet("color: yellow;"
                                   "background-color: red;")

