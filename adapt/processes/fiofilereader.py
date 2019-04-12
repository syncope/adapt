# Copyright (C) 2019  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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


# recent re-structuring: use psio library for reading fio files

try:
    from psio import dataHandler
except ImportError:
    print("[proc:stdreader] library psio not found; it will not be available!")
    pass

from adapt.iProcess import *


class fiofilereader(IProcess):

    def __init__(self, ptype="fiofilereader"):
        super(fiofilereader, self).__init__(ptype)

        self._inPar = ProcessParameter("filenames", list)
        self._outPar = ProcessParameter("output", str)
        self._parameters.add(self._inPar)
        self._parameters.add(self._outPar)

    def initialize(self):
        self._outname = self._outPar.get()
        self.data = dataHandler.DataHandler(self._inPar.get(), typehint="fio").getFileHandler().getAll()
        self.dataIterator = iter(self.data)

    def execute(self, data):
        currentdatum = self.dataIterator.__next__()
        data.addData(self._outname, currentdatum)

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def getData(self):
        return self.data

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def getConfigGUI(self):
        return fiofilereaderGUI()


class fiofilereaderGUI(QtGui.QWidget):
    valuesSet = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(fiofilereaderGUI, self).__init__(parent)
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        formfile = os.path.join(dir_path, "ui/fiofilereader.ui")
        uic.loadUi(formfile, self)
        self.chooseInputFileBtn.clicked.connect(self.getAndOpenFile)
        self.okBtn.clicked.connect(self._doemit)
        self.okBtn.clicked.connect(self.close)
        self.cancel.clicked.connect(self.close)
        self.okBtn.setDisabled(True)
        self._fioReaderDict = {}
        self._files = None
        self.chooseInputFileBtn.setToolTip("Click here to open a file dialog to select a fio file.")
        self.fileList.setToolTip("Here the names of the fio files will be displayed after choosing by dialog.")

    def reset(self):
        self.inputFileLE.setText('')
        self.okBtn.setDisabled(True)
        self._files = None
        self._fioReaderDict.clear()

    def getAndOpenFile(self):
        self._files = QtGui.QFileDialog.getOpenFileNames(self, 'Choose FIO file(s)', '.', "FIO files (*.fio)")
        self.fileList.addItems(self._files)
        self._checkValues()

    def getParameterDict(self):
        self._fioReaderDict["type"] = "fiofilereader"
        self._fioReaderDict["filenames"] = self._files
        self._fioReaderDict["output"] = "default"
        return self._fioReaderDict

    def setParameterDict(self, paramDict):
        self._fioReaderDict = paramDict
        self._files = self._fioReaderDict["filenames"]
        # fio parts are missing
        #~ self.inputFileLE.setText(self._file)
        self.okBtn.setDisabled(False)

    def _checkValues(self):
        if self._files is not None:
            self.okBtn.setDisabled(False)

    def _doemit(self):
        self.valuesSet.emit("fio")
