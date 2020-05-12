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


class QCustomQWidget_2(QWidget):
    def __init__(self, imagePath, parent=None, text=None):
        super(QCustomQWidget_2, self).__init__(parent)
        self.imagePath = imagePath
        self.text = text
        self.textQVBoxLayout = QVBoxLayout()
        self.textUpQLabel = QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.allQHBoxLayout = QHBoxLayout()
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

    def getText(self):
        return self.text

    # def mousePressEvent(self, event):
    #     print("clicked")



class QCustomQWidget_3(QWidget):
    def __init__(self, imagePath, parent=None, text=None, nameLabel=None ):
        super(QCustomQWidget_3, self).__init__(parent)
        self.imagePath = imagePath
        self.text = text
        self.textUpQLabel = QLabel()
        self.textUpQLabel.setAlignment(Qt.AlignCenter)
        self.allQHBoxLayout = QVBoxLayout()
        self.iconQLabel = QLabel()
        self.iconQLabel.setAlignment(Qt.AlignCenter)
        self.allQHBoxLayout.addWidget(self.iconQLabel)
        self.allQHBoxLayout.addWidget(self.textUpQLabel)
        self.setLayout(self.allQHBoxLayout)
        self.textUpQLabel.setStyleSheet('''
            color: rgb(255, 255, 255);
        ''')
        # pxmap = QPixmap(imagePath)
        self.iconQLabel.setPixmap(QPixmap(imagePath).scaledToWidth(32))
        # self.iconQLabel.setMaximumWidth(50)
        self.textUpQLabel.setText(self.text)
        self.textUpQLabel.setFont(QFont('SansSerif', 10))
        self.nameLabel = nameLabel

    def getText(self):
        return self.text

    def mousePressEvent(self, event):
        self.nameLabel.setText('{}'.format(self.text))
        print("clicked:",self.text)

