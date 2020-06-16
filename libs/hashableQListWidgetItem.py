#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    # needed for py3+qt4
    # Ref:
    # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
    # http://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

# PyQt5: TypeError: unhashable type: 'QListWidgetItem'


class HashableQTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, *args):
        super(HashableQTreeWidgetItem, self).__init__(*args)
        self.setCheckState(0, Qt.Checked)
        self.setFlags(self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)


    def __hash__(self):
        # return hash(id(self))
        # print(id(self))
        return hash(id(self))

class HashableQListWidgetItem(QListWidgetItem):

    def __init__(self, *args):
        super(HashableQListWidgetItem, self).__init__(*args)

    def __hash__(self):
        # return hash(id(self))
        print(id(self))
        return hash(id(self))
