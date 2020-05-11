try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5 import QtTest

except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
# import pandas as pd
from libs.utils import newIcon, labelValidator
from libs.ustr import ustr
from qtmodern import styles, windows
import sys
import os
BB = QDialogButtonBox



class QCustomQWidget_3(QWidget):
    def __init__(self, imagePath, parent=None, text=None, foldername=None,nameLabel=None ):
        super(QCustomQWidget_3, self).__init__(parent)
        self.imagePath = imagePath
        self.text = text
        self.textQVBoxLayout = QVBoxLayout()
        self.textUpQLabel = QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.allQHBoxLayout = QVBoxLayout()
        self.iconQLabel = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout)
        self.setLayout(self.allQHBoxLayout)
        self.textUpQLabel.setStyleSheet('''
            color: rgb(255, 255, 255);
        ''')
        # pxmap = QPixmap(imagePath)
        self.iconQLabel.setPixmap(QPixmap(imagePath).scaledToWidth(32))
        # self.iconQLabel.setMaximumWidth(50)
        self.textUpQLabel.setText(self.text)
        self.textUpQLabel.setFont(QFont('SansSerif', 13))
        self.foldername=foldername
        self.nameLabel=nameLabel

    def getText(self):
        return self.text

    def mousePressEvent(self, event):
        print("clicked")
        self.foldername = self.text
        self.nameLabel.setText('your choose: {}'.format(self.foldername))

class folderServerDialog(QDialog):

    def __init__(self, parent=None, data_folders = ['aa', 'ccc', 'dd', 'ee']*10):
        super(folderServerDialog, self).__init__(parent)
        title = 'get data from server'
        self.setWindowTitle(title)
        grid = QGridLayout()

        self.exists_folders_label = QLabel('exists data in server')
        grid.addWidget(self.exists_folders_label)

        self.foldername = None
        self.nameLabel = QLabel('your choose: {}'.format(self.foldername))

        self.data_folders = data_folders
        # self.fileListWidget = QGridLayout()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.fileListWidget = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        grid.addWidget(self.scrollArea)

        folder_icon_path = 'resources/icons/open.png'
        for i, fname in enumerate(self.data_folders):
            myQCustomQWidget = QCustomQWidget_3(folder_icon_path, text=fname,  foldername=self.foldername,nameLabel=self.nameLabel)
            self.fileListWidget.addWidget(myQCustomQWidget, i//5, i%5)

        # grid.addItem(self.fileListWidget)
        grid.addWidget(self.nameLabel)

        self.saveDirLayout = QHBoxLayout()

        self.saveDir =  os.getcwd()
        self.saveDirBtn = QPushButton('Save dir')
        self.saveDirBtn.clicked.connect(self.saveFileDialog)
        self.saveDirLayout.addWidget(self.saveDirBtn)

        self.SaveLabel = QLabel('Save dir: {}'.format(self.saveDir))
        self.saveDirLayout.addWidget(self.SaveLabel)
        grid.addItem(self.saveDirLayout)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)
        # self.scroll.setWidget(grid)


    def saveFileDialog(self):
        targetDirPath = QFileDialog.getExistingDirectory(self, 'save Directory', self.saveDir,
                                                         QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if targetDirPath is not None and len(targetDirPath) > 1:
            self.saveDir = targetDirPath
            self.SaveLabel.setText('Save dir: {}'.format(self.saveDir))
        return

    def get_name(self):
        return (self.foldername, self.saveDir) if self.exec_() else (None,None)



def get_main_app(argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    styles.dark(app)
    app.setApplicationName('test')
    app.setWindowIcon(newIcon("app"))
    win = folderServerDialog()
    win.show()
    return app, win


def main():
    '''construct main app and run it'''
    app, _win = get_main_app()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
