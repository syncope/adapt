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



class iintInspectAnalyze(QtGui.QWidget):

    def __init__(self, parent=None):
        super(iintInspectAnalyze, self).__init__(parent)
        uic.loadUi(getUIFile("inspectAnalyze.ui"), self)
        self.trackData.setToolTip("Open a dialog to select column and header data to be included in the output file.")
        self.polAnalysis.setToolTip("Run a polarization analysis on the current data; non-interactive. A pdf file and a .stokes file with be created and saved. The pdf file will be opened in an external viewer.")
        self.saveResults.setToolTip("Opens a dialog to allow the saving of the output file. The file automatically contains the scan number, all fit parameters and the iint sum including their errors. In addition the data is included that has been selected in the 'Choose data to track' dialog.")
        self.inspectionPlots.setToolTip("Create and save a pdf file that shows the temperature and magnetic field dependence of the fit parameters and the calculated iint sum. Non-interactive. Will open an external pdf viewer showing the created pdf file.")


    def activate(self):
        self.trackData.setDisabled(False)
        self.polAnalysis.setDisabled(False)
        self.saveResults.setDisabled(False)
        self.inspectionPlots.setDisabled(False)

    def reset(self):
        self.trackData.setDisabled(True)
        self.polAnalysis.setDisabled(True)
        self.saveResults.setDisabled(True)
        self.inspectionPlots.setDisabled(True)
