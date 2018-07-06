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


class LoggerBox(QtGui.QWidget):

    def __init__(self, parent=None):
        super(LoggerBox, self).__init__(parent)
        uic.loadUi(getUIFile("logBOX.ui"), self)

    def addText(self,text):
        self.messageWindow.append(text)
        #~ self.messageWindow.insertPlainText(text)

    def addRedText(self, text):
        self.messageWindow.setTextColor(QtGui.QColor(255, 0, 0))
        self.messageWindow.append(text)
        self.messageWindow.setTextColor(QtGui.QColor(0, 0, 0))

