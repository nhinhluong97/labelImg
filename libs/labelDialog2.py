try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5 import QtTest

except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
# from labelImg import MainWindow
import pandas as pd
from libs.utils import newIcon, labelValidator
from libs.custom_widget import QCustomQWidget_2, QCustomQWidget_3, QCustomQWidget
from libs.ustr import ustr
import os
BB = QDialogButtonBox
BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
folder_icon_path = os.path.join(BASE_DIR, 'resources/icons/open.png')
txt_icon_path = os.path.join(BASE_DIR, 'resources/icons/txt2.png')
# txt_icon_path = os.path.join(BASE_DIR, 'resources/icons/txt2.png')

class LabelDialog(QDialog):

    def __init__(self,  label=None, subLabels=None):
        super(LabelDialog, self).__init__()
        title = 'Label win'
        self.setWindowTitle(title)

        self.count = 0
        self.layout = QGridLayout()

        self.layout_label = QGridLayout()
        self.listLabel = []
        self.mainLabel = None

        self.addLabel(txt=label, opt=False)
        if subLabels is not None:
            for lb in subLabels:
                self.addLabel(lb)


        self.addBtn = QPushButton('Add')
        self.addBtn.clicked.connect( lambda x: self.addLabel(txt=None, listHint=[], opt=True))

        self.saveCheckBox = QCheckBox('Save format')
        self.saveCheckBox.setChecked(False)

        checkAddLayout = QVBoxLayout()
        checkAddLayout.addWidget(self.saveCheckBox)
        checkAddLayout.addWidget(self.addBtn)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)

        self.layout.addLayout(self.layout_label, 0,0, 1, 5)
        self.layout.addLayout(checkAddLayout, 0, 5)

        # self.layout.addWidget(self.addBtn, 1, 1)
        self.layout.addWidget(bb, 2, 0)

        self.layout.setColumnStretch(0, 5)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

        self.setLayout(self.layout)
        # self.mainLabel.show
        # self.resize(self.sizeHint())

        # self.mainLabel.setMinimumWidth(300)
        # self.mainLabel.showMaximized()
        # self.showMaximized()

        self.mainLabel.setFocus()


    def updateLayout(self):
        # for idx, lb in enumerate(self.listLabel):

        return

    def removeLabel(self, singleLB):
        self.listLabel.remove(singleLB)
        for i in reversed(range(singleLB.count())):
            singleLB.itemAt(i).widget().deleteLater()
        self.layout_label.removeItem(singleLB)
        self.resize(self.sizeHint())
        # self.layout_label.removeWidget(singleLB)
        return

    def addLabel(self, txt = None, listHint=[], opt=True):
        self.count += 1
        if opt:
            holderText = 'sub label'
        else:
            holderText = 'text label'

        singleLB = QGridLayout()
        edit = QLineEdit()
        if txt is None:
            edit.setPlaceholderText('{}'.format(holderText))
        else:
            edit.setPlaceholderText('{}'.format(holderText))
            edit.setText(txt)

        edit.setValidator(labelValidator())

        model = QStringListModel()
        model.setStringList(listHint)
        completer = QCompleter()
        completer.setModel(model)
        edit.setCompleter(completer)


        edit.setFont(QFont('SansSerif', 15))
        w_size = int(QFontMetrics(QFont('SansSerif', 15)).width(txt) * 1.6)
        edit.setMinimumWidth(max(w_size, 150))

        singleLB.addWidget(edit, 0, 0)

        if not opt:
            # print('txt', txt)
            self.mainLabel = edit

        if opt:
            btn = QPushButton('Remove')
            btn.clicked.connect(lambda i: self.removeLabel(singleLB))
            singleLB.addWidget(btn, 0, 1)

        self.listLabel.append(singleLB)
        self.layout_label.addLayout(singleLB,len(self.listLabel) - 1, 0)


    def validate(self):
        try:
            if all([l.itemAt(0).widget().text().trimmed() for l in self.listLabel]):
                self.accept()
        except AttributeError:
            # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
            if all([l.itemAt(0).widget().text().strip() for l in self.listLabel]):
                self.accept()
        return

    def postProcess(self):
        try:
            self.edit.setText(self.edit.text().trimmed())
        except AttributeError:
            # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
            self.edit.setText(self.edit.text())

    def popUp(self, list_text=None, move=True):
        if list_text is not None:
            assert (len(list_text)==len(self.listLabel)), 'len(list_text) must same len(self.listLabel)'
            for txt, layout in zip(list_text, self.listLabel):
                layout.itemAt(0).widget().setText(txt)
        return ([l.itemAt(0).widget().text().strip() for l in self.listLabel], self.saveCheckBox.checkState()) if self.exec() else (None, None)

