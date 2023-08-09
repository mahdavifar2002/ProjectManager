# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform
from time import sleep
from typing import Optional

from model.user import User

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets: Optional[Ui_MainWindow] = None
user: Optional[User] = None


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        app_functions.widgets = widgets
        app_functions.mainWindow = self

        # SET CLIENT FOR BROADCAST PACKAGES
        # ///////////////////////////////////////////////////////////////
        prepareClientThread()

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        self.title = "Project Manager"
        self.description = ""

        # APPLY TEXTS
        if len(sys.argv) >= 4:
            self.setWindowTitle("Message " + sys.argv[3])
        else:
            self.setWindowTitle(self.title)

        widgets.titleRightInfo.setText(self.description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_messenger.clicked.connect(self.buttonClick)
        widgets.btn_add.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)

        # HIDE FEATURES THAT AREN'T YET IMPLEMENTED OR WANTED
        widgets.bottomBar.hide()
        widgets.btn_share.hide()
        widgets.btn_widgets.hide()
        widgets.btn_add.hide()
        widgets.btn_new.hide()
        widgets.btn_save.hide()
        widgets.btn_exit.hide()

        # EXTRA LEFT BOX
        widgets.toggleLeftBox.clicked.connect(self.openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(self.openCloseLeftBox)

        # EXTRA RIGHT BOX
        widgets.settingsTopBtn.clicked.connect(self.openCloseLeftMenu)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = True
        themeFiles = ["themes\\py_dracula_dark.qss", "themes\\py_dracula_light.qss"]
        themeCounter = 0

        def toggleTheme():
            nonlocal themeCounter
            # SET THEME AND HACKS
            if useCustomTheme:
                # LOAD AND APPLY STYLE
                UIFunctions.theme(self, themeFiles[themeCounter % 2], True)

                # SET HACKS
                AppFunctions.setThemeHack(self, themeCounter % 2)
                themeCounter += 1

        toggleTheme()
        widgets.themeBtn.clicked.connect(toggleTheme)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        prepareHomePage()
        prepareAddTaskPage()
        prepareMessengerPage()
        prepareShowTasks()
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

        # LOGIN IF COMMANDLINE PASSED LOGIN INFO
        # ///////////////////////////////////////////////////////////////
        if len(sys.argv) >= 3:

            try:
                with open("userpass.txt", "r") as file:
                    username, password = file.read().split('\n')
            except Exception as e:
                username = sys.argv[1]
                password = sys.argv[2]

            widgets.usernameLineEdit.setText(username)
            widgets.passwordLineEdit.setText(password)

            if app_functions.loginUser(by_GUI=False):
                self.resize(460, 600)
                widgets.stackedWidget.setCurrentWidget(widgets.messenger)
                UIFunctions.resetStyle(self, widgets.btn_messenger.objectName())
                widgets.btn_messenger.setStyleSheet(UIFunctions.selectMenu(widgets.btn_messenger.styleSheet()))
                widgets.leftMenuBg.hide()

                if len(sys.argv) >= 4:
                    app_functions.reloadChat(sys.argv[3])
                    widgets.messengerTextEdit.setFocus()

                else:
                    self.openLeftBox()

    # EMOJI CLICK
    # ///////////////////////////////////////////////////////////////
    def connectEmojiButtons(self, emojiButtons):
        for emojiButton in emojiButtons:
            emojiButton.clicked.connect(self.emojiClicked)

    def emojiClicked(self):
        btn = self.sender()
        editor = widgets.messengerTextEdit

        # add emoji to text editor
        # editor.setPlainText(editor.toPlainText() + btn.text())
        editor.insertPlainText(btn.text())
        editor.setFocus()

        # # move cursor to the end of text editor
        # textCursor = editor.textCursor()
        # textCursor.setPosition(2*len(editor.toPlainText()))
        # editor.setTextCursor(textCursor)

    # STICKER CLICK
    # ///////////////////////////////////////////////////////////////
    def connectStickerButtons(self, stickerButtons):
        for stickerButton in stickerButtons:
            stickerButton.clicked.connect(self.stickerClicked)

    def stickerClicked(self):
        btn = self.sender()
        editor = widgets.messengerTextEdit

        # send sticker
        widgets.stickersGridLayout.setProperty("sticker_path", btn.property("sticker_path"))

        app_functions.sendMessage(force_send=True)

    # CONTACT CLICK
    # ///////////////////////////////////////////////////////////////
    def connectContactButtons(self, contact_buttons):
        for contact_button in contact_buttons:
            contact_button.clicked.connect(self.contactClick)

    def contactClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        app_functions.reloadChat(btn.user.username, btn.selected_message_id)
        self.closeLeftBox()

        btn = widgets.btn_messenger
        UIFunctions.resetStyle(self, btn.objectName())
        btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    # SEND TO CLICK
    # ///////////////////////////////////////////////////////////////
    def connectSendToActions(self, sendToActions):
        for sendToAction in sendToActions:
            sendToAction.triggered.connect(self.sendToTrigger)

    def sendToTrigger(self):
        action = self.sender()
        forward_username = action.property("username")
        forward_message_id = action.property("message_id")
        print(f"forward message with id {forward_message_id} to user {forward_username}")
        app_functions.forwardMessage(forward_message_id, forward_username)



    # EXTRA LEFT BOX
    # ///////////////////////////////////////////////////////////////
    def openCloseLeftBox(self):
        if not self.leftBoxIsOpen() and widgets.contactsVerticalLayout.count() == 0:
            app_functions.reload_contacts_list()

        UIFunctions.toggleLeftBox(self, True)

    def leftBoxIsOpen(self):
        return self.ui.extraLeftBox.width() != 0

    def closeLeftBox(self):
        if self.leftBoxIsOpen():
            self.openCloseLeftBox()

    def openLeftBox(self):
            self.openCloseLeftBox()

    # EXTRA RIGHT BOX
    # ///////////////////////////////////////////////////////////////
    def openCloseRightBox(self):
        if not self.leftBoxIsOpen() and widgets.stickersGridLayout.count() == 1 and widgets.emojisGridLayout.count() == 1:
            app_functions.reload_stickers()

        UIFunctions.toggleRightBox(self, True)
        widgets.messengerTextEdit.setFocus()

    def rightBoxIsOpen(self):
        return self.ui.extraRightBox.width() != 0

    def closeRightBox(self):
        if self.rightBoxIsOpen():
            self.openCloseRightBox()

    def openRightBox(self):
        if not self.rightBoxIsOpen():
            self.openCloseRightBox()

    # EXTRA RIGHT BOX
    # ///////////////////////////////////////////////////////////////
    def openCloseLeftMenu(self):
        UIFunctions.toggleLeftMenu(self, True)
        widgets.messengerTextEdit.setFocus()

    def leftMenuIsOpen(self):
        return self.ui.leftMenuBg.width() != 0

    def closeLeftMenu(self):
        if self.leftMenuIsOpen():
            self.openCloseLeftMenu()

    def openLeftMenu(self):
        if not self.leftMenuIsOpen():
            self.openCloseLeftMenu()

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # Reset name of window
        self.setWindowTitle(self.title)

        # CLOSE EXTRA LEFT BOX (CONTACTS BOX)
        self.closeLeftBox()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            prepareHomePage()
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW ADD TASK PAGE
        if btnName == "btn_add":
            widgets.stackedWidget.setCurrentWidget(widgets.add_task)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW MESSENGER PAGE
        if btnName == "btn_messenger":
            widgets.stackedWidget.setCurrentWidget(widgets.messenger)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.openLeftBox()

            if app_functions.target_username is not None:
                self.setWindowTitle("Message " + app_functions.target_username)

        # SHOW NEW PAGE
        if btnName == "btn_new":
            reloadTasks()
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    # USER MANAGEMENT
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def setUser(new_user):
        global user
        user = new_user


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
