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

import jdatetime

# MAIN FILE
# ///////////////////////////////////////////////////////////////
from main import *
from model import conf
from model.message import Message
from model.task import Task
from model.user import User

widgets: Optional[Ui_MainWindow] = None
mainWindow: Optional[MainWindow] = None
user: Optional[User] = None
target_username: Optional[str] = None


# WITH ACCESS TO MAIN WINDOW WIDGETS
# ///////////////////////////////////////////////////////////////
class AppFunctions(MainWindow):
    def setThemeHack(self, is_light):
        Settings.BTN_LEFT_BOX_COLOR = "background-color: #495474;"
        Settings.BTN_RIGHT_BOX_COLOR = "background-color: #495474;"
        Settings.MENU_SELECTED_STYLESHEET = MENU_SELECTED_STYLESHEET = """
        border-left: 22px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
        background-color: #566388;
        """

        # SET MANUAL STYLES
        self.ui.lineEdit.setStyleSheet("background-color: #6272a4;")
        self.ui.pushButton.setStyleSheet("background-color: #6272a4;")
        self.ui.plainTextEdit.setStyleSheet("background-color: #6272a4;")
        self.ui.tableWidget.setStyleSheet(
            "QScrollBar:vertical { background: #6272a4; } QScrollBar:horizontal { background: #6272a4; }")
        self.ui.scrollArea.setStyleSheet(
            "QScrollBar:vertical { background: #6272a4; } QScrollBar:horizontal { background: #6272a4; }")
        self.ui.comboBox.setStyleSheet("background-color: #6272a4;")
        self.ui.horizontalScrollBar.setStyleSheet("background-color: #6272a4;")
        self.ui.verticalScrollBar.setStyleSheet("background-color: #6272a4;")
        self.ui.commandLinkButton.setStyleSheet("color: #ff79c6;")

        # REMOVE STACKED WIDGET TRANSPARENT BACKGROUND
        widgets.stackedWidget.setStyleSheet("")

        # STYLE THE chatTextBox
        if is_light:
            widgets.chatTextBox.setStyleSheet("background-color: #6272a4; color: #ffffff;")
        else:
            widgets.chatTextBox.setStyleSheet("background-color: rgb(33, 37, 43); color: #ffffff;")


def prepareHomePage():
    if user is None:
        widgets.logOutArea.hide()
        widgets.logInArea.show()
        widgets.leftMenuBg.hide()
    else:
        widgets.logInArea.hide()
        widgets.logOutArea.show()
        widgets.leftMenuBg.show()

    widgets.loginPushButton.clicked.connect(loginUser)
    widgets.logoutPushButton.clicked.connect(logoutUser)


def logoutUser():
    global user

    user = None
    MainWindow.setUser(user)
    prepareHomePage()

    widgets.loginResult.setStyleSheet("color: green;")
    widgets.loginResult.setText("You logged out successfully")


def loginUser():
    global user

    username = widgets.usernameLineEdit.text()
    password = widgets.passwordLineEdit.text()

    print(username, ":", password)

    try:
        logged_in_user = User.find_by_username(username)
        if logged_in_user.password == password:
            user = logged_in_user
            MainWindow.setUser(user)

            widgets.loginResult.setStyleSheet("color: green;")
            widgets.loginResult.setText("You logged in successfully")

            image_url = f"{os.getcwd()}\\resources\\images\\{user.username}.jpg"
            widgets.userImage.setPixmap(QPixmap(image_url))
            widgets.loggedInUsernameLineEdit.setText(user.username)
            widgets.fullNameLineEdit.setText(user.fullname)
        else:
            widgets.loginResult.setStyleSheet("color: red;")
            widgets.loginResult.setText("Wrong password")
    except Exception as e:
        print(traceback.format_exc())
        widgets.loginResult.setStyleSheet("color: red;")
        widgets.loginResult.setText("Wrong username")

    prepareHomePage()


def prepareAddTaskPage():
    setUsersForAddTask()
    widgets.addTaskPushButton.clicked.connect(addTask)
    widgets.assignUserComboBox.setCurrentIndex(-1)