class trainDialog(QDialog):

    def __init__(self, parent=None, listData=['a', 'c'], listPretrain=['c', 'd'],listnote=['c', 'd'], numEpoch=1000, charlists=None):
        super(trainDialog, self).__init__()
        title = 'Setting To Start Training'
        self.setWindowTitle(title)

        self.listDataBox = len(listData)*['']
        grid = QGridLayout()
        self.choose = []
        self.dataLabel = QLabel('Data folders')
        grid.addWidget(self.dataLabel, 0, 1)
        for i, v in enumerate(listData):
            self.listDataBox[i] = QCheckBox(v)
            grid.addWidget(self.listDataBox[i], i+1, 1)

        self.PretrainLabel = QLabel('Pretrain checkpoint')
        grid.addWidget(self.PretrainLabel, 0, 0)
        self.listPretrainBox = QComboBox(self)
        self.listPretrain = listPretrain
        for i, (v, note) in enumerate(zip(listPretrain, listnote)):
            self.listPretrainBox.addItem( '{} (note: {})'.format(v, note))
        grid.addWidget(self.listPretrainBox,1, 0)

        self.charlistLabel = QLabel('Charlist file')
        grid.addWidget(self.charlistLabel, 2, 0)
        self.charlistsBox = QComboBox(self)
        self.charlists = charlists
        for i, v in enumerate(charlists):
            self.charlistsBox.addItem( '{}'.format(v))
        grid.addWidget(self.charlistsBox,3, 0)

        self.numEpochLabel = QLabel('Number Epochs trainning')
        grid.addWidget(self.numEpochLabel, 4, 0)
        self.numEpochEdit = QLineEdit()
        self.numEpochEdit.setPlaceholderText('number epoch')
        self.numEpochEdit.setText('{}'.format(numEpoch))
        self.numEpochEdit.setValidator(QIntValidator())
        grid.addWidget(self.numEpochEdit, 5, 0)

        self.prefixNameLabel = QLabel('Model tag insert to folder checkpoint name')
        grid.addWidget(self.prefixNameLabel, 6, 0)
        self.prefixNameEdit = QLineEdit()
        self.prefixNameEdit.setPlaceholderText('model_tag')
        self.prefixNameEdit.setText('{}'.format('model_tag'))
        # self.numEpochEdit.setValidator(QIntValidator())
        grid.addWidget(self.prefixNameEdit, 7, 0)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Train')

        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.acceptTraining)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)


    def acceptTraining(self):
        for i, v in enumerate(self.listDataBox):
            if v.checkState():
                self.choose.append(v.text())
        self.accept()

    def get_synDir_chose(self):
        return (self.choose, self.listPretrain[self.listPretrainBox.currentIndex()], int(self.numEpochEdit.text()), str(self.prefixNameEdit.text()), self.charlists[self.charlistsBox.currentIndex()])  if self.exec_() else (None, None, None, None, None)

class choose_checkpoint(QDialog):

    def __init__(self, parent=None, listcheck=None, curCpt=None):
        super(choose_checkpoint, self).__init__()
        self.setWindowTitle('Choose checkpoint product use')

        self.listCheckBox = listcheck
        self.curCpt = curCpt
        grid = QGridLayout()
        self.choose = None
        self.ButtonGroup = QButtonGroup()
        for i, c in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QRadioButton(c)
            if c == self.curCpt:
                self.listCheckBox[i].setStyleSheet("font-weight:bold;")
            self.ButtonGroup.addButton(self.listCheckBox[i])
            grid.addWidget(self.listCheckBox[i], i, 0)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Choose')

        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.acceptCheckpoint)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)
        self.resize(self.sizeHint())

        self.setLayout(grid)


    def acceptCheckpoint(self):
        v = self.ButtonGroup.checkedButton()
        if v != 0:
            self.choose = v.text()
            print(self.choose)
            self.accept()
        else:
            print("must choose")


    def get_chose(self):
        return self.choose if self.exec_() else None

