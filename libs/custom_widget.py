#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import cv2
import numpy as np
from shutil import copyfile

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

from libs.utils import newIcon
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QCustomQWidget(QWidget):
    def __init__(self, imagePath, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        self.imagePath = imagePath
        self.parent = parent
        self.textUpQLabel = QLabel()
        self.allQHBoxLayout = QHBoxLayout()
        # self.iconQLabel = None
        self.iconQLabel = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel)
        self.allQHBoxLayout.addWidget(self.textUpQLabel)

        self.btn = QPushButton('')
        self.btn.setIcon(newIcon('rotate90_2'))
        self.btn.clicked.connect(self.rotate90)        
        self.allQHBoxLayout.addWidget(self.btn)

        self.CBox = QCheckBox()
        self.CBox.setChecked(False)
        # self.CBox.resize(QSize(10,10))
        # self.CBox.setStyleSheet("color: white; border: 3px solid; background-color: white;")
        self.CBox.setStyleSheet('''background-color: white;''')

        self.allQHBoxLayout.addWidget(self.CBox)
        self.CBox.setFixedSize(self.CBox.sizeHint())

        self.VBoxLayout = QVBoxLayout()
        self.VBoxLayout.addLayout(self.allQHBoxLayout)

        self.line = QHLine()
        self.VBoxLayout.addWidget(self.line, Qt.AlignBottom)
        self.line.resize(self.line.minimumSizeHint())
        self.line.setStyleSheet("padding-top: 5px;  color: black;")
        self.line.hide()

        self.setLayout(self.VBoxLayout)
        self.textUpQLabel.setStyleSheet('''
            color: rgb(255, 255, 255);
        ''')
        # # pxmap = QPixmap(imagePath)

        self.imageData = self.read(self.imagePath, None)
        # img = cv2.imdecode(np.fromstring(self.imageData, np.uint8), cv2.IMREAD_COLOR)
        img = cv2.imdecode(np.fromstring(self.imageData, np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            height, width, byteValue = image.shape
            byteValue = byteValue * width

            image = QImage(image, width, height, byteValue, QImage.Format_RGB888)

            self.iconQLabel.setPixmap(QPixmap.fromImage(image).scaledToWidth(64))

        self.textUpQLabel.setText(os.path.basename(imagePath))



    def getPath(self):
        return self.imagePath

    def isCheck(self):
        return self.CBox.isChecked()

    def select(self):
        self.textUpQLabel.setStyleSheet("background-color: rgba(255, 141, 0, 0.68); color: black;")
        self.iconQLabel.setStyleSheet("background-color")

    def deselect(self):
        self.textUpQLabel.setStyleSheet("background-color: none; color: white;")
        self.iconQLabel.setStyleSheet("color: red")


    def read(self, filename, default=None):
        try:
            with open(filename, 'rb') as f:
                return f.read()
        except:
            return default

    def rotate90(self):

        # reload img
        self.imageData = self.read(self.imagePath, None)
        # img = cv2.imdecode(np.fromstring(self.imageData, np.uint8), cv2.IMREAD_COLOR)
        img = cv2.imdecode(np.fromstring(self.imageData, np.uint8), cv2.IMREAD_COLOR)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        s = 'save.jpg'
        s = os.path.abspath(s)
        # print(s)
        cv2.imwrite(s, img) # windows-1252
        
        copyfile(s, self.imagePath)
        # cv2.imwrite(s.encode('utf-8'), img) # windows-1252

        if self.imagePath == self.parent.filePath:
            self.parent.loadFile(self.parent.filePath)

        if img is not None and self.iconQLabel is not None:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            height, width, byteValue = image.shape
            byteValue = byteValue * width

            image = QImage(image, width, height, byteValue, QImage.Format_RGB888)

            self.iconQLabel.setPixmap(QPixmap.fromImage(image).scaledToWidth(64))



class QCustomQWidget_2(QWidget):
    def __init__(self, imagePath, text=None,):
        super(QCustomQWidget_2, self).__init__()
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
        self.show()


class QCustomQWidget_3(QWidget):
    def __init__(self, imagePath, parent=None, text=None, nameLabel=None ):
        super(QCustomQWidget_3, self).__init__(parent)
        self.imagePath = imagePath
        self.text = text
        self.parent = parent
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
        self.parent.selectedList(self)

    def mouseDoubleClickEvent(self, event):
        self.nameLabel.setText('{}'.format(self.text))
        self.parent.selectedList(self)
        self.parent.insideFolder(self.text)

    def select(self):
        self.textUpQLabel.setStyleSheet("background-color: rgba(255, 141, 0, 0.68); color: black;")
        self.iconQLabel.setStyleSheet("background-color")

    def deselect(self):
        self.textUpQLabel.setStyleSheet("background-color: rgba(255, 255, 255, 10); color: white;")
        self.iconQLabel.setStyleSheet("color: red")