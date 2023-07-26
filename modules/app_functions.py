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
import datetime
from typing import Optional, Dict

import jdatetime

# MAIN FILE
# ///////////////////////////////////////////////////////////////
from main import *
from model import conf
from model.message import Message
from model.task import Task
from model.user import User
from modules.server import send_broadcast
from modules.client import receive_broadcast

widgets: Optional[Ui_MainWindow] = None
mainWindow: Optional[MainWindow] = None
user: Optional[User] = None
messages_dict: Dict[int, QWidget] = {}
target_username: Optional[str] = None
last_user_update: datetime.datetime = datetime.datetime.now()


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
    global target_username

    user = None
    MainWindow.setUser(user)
    prepareHomePage()

    target_username = None
    reloadChat()

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
            reload_contacts_list()

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
    new_text_edit.textChanged.connect(messenger_text_changed)
    widgets.chatTextBoxHorizontalLayout.replaceWidget(widgets.messengerTextEdit, new_text_edit)
    widgets.messengerTextEdit.deleteLater()
    widgets.messengerTextEdit = new_text_edit

    reload_contacts_list()

    # Prepare send button
    widgets.chatSendButton.clicked.connect(sendMessage)

    QShortcut(QKeySequence("Ctrl+Return"),
              widgets.messengerTextEdit,
              sendMessage)

    # Prepare emoji button
    widgets.emojiButton.clicked.connect(mainWindow.openCloseRightBox)

    # Prepare emojies buttons
    emojis_list = "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩" \
                  "🥳😏😒😞😔😟😕🙁😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😶😱😨😰😥😓🤗" \
                  "🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😮😵😵💫🤐🥴🤢🤮🤧😷🤒🤕" \
                  "🤑🤠😈👿👹👺🤡👻💀👽👾🤖🎃😺😸😹😻😼😽🙀😿😾🤲👐🙌👏🤝👍👎👊" \
                  "✊🤛🤜🤞🤟🤘👌🤏👈👉👆👇✋🤚🖐🖖👋🤙💪🙏"
    emojiButtons = []

    for i, item in enumerate(emojis_list):
        emojiButton = QPushButton(emojis_list[i])
        emojiButton.setStyleSheet("font: 14pt; text-align: center;")
        widgets.emojisGridLayout.addWidget(emojiButton, i / 4 + 1, i % 4)
        emojiButtons.append(emojiButton)

    mainWindow.connectEmojiButtons(emojiButtons)

    # Prepare search button
    widgets.searchPushButton.clicked.connect(lambda: reload_contacts_list(widgets.searchLineEdit.text()))

    QShortcut(QKeySequence("Ctrl+F"),
              widgets.messengerTextEdit,
              lambda: (mainWindow.openLeftBox(), widgets.searchLineEdit.setFocus()))

    QShortcut(QKeySequence("Return"),
              widgets.messengerTextEdit,
              lambda: reload_contacts_list(widgets.searchLineEdit.text()))

    # Set current widget to 'select a chat'
    widgets.chatStackedWidget.setCurrentWidget(widgets.selectChatPage)

    # Prepare reply area
    widgets.replyFrame.hide()
    widgets.closeReplyButton.clicked.connect(lambda: widgets.replyFrame.hide())

    # Prepare edit area
    widgets.editFrame.hide()
    widgets.closeEditButton.clicked.connect(close_edit_area)

    # Prepare pin area
    widgets.pinFrame.hide()
    widgets.pinLabel.setToolTip(str(-1))
    widgets.pinLabel.mousePressEvent = jump_to_pin_message
    widgets.closePinButton.clicked.connect(unpin_message)

    # # Prepare handling seen messages
    # widgets.chatScrollArea.verticalScrollBar().actionTriggered.connect(on_chat_scroll)

    # Prepare 'load more messages' button
    widgets.loadMoreButton.clicked.connect(fetch_ten_messages)

    # # Prepare chat scroll bar
    # widgets.chatScrollArea.verticalScrollBar().setMinimum(200)