# class download_checkpoint(QDialog):
#
#     def __init__(self, parent=None, listcheck=None):
#         super(download_checkpoint, self).__init__(parent)
#         self.setWindowTitle('choose checkpoint want download')
#
#         self.listCheckBox = list(listcheck)
#         grid = QGridLayout()
#         self.choose = None
#         self.ButtonGroup = QButtonGroup()
#         for i, c in enumerate(self.listCheckBox):
#             self.listCheckBox[i] = QRadioButton(str(c))
#             self.ButtonGroup.addButton(self.listCheckBox[i])
#             grid.addWidget(self.listCheckBox[i], i, 0)
#
#         self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
#         bb.button(BB.Ok).setIcon(newIcon('done'))
#         bb.button(BB.Ok).setText('Choose')
#
#         bb.button(BB.Cancel).setIcon(newIcon('undo'))
#         bb.accepted.connect(self.acceptCheckpoint)
#         bb.rejected.connect(self.reject)
#         grid.addWidget(bb)
#         self.resize(self.sizeHint())
#
#         self.setLayout(grid)
#
#
#     def acceptCheckpoint(self):
#         v = self.ButtonGroup.checkedButton()
#         if v != 0:
#             self.choose = v.text()
#             print(self.choose)
#             self.accept()
#         else:
#             print("must choose")
#
#
#     def get_chose(self):
#         return self.choose if self.exec_() else None

class waitDialog(QProgressDialog):
    def __init__(self,title = 'Waitting', txtt = 'Wait untill done', num=0, parent=None, ):
        super(waitDialog, self).__init__()
        self.setWindowTitle(title)
        self.setLabelText(txtt)
        self.setSizeGripEnabled(False)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setModal(True)
        self.setAutoClose(False)
        #
        # self.btn = QPushButton('Ok')
        self.setCancelButton(None)
        # self.btn.hide()
        self.show()

        self.num = num
        self.mess = None # "Data Loaded"
        # QtTest.QTest.qWait(100)
        self.setRange(0, self.num)
        self.setMinimumDuration(0)
        self.setValue(self.num)

        self.delay(100)

    def done_close(self):
        print('close')
        if self.mess is not None:
            QMessageBox.information(self, "Message", self.mess)
        self.cancel()

    # can not cancel, wait until
    def closeEvent(self, event):
        print('can not cancel, wait until')
        event.ignore()

    def delay(self, s = 600):
        QtTest.QTest.qWait(s)


class uploadDialog(QDialog):

    def __init__(self, parent=None,  name='', exists_folders =  {'aa':['a.txt'], 'ccc':['c.txt'], 'dd':['b.txt'], 'ee':['b.txt']}):
        super(uploadDialog, self).__init__()
        title = 'Uploading'
        self.setWindowTitle(title)
        grid = QGridLayout()

        self.exists_folders_label = QLabel('You can upload to exists folders in server')
        grid.addWidget(self.exists_folders_label)

        self.parent = parent
        self.data_folders = exists_folders
        self.name_folders = list(exists_folders.keys())

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.fileListWidget = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        grid.addWidget(self.scrollArea)

        self.nameLabel = QLabel('Folder name to upload')

        self.nameEdit = QLineEdit()
        self.nameEdit.setPlaceholderText('folder name to upload')
        self.nameEdit.setText('{}'.format(name))
        self.nameEdit.textChanged.connect(self.checkChange)
        self.folderList = []
        for i, fname in enumerate(self.name_folders):
            myQCustomQWidget = QCustomQWidget_3(folder_icon_path, text=fname, nameLabel=self.nameEdit, parent=self)
            self.fileListWidget.addWidget(myQCustomQWidget, i//3, i%3)
            self.folderList.append(myQCustomQWidget)

        grid.addWidget(self.nameLabel)
        grid.addWidget(self.nameEdit)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.accepted.connect(self.confirm)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)

    def selectedList(self, widget):
        for x in self.folderList:
            x.deselect()
        widget.select()

    def get_name(self):
        return self.nameEdit.text() if self.exec_() else None

    def checkChange(self):
        if self.nameEdit.text() not in self.name_folders:
            self.nameLabel.setStyleSheet("background-image: url(black.gif); color: rgb(255, 255, 255)")
            self.nameLabel.setText('Folder name')
        else:
            self.nameLabel.setStyleSheet("background-image: url(black.gif); color: rgb(255, 0, 0)")
            self.nameLabel.setText('{} already exist in server. Insert to this folder'.format(self.nameEdit.text()))

    def confirm(self):
        no, ok = QMessageBox.No, QMessageBox.Ok,

        if self.nameEdit.text() == '':
            msg = 'You choice not valid'
            QMessageBox.information(self, "Message", msg)
            return
        if self.nameEdit.text() in self.name_folders:
            gts = [f for f in os.listdir(self.parent.defaultSaveDir) if f[-3:]=='txt']
            for gt in gts:
                if gt in self.data_folders[self.nameEdit.text()]:
                        msg = 'some file already exists, replace it?'
                        res = QMessageBox.warning(self, u'Attention', msg, no|ok , no)
                        if res == ok:
                            self.accept()
                            self.parent.upLoad(self.nameEdit.text())
                        return
            else:
                self.accept()
                self.parent.upLoad(self.nameEdit.text())
        else:
            self.accept()
            self.parent.upLoad(self.nameEdit.text())

    def insideFolder(self, folderName):
        sub = insideFolderDialog(parent=self, name=folderName, listFiles=self.data_folders[folderName])
        sub.setWindowModality(Qt.ApplicationModal)
        sub.exec_()
        return

