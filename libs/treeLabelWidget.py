
from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
import sys

class TreeLabel(QTreeWidget):

    def __init__(self, parent=None, listcheck=None):
        super(TreeLabel, self).__init__(parent)

    def addParent(self, label = '', subLabel=[]):
        parent = QTreeWidgetItem(self)
        parent.setText(0, label)
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for s in subLabel:
            child = QTreeWidgetItem(parent)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, s)
            child.setCheckState(0, Qt.Unchecked)