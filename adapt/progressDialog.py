# Copyright (C) 2019  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
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

from . import adaptException
from PyQt4 import QtCore, QtGui, uic

'''An implementation of the progress dialog of pyqt.
Overrides the close event by raising an exception.'''


class ProgressDialog(QtGui.QProgressDialog):

    def __init__(self, **kwargs):
        super(ProgressDialog, self).__init__()
        self.setRange(0, 100)
        self._button = QtGui.QPushButton("Stop processing")
        self._label = QtGui.QLabel("Processing...")
        self.setCancelButton(self._button)
        self.setLabel(self._label)
        self._button.clicked.connect(self._stoppit)
        self._stop = False

    def _stoppit(self):
        self._stop = True

    def isStopped(self):
        return self._stop

    def setValue(self, value):
        QtGui.QApplication.processEvents()
        super(ProgressDialog, self).setValue(value)