class upChalistDialog(QDialog):

    def __init__(self, parent=None,  charlists = ['aa.txt', 'ccc.txt', 'dd.txt', 'ee.txt']):
        super(upChalistDialog, self).__init__()
        title = 'Upload Charlist File'
        self.setWindowTitle(title)
        grid = QGridLayout()

        self.exists_charlists_label = QLabel('You can upload to exists folders in server')
        grid.addWidget(self.exists_charlists_label)

        self.exists_charlists = charlists

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.fileListWidget = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        grid.addWidget(self.scrollArea)

        # self.nameEdit.textChanged.connect(self.checkChange)

        for i, fname in enumerate(self.exists_charlists):
            myQCustomQWidget = QCustomQWidget_2(txt_icon_path, fname)
            self.fileListWidget.addWidget(myQCustomQWidget, i//3, i%3)

        self.note = QLabel('')
        self.note.hide()
        grid.addWidget(self.note)

        self.charlistLayout = QHBoxLayout()

        self.charlist_file =  None
        self.charlistBtn = QPushButton('Charlist File')
        self.charlistBtn.clicked.connect(self.getFileDialog)
        self.charlistLayout.addWidget(self.charlistBtn)

        self.fileLabel = QLabel('{}'.format(self.charlist_file))
        # self.fileLabel.textChanged.connect(self.checkChange)
        self.charlistLayout.addWidget(self.fileLabel)
        grid.addItem(self.charlistLayout)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)


    def getFileDialog(self):
        targetFile = QFileDialog.getOpenFileName(None, 'Open charlist file',
                                            'c:\\', "text files (*.txt)")
        targetFile =targetFile[0]

        if targetFile is not None and len(targetFile) > 1:
            self.charlist_file = targetFile
            self.fileLabel.setText('{}'.format(self.charlist_file))
            self.checkChange()
        return

    def get_path(self):
        return self.charlist_file if self.exec_() else None

    def checkChange(self):
        basename = os.path.basename(self.charlist_file)
        if basename not in self.exists_charlists:
            self.note.hide()
        else:
            self.note.show()
            self.note.setStyleSheet("background-image: url(black.gif); color: rgb(255, 0, 0)")
            self.note.setText('{} already exist in server. Replace it?'.format(basename))