def messenger_text_changed():
    global user
    global target_username
    global last_user_update

    if conf.time_diff_in_second(datetime.datetime.now(), last_user_update) < 1:
        return

    last_user_update = datetime.datetime.now()

    if target_username is not None:
        user.set_typing(target_username)
        user.save()
        send_broadcast(f"reload_user {user.username}")


def close_edit_area():
    widgets.editFrame.hide()
    widgets.messengerTextEdit.setPlainText("")


def reload_contacts_list(search: str | None = None):
    clearLayout(widgets.contactsVerticalLayout)

    if search is None or search == "":
        users = User.users()
        user_buttons = [None for _ in range(len(users))]

        for i, other_user in enumerate(users):
            # if user is not None:
            #     user_buttons[i] = ContactButton(other_user, user.last_message(other_user.username))
            # else:
            user_buttons[i] = ContactButton(other_user, None)
            widgets.contactsVerticalLayout.addWidget(user_buttons[i])

    else:
        messages = user.search_messages(search)
        users = [user.find_by_username(
            message.sender_username if message.sender_username != user.username else message.receiver_username)
            for message in messages]
        user_buttons = [None for _ in range(len(users))]

        for i, other_user in enumerate(users):
            user_buttons[i] = ContactButton(other_user, messages[i])
            widgets.contactsVerticalLayout.addWidget(user_buttons[i])

    widgets.contactsVerticalLayout.addStretch()
    mainWindow.connectContactButtons(user_buttons)


class ContactButton(QPushButton):
    def __init__(self, other_user, selected_message: Message | None):
        image_url = f"{os.getcwd()}\\resources\\images\\{other_user.username}.jpg"
        super().__init__()
        self.user = other_user
        self.selected_message = selected_message
        self.selected_message_id = selected_message.id if selected_message is not None else None

        self.setToolTip(self.user.username)
        self.setIcon(QIcon(image_url))
        self.setIconSize(QSize(45, 45))
        self.setMinimumHeight(60)
        self.setStyleSheet("text-align: left; border: none;")

        # Prepare user_button text (username + last message, if any)
        self.updateUser()

    def updateUser(self):
        conf.session.commit()
        self.user = User.find_by_username(self.user.username)

        text = "   " + self.user.fullname + "   " + "\n"

        if (user is not None) and self.user.is_typing_for(user.username):
            text += "   ...is typing   "

            # Create timer object
            timer = QTimer(self)
            timer.timeout.connect(self.updateUser)
            timer.setSingleShot(True)
            timer.start(3000)

        # if user is not None and message is None:
        #     message = user.last_message(other_user.username)

        elif self.selected_message is not None:
            text += "   " + self.selected_message.short_text() + "   "

        self.setText(text)


def sendMessage():
    if not widgets.messengerTextEdit.hasFocus() and not widgets.chatSendButton.hasFocus():
        return

    sender = user.username
    receiver = target_username
    text = widgets.messengerTextEdit.toPlainText().strip()

    if len(text) > 0:
        # send new message
        if widgets.editFrame.isHidden():
            reply_to = None if widgets.replyFrame.isHidden() else int(widgets.replyLabel.toolTip())
            message = Message(sender_username=sender, receiver_username=receiver, text=text, reply_to=reply_to)
            message.save()
            reloadChat()
            send_broadcast(f"reload_chat {receiver}")
        # edit old message
        else:
            message_widget = messages_dict[int(widgets.editLabel.toolTip())]
            message = message_widget.message
            message.text = text
            message.has_been_edited = True
            message.save()
            send_broadcast(f"reload_message {message.id}")
            widgets.editFrame.hide()

    widgets.messengerTextEdit.setPlainText("")
    widgets.replyFrame.hide()


