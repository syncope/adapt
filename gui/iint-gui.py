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


import sys
from PyQt4 import QtCore, QtGui, uic

from adapt import processingConfiguration

__version__ ="0.0.1"

class iintGUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(iintGUI, self).__init__(parent)
        uic.loadUi("iint-gui.ui", self)
        
        self._procConfig = processingConfiguration.ProcessingConfiguration()
        
        # define the connections
        # input section:
        self.chooseInputFileBtn.clicked.connect(self.getFile)

        # output section
        self.chooseOutputFileBtn.clicked.connect(self.defineOutput)
        
        # observable section
        
        # background section
        
        # signal section
        
        # processing section

    def getFile(self):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose spec file', '.')

    def defineOutput(self):
        self._outfile = QtGui.QFileDialog.getOpenFileName(self, 'Select output file', '.')
        
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = iintGUI()
    ui.show()
    sys.exit(app.exec_())

