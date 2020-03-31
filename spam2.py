from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import  sys
from PyQt5 import QtTest

BB = QDialogButtonBox



class uploadDialog(QDialog):

    def __init__(self, parent=None,  name=10):
        super(uploadDialog, self).__init__(parent)
        title = 'uploading'
        self.setWindowTitle(title)

        grid = QGridLayout()

        self.nameLabel = QLabel('folder name to upload')
        grid.addWidget(self.nameLabel, 4, 0)
        self.nameEdit = QLineEdit()
        self.nameEdit.setPlaceholderText('folder name to upload')
        self.nameEdit.setText('{}'.format(name))
        # self.nameEdit.setValidator(QIntValidator())
        grid.addWidget(self.nameEdit)
        print(type(self.nameEdit.text()))

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        # bb.button(BB.Ok).setIcon(newIcon('done'))
        # bb.button(BB.Ok).setText('Train')

        # bb.button(BB.Cancel).setIcon(('undo'))
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)


    def get_name(self):
        return self.nameEdit.text() if self.exec_() else None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = uploadDialog()
    window.show()
    sys.exit(app.exec_())
