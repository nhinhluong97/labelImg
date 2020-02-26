try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
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
        self.listBtn = []

        self.addLabel(txt=label)

        for lb in subLabels:
            self.addLabel(lb)

        self.addBtn = QPushButton('add')
        self.addBtn.clicked.connect( lambda x: self.addLabel(txt=None, listHint=[]))

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)

        self.layout.addLayout(self.layout_label, 0,0)
        self.layout.addLayout(self.layout_label, 0,0)
        self.layout.addWidget(self.addBtn, 1, 2)
        self.layout.addWidget(bb, 2, 2)
        self.setLayout(self.layout)
        self.show()

    def updateLayout(self):
        # for idx, lb in enumerate(self.listLabel):

        return

    def removeLabel(self, singleLB):
        self.listLabel.remove(singleLB)
        for i in reversed(range(singleLB.count())):
            singleLB.itemAt(i).widget().deleteLater()
        self.layout_label.removeItem(singleLB)
        print(len(self.listLabel))
        # self.layout_label.removeWidget(singleLB)
        return

    def addLabel(self, txt = None, listHint=[]):
        self.count += 1
        # singleLB = QGridLayout()
        edit = QLineEdit()
        if txt is None:
            edit.setPlaceholderText('edit label here {}'.format(self.count))
        else:
            edit.setText(txt)

        edit.setValidator(labelValidator())

        model = QStringListModel()
        model.setStringList(listHint)
        completer = QCompleter()
        completer.setModel(model)
        edit.setCompleter(completer)
        edit.setMinimumWidth(100)

        btn = QPushButton('remove')
        btn.clicked.connect(lambda i: self.removeLabel(self.count))
        self.listLabel.append(edit)
        self.listBtn.append(btn)

        # self.layout_label.addLayout(singleLB,len(self.listLabel) - 1, 0)



    def addtextToList(self, texts=[], textsNote=[]):
        # self.listWidget.insertItems(0, texts)
        for txt in texts:
            self.listWidget.insertItem(0,txt)

        for txt in textsNote:
            self.listWidget3.insertItem(0,txt)


    def validate(self):
        # retList = self.getLabels()
        # print('retList:', retList)
        self.accept()
        # self.close()
        # try:
        #     if self.edit.text().trimmed():
        #         self.accept()
        # except AttributeError:
        #     # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
        #     if self.edit.text().strip():
        #         self.accept()
        return

    def postProcess(self):
        try:
            self.edit.setText(self.edit.text().trimmed())
        except AttributeError:
            # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
            self.edit.setText(self.edit.text())

    # def getLabels(self):
    #     retList = []
    #     for layoutt in  self.listLabel:
    #         items = (layoutt.itemAt(i) for i in range(layoutt.count()))
    #         for w in items:
    #             w = w.widget()
    #             # print(type(w))
    #             # print(w.objectName())
    #             if isinstance(w, QLineEdit):
    #                 print('txt:', w.text())
    #                 retList.append(w)
    #     # print("curr:", retList)
    #     return retList

    def popUp(self, list_text=None, move=True):
        assert len(list_text)==len(self.listLabel) or list_text is None, 'len(list_text) must same len(self.listLabel)'
        if list_text is not None:
            for txt, layout in zip(list_text, self.listLabel):
                layout.itemAt(0).widget().setText(txt)

        return [l.itemAt(0).widget().text() for l in self.listLabel ] if self.exec() else None

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

# wait for down or upload
class waitDialog(QProgressDialog):
    def __init__(self, txtt = 'wait untill done', num=10, parent=None):
        super(waitDialog, self).__init__(parent)
        self.setWindowTitle('wait')
        self.setLabelText(txtt)
        self.setSizeGripEnabled(False)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setModal(True)
        self.setCancelButton(None)
        self.show()

        from PyQt5 import QtTest
        QtTest.QTest.qWait(100)

        self.setRange(0, num)
        self.setMinimumDuration(0)
        self.setValue(0)

    def done_close(self):
        self.close()

    # can not cancel, wait until
    def closeEvent(self, event):
        print('can not close')
        event.ignore()

