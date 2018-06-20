
from PyQt4 import QtCore, QtGui

import ui_adaptConfig

class adapt_mw(QtGui.QMainWindow, ui_adaptConfig.Ui_adaptConfig):
    
    def __init__(self, parent=None):
        super(adapt_mw, self).__init__(parent)
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
    myapp = adapt_mw()
    myapp.show()
    sys.exit(app.exec_())

