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
except ImportError:
    print("[proc:stdreader] library psio not found; it will not be available!")
    pass

from adapt.iProcess import *


class specfilereader(IProcess):

    def __init__(self, ptype="specfilereader"):
        super(specfilereader, self).__init__(ptype)

        self._inPar = ProcessParameter("filename", str)
        self._outPar = ProcessParameter("outputdata", str)
        self._scanlistPar = ProcessParameter("scanlist", str, None, optional=True)
        self._stridePar = ProcessParameter("stride", int, 1, optional=True)
        self._parameters.add(self._inPar)
        self._parameters.add(self._outPar)
        self._parameters.add(self._scanlistPar)
        self._parameters.add(self._stridePar)

    def initialize(self):
        self._scanlist = self._scanlistPar.get()
        self.data = dataHandler.DataHandler(self._inPar.get(), typehint="spec").getFileHandler().getAll(self._scanlist)
        self._stride = self._stridePar.get()
        self.dataIterator = iter(self.data)

    def execute(self, data):
        # read next entry from spec file, 
        # put scandata object to common memory
        try:
            data.addData(self._outPar.get(), next(self.dataIterator))
        except StopIteration:
            print("---End of data reading from spec file ---")
            raise StopIteration

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def getData(self):
        return self.data

    def getConfigGUI(self):
        return specfilereaderGUI()


class specfilereaderGUI(QtGui.QWidget):
    pDict = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(specfilereaderGUI, self).__init__(parent)
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        formfile = os.path.join(dir_path, "ui/specfilereader.ui")
        uic.loadUi(formfile, self)
        self.chooseInputFileBtn.clicked.connect(self.getAndOpenFile)
        self.okBtn.clicked.connect(self.emittit)
        self.okBtn.setDisabled(True)
        self._specReaderDict = {}

    def getAndOpenFile(self):
        self._file = QtGui.QFileDialog.getOpenFileName(self, 'Choose spec file', '.', "SPEC files (*.spc *.spe *.spec)")
        self.inputFileLE.setText(self._file)
        if self._file is not None:
            self.okBtn.setDisabled(False)

    def getParameterDict(self):
        return self._specReaderDict

    def setParameterDict(self, paramDict):
         self._specReaderDict = paramDict
         self.inputFileLE.setText(self._specReaderDict["filename"])
         self.scanSelectionInput.setText(self._specReaderDict["scanlist"])

    def emittit(self):
        self._specReaderDict["type"] = "specfilereader"
        self._specReaderDict["filename"] =  self._file
        self._specReaderDict["scanlist"] = self.scanSelectionInput.text()
        self._specReaderDict["outputdata"] = "default"
        self.pDict.emit(self._specReaderDict)
