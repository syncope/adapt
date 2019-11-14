# Copyright (C) 2017-8  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in version 2
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


# recent re-structuring: use psio library for reading spec files

try:
    from psio import dataHandler
    from psio import psioException
except ImportError:
    print("[proc:stdreader] library psio not found; it will not be available!")
    pass

from adapt.iProcess import *
from adapt.adaptException import AdaptFileReadException


class specfilereader(IProcess):

    def __init__(self, ptype="specfilereader"):
        super(specfilereader, self).__init__(ptype)

        self._inPar = ProcessParameter("filename", str)
        self._outPar = ProcessParameter("output", str)
        self._scanlistPar = ProcessParameter("scanlist", str, None, optional=True)
        self._parameters.add(self._inPar)
        self._parameters.add(self._outPar)
        self._parameters.add(self._scanlistPar)

    def initialize(self):
        self._scanlist = self._scanlistPar.get()
        self._outname = self._outPar.get()
        try:
            self.data = dataHandler.DataHandler(self._inPar.get(), typehint="spec").getFileHandler().getAll(self._scanlist)
        except(psioException.PSIOException):
            raise AdaptFileReadException
        self.dataIterator = iter(self.data)

    def execute(self, data):
        currentdatum = self.dataIterator.__next__()
        data.addData(self._outname, currentdatum)
        if currentdatum.getMCAName() != '':
            data.addData("MCAName", datum.getMCAName())
            data.addData("MCA", datum.getMCA())

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def getData(self):
        return self.data

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def getConfigGUI(self):
        return specfilereaderGUI()


class specfilereaderGUI(QtGui.QWidget):
    valuesSet = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(specfilereaderGUI, self).__init__(parent)
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        formfile = os.path.join(dir_path, "ui/specfilereader.ui")
        uic.loadUi(formfile, self)
        self.chooseInputFileBtn.clicked.connect(self.getAndOpenFile)
        self.scanSelectionInput.textEdited.connect(self._checkValues)
        self.okBtn.clicked.connect(self._doemit)
        self.okBtn.clicked.connect(self.close)
        self.cancel.clicked.connect(self.close)
        self.okBtn.setDisabled(True)
        self._specReaderDict = {}
        self._file = None
        self.chooseInputFileBtn.setToolTip("Click here to open a file dialog to select a spec file.")
        self.inputFileLE.setToolTip("Here the name of the spec file can be typed; or it will be displayed after choosing by dialog.")
        self.scanSelectionInput.setToolTip("Enter here the numbers of the scans of interest.\n" +
                                           "The style follows printer dialogs. A comma ',' separates selections, a minus '-' defines ranges.\n" +
                                           "A double colon ':' selects the step size.\n" +
                                           "Examples:\n" +
                                           "'361-374:3' choses every third scan in the range between 361 and 374, and \n" +
                                           "'361, 364, 367, 370, 373' selects the same scans.")

    def reset(self):
        self.inputFileLE.setText('')
        self.scanSelectionInput.setText('')
        self.okBtn.setDisabled(True)
        self._file = None
        self._specReaderDict.clear()

    def getAndOpenFile(self):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose spec file', '.', "SPEC files (*.spc *.spe *.spec)")
        self.inputFileLE.setText(self._file)

    def getParameterDict(self):
        self._specReaderDict["type"] = "specfilereader"
        self._specReaderDict["filename"] = self._file
        self._specReaderDict["scanlist"] = self.scanSelectionInput.text()
        self._specReaderDict["output"] = "default"
        return self._specReaderDict

    def setParameterDict(self, paramDict):
        self._specReaderDict = paramDict
        self._file = self._specReaderDict["filename"]
        self.inputFileLE.setText(self._file)
        self.scanSelectionInput.setText(self._specReaderDict["scanlist"])
        self.okBtn.setDisabled(False)

    def _checkValues(self):
        if self._file is not None and self.scanSelectionInput.text() != '':
            self.okBtn.setDisabled(False)

    def _doemit(self):
        self.valuesSet.emit("spec")