def reloadChat(message_id: int | None = None):
    global target_username
    global messages_dict

    # Clear chatbox
    clearLayout(widgets.chatGridLayout)
    clearLayout(widgets.contactInfoHorizontalLayout)
    # remove pin frame
    widgets.pinFrame.hide()
    widgets.pinLabel.setToolTip(str(-1))

    # if no target, go to "select a chat" page
    if target_username is None:
        widgets.chatStackedWidget.setCurrentWidget(widgets.selectChatPage)
        return
    # else, go to "chat" page
    widgets.chatStackedWidget.setCurrentWidget(widgets.chatPage)
    widgets.stackedWidget.setCurrentWidget(widgets.messenger)

    # Contact info box
    target_user = User.find_by_username(target_username)
    user_button = ContactButton(target_user, None)
    widgets.contactUserButton = user_button
    widgets.contactInfoHorizontalLayout.addWidget(user_button)

    # Messages
    messages_dict = {}

    fetch_ten_messages(load_all=True)

    #  scroll to the end of chat
    if message_id is None:
        for i in range(2):
            QCoreApplication.processEvents()
            widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())
    else:
        # scroll to selected message
        message_widget = messages_dict[message_id]
        for i in range(2):
            QCoreApplication.processEvents()
            widgets.chatScrollArea.ensureWidgetVisible(message_widget)
        message_widget.setFocus()

    # # check seen messages
    # on_chat_scroll()


def fetch_ten_messages(load_all=False):
    global target_username
    global messages_dict
    global user

    # get the id of earliest of already fetched messages
    before_id = min(messages_dict, default=2147483647)

    if load_all:
        messages = user.messages(target_username)
    else:
        messages = user.ten_messages(target_username, before_id)

    # Add an empty widget at top of chatbox to force reload
    widgets.chatGridLayout.addWidget(QLabel(""), 0, 0)

    for i, message in enumerate(messages):
        is_sender = (message.sender_username == user.username)
        message_widget = MessageWidget(message, widgets)
        widgets.chatGridLayout.addWidget(message_widget, 1 + message.id, is_sender, 1, 2)

        # Fill the message dictionary
        messages_dict[message.id] = message_widget

        # check for pin
        if message.pinned:
            message_widget.pinMessage()


def on_chat_scroll():
    # if widgets.chatScrollArea.verticalScrollBar().value() == widgets.chatScrollArea.verticalScrollBar().minimum():
    #     widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().minimum() + 50)
    #     fetch_ten_messages()

    pass
    # # check seens
    # for message_widget in messages_dict.values():
    #     if message_widget.message.receiver_username == user.username:
    #         if not message_widget.visibleRegion().isEmpty():
    #             if not message_widget.message.has_been_seen:
    #                 message_widget.message.has_been_seen = True
    #                 message_widget.message.save()
    #                 send_broadcast(f"reload_message {message_widget.message.id}")


def jump_to_pin_message(event):
    message_id = int(widgets.pinLabel.toolTip())
    if message_id in messages_dict:
        messages_dict[message_id].jumpTo()


def unpin_message():
    message_id = int(widgets.pinLabel.toolTip())
    if message_id in messages_dict:
        message_widget = messages_dict[message_id]
        message = message_widget.message

        widgets.pinFrame.hide()
        widgets.pinLabel.setToolTip(str(-1))

        for widget in messages_dict.values():
            if widget.message.pinned:
                widget.pinMessage()

        if message.pinned:
            message.pinned = False
            message_widget.message.save()
            send_broadcast(f"reload_message {message.id}")