class folderServerDialog(QDialog):

    def __init__(self, parent=None, data_folders = ['aa', 'ccc', 'dd', 'ee']*10):
        super(folderServerDialog, self).__init__()
        title = 'Get folder data from server'
        self.setWindowTitle(title)
        grid = QGridLayout()
        self.parent = parent
        self.exists_folders_label = QLabel('Exists data in server')
        grid.addWidget(self.exists_folders_label)


        self.data_folders = data_folders
        # self.fileListWidget = QGridLayout()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.fileListWidget = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        grid.addWidget(self.scrollArea)

        self.foldername = ''
        self.Label1 = QLabel('Your choose:')
        self.nameLabel = QLabel('{}'.format(self.foldername))
        self.nameLabelLayout = QHBoxLayout()
        self.nameLabelLayout.addWidget(self.Label1)
        self.nameLabelLayout.addWidget(self.nameLabel)

        self.folderList = []
        for i, fname in enumerate(self.data_folders):
            myQCustomQWidget = QCustomQWidget_3(folder_icon_path, text=fname, nameLabel=self.nameLabel, parent=self)
            self.fileListWidget.addWidget(myQCustomQWidget, i//3, i%3)
            self.folderList.append(myQCustomQWidget)

        self.note = QLabel('')
        self.note.hide()
        grid.addWidget(self.note)

        grid.addItem(self.nameLabelLayout)

        self.saveDirLayout = QHBoxLayout()

        self.saveDir =  os.getcwd()
        self.saveDirBtn = QPushButton('Save dir')
        self.saveDirBtn.clicked.connect(self.saveFileDialog)
        self.saveDirLayout.addWidget(self.saveDirBtn)

        self.SaveLabel = QLabel('Save dir: {}'.format(self.saveDir))
        self.saveDirLayout.addWidget(self.SaveLabel)
        grid.addItem(self.saveDirLayout)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.accepted.connect(self.accept_check)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)

    def accept_check(self):
        path = os.path.join(self.saveDir,self.nameLabel.text())
        if self.nameLabel.text() == '' or not (self.nameLabel.text() in self.data_folders):
            QMessageBox.information(self, "Message", 'You choice not valid')
        elif os.path.exists(path):
            QMessageBox.information(self, "Message", '{} already exist in saver dir'.format(self.nameLabel.text()))
        else:
            self.accept()

    def selectedList(self, widget):
        for x in self.folderList:
            x.deselect()
        widget.select()

    def saveFileDialog(self):
        targetDirPath = QFileDialog.getExistingDirectory(self, 'Save Directory', self.saveDir,
                                                         QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if targetDirPath is not None and len(targetDirPath) > 1:
            self.saveDir = targetDirPath
            self.SaveLabel.setText('Save dir: {}'.format(self.saveDir))
        return

    def get_name(self):
        return (self.nameLabel.text(), self.saveDir) if self.exec_() else (None,None)

class insideFolderDialog(QDialog):

    def __init__(self, parent=None, name=None, listFiles =['a.txt','a.txt','a.txt','a.txt']):
        super(insideFolderDialog, self).__init__()
        title = name
        self.setWindowTitle(title)
        grid = QGridLayout()

        self.exists_folders_label = QLabel('Exists file')
        grid.addWidget(self.exists_folders_label)
        self.setWindowModality(Qt.ApplicationModal)
        self.parent = parent
        self.listFiles = listFiles
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.fileListWidget = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        grid.addWidget(self.scrollArea)

        self.folderList = []
        for i, fname in enumerate(self.listFiles):
            myQCustomQWidget = QCustomQWidget_2(txt_icon_path, text=fname)
            self.fileListWidget.addWidget(myQCustomQWidget, i//5, i%5)
            self.folderList.append(myQCustomQWidget)

        self.buttonBox = BB(BB.Ok, Qt.Horizontal, self)

        self.buttonBox.button(BB.Ok).clicked.connect(self.accept)
        grid.addWidget(self.buttonBox)

        self.setLayout(grid)
        self.resize(self.sizeHint())
        self.show()

class viewServerDataDialog(QDialog):

    def __init__(self, parent=None, data_folders = {'aa':['a.txt'], 'ccc':['c.txt'], 'dd':['b.txt'], 'ee':['b.txt']}):
        super(viewServerDataDialog, self).__init__()
        title = 'List folder data from server'
        self.setWindowTitle(title)
        grid = QGridLayout()

        self.exists_folders_label = QLabel('Exists data in server')
        grid.addWidget(self.exists_folders_label)

        self.parent = parent
        self.data_folders = data_folders
        self.name_folders = list(data_folders.keys())
        # self.fileListWidget = QGridLayout()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.fileListWidget = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        grid.addWidget(self.scrollArea)

        self.foldername = ''
        self.Label1 = QLabel('Your choose:')
        self.Label1.hide()

        self.nameLabel = QLabel('{}'.format(self.foldername))
        self.nameLabel.hide()

        self.nameLabelLayout = QHBoxLayout()
        self.nameLabelLayout.addWidget(self.Label1)
        self.nameLabelLayout.addWidget(self.nameLabel)

        self.folderList = []
        for i, fname in enumerate(self.name_folders):
            myQCustomQWidget = QCustomQWidget_3(folder_icon_path, text=fname, nameLabel=self.nameLabel, parent=self)
            self.fileListWidget.addWidget(myQCustomQWidget, i//3, i%3)
            self.folderList.append(myQCustomQWidget)

        self.note = QLabel('')
        self.note.hide()
        grid.addWidget(self.note)

        grid.addItem(self.nameLabelLayout)

        self.saveDirLayout = QHBoxLayout()

        self.saveDir =  os.getcwd()

        self.buttonBox = bb = BB(BB.Save | BB.No | BB.Cancel, Qt.Horizontal, self)

        self.buttonBox.button(BB.Save).clicked.connect(self.download)
        self.buttonBox.button(BB.No).clicked.connect(self.delFolder)
        self.buttonBox.button(BB.Cancel).clicked.connect(self.reject)


        self.buttonBox.button(BB.No).setIcon(newIcon('del'))
        self.buttonBox.button(BB.No).setText('Del')

        # bb.Save.connect(self.accept_check)
        grid.addWidget(bb)

        w_size = int(QFontMetrics(QFont()).width(title) * 1.6)

        self.setMinimumWidth(w_size)
        self.setLayout(grid)
        self.show()

    def delFolder(self):

        if self.nameLabel.text() == '' or not (self.nameLabel.text() in self.name_folders):
            msg = 'You choice not valid'
            QMessageBox.information(self, "Message", msg)
            return

        self.accept()
        self.parent.delServerFolder(self.nameLabel.text())
        return

    def download(self):
        no, ok = QMessageBox.No, QMessageBox.Ok,

        if self.nameLabel.text() == '' or not (self.nameLabel.text() in self.name_folders):
            msg = 'You choice not valid'
            QMessageBox.information(self, "Message", msg)
            return

        while True:
            targetDirPath = QFileDialog.getExistingDirectory(self, 'Save Directory', self.saveDir,
                                                             QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if targetDirPath is not None and len(targetDirPath) > 1:
                self.saveDir = targetDirPath

                path = os.path.join(self.saveDir,self.nameLabel.text())

                if os.path.exists(path):
                    msg = '{} already exist in saver dir, choose another?'.format(self.nameLabel.text())
                    res = QMessageBox.information(self, "Message", msg,  no | ok, no)
                    if res == no:
                        return
                else:
                    self.accept()
                    self.parent.downServerFolder(self.nameLabel.text(), self.saveDir)
                    return
            else:
                return


    def selectedList(self, widget):
        for x in self.folderList:
            x.deselect()
        widget.select()

    def insideFolder(self, folderName):
        sub = insideFolderDialog(parent=self, name=folderName, listFiles=self.data_folders[folderName])
        sub.setWindowModality(Qt.ApplicationModal)
        sub.exec_()
        return

    def get_name(self):
        return (self.nameLabel.text(), self.saveDir) if self.exec_() else (None,None)


class TrainStatus(QDialog):
    def __init__(self, checkpointDf=None, parent=None, training_log=None):
        super(TrainStatus, self).__init__()
        title = 'Train Status'
        self.setWindowTitle(title)

        self.isStop = False
        self.parent = parent

        self.checkpointDf = checkpointDf
        self.tableWidget = QTableWidget()
        self.setData()
        self.tableWidget.resize(self.tableWidget.sizeHint())
        self.tableWidget.doubleClicked.connect(self.on_click)

        self.training_log = training_log
        if self.training_log is not None:
            self.tableWidget_log = QTableWidget()
            self.setData_log()
            self.tableWidget_log.resize(self.tableWidget_log.sizeHint())
            self.tableWidget_log.doubleClicked.connect(self.on_click_log)


        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.button(BB.Cancel).setIcon(newIcon('cancel'))
        bb.button(BB.Cancel).hide()

        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Ok')

        bb.accepted.connect(self.continueBtn)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QGridLayout()

        self.Label1 = QLabel('Finished models')
        self.Label1.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.Label1)
        self.layout.addWidget(self.tableWidget)

        if self.training_log is not None:
            self.Label2 = QLabel('Traning Status')
            self.Label2.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.Label2)
            self.layout.addWidget(self.tableWidget_log)

        self.setLayout(self.layout)
        self.layout.addWidget(bb, 1, 0)


    def stopbtn(self):
        # stop trainning ?
        self.isStop = True
        self.accept()
        return

    def continueBtn(self):
        # stop trainning ?
        self.isStop = False
        self.accept()
        return

    @pyqtSlot()
    def on_click(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            row = currentQTableWidgetItem.row()
            cpt_name = self.checkpointDf['name'][row]
            status = list(self.checkpointDf['status'])[row]
            print('on_click', row, cpt_name, status)
            if status == 'finish':
                self.parent.train_history(cpt_name=cpt_name)
            else:
                print('status error:',status, cpt_name)
                self.parent.train_history(cpt_name=cpt_name)

    @pyqtSlot()
    def on_click_log(self):
        for currentQTableWidgetItem in self.tableWidget_log.selectedItems():
            row = currentQTableWidgetItem.row()
            print('on_click_log', row)
            istop = self.parent.current_trainning_log()
            if istop:
                self.accept()

    def setData(self):
        # Create table
        status_key = 'status'
        status_collum = pd.DataFrame({status_key: ['finish']*self.checkpointDf.shape[0]})
        self.checkpointDf = self.checkpointDf.reset_index(drop=True)
        status_collum = status_collum.reset_index(drop=True)
        self.checkpointDf = self.checkpointDf.join(status_collum)

        ignoreKeys = 'fullPath'
        row_num = self.checkpointDf.shape[0]
        col_num = self.checkpointDf.shape[1] - 1 if ignoreKeys in list(self.checkpointDf.keys()) else self.checkpointDf.shape[1]
        self.tableWidget.setRowCount(row_num)

        self.tableWidget.setColumnCount(col_num)

        horHeaders = []
        colIndex = 0
        for n, key in enumerate(self.checkpointDf.keys()):
            if key == ignoreKeys:
                continue
            horHeaders.append(key)
            for m, item in enumerate(self.checkpointDf[key]):
                newitem = QTableWidgetItem(str(item))
                self.tableWidget.setItem(m, colIndex, newitem)
                if key != 'note':
                    newitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            colIndex +=1

        self.tableWidget.setHorizontalHeaderLabels(horHeaders)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def setData_log(self):
        ignoreKeys = 'fullPath'
        self.training_log['status'] = 'training'
        self.tableWidget_log.setRowCount(1)
        self.tableWidget_log.setColumnCount(len(self.training_log))

        horHeaders = []
        colIndex = 0
        for n, key in enumerate(self.training_log.keys()):
            if key == ignoreKeys:
                continue
            horHeaders.append(key)
            newitem = QTableWidgetItem(str(self.training_log[key]))
            self.tableWidget_log.setItem(0, colIndex, newitem)
            colIndex +=1

        self.tableWidget_log.setHorizontalHeaderLabels(horHeaders)

        self.tableWidget_log.verticalHeader().setVisible(False)
        self.tableWidget_log.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget_log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def get_note(self):
        return self.ret_note() if self.exec() else None

    def ret_note(self):
        notes = []
        headercount = self.tableWidget.columnCount()
        for row in range(0, self.tableWidget.rowCount(), 1):
            for collum in range(0, headercount, 1):
                headertext = self.tableWidget.horizontalHeaderItem(collum).text()
                if 'note' == headertext:
                    cell = self.tableWidget.item(row, collum).text()  # get cell at row, col
                    notes.append(cell)
        if all(notes[:self.checkpointDf.shape[0]] == self.checkpointDf['note']):
            return None
        else:
            return notes

    def genData(self):

        df = pd.DataFrame(columns=('name', 'loss', 'time', 'best'))
        df = df.append([{'name': 'None', 'time': 'nadfffffffff', 'loss': 'nfffffffffffffffffffffffffffffffffffffffffffff', 'best': 'None'}])
        df = df.append([{'name': 'None', 'time': 'None', 'loss': 'None', 'best': 'None'}])
        df = df.append([{'name': 'None', 'time': 'None', 'loss': 'None', 'best': 'None'}])
        df = df.append([{'name': 100, 'time': '22.19', 'loss': 0.9, 'best': '0'}])
        return df

class trainning_history_dialog(QDialog):
    def __init__(self, checkpointDf=None, parent=None):
        super(trainning_history_dialog, self).__init__()

        self.isStop = False
        self.checkpointDf = checkpointDf
        self.tableWidget = QTableWidget()
        self.setData()
        self.tableWidget.resize(self.tableWidget.sizeHint())

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.button(BB.Cancel).setIcon(newIcon('cancel'))
        bb.button(BB.Cancel).hide()

        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Ok')

        bb.accepted.connect(self.continueBtn)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QGridLayout()

        self.Label1 = QLabel('History Train')
        self.Label1.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.Label1)

        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.layout.addWidget(bb, 1, 0)


    def stopbtn(self):
        # stop trainning ?
        self.isStop = True
        self.accept()
        return

    def continueBtn(self):
        # stop trainning ?
        self.isStop = False
        self.accept()
        return

    def setData(self):
        # Create table
        ignoreKeys = 'fullPath'
        row_num = self.checkpointDf.shape[0]
        col_num = self.checkpointDf.shape[1] - 1 if ignoreKeys in list(self.checkpointDf.keys()) else self.checkpointDf.shape[1]
        self.tableWidget.setRowCount(row_num)

        self.tableWidget.setColumnCount(col_num)

        horHeaders = []
        colIndex = 0
        for n, key in enumerate(self.checkpointDf.keys()):
            if key == ignoreKeys:
                continue
            horHeaders.append(key)
            for m, item in enumerate(self.checkpointDf[key]):
                newitem = QTableWidgetItem(str(item))
                # newitem.setEdit
                # item.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(m, colIndex, newitem)
                if key != 'note':
                    newitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            colIndex +=1

        self.tableWidget.setHorizontalHeaderLabels(horHeaders)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def get_note(self):
        return self.ret_note() if self.exec() else None

    def ret_note(self):
        notes = []
        headercount = self.tableWidget.columnCount()
        for row in range(0, self.tableWidget.rowCount(), 1):
            for collum in range(0, headercount, 1):
                headertext = self.tableWidget.horizontalHeaderItem(collum).text()
                if 'note' == headertext:
                    cell = self.tableWidget.item(row, collum).text()  # get cell at row, col
                    notes.append(cell)
        if all(notes[:self.checkpointDf.shape[0]] == self.checkpointDf['note']):
            return None
        else:
            return notes


class trainning_log_dialog(QDialog):
    def __init__(self, checkpointDf=None, parent=None, training_log=None):
        super(trainning_log_dialog, self).__init__()

        self.isStop = False

        self.checkpointDf = checkpointDf
        if self.checkpointDf.shape[0] > 0:
            self.tableWidget = QTableWidget()
            self.setData()
            self.tableWidget.resize(self.tableWidget.sizeHint())

        self.training_log = training_log
        if self.training_log is not None:
            self.tableWidget_log = QTableWidget()
            self.setData_log()
            self.tableWidget_log.resize(self.tableWidget_log.sizeHint())

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)

        bb.button(BB.Cancel).setIcon(newIcon('cancel'))
        bb.button(BB.Cancel).setText('Stop Train')

        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Ok')

        bb.accepted.connect(self.continueBtn)
        bb.rejected.connect(self.stopbtn)

        bb.button(BB.Cancel).show()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QGridLayout()
        if self.checkpointDf.shape[0] > 0:
            self.Label1 = QLabel('training history')
            self.Label1.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.Label1)
            self.layout.addWidget(self.tableWidget)
        if self.training_log is not None:
            self.Label2 = QLabel('training status')
            self.Label2.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.Label2)
            self.layout.addWidget(self.tableWidget_log)
        self.layout.addWidget(bb)
        self.setLayout(self.layout)

    def stopbtn(self):
        # stop trainning ?????????????????
        self.isStop = True
        self.accept()
        return

    def continueBtn(self):
        # stop trainning ?????????????????
        self.isStop = False
        self.accept()
        return


    def setData(self):
        # Create table
        ignoreKeys = 'fullPath'
        self.tableWidget.setRowCount(self.checkpointDf.shape[0])

        self.tableWidget.setColumnCount(self.checkpointDf.shape[1] - 1 if ignoreKeys in list(self.checkpointDf.keys()) else self.checkpointDf.shape[1])

        horHeaders = []
        colIndex = 0
        for n, key in enumerate(self.checkpointDf.keys()):
            if key == ignoreKeys:
                continue
            horHeaders.append(key)
            for m, item in enumerate(self.checkpointDf[key]):
                newitem = QTableWidgetItem(str(item))
                # newitem.setEdit
                # item.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(m, colIndex, newitem)
                if key != 'note':
                    newitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            colIndex +=1

        self.tableWidget.setHorizontalHeaderLabels(horHeaders)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def setData_log(self):
        # Create table
        ignoreKeys = 'fullPath'
        self.tableWidget_log.setRowCount(1)

        self.tableWidget_log.setColumnCount(len(self.training_log))

        horHeaders = []
        colIndex = 0
        for n, key in enumerate(self.training_log.keys()):
            if key == ignoreKeys:
                continue
            horHeaders.append(key)
            newitem = QTableWidgetItem(str(self.training_log[key]))
            self.tableWidget_log.setItem(0, colIndex, newitem)
            colIndex +=1

        self.tableWidget_log.setHorizontalHeaderLabels(horHeaders)

        self.tableWidget_log.verticalHeader().setVisible(False)
        self.tableWidget_log.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget_log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def chose_stop(self):
        return self.isStop if self.exec() else None


