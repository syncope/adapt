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
from PyQt4 import QtCore, QtGui

from addprocess_widget import addProcess

__version__ ="0.0.0a"



class adaptmaingui(QtGui.QMainWindow):
    '''Base definition of the main window display for adapt'''

    def __init__(self, parent=None):
        super(adaptmaingui, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        # define global layout: horizontal division
        self._central = QtGui.QWidget()
        globallayout = QtGui.QHBoxLayout()
        listhandler = listHandler()
        globallayout.addLayout(listhandler)
        globallayout.addWidget(actionTabHandler())
        self._central.setLayout(globallayout)
        self.setCentralWidget(self._central)

        self.setWindowTitle("ADAPT")

class twobuttons(QtGui.QWidget):
    def __init__(self, parent=None):
        super(twobuttons, self).__init__(parent)
        self._layout = QtGui.QHBoxLayout()
        self._addButton = QtGui.QPushButton("Add process")
        self._removeButton = QtGui.QPushButton("Remove process")
        self._layout.addWidget(self._addButton)
        self._layout.addWidget(self._removeButton)
        self.setLayout(self._layout)
        self._addProcess = addProcess()
        self._addButton.clicked.connect(self._addProcess.show)

class listHandler(QtGui.QVBoxLayout):

    def __init__(self, parent=None):
        super(listHandler, self).__init__(parent)

        self._listHandle = guiListHandler()
        self.addWidget(self._listHandle)
        self.addWidget(twobuttons())
        
    def addProcess(self):
        pass

    def removeProcess(self):
        pass

class guiListHandler(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(guiListHandler, self).__init__(parent)

        #~ li = ["hallo", "nachbar", "ich", "nicht"]
        #~ self.addItems(li)

class actionTabHandler(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(actionTabHandler, self).__init__(parent)
        self.addTab(parameterConfigDisplay(self),"Process configuration")
        self.addTab(runControl(self),"Run control")
        self.addTab(runControl(self),"Visualization")

class parameterConfigDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        super(parameterConfigDisplay, self).__init__(parent)

class runControl(QtGui.QWidget):
    def __init__(self, parent=None):
        super(runControl, self).__init__(parent)
                
class visualizationHelpers(QtGui.QWidget):
    def __init__(self, parent=None):
        super(visualizationHelpers, self).__init__(parent)


def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = adaptmaingui()
    ex.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