class MessageWidget(QFrame):
    def __init__(self, message: Message, widgets: Ui_MainWindow):
        super().__init__()
        self.widgets = widgets
        self.message = message

        self.text_edit = MessageTextWidget(self)
        self.updateMessage()

        message_vbox = QVBoxLayout()
        self.setLayout(message_vbox)

        if message.reply_to is not None:
            replied_widget = RepliedWidget(message, self)
            message_vbox.addWidget(replied_widget)

        if True:
            voice_widget = VoiceWidget(self)
            message_vbox.addWidget(voice_widget)

        message_vbox.addWidget(self.text_edit)

        is_sender = (message.sender_username == user.username)
        self.setObjectName("from-me" if is_sender else "from-them")

    def jumpTo(self):
        widgets.chatScrollArea.ensureWidgetVisible(self)
        self.setFocus()

    def pinMessage(self):
        # check if no later message is already pinned
        if self.message.id > int(widgets.pinLabel.toolTip()):
            # put message in pin frame
            widgets.pinLabel.setText(self.message.short_text())
            widgets.pinLabel.setToolTip(str(self.message.id))

            # show pin frame
            widgets.pinFrame.show()

            # blur the pin message if the message is itself blured
            if self.text_edit.graphicsEffect() is not None:
                self.pin_blur_effect = QGraphicsBlurEffect(blurRadius=15)
                widgets.pinLabel.setGraphicsEffect(self.pin_blur_effect)
            else:
                widgets.pinLabel.setGraphicsEffect(None)

    def updateMessage(self):
        conf.session.commit()
        self.message = Message.find_by_id(self.message.id)

        if self.message.pinned:
            self.pinMessage()
        elif widgets.pinLabel.toolTip() == str(self.message.id):
            unpin_message()

        if self.message.deleted:
            self.hide()
        else:
            is_sender = (self.message.sender_username == user.username)
            main_text = self.message.text.replace("\n", "<br/>")
            seen_text = "✅ " if is_sender and self.message.has_been_seen else ""
            pin_text = "📌 " if self.message.pinned else ""
            edit_text = " (edited)" if self.message.has_been_edited else ""
            main_text += "\n" + "<p style='color: gray;'>" + seen_text + pin_text + self.message.get_time_created() + edit_text + "</p>"
            self.text_edit.setHtml(main_text)

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)

        # reply
        replyAction = QAction('Reply', self)
        replyAction.triggered.connect(lambda: self.replySlot(event))
        self.menu.addAction(replyAction)

        # pin
        pinAction = QAction('Pin / Unpin', self)
        pinAction.triggered.connect(lambda: self.pinSlot(event))
        self.menu.addAction(pinAction)

        # edit
        if self.message.sender_username == user.username:
            editAction = QAction('Edit', self)
            editAction.triggered.connect(lambda: self.editSlot(event))
            self.menu.addAction(editAction)

            editAction = QAction('Delete', self)
            editAction.triggered.connect(lambda: self.deleteSlot(event))
            self.menu.addAction(editAction)

        # add other required actions
        self.menu.popup(QCursor.pos())

    def replySlot(self, event):
        widgets.replyLabel.setText(self.message.short_text())
        widgets.replyLabel.setToolTip(str(self.message.id))
        if self.text_edit.graphicsEffect() is not None:
            self.reply_blur_effect = QGraphicsBlurEffect(blurRadius=15)
            widgets.replyLabel.setGraphicsEffect(self.reply_blur_effect)
        else:
            widgets.replyLabel.setGraphicsEffect(None)

        widgets.editFrame.hide()
        widgets.replyFrame.show()
        widgets.messengerTextEdit.setFocus()

    def pinSlot(self, event):
        self.message.pinned = not self.message.pinned
        self.message.save()
        send_broadcast(f"reload_message {self.message.id}")

    def editSlot(self, event):
        widgets.editLabel.setText(self.message.short_text())
        widgets.editLabel.setToolTip(str(self.message.id))

        editor = widgets.messengerTextEdit
        editor.setPlainText(self.message.text)

        textCursor = editor.textCursor()
        textCursor.setPosition(len(editor.toPlainText()))
        editor.setTextCursor(textCursor)

        widgets.replyFrame.hide()
        widgets.editFrame.show()
        widgets.messengerTextEdit.setFocus()

    def deleteSlot(self, event):
        self.message.deleted = True
        self.message.pinned = False
        self.message.save()
        send_broadcast(f"reload_message {self.message.id}")