def addTask():
    if widgets.assignUserComboBox.currentIndex() != -1:
        task = Task(assigner_username=user.username,
                    assignee_username=widgets.assignUserComboBox.currentText(),
                    description=widgets.taskPlainTextEdit.toPlainText())
        task.save()

        widgets.assignUserComboBox.setCurrentIndex(-1)
        widgets.taskPlainTextEdit.setPlainText("")


def setUsersForAddTask():
    widgets.assignUserComboBox.clear()

    for other_user in User.users():
        widgets.assignUserComboBox.addItem(other_user.username)


def prepareMessengerPage():
    new_text_edit = AutoResizingTextEdit()
    new_text_edit.setStyleSheet(widgets.messengerTextEdit.styleSheet())
    widgets.horizontalLayout_10.replaceWidget(widgets.messengerTextEdit, new_text_edit)
    widgets.messengerTextEdit.deleteLater()
    widgets.messengerTextEdit = new_text_edit

    users = User.users()
    user_buttons = [None for i in range(len(users))]

    for i, other_user in enumerate(User.users()):
        image_url = f"{os.getcwd()}\\resources\\images\\{other_user.username}.jpg"

        user_buttons[i] = QPushButton("   " + other_user.fullname + "   ")
        user_buttons[i].setToolTip(other_user.username)
        user_buttons[i].setIcon(QIcon(image_url))
        user_buttons[i].setIconSize(QSize(45, 45))
        user_buttons[i].setMinimumHeight(60)
        user_buttons[i].setStyleSheet("text-align: left;")
        # user_buttons[i].clicked.connect(lambda j=user_buttons[i]: reloadChat(j.toolTip()))
        widgets.contactsVerticalLayout.addWidget(user_buttons[i])

    widgets.contactsVerticalLayout.addStretch()

    # Prepare send button
    widgets.chatSendButton.clicked.connect(sendMessage)

    return user_buttons


def sendMessage():
    sender = user.username
    receiver = target_username
    text = widgets.messengerTextEdit.toPlainText()
    message = Message(sender_username=sender, receiver_username=receiver, text=text)
    message.save()

    widgets.messengerTextEdit.setPlainText("")

    reloadChat(target_username)


def reloadChat(username: str):
    global target_username
    target_username = username

    # Clear chatbox
    clearLayout(widgets.chatGridLayout)

    widgets.stackedWidget.setCurrentWidget(widgets.messenger)
    widgets.chatStackedWidget.setCurrentWidget(widgets.chatPage)

    messages = user.messages(username)

    for i, message in enumerate(messages):
        is_sender = (message.sender_username == user.username)
        label = AutoResizingTextEdit()
        label_text = message.text + "\n" + message.get_time_created()
        label.setText(label_text)
        # label.setReadOnly(True)
        label.setObjectName("from-me" if is_sender else "from-them")
        widgets.chatGridLayout.addWidget(label, 1 + i, is_sender, 1, 2)

        # widgets.chatGridLayout.setRowStretch(i, 1)

    # if not widgets.chatScrollArea.verticalScrollBar().isVisible():
    #     widgets.chatScrollVerticalLayout.addStretch()

    QCoreApplication.processEvents()
    widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())
    QCoreApplication.processEvents()
    widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())


def prepareShowTasks():
    reloadTasks()


def reloadTasks():
    widgets.userTasksTableWidget.setRowCount(1)

    if user is not None:
        for task in user.tasks():
            date = task.get_time_created()

            rowPosition = widgets.userTasksTableWidget.rowCount()
            widgets.userTasksTableWidget.insertRow(rowPosition)
            widgets.userTasksTableWidget.setItem(rowPosition, 0, QTableWidgetItem(task.assigner_username))
            widgets.userTasksTableWidget.setItem(rowPosition, 1, QTableWidgetItem(date))
            widgets.userTasksTableWidget.setItem(rowPosition, 2, QTableWidgetItem(task.description))


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
