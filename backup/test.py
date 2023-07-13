import sys
from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6 import QtGui
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class LayoutTest(QWidget):
    def __init__(self):
        super(LayoutTest, self).__init__()
        self.horizontalLayout = QVBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 380, 280))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.gridLayout = QGridLayout()
        self.horizontalLayout_2.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.add_button = QPushButton("Add Items")
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.addButtons)
        self.setGeometry(300, 200, 400, 300)

    def addButtons(self):
        for i in range(0, 50):
            self.r_button = QPushButton("Button %s " % i)
            self.gridLayout.addWidget(self.r_button)


def run():
    app = QApplication(sys.argv)
    ex = LayoutTest()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
