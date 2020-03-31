import sys, time
# from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# from libs.labelDialog2 import TrainStatus
# import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import pyqtSlot
class TrainStatus(QDialog):
    def __init__(self, checkpointDf=None, parent=None):
        super(TrainStatus, self).__init__(parent)

        self.checkpointDf = self.genData()
        self.tableWidget = QTableWidget()
        self.setData()
        self.tableWidget.resize(self.tableWidget.sizeHint())

        self.filename = '/home/aimenext/Downloads/img/86230015_614944025957783_8799739092960018432_o.jpg'
        self.repaint()
        # self.imgwidget = QWidget()
        # self.imgwidget.pixmap = QPixmap()
        oImage = QImage(self.filename)
        # sImage = oImage.scaled()  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QGridLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # self.setMaximumHeight(300)
        # self.resize(500,200)


    def setData(self):
        # Create table
        self.tableWidget.setRowCount(self.checkpointDf.shape[0])
        self.tableWidget.setColumnCount(self.checkpointDf.shape[1])

        horHeaders = []
        for n, key in enumerate(self.checkpointDf.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.checkpointDf[key]):
                newitem = QTableWidgetItem(str(item))
                self.tableWidget.setItem(m, n, newitem)
                newitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.tableWidget.setHorizontalHeaderLabels(horHeaders)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def genData(self):

        import pandas as pd
        df = pd.DataFrame(columns=('name', 'loss', 'time', 'best'))
        df = df.append([{'name': 'None', 'time': 'nadfffffffff', 'loss': 'nfffffffffffffffffffffffffffffffffffffffffffff', 'best': 'None'}])
        df = df.append([{'name': 'None', 'time': 'None', 'loss': 'None', 'best': 'None'}])
        df = df.append([{'name': 'None', 'time': 'None', 'loss': 'None', 'best': 'None'}])
        return df

    # def spam(self):
    #     self.imageData = QImage(self.filename)
    #     image = QImage.fromData(self.imageData)
    #     self.image = image
    #     self.pix
    #     self.canvas.loadPixmap(QPixmap.fromImage(image))
    #
    #
    #
    # def paintEvent(self, event):
    #     if not self.pixmap:
    #         return super(Canvas, self).paintEvent(event)
    #
    #     p = self._painter
    #     p.begin(self)
    #     p.setRenderHint(QPainter.Antialiasing)
    #     p.setRenderHint(QPainter.HighQualityAntialiasing)
    #     p.setRenderHint(QPainter.SmoothPixmapTransform)
    #
    #     p.scale(self.scale, self.scale)
    #     p.translate(self.offsetToCenter())
    #
    #     p.drawPixmap(0, 0, self.pixmap)
    #
    #     self.setAutoFillBackground(True)
    #     if self.verified:
    #         pal = self.palette()
    #         # pal.setColor(self.backgroundRole(), QColor(184, 239, 38, 128))
    #         pal.setColor(self.backgroundRole(),QColor(179, 200, 200))
    #         self.setPalette(pal)
    #     else:
    #         pal = self.palette()
    #         pal.setColor(self.backgroundRole(),  QColor(211, 238, 255))
    #         # pal.setColor(self.backgroundRole(), QColor(232, 232, 232, 255))
    #         self.setPalette(pal)
    #
    #     p.end()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TrainStatus()
    ex.show()
    sys.exit(app.exec_())