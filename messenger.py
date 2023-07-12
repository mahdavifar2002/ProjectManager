import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
import sys

import conf
from message import Message
from user import User


class MessengerUI(QWidget):
    def __init__(self, user: User):
        super(MessengerUI, self).__init__()
        self.user = user

        # Load the ui file
        uic.loadUi("messenger.ui", self)
        # self.ui = Ui_Form()
        # self.ui.setupUi(self.window)

        self.setWindowTitle("Product Manager | Messenger")

        self.load_users()

        # Define our widgets
        self.usersVerticalLayout = self.findChild(QVBoxLayout, "usersVerticalLayout")
        self.textEdit = self.findChild(QTextEdit, "textEdit")
        self.sendPushButton: QPushButton = self.findChild(QPushButton, "sendPushButton")
        self.sendPushButton.setIcon(QIcon("./resources/icons/send.svg"))
        self.sendPushButton.clicked.connect(self.send_cliecked)
        self.messagesScrollArea = self.findChild(QScrollArea, "messagesScrollArea")
        self.messagesVerticalLayout = self.findChild(QVBoxLayout, "messagesVerticalLayout")

        # Set default target of messanger as nobody
        self.set_target("")

        # Show the app
        self.show()

    def send_cliecked(self):
        text = self.textEdit.toPlainText()
        message = Message(sender_username=self.user.username, receiver_username=self.target_username, text=text)
        message.save()
        self.load_messages()
    def load_users(self):
        users = conf.session.query(User).all()

        for user in users:
            if user != self.user:
                print(user.username)
                image_url = f"{os.getcwd()}\\resources\\images\\{user.username}.jpg"

                user_btn = QPushButton()
                user_btn.setIcon(QIcon(image_url))
                user_btn.setIconSize(QSize(48, 48))
                user_btn.clicked.connect(lambda x, u=user.username: self.set_target(u))
                self.usersVerticalLayout.addWidget(user_btn)


    def set_target(self, target_username):
        self.target_username = target_username

        if target_username == "":
            self.textEdit.hide()
            self.sendPushButton.hide()
        else:
            self.textEdit.show()
            self.sendPushButton.show()
            self.load_messages()

    def load_messages(self):
        print(f"loading messages for target user '{self.target_username}'")
        for i in reversed(range(self.messagesVerticalLayout.count())):
            self.messagesVerticalLayout.itemAt(i).widget().setParent(None)

        messages = self.user.messages(self.target_username)

        for message in messages:
            textBrowser = QTextBrowser(self.messagesScrollArea)
            textBrowser.setDocument(QTextDocument(message.text))
            textBrowser.setFixedHeight(int(textBrowser.document().size().height()))
            self.messagesVerticalLayout.addWidget(textBrowser)


def mask_image(imgdata, imgtype='png', size=64):
    # Load image
    image = QImage.fromData(imgdata, imgtype)

    # convert image to 32-bit ARGB (adds an alpha
    # channel ie transparency factor):
    image.convertToFormat(QImage.Format.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) // 2,
        (image.height() - imgsize) // 2,
        imgsize,
        imgsize,
    )

    image = image.copy(rect)

    # Create the output image with the same dimensions
    # and an alpha channel and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format.Format_ARGB32)
    out_img.fill(Qt.GlobalColor.transparent)

    # Create a texture brush and paint a circle
    # with the original image onto the output image:
    brush = QBrush(image)

    # Paint the output image
    painter = QPainter(out_img)
    painter.setBrush(brush)

    # Don't draw an outline
    painter.setPen(Qt.PenStyle.NoPen)

    # drawing circle
    painter.drawEllipse(0, 0, imgsize, imgsize)

    # closing painter event
    painter.end()

    # Convert the image to a pixmap and rescale it.
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    size = int(size)
    pm = pm.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                   Qt.TransformationMode.SmoothTransformation)

    # return back the pixmap data
    return pm
