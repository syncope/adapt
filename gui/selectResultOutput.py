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


class SelectResultOutput(QtGui.QDialog):
    accept = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SelectResultOutput, self).__init__(parent)
        uic.loadUi(getUIFile("selectResultOutput.ui"), self)
        self.cancel.clicked.connect(self.close)
        self.ok.clicked.connect(self._returnOK)

    def _returnOK(self):
        self.accept.emit()
        self.close()

    def setNames(self, resultfilename=None, fitresultfilename=None):
        self.resultFilename.setText(resultfilename)
        self.pdfFilename.setText(fitresultfilename)

    def getNames(self):
        return self.resultFilename.text(), self.pdfFilename.text()
