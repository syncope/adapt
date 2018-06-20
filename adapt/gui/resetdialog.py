
from PyQt4 import QtCore, QtGui

import ui_resetdialog

class resetDialog(QtGui.QDialog, ui_resetdialog.Ui_Dialog):
    
    def __init__(self, parent=None):
        super(resetDialog, self).__init__(parent)
        self.setupUi(self)
        #~ self.updateUi()

    def updateUi(self):
        pass

    @QtCore.pyqtSlot()
    def reject(self):
        print("reject")
        self.close()

    @QtCore.pyqtSlot()
    def accept(self):
        print("accept")

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    myapp = resetDialog()
    myapp.show()
    sys.exit(app.exec_())

