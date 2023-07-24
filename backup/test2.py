#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class MyPopupDialog(QDialog):
    def __init__(self, parent=None):
        # Regular init stuff...
        # and other things you might want
        super().__init__()


class MyForm(QDialog):
    def __init__(self, parent=None):
        # Here, you should call the inherited class' init, which is QDialog
        QDialog.__init__(self, parent)

        # Usual setup stuff
        # self.ui = Ui_Dialog()
        # self.ui.setupUi(self)

        # Use new style signal/slots
        self.pushButton = QPushButton("hello")
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.pushButton)
        self.pushButton.clicked.connect(self.popup)

        # Other things...

    def popup(self):
        self.dialog = MyPopupDialog()
        # For Modal dialogs
        self.dialog.exec_()

        # Or for modeless dialogs
# self.dialog.show()

if __name__ == "__main__":
   app = QApplication(sys.argv)
   myapp= MyForm()
   myapp.show()
   sys.exit(app.exec_())