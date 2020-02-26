try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5 import QtTest

except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.utils import newIcon, labelValidator

BB = QDialogButtonBox


class LabelDialog(QDialog):

    def __init__(self, text="Enter object label", parent=None, label=None, subLabels=None):
        super(LabelDialog, self).__init__(parent)

        self.count = 0
        self.layout = QGridLayout()

        self.layout_label = QGridLayout()
        self.listLabel = []

        self.addLabel(txt=label, opt=False)
        if subLabels is not None:
            for lb in subLabels:
                self.addLabel(lb)

        self.addBtn = QPushButton('add')
        self.addBtn.clicked.connect( lambda x: self.addLabel(txt=None, listHint=[], opt=True))

        self.saveCheckBox = QCheckBox('save format')
        self.saveCheckBox.setChecked(False)

        checkAddLayout = QVBoxLayout()
        checkAddLayout.addWidget(self.saveCheckBox)
        checkAddLayout.addWidget(self.addBtn)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)



        self.layout.addLayout(self.layout_label, 0,0)
        self.layout.addLayout(checkAddLayout, 0, 1)

        # self.layout.addWidget(self.addBtn, 1, 1)
        self.layout.addWidget(bb, 2, 0)
        self.setLayout(self.layout)
        # self.show()

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
        edit.setMinimumWidth(100)
        singleLB.addWidget(edit, 0, 0)

        if opt:
            btn = QPushButton('remove')
            btn.clicked.connect(lambda i: self.removeLabel(singleLB))
            singleLB.addWidget(btn, 0, 1)

        self.listLabel.append(singleLB)
        self.layout_label.addLayout(singleLB,len(self.listLabel) - 1, 0)


    def validate(self):
        # retList = self.getLabels()
        # print('retList:', retList)
        # self.accept()
        # self.close()
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
        # if move:
        #     self.move(QCursor.pos())
        return ([l.itemAt(0).widget().text() for l in self.listLabel], self.saveCheckBox.checkState()) if self.exec() else (None, None)

class trainDialog(QDialog):

    def __init__(self, parent=None, listcheck=None):
        super(trainDialog, self).__init__(parent)
        self.setWindowTitle('choose data to start training')

        self.listCheckBox = listcheck
        grid = QGridLayout()
        self.choose = []

        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            grid.addWidget(self.listCheckBox[i], i, 0)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Train')

        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.acceptTraining)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

        self.setLayout(grid)

    def acceptTraining(self):
        for i, v in enumerate(self.listCheckBox):
            if v.checkState():
                self.choose.append(v.text())
        self.accept()

    def get_synDir_chose(self):
        return self.choose if self.exec_() else None

class choose_checkpoint(QDialog):

    def __init__(self, parent=None, listcheck=None):
        super(choose_checkpoint, self).__init__(parent)
        self.setWindowTitle('choose checkpoint will use')

        self.listCheckBox = listcheck
        grid = QGridLayout()
        self.choose = None
        self.ButtonGroup = QButtonGroup()
        for i, c in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QRadioButton(c)
            self.ButtonGroup.addButton(self.listCheckBox[i])
            grid.addWidget(self.listCheckBox[i], i, 0)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Ok).setText('Choose')

        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.acceptCheckpoint)
        bb.rejected.connect(self.reject)
        grid.addWidget(bb)

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

# wait for down or upload
class waitDialog(QProgressDialog):
    def __init__(self, txtt = 'wait untill done', num=0, parent=None):
        super(waitDialog, self).__init__(parent)
        self.setWindowTitle('wait')
        self.setLabelText(txtt)
        self.setSizeGripEnabled(False)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setModal(True)
        self.setCancelButton(None)
        self.show()
        self.num = num
        QtTest.QTest.qWait(100)
        self.setRange(0, num)
        self.setMinimumDuration(0)
        self.setValue(0)

    def done_close(self):
        print('close')
        self.cancel()
        # self.close()

    # can not cancel, wait until
    def closeEvent(self, event):
        print('can not close')
        event.ignore()

    def delay(self, s = 600):
        QtTest.QTest.qWait(s)

