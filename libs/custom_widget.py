#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    if sys.version_info.major >= 3:
        import sip

        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *


class QCustomQWidget(QWidget):
    def __init__(self, imagePath, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        self.imagePath = imagePath
        self.textQVBoxLayout = QVBoxLayout()
        self.textUpQLabel = QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.allQHBoxLayout = QHBoxLayout()
        self.iconQLabel = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        self.textUpQLabel.setStyleSheet('''
            color: rgb(255, 255, 255);
        ''')
        # pxmap = QPixmap(imagePath)
        self.iconQLabel.setPixmap(QPixmap(imagePath).scaledToWidth(64))
        # self.iconQLabel.setMaximumWidth(50)
        # self.iconQLabel.setMaximumHeight(50)
        self.textUpQLabel.setText(os.path.basename(imagePath))

    def getPath(self):
        return self.imagePath