class MessageTextWidget(AutoResizingTextEdit):
    def __init__(self, messageWidget: MessageWidget):
        super().__init__()
        self.messageWidget = messageWidget
        self.setReadOnly(True)
        self.setStyleSheet("background-color: transparent;")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(messageWidget.contextMenuEvent)

        # creating a blur effect
        self.blur_effect = QGraphicsBlurEffect(blurRadius=15)

        if messageWidget.message.receiver_username == user.username and messageWidget.message.has_been_seen == False:
            self.setGraphicsEffect(self.blur_effect)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.setGraphicsEffect(None)
            if not self.messageWidget.message.has_been_seen and self.messageWidget.message.receiver_username == user.username:
                self.messageWidget.message.has_been_seen = True
                self.messageWidget.message.save()
                send_broadcast(f"reload_message {self.messageWidget.message.id}")


class RepliedWidget(AutoResizingTextEdit):
    def __init__(self, message: Message, messageWidget: MessageWidget):
        # create the replied box
        replied_message = Message.find_by_id(message.reply_to)
        replied_text = "<p direction='ltr' style='color: gray;'>" + User.find_by_username(
            replied_message.sender_username).fullname + "</p>" + \
                       "<p>" + replied_message.short_text() + "</p>"

        self.message = message
        self.messageWidget = messageWidget
        super().__init__(replied_text)

        self.setReadOnly(True)
        self.setStyleSheet(
            "background-color: transparent; margin: 3px; border: 1px solid; border-color: gray;")
        # connect right click to the context menu of parent message
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(messageWidget.contextMenuEvent)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            message_widget = messages_dict[self.message.reply_to]
            message_widget.jumpTo()


class VoiceWidget(QFrame):
    def __init__(self, message_widget):
        super().__init__()
        self.message_widget = message_widget

        self.slider = ClickSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setMinimumHeight(40)

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.slider)


class ClickSlider(QSlider):
    """A slider with a signal that emits its position when it is pressed.
    Created to get around the slider only updating when the handle is dragged, but not when a new position is clicked"""

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        # Jump to click position
        value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width())
        self.setValue(value)


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


# Step 1: Create a worker class
class Worker(QObject):
    finished = Signal()
    progress = Signal(str)

    def run(self):
        """Long-running task."""
        while True:
            self.progress.emit(receive_broadcast())
        self.finished.emit()


def actionOnBroadcast(msg: str):
    command = msg.split(" ")

    if command[0] == "reload_chat":
        if command[1] == user.username:
            print("reloading...")
            reloadChat()

    elif command[0] == "reload_message":
        message_id = int(command[1])
        if message_id in messages_dict:
            message_widget = messages_dict[message_id]
            message = message_widget.message
            if message.sender_username == user.username or message.receiver_username == user.username:
                print("reloading message...")
                message_widget.updateMessage()

    elif command[0] == "reload_user":
        user_username = command[1]
        if target_username == user_username:
            widgets.contactUserButton.updateUser()


def prepareClientThread():
    # Step 2: Create a QThread object
    widgets.thread = QThread()
    # Step 3: Create a worker object
    widgets.worker = Worker()
    # Step 4: Move worker to the thread
    widgets.worker.moveToThread(widgets.thread)
    # Step 5: Connect signals and slots
    widgets.thread.started.connect(widgets.worker.run)
    widgets.worker.finished.connect(widgets.thread.quit)
    widgets.worker.finished.connect(widgets.worker.deleteLater)
    widgets.thread.finished.connect(widgets.thread.deleteLater)
    widgets.worker.progress.connect(actionOnBroadcast)
    # Step 6: Start the thread
    widgets.thread.start()


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
