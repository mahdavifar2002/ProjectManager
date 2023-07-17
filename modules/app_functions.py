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
            widgets.contactInfoBox.setStyleSheet("background-color: #6272a4; color: #ffffff;")
        else:
            widgets.chatTextBox.setStyleSheet("background-color: rgb(33, 37, 43); color: #ffffff;")
            widgets.contactInfoBox.setStyleSheet("background-color: rgb(33, 37, 43); color: #ffffff;")


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

    reloadChat(None)

    widgets.loginResult.setStyleSheet("color: green;")
    widgets.loginResult.setText("You logged out successfully")


def loginUser():
    global user

    username = widgets.usernameLineEdit.text()
    password = widgets.passwordLineEdit.text()

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
    new_text_edit = AutoResizingTextEdit(widgets.chatTextBox)
    new_text_edit.setStyleSheet(widgets.messengerTextEdit.styleSheet())
    widgets.chatTextBoxHorizontalLayout.replaceWidget(widgets.messengerTextEdit, new_text_edit)
    widgets.messengerTextEdit.deleteLater()
    widgets.messengerTextEdit = new_text_edit

    users = User.users()
    user_buttons = [None for _ in range(len(users))]

    for i, other_user in enumerate(User.users()):
        user_buttons[i] = create_user_button(other_user)
        widgets.contactsVerticalLayout.addWidget(user_buttons[i])

    widgets.contactsVerticalLayout.addStretch()

    # Prepare send button
    widgets.chatSendButton.clicked.connect(sendMessage)

    # Set current widget to 'select a chat'
    widgets.chatStackedWidget.setCurrentWidget(widgets.selectChatPage)

    # Prepare reply area
    widgets.replyFrame.hide()
    widgets.closeReplyButton.clicked.connect(lambda: widgets.replyFrame.hide())

    return user_buttons


def create_user_button(other_user):
    image_url = f"{os.getcwd()}\\resources\\images\\{other_user.username}.jpg"
    user_button = QPushButton("   " + other_user.fullname + "   ")
    user_button.setToolTip(other_user.username)
    user_button.setIcon(QIcon(image_url))
    user_button.setIconSize(QSize(45, 45))
    user_button.setMinimumHeight(60)
    user_button.setStyleSheet("text-align: left; border: none;")
    return user_button


def sendMessage():
    sender = user.username
    receiver = target_username
    text = widgets.messengerTextEdit.toPlainText().strip()

    if len(text) > 0:
        reply_to = None if widgets.replyFrame.isHidden() else int(widgets.replyLabel.toolTip())
        message = Message(sender_username=sender, receiver_username=receiver, text=text, reply_to=reply_to)
        message.save()
        reloadChat(target_username)

    widgets.messengerTextEdit.setPlainText("")
    widgets.replyFrame.hide()


def reloadChat(username: str | None):
    global target_username
    target_username = username

    # Clear chatbox
    clearLayout(widgets.chatGridLayout)
    clearLayout(widgets.contactInfoHorizontalLayout)

    if username is None:
        widgets.chatStackedWidget.setCurrentWidget(widgets.selectChatPage)
        return

    widgets.chatStackedWidget.setCurrentWidget(widgets.chatPage)
    widgets.stackedWidget.setCurrentWidget(widgets.messenger)

    # Contact info box
    target_user = User.find_by_username(target_username)
    user_button = create_user_button(target_user)
    widgets.contactInfoHorizontalLayout.addWidget(user_button)

    # Messages
    messages = user.messages(username)

    for i, message in enumerate(messages):
        is_sender = (message.sender_username == user.username)
        message_widget = MessageWidget(message, widgets)
        widgets.chatGridLayout.addWidget(message_widget, 1 + i, is_sender, 1, 2)

        # widgets.chatGridLayout.setRowStretch(i, 1)

    # if not widgets.chatScrollArea.verticalScrollBar().isVisible():
    #     widgets.chatScrollVerticalLayout.addStretch()

    QCoreApplication.processEvents()
    widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())
    QCoreApplication.processEvents()
    widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())


class MessageWidget(QFrame):
    def __init__(self, message: Message, widgets: Ui_MainWindow):
        super().__init__()
        self.widgets = widgets
        self.message = message

        text_edit = AutoResizingTextEdit()
        main_text = message.text.replace("\n", "<br/>")
        main_text += "\n" + "<p style='color: gray;'>" + message.get_time_created() + "</p>"
        text_edit.setHtml(main_text)
        text_edit.setReadOnly(True)
        text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        text_edit.customContextMenuRequested.connect(self.contextMenuEvent)

        message_vbox = QVBoxLayout()
        self.setLayout(message_vbox)

        if message.reply_to is not None:
            replied_message = Message.find_by_id(message.reply_to)
            replied_text = replied_message.short_text()
            replied_label = QLabel(replied_text)
            replied_label.setStyleSheet("margin: 3px; border-left: 3px solid; border-color: gray;")
            message_vbox.addWidget(replied_label)

        message_vbox.addWidget(text_edit)

        is_sender = (message.sender_username == user.username)
        text_edit.setObjectName("from-me" if is_sender else "from-them")
        self.setObjectName("from-me" if is_sender else "from-them")

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        replyAction = QAction('Reply', self)
        replyAction.triggered.connect(lambda: self.replySlot(event))
        self.menu.addAction(replyAction)
        # add other required actions
        self.menu.popup(QCursor.pos())

    def replySlot(self, event):
        widgets.replyLabel.setText(self.message.short_text())
        widgets.replyLabel.setToolTip(str(self.message.id))
        widgets.replyFrame.show()


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
