import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()

        self.home()

    def home(self):


        comboBox.activated[str].connect(self.style_choice)

        self.show()

    def style_choice(self, text):
        self.styleChoice.setText(text)
        QApplication.setStyle(QStyleFactory.create(text))


def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()