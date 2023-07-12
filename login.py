import traceback

from PyQt6.QtWidgets import *
from PyQt6 import uic
import sys

from sqlalchemy.exc import NoResultFound

from messenger import MessengerUI
from user import User


class LoginUI(QWidget):
    def __init__(self):
        super(LoginUI, self).__init__()

        # Load the ui file
        uic.loadUi("login.ui", self)
        self.setWindowTitle("Product Manager | Login")

        # Define our widgets
        self.btn = self.findChild(QPushButton, "loginPushButton")
        self.usernameLineEdit = self.findChild(QLineEdit, "usernameLineEdit")
        self.passwordLineEdit = self.findChild(QLineEdit, "passwordLineEdit")
        self.btn.clicked.connect(self.btn_clicked)

        # Show the app
        self.show()

    def btn_clicked(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        print(username, password)

        try:
            user = User.find_by_username(username)
            if user.password == password:
                print("You logged in successfully")
                self.open_messenger(user)
            else:
                print("Wrong password")
        except NoResultFound as e:
            # print( type(e).__name__, ":", e)
            print("Wrong username")

    def open_messenger(self, user: User):
        try:
            self.window = MessengerUI(user)
            self.close()
        except Exception as e:
            print(traceback.format_exc())


app = QApplication(sys.argv)
UIWindow = LoginUI()
app.exec()
