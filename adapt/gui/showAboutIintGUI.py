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
from adapt import __version__ as ver
from adapt import __iintguiversion__ as igver

class ShowAboutIintGUI(QtGui.QDialog):
    
    def __init__(self, parent=None):
        super(ShowAboutIintGUI, self).__init__(parent)
        uic.loadUi(getUIFile("about-iintgui.ui"), self)
        
        self.adaptText = '''iint-gui is an application built within the ADAPT framework.
        ADAPT is written and maintained by Christoph Rosemann (FS-EC @ DESY)
        mail address: christoph.rosemann@desy.de'''
        self.iintText = '''iint-gui is based on iint, written by Sonia Francoual (beamline P09, FS-PEX @ DESY)
        mail address: sonia.francoual@desy.de'''
                            
        self.infoText = 'This is version ' + str(ver) + ' of ADAPT and version ' + str(igver) + ' of iint-gui'
        self._setAndShow()

    def _setAndShow(self):
        self.adaptlabel.setText(self.adaptText)
        self.iintlabel.setText(self.iintText)
        self.infolabel.setText(self.infoText)
        font = QtGui.QFont("Arial", 12)
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.adaptlabel.setFont(font)
        self.iintlabel.setFont(font)
        self.infolabel.setFont(font)
        self.show()
