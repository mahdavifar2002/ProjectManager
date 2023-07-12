from PyQt6.QtWidgets import *
from PyQt6 import uic
import sys


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load the ui file
        uic.loadUi("template.ui", self)
        self.setWindowTitle("Hello, world!")

        # Define our widgets
        self.btn = self.findChild(QPushButton, "pushButton")
        self.label = self.findChild(QLabel, "label")
        self.lineEdit = self.findChild(QLineEdit, "lineEdit")
        self.btn.clicked.connect(self.btn_clicked)

        # Show the app
        self.show()

    def btn_clicked(self):
        text = self.lineEdit.text()
        self.label.setText(text)


app = QApplication(sys.argv)
UIWindow = UI()
app.exec()
