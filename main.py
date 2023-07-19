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
        title = "Project Manager"
        description = "Project Manager"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

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

        # EXTRA LEFT BOX
        widgets.toggleLeftBox.clicked.connect(self.openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(self.openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

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

    # CONTACT CLICK
    # ///////////////////////////////////////////////////////////////
    def connectContactButtons(self, contact_buttons):
        for contact_button in contact_buttons:
            contact_button.clicked.connect(self.contactClick)

    def contactClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        app_functions.target_username = btn.contact_username
        reloadChat(btn.selected_message_id)

        btn = widgets.btn_messenger
        UIFunctions.resetStyle(self, btn.objectName())
        btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    # EXTRA LEFT BOX
    # ///////////////////////////////////////////////////////////////
    def openCloseLeftBox(self):
        UIFunctions.toggleLeftBox(self, True)

    def leftBoxIsOpen(self):
        return self.ui.extraLeftBox.width() != 0

    def closeLeftBox(self):
        if self.leftBoxIsOpen():
            self.openCloseLeftBox()

    def openLeftBox(self):
        if not self.leftBoxIsOpen():
            self.openCloseLeftBox()

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

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
