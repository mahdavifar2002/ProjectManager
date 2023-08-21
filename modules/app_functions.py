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
import multiprocessing
import os
import pathlib
import shutil
import signal
import subprocess
import threading
import time
import traceback
from typing import Optional, Dict

import jdatetime
import psutil
import win32api

# MAIN FILE
# ///////////////////////////////////////////////////////////////
from main import *
from model import conf
from model.message import Message
from model.task import Task
from model.user import User
from modules.server import send_broadcast
from modules.client import receive_broadcast, check_share

widgets: Optional[Ui_MainWindow] = None
mainWindow: Optional[MainWindow] = None
user: Optional[User] = None
messages_dict: Dict[int, QWidget] = {}
messages_dict_full: bool = False
search_messages_dict: Dict[int, QWidget] = {}
search_messages_dict_full: bool = False
target_username: Optional[str] = None
last_user_update: datetime.datetime = datetime.datetime.now()

image_me: Optional[QImage] = None
image_them: Optional[QImage] = None

audioInput: Optional[QAudioInput] = None
recorder: Optional[QMediaRecorder] = None
captureSession: Optional[QMediaCaptureSession] = None
snippingWindow = None

emojis_list = "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩" \
              "🥳😏😒😞😔😟😕🙁😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😶😱😨😰😥😓🤗" \
              "🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😮😵😵💫🤐🥴🤢🤮🤧😷🤒🤕" \
              "🤑🤠😈👿👹👺🤡👻💀👽👾🤖🎃😺😸😹😻😼😽🙀😿😾🤲👐🙌👏🤝👍👎👊" \
              "✊🤛🤜🤞🤟🤘👌🤏👈👉👆👇✋🤚🖐🖖👋🤙💪🙏"


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


def updateHomepageVisibilities():
    if user is None:
        widgets.logOutArea.hide()
        widgets.logInArea.show()
        widgets.leftMenuBg.hide()
    else:
        widgets.logInArea.hide()
        widgets.logOutArea.show()
        widgets.leftMenuBg.show()


def prepareHomePage():
    try:
        with open("userpass.txt", "r") as file:
            username, password = file.read().split('\n')
            widgets.usernameLineEdit.setText(username)
            widgets.passwordLineEdit.setText(password)
    except:
        pass

    widgets.loginPushButton.clicked.connect(lambda: loginUser(by_GUI=True))
    widgets.logoutPushButton.clicked.connect(logoutUser)

    updateHomepageVisibilities()


def logoutUser():
    global user
    global target_username

    user = None
    MainWindow.setUser(user)
    updateHomepageVisibilities()

    reloadChat(None)

    with open("userpass.txt", "w") as file:
        file.write(str(['', '']))

    widgets.loginResult.setStyleSheet("color: green;")
    widgets.loginResult.setText("You logged out successfully")


def loginUser(by_GUI=True) -> bool:
    global user

    username = widgets.usernameLineEdit.text()
    password = widgets.passwordLineEdit.text()

    try:
        logged_in_user = User.find_by_username(username)
        if logged_in_user.password == password:
            user = logged_in_user
            MainWindow.setUser(user)
            # reload_contacts_list()

            widgets.loginResult.setStyleSheet("color: green;")
            widgets.loginResult.setText("You logged in successfully")

            widgets.userImage.setPixmap(QPixmap(user.image_path))
            widgets.loggedInUsernameLineEdit.setText(user.username)
            widgets.shareLineEdit.setText(user.share)
            widgets.fullNameLineEdit.setText(user.fullname)
            updateHomepageVisibilities()

            if by_GUI:
                with open("userpass.txt", "w") as file:
                    file.write(str([username, password]))

                    new_share = (os.environ["COMPUTERNAME"]).lower()
                    if new_share != user.share:
                        def msgbtn(i):
                            if i.text() == "&Yes":
                                user.share = new_share
                                widgets.shareLineEdit.setText(user.share)
                                user.save()

                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Information)
                        msgBox.setText(f"شما از یک سیستم جدید لاگین کردید.")
                        msgBox.setInformativeText("آیا مایلید share اکانت شما این سیستم باشد؟")
                        msgBox.setWindowTitle("سیستم جدید")
                        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        msgBox.buttonClicked.connect(msgbtn)
                        msgBox.exec()

            return True
        else:
            widgets.loginResult.setStyleSheet("color: red;")
            widgets.loginResult.setText("Wrong password")
            return False
    except Exception as e:
        print(traceback.format_exc())
        widgets.loginResult.setStyleSheet("color: red;")
        widgets.loginResult.setText("Wrong username")
        return False


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


class MessengerTextEdit(AutoResizingTextEdit):
    def __init__(self, parent):
        self.old_keyboard_layout = '00000429'
        super().__init__(parent)
        self.setMinimumLines(3)

    def focusInEvent(self, e):
        self.old_keyboard_layout = win32api.GetKeyboardLayout()
        win32api.LoadKeyboardLayout('00000429', 1)
        super().focusInEvent(e)

    def focusOutEvent(self, e):
        # Stay Persian
        if self.old_keyboard_layout == 0x4290429:
            win32api.LoadKeyboardLayout('00000429', 1)
        # back to English
        if self.old_keyboard_layout == 0x4090409:
            win32api.LoadKeyboardLayout('00000409', 1)

            # win32api.LoadKeyboardLayout(self.old_keyboard_layout, 1)
        super().focusOutEvent(e)


def prepareMessengerPage():
    new_text_edit = MessengerTextEdit(widgets.chatTextBox)
    new_text_edit.setStyleSheet(widgets.messengerTextEdit.styleSheet())
    new_text_edit.textChanged.connect(messenger_text_changed)
    widgets.chatTextBoxVerticalLayout.replaceWidget(widgets.messengerTextEdit, new_text_edit)
    widgets.messengerTextEdit.deleteLater()
    widgets.messengerTextEdit = new_text_edit

    # reload_contacts_list()

    # Prepare send button
    widgets.chatSendButton.clicked.connect(sendMessage)

    # Prepare record button
    widgets.recordButton.setProperty("voice_path", "")
    widgets.recordButton.clicked.connect(recordMessage)

    QShortcut(QKeySequence("Ctrl+Return"),
              widgets.messengerTextEdit,
              sendMessage)

    # Prepare snipping button
    widgets.snippingButton.clicked.connect(snippingTool)
    widgets.snippingButton.setToolTip("screenshot")

    # Prepare emoji button
    widgets.emojiButton.clicked.connect(mainWindow.openCloseRightBox)

    # Prepare search button
    widgets.searchPushButton.clicked.connect(lambda: (widgets.searchLineEdit.setText(""),
                                                      reload_contacts_list(widgets.searchLineEdit.text())))

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

    # Prepare handling scroll to top to fetch new messages
    widgets.chatScrollArea.verticalScrollBar().actionTriggered.connect(on_chat_scroll)
    # Prepare handling scroll to top to fetch new search messages
    widgets.contactsScrollArea.verticalScrollBar().actionTriggered.connect(on_search_scroll)

    # # Prepare 'load more messages' button
    # widgets.loadMoreButton.clicked.connect(fetch_ten_messages)

    # Prepare drag and drop of image
    prepareDragAndDrop()

    # # Overlapping contact
    # child = widgets.chatPageGridLayout.removeWidget(widgets.chatScrollArea)
    # widgets.chatPageGridLayout.addWidget(widgets.chatScrollArea, 0, 0)
    # widgets.chatScrollArea.stackUnder(widgets.contactInfoBox)

    # # Overlapping toEnd button
    # widgets.chatPageGridLayout.removeWidget(widgets.toEndVerticalWidget)
    # widgets.chatPageGridLayout.addWidget(widgets.toEndVerticalWidget, 1, 0)
    # widgets.chatScrollArea.stackUnder(widgets.toEndVerticalWidget)
    # widgets.chatPageGridLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
    # widgets.toEndVerticalWidget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    # widgets.toEndPushButton.clicked.connect(scroll_to_end_of_chat)
    widgets.toEndVerticalWidget.hide()


def resize_emoji(emoji):
    return f"<span style='font-size: 20px;'>{emoji}</span>"


def reload_stickers():
    # Prepare emojis buttons
    emojiButtons = []

    for i, item in enumerate(emojis_list):
        emojiButton = QPushButton(emojis_list[i])
        emojiButton.setStyleSheet("font: 14pt; text-align: center; border: 0;")
        widgets.emojisGridLayout.addWidget(emojiButton, i / 4 + 1, i % 4)
        emojiButtons.append(emojiButton)

    mainWindow.connectEmojiButtons(emojiButtons)

    # Prepare stickers buttons
    stickerButtons = []

    stickers_directory = f"\\\\alireza\\E\\Works Manager\\Messenger\\resources\\stickers"
    files = pathlib.Path(stickers_directory).glob('*')
    for i, sticker_file in enumerate(files):
        sticker_path = str(sticker_file)
        if sticker_path[-3:] in ['jpg', 'png']:
            stickerButton = QPushButton()
            stickerButton.setIcon(QIcon(sticker_path))
            stickerButton.setIconSize(QSize(40, 40))
            stickerButton.setProperty("sticker_path", sticker_path)
            stickerButton.setStyleSheet("border: 0;")
            widgets.stickersGridLayout.addWidget(stickerButton, i / 3 + 1, i % 3)
            stickerButtons.append(stickerButton)

    mainWindow.connectStickerButtons(stickerButtons)


def prepareDragAndDrop():
    widgets.chatPage.setProperty("file_path", "")

    widgets.chatPage.setAcceptDrops(True)
    widgets.chatPage.dragEnterEvent = customDragEnterEvent
    widgets.chatPage.dragLeaveEvent = customDragLeaveEvent
    widgets.chatPage.dropEvent = customDropEvent

    widgets.messengerTextEdit.dragEnterEvent = customDragEnterEvent
    widgets.messengerTextEdit.dragLeaveEvent = customDragLeaveEvent
    widgets.messengerTextEdit.dropEvent = customDropEvent


chatPage_blur_effect = None


def customDragEnterEvent(event):
    global chatPage_blur_effect
    chatPage_blur_effect = QGraphicsBlurEffect(blurRadius=15)
    widgets.chatPage.setGraphicsEffect(chatPage_blur_effect)
    event.accept()


def customDragLeaveEvent(event):
    global chatPage_blur_effect
    chatPage_blur_effect = None
    widgets.chatPage.setGraphicsEffect(None)
    widgets.chatPage.setStyleSheet("")
    event.accept()


def customDropEvent(event: QDropEvent):
    chatPage_blur_effect = None
    widgets.chatPage.setGraphicsEffect(None)
    widgets.chatPage.setStyleSheet("")

    # ask for link or copy
    menu = QMenu(widgets.chatPage)
    menu.move(QCursor.pos())
    menu.addAction("Link")
    menu.addAction("Copy")

    user_action = menu.exec()

    if event.mimeData().hasUrls():
        for raw_url in event.mimeData().urls():
            url = raw_url.toLocalFile()

            # convert local link to share link
            url = url_local_to_share(url)
            widgets.chatPage.setProperty("file_path", url)

            if user_action is not None:
                if user_action.text() == "Link":
                    widgets.chatPage.setProperty("file_copy", False)
                elif user_action.text() == "Copy":
                    widgets.chatPage.setProperty("file_copy", True)

                # send url
                widgets.messengerTextEdit.setFocus()
                sendMessage(force_send=True)

        event.accept()
    else:
        event.ignore()


def url_local_to_share(url):
    if url[0:2] != "//":
        url = "//" + user.share + "/" + url
    url = url.replace(":", "").replace("/", "\\")
    return url


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


def reload_contacts_list(search=None):
    global search_messages_dict
    global search_messages_dict_full

    clearLayout(widgets.contactsVerticalLayout)
    search_messages_dict.clear()
    search_messages_dict_full = False

    if search is None or search == "":
        users = User.users()
        user_buttons = [None for _ in range(len(users))]

        for i, other_user in enumerate(users):
            # if user is not None:
            #     user_buttons[i] = ContactButton(other_user, user.last_message(other_user.username))
            # else:
            user_buttons[i] = ContactButton(other_user, None)
            widgets.contactsVerticalLayout.addWidget(user_buttons[i])

        mainWindow.connectContactButtons(user_buttons)

    else:
        fetch_ten_search_messages(search)

    widgets.contactsVerticalLayout.addStretch()


def fetch_ten_search_messages(search):
    if search is None or search == "":
        return

    before_id = min(search_messages_dict, default=2147483647)

    messages = user.ten_search_messages(search, before_id)
    users = [user.find_by_username(
        message.sender_username if message.sender_username != user.username else message.receiver_username)
        for message in messages]
    user_buttons = [None for _ in range(len(users))]
    for i, other_user in enumerate(users):
        user_buttons[i] = ContactButton(other_user, messages[i])
        widgets.contactsVerticalLayout.addWidget(user_buttons[i])
        search_messages_dict[messages[i].id] = user_buttons[i]

    mainWindow.connectContactButtons(user_buttons)

    return len(user_buttons)


class ContactButton(QPushButton):
    def __init__(self, other_user, selected_message, top=False):
        super().__init__()
        self.user = other_user
        self.selected_message = selected_message
        self.selected_message_id = selected_message.id if selected_message is not None else None

        self.setToolTip(self.user.username)
        self.setIcon(QIcon(other_user.image_path))
        if top:
            if not check_share(other_user.share):
                self.setIcon(QIcon(other_user.offline_image_path()))
            self.mouseMoveEvent = widgets.titleRightInfo.mouseMoveEvent
            self.mousePressEvent = widgets.titleRightInfo.mousePressEvent
            self.setIconSize(QSize(35, 35))
            self.setMinimumHeight(45)
        else:
            self.setIconSize(QSize(45, 45))
            self.setMinimumHeight(60)
        self.setStyleSheet("text-align: left; border: none; padding: 7px;")

        # Prepare user_button text (username + last message, if any)
        self.updateUser()

    def updateUser(self):
        conf.session.commit()
        self.user = User.find_by_username(self.user.username)

        text = "   " + self.user.fullname + "   " + "\n"

        if (user is not None) and self.user.is_typing_for(user.username):
            text += "...is typing"

            # Create timer object
            timer = QTimer(self)
            timer.timeout.connect(self.updateUser)
            timer.setSingleShot(True)
            timer.start(3000)

        # if user is not None and message is None:
        #     message = user.last_message(other_user.username)

        elif self.selected_message is not None:
            text += self.selected_message.short_text()

        # else:
        #     text += self.user.get_last_seen()

        self.setText(text)


def watch_copy_file(message: Message):
    file_size = FileWidget.fileSize(message.file_path)

    while file_size != message.file_size:
        sleep(0.3)
        file_size = FileWidget.fileSize(message.file_path)
        send_broadcast(f"reload_message {message.id}")
        if not psutil.pid_exists(message.copy_pid):
            break

    send_broadcast(f"reload_message {message.id}")


def forwardMessage(forward_message_id, forward_username):
    message = Message.find_by_id(forward_message_id)
    clone_message = conf.clone_model(message)
    # clone_message.text = f"<p style='color: gray; white-space:pre;'>[بازارسال‌شده از {message.sender_username}]</p>" + clone_message.text
    # clone_message.text = clone_message.text.strip()
    clone_message.sender_username = user.username
    clone_message.receiver_username = forward_username
    clone_message.time_created = conf.db_time()
    clone_message.has_been_seen = False

    def msgbtn(i):
        if i.text() == "&Yes":
            clone_message.save()
            send_broadcast(f"new_message {clone_message.receiver_username} {user.username} {clone_message.id}")

            # Open window of the person whom a message is forwarded to (if it's not open already)
            try:
                windowName = "Message " + forward_username
                ID = win32gui.FindWindowEx(None, None, None, windowName)
                assert ID != 0

            except Exception as e:
                subprocess.Popen(["pythonw",
                                  "E:\\Works Manager\\Messenger\\main.py",
                                  user.username,
                                  user.password,
                                  forward_username],
                                 cwd="E:\\Works Manager\\Messenger")

            # Make the window foreground
            try:
                time.sleep(1)
                windowName = "Message " + forward_username
                ID = win32gui.FindWindowEx(None, None, None, windowName)
                assert ID != 0
                result = win32gui.FlashWindow(ID, True)
                result = win32gui.SetForegroundWindow(ID)

            except Exception as e:
                pass
            # subprocess.Popen(["pythonw",
            #                   "E:\\Works Manager\\Messenger\\main.py",
            #                   user.username,
            #                   user.password,
            #                   forward_username],
            #                  cwd="E:\\Works Manager\\Messenger")

    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"Forwarding to {forward_username}")
    msgBox.setInformativeText("Are you sure?")
    msgBox.setWindowTitle("Send to...")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.buttonClicked.connect(msgbtn)
    msgBox.exec()


def sendMessage(force_send=False):
    if not force_send and \
            not widgets.messengerTextEdit.hasFocus() \
            and not widgets.chatSendButton.hasFocus() \
            and not widgets.recordButton.hasFocus():
        return

    sender = user.username
    receiver = target_username
    text = widgets.messengerTextEdit.toPlainText()
    voice_path = widgets.recordButton.property("voice_path")
    widgets.recordButton.setProperty("voice_path", "")
    sticker_path = widgets.stickersGridLayout.property("sticker_path")
    widgets.stickersGridLayout.setProperty("sticker_path", "")
    file_path = widgets.chatPage.property("file_path")
    widgets.chatPage.setProperty("file_path", "")
    file_copy = widgets.chatPage.property("file_copy")
    widgets.chatPage.setProperty("file_copy", False)
    file_size = 0
    file_is_dir = False
    if QFile.exists(file_path):
        file_size = FileWidget.fileSize(file_path)
    if os.path.isdir(file_path):
        file_is_dir = True

    if QFile.exists(sticker_path):
        text = f'<center><img height="150" src="{sticker_path}"></center>'

    if len(text) > 0 or QFile.exists(voice_path) or QFile.exists(file_path):
        # copy, if asked
        if file_copy:
            source_file_path = file_path
            file_name = file_path.split("\\")[-1]
            folder_name = datetime.datetime.now().strftime('%A') + '      '
            folder_name += str(jdatetime.datetime.now().isoformat(' ', 'seconds')).replace(':', '.').replace(' ',
                                                                                                             '      ')
            works_manager_dir = "\\\\" + User.find_by_username(target_username).share + "\\e\\Works Manager"

            if not os.path.exists(works_manager_dir):
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText(f"Cannot copy")
                msgBox.setInformativeText("سیستم مقابل خاموش است یا شما دسترسی کپی به آن سیستم را ندارید.")
                msgBox.setWindowTitle("Copy failed")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec()
                return

            file_dir = works_manager_dir + "\\Attach\\" + folder_name
            file_path = f"{file_dir}\\{file_name}"

            if not os.path.exists(file_dir):
                try:
                    os.makedirs(file_dir)
                except:
                    pass

            if file_is_dir:
                copy_process = multiprocessing.Process(target=shutil.copytree, args=(source_file_path, file_path))
            else:
                copy_process = multiprocessing.Process(target=shutil.copy, args=(source_file_path, file_path))
            copy_process.start()
            copy_pid = copy_process.pid
        else:
            copy_pid = 0

        # resize emojis
        for emoji in emojis_list:
            text = text.replace(emoji, resize_emoji(emoji))

        # send new message
        if widgets.editFrame.isHidden():
            reply_to = None if widgets.replyFrame.isHidden() else int(widgets.replyLabel.toolTip())
            message = Message(sender_username=sender, receiver_username=receiver, text=text, reply_to=reply_to,
                              voice_path=voice_path, file_path=file_path, file_size=file_size, file_copy=file_copy,
                              copy_pid=copy_pid, file_is_dir=file_is_dir)
            message.save()
            newMessage(message.id)
            send_broadcast(f"new_message {receiver} {user.username} {message.id}")

            if file_copy:
                thread = threading.Thread(target=watch_copy_file, args=(message,))
                thread.start()

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


def snippingTool():
    global snippingWindow
    snippingWindow = SnippingWidget()
    snippingWindow.show()


class SnippingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping ")
        self.begin = QPoint()
        self.end = QPoint()

        self.setWindowOpacity(0.3)

        self.setCursor(QCursor(Qt.CrossCursor))
        self.setWindowFlags(Qt.FramelessWindowHint)
        print("Capture the screen...")

        self.showFullScreen()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(QPen(QColor("black"), 3))
        qp.setBrush(QColor(128, 128, 255, 128))
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.begin = event.globalPosition().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.end = event.globalPosition().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()
        QTimer.singleShot(1000, self.screenshot)

    def screenshot(self):
        print("screenshot")
        screen = QGuiApplication.primaryScreen()
        window = self.windowHandle()
        if window is not None:
            screen = window.screen()
        if screen is None:
            print("failed")
            return

        original_pixmap = screen.grabWindow(0)
        output_pixmap = original_pixmap.copy(
            QRect(self.begin, self.end).normalized()
        )

        def msgbtn(i):
            print(i.text())
            if i.text() == "OK":
                filename = conf.generate_filename(user.username, "png", prefix="Screenshot ")
                filepath = str(
                    pathlib.Path(QDir.toNativeSeparators("//alireza/E/Works Manager/Screenshots")) / filename)
                output_pixmap.save(filepath)

                # self.label = QLabel(pixmap=output_pixmap)
                # self.label.show()

                widgets.chatPage.setProperty("file_path", filepath)
                widgets.chatPage.setProperty("file_copy", False)

                # send url
                widgets.messengerTextEdit.setFocus()
                sendMessage(force_send=True)

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Screenshot")
        # msgBox.setText(f"Sending Screenshot")
        # msgBox.setInformativeText("Are you sure?")
        msgBox.setIconPixmap(output_pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.buttonClicked.connect(msgbtn)
        msgBox.exec()


def recordMessage():
    global user
    global recorder
    global audioInput
    global captureSession

    if widgets.recordButton.toolTip() == "record":
        captureSession = QMediaCaptureSession()
        audioInput = QAudioInput()
        captureSession.setAudioInput(audioInput)
        recorder = QMediaRecorder()
        captureSession.setRecorder(recorder)
        recorder.setMediaFormat(QMediaFormat.FileFormat.MP3)
        recorder.setQuality(QMediaRecorder.Quality.HighQuality)
        filename = conf.generate_filename(user.username, "mp3")
        filepath = pathlib.Path(QDir.toNativeSeparators("//alireza/E/Works Manager/Voices")) / filename
        widgets.recordButton.setProperty("voice_path", str(filepath))
        url = QUrl.fromLocalFile(os.fspath(filepath))
        recorder.setOutputLocation(url)
        recorder.record()

        widgets.recordButton.setIcon(QIcon("./images/icons/cil-media-stop.png"))
        widgets.recordButton.setToolTip("stop")

    else:
        recorder.stop()
        sendMessage()

        widgets.recordButton.setIcon(QIcon("./images/icons/cil-microphone.png"))
        widgets.recordButton.setToolTip("record")


def newMessage(message_id: int):
    global target_username
    global messages_dict

    message = Message.find_by_id(message_id)
    addMessageWidget(message)

    scroll_to_end_of_chat()


def scroll_to_end_of_chat():
    for i in range(2):
        QCoreApplication.processEvents()
        widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())


def reloadChat(new_target, message_id=None):
    global target_username
    global messages_dict
    global messages_dict_full
    global image_me
    global image_them

    # Load image of me and them
    try:
        image_me = QImage(user.image_path).scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_them = QImage(User.find_by_username(new_target).image_path).scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    except:
        pass

    if new_target == target_username:
        if message_id is not None:
            # scroll to selected message
            while message_id not in messages_dict:
                if not fetch_ten_messages(load_all=False):
                    break
            scroll_to_message_id(message_id)
        return

    target_username = new_target

    # Clear chatbox
    clearLayout(widgets.chatGridLayout)
    clearLayout(widgets.contactInfoHorizontalLayout)
    clearLayout(widgets.leftBoxHorizontalLayout)
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
    user_button = ContactButton(target_user, None, top=True)
    widgets.contactUserButton = user_button
    widgets.leftBoxHorizontalLayout.addWidget(user_button, 1)

    # Messages
    messages_dict.clear()
    messages_dict_full = False

    fetch_ten_messages(load_all=False)

    #  scroll to the end of chat
    if message_id is None:
        for i in range(2):
            QCoreApplication.processEvents()
            widgets.chatScrollArea.verticalScrollBar().setValue(widgets.chatScrollArea.verticalScrollBar().maximum())
    else:
        # scroll to selected message
        while message_id not in messages_dict:
            if not fetch_ten_messages(load_all=False):
                break
        scroll_to_message_id(message_id)

    # Set window name
    mainWindow.title = "Message " + target_username
    mainWindow.setWindowTitle(mainWindow.title)

    # # check seen messages
    # on_chat_scroll()


def scroll_to_message_id(message_id, focus=True):
    global messages_dict

    message_widget = messages_dict[message_id]
    for i in range(2):
        QCoreApplication.processEvents()
        widgets.chatScrollArea.ensureWidgetVisible(message_widget)

    if focus:
        message_widget.setFocus()


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

    for _, message in enumerate(messages):
        addMessageWidget(message)

    return len(messages)


def addMessageWidget(message: Message):
    global user
    global messages_dict

    if message.id in messages_dict:
        return

    is_sender = (message.sender_username == user.username)
    message_widget = MessageWidget(message, widgets)
    widgets.chatGridLayout.addWidget(message_widget, 1 + message.id, is_sender, 1, 4)
    # Fill the message dictionary
    messages_dict[message.id] = message_widget
    # check for pin
    if message.pinned:
        message_widget.pinMessage()


def on_search_scroll():
    global search_messages_dict
    global search_messages_dict_full

    if not search_messages_dict_full:
        if widgets.contactsScrollArea.verticalScrollBar().value() == widgets.contactsScrollArea.verticalScrollBar().maximum():
            if fetch_ten_search_messages(widgets.searchLineEdit.text()):
                QApplication.processEvents()
            else:
                search_messages_dict_full = True


def on_chat_scroll():
    global messages_dict
    global messages_dict_full

    if not messages_dict_full:
        if widgets.chatScrollArea.verticalScrollBar().value() == widgets.chatScrollArea.verticalScrollBar().minimum():
            topmost_message_id = min(messages_dict)
            if fetch_ten_messages():
                scroll_to_message_id(topmost_message_id, focus=False)
            else:
                messages_dict_full = True

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

        is_sender = (message.sender_username == user.username)
        self.setObjectName("from-me" if is_sender else "from-them")

        self.message_core = MessageCoreWidget(self)
        self.updateMessage()

        message_hbox = QHBoxLayout()
        message_hbox.setContentsMargins(0, 0, 0, 0)
        message_hbox.setSpacing(0)
        self.setLayout(message_hbox)

        if is_sender:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            message_hbox.setAlignment(Qt.AlignmentFlag.AlignRight)


        self.sender_image = QLabel()

        self.sender_image.setPixmap(QPixmap(image_me if is_sender else image_them))
        message_hbox.addWidget(self.sender_image)
        self.sender_image.setObjectName("image-me" if is_sender else "image-them")

        message_vbox_widget = QWidget()
        message_vbox_widget.setStyleSheet("background-color: transparent;")
        message_vbox = QVBoxLayout()
        message_vbox_widget.setLayout(message_vbox)
        message_hbox.addWidget(message_vbox_widget)

        if message.reply_to is not None:
            replied_widget = RepliedWidget(message, self)
            message_vbox.addWidget(replied_widget)

        message_vbox.addWidget(self.message_core)

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
            if self.message_core.graphicsEffect() is not None:
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
            main_text = "<p style='white-space: pre-wrap;'>" + self.message.text.replace("\n", "<br/>") + "</p>"
            seen_text = "✅ " if is_sender and self.message.has_been_seen else ""
            pin_text = "📌 " if self.message.pinned else ""
            edit_text = "<p dir='ltr' style='color: gray; white-space:pre;'> (ویرایش‌شده) </p>" if self.message.has_been_edited else ""
            date_label_text = "<p dir='ltr' style='color: gray; white-space:pre;'>" + seen_text + pin_text + self.message.get_time_created() + "</p>"
            self.message_core.text_edit.setHtml(main_text)
            self.message_core.edit_label.setText(edit_text)
            self.message_core.date_label.setText(date_label_text)

            # Set tooltip of edit time
            if edit_text == "":
                self.message_core.edit_label.hide()
            else:
                self.message_core.edit_label.setToolTip("Edited at   " + self.message.get_time_updated())
            # Set tooltip of seen time
            if is_sender and self.message.has_been_seen and self.message.time_seen is not None:
                self.message_core.date_label.setToolTip("Seen at   " + self.message.get_time_seen())

            # Update file size
            if self.message_core.file_widget is not None:
                self.message_core.file_widget.updateFileSize()

    def contextMenuEvent(self, event):
        # don't show context menu if message is blur (unseen)
        if self.message_core.isBlur:
            return

        self.menu = QMenu(self)
        self.menu.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        if self.message.file_path is not None and len(self.message.file_path) > 0:
            # show in folder
            replyAction = QAction('Show in Folder', self)
            replyAction.triggered.connect(lambda: self.openFolder(event))
            self.menu.addAction(replyAction)

        # reply
        replyAction = QAction('Reply', self)
        replyAction.triggered.connect(lambda: self.replySlot(event))
        self.menu.addAction(replyAction)

        # pin
        pinAction = QAction('Pin / Unpin', self)
        pinAction.triggered.connect(lambda: self.pinSlot(event))
        self.menu.addAction(pinAction)

        # copy
        copyAction = QAction('Copy', self)
        copyAction.triggered.connect(lambda: self.copySlot(event))
        self.menu.addAction(copyAction)

        # edit
        if self.message.sender_username == user.username:
            editAction = QAction('Edit', self)
            editAction.triggered.connect(lambda: self.editSlot(event))
            self.menu.addAction(editAction)

            editAction = QAction('Delete', self)
            editAction.triggered.connect(lambda: self.deleteSlot(event))
            self.menu.addAction(editAction)

        # send to other user
        self.sendTo = self.menu.addMenu("Send to...")

        sendToUserActions = []
        for i, target_user in enumerate(User.users()):
            sendToUserAction = QAction(target_user.fullname, self)
            sendToUserAction.setProperty("username", target_user.username)
            sendToUserAction.setProperty("message_id", self.message.id)
            sendToUserActions.append(sendToUserAction)
            self.sendTo.addAction(sendToUserAction)

        mainWindow.connectSendToActions(sendToUserActions)

        # add other required actions
        self.menu.popup(QCursor.pos())

    def openFolder(self, event):
        subprocess.Popen(f'explorer /select, "{self.message.file_path}"')

    def replySlot(self, event):
        widgets.replyLabel.setText(self.message.short_text())
        widgets.replyLabel.setToolTip(str(self.message.id))
        if self.message_core.graphicsEffect() is not None:
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

    def copySlot(self, event):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.message_core.text_edit.toPlainText(), mode=cb.Clipboard)

    def editSlot(self, event):
        widgets.editLabel.setText(self.message.short_text())
        widgets.editLabel.setToolTip(str(self.message.id))

        text = self.message.text
        # remove emojis resize tag
        for emoji in emojis_list:
            text = text.replace(resize_emoji(emoji), emoji)

        editor = widgets.messengerTextEdit
        editor.setHtml(text)

        textCursor = editor.textCursor()
        textCursor.setPosition(len(editor.toPlainText()))
        editor.setTextCursor(textCursor)

        widgets.replyFrame.hide()
        widgets.editFrame.show()
        widgets.messengerTextEdit.setFocus()

    def deleteSlot(self, event):
        def msgbtn(i):
            if i.text() == "&Yes":
                self.deleteMessage()

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(f"Deleting message")
        msgBox.setInformativeText("Are you sure?")
        msgBox.setWindowTitle("Delete")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.buttonClicked.connect(msgbtn)
        msgBox.exec()

    def deleteMessage(self):
        self.message.deleted = True
        self.message.pinned = False
        self.message.save()
        send_broadcast(f"reload_message {self.message.id}")


class MessageCoreWidget(QFrame):
    def __init__(self, messageWidget: MessageWidget):
        super().__init__()
        self.messageWidget = messageWidget
        self.text_edit = MessageTextWidget(messageWidget)
        self.edit_label = QLabel()
        self.date_label = QLabel()

        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        if messageWidget.message.voice_path is not None and QFile.exists(messageWidget.message.voice_path):
            self.voice_widget = VoiceWidget(messageWidget)
            self.layout().addWidget(self.voice_widget)

        self.file_widget = None

        if messageWidget.message.file_path is not None and len(self.messageWidget.message.file_path) > 0:
            self.file_widget = FileWidget(messageWidget)
            self.layout().addWidget(self.file_widget)

        self.layout().addWidget(self.text_edit)
        self.layout().addWidget(self.edit_label)
        self.layout().addWidget(self.date_label)

        # creating a blur effect
        self.blur_effect = QGraphicsBlurEffect(blurRadius=15)

        self.isBlur = False

        if messageWidget.message.receiver_username == user.username \
                and messageWidget.message.sender_username != user.username \
                and messageWidget.message.has_been_seen == False:
            self.isBlur = True
            self.setGraphicsEffect(self.blur_effect)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.isBlur = False
            self.setGraphicsEffect(None)
            if not self.messageWidget.message.has_been_seen and self.messageWidget.message.receiver_username == user.username:
                self.messageWidget.message.has_been_seen = True
                self.messageWidget.message.time_seen = conf.func.now()
                self.messageWidget.message.save()
                send_broadcast(f"reload_message {self.messageWidget.message.id}")


class MessageTextWidget(AutoResizingTextEdit):
    def __init__(self, messageWidget: MessageWidget):
        super().__init__()
        self.messageWidget = messageWidget
        self.setReadOnly(True)
        self.setStyleSheet("background-color: transparent;")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(messageWidget.contextMenuEvent)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton and self.parent().isBlur:
            self.parent().mousePressEvent(e)
        else:
            super().mousePressEvent(e)


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

        self.is_playing = False
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        self.fileName = self.message_widget.message.voice_path
        self.player.setSource(QUrl(self.fileName))
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.mediaStatusChanged.connect(self.media_status_changed)

        self.playPauseButton = QPushButton(self)
        self.playPauseButton.setIconSize(QSize(16, 16))
        self.playPauseButton.setStyleSheet("background-color: transparent;")
        self.playPauseButton.clicked.connect(self.play_music)

        self.slider = ClickSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.slider_changed)

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(10)
        self.setLayout(self.hbox)
        self.hbox.addWidget(self.playPauseButton)

        # self.timeLabel = QLabel("00:00:00")
        self.timeLabel = QLabel(self.position_to_time_str(self.player.duration()))
        self.timeLabel.setStyleSheet("color: gray;")

        self.voiceFrame = QFrame()
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.voiceFrame.setLayout(self.vbox)
        self.vbox.addWidget(self.slider)
        self.vbox.addWidget(self.timeLabel)

        self.hbox.addWidget(self.voiceFrame)

        self.pause()

    def pause(self):
        self.is_playing = False
        self.playPauseButton.setIcon(QIcon("./images/icons/cil-media-play.png"))
        self.player.pause()

    def play(self):
        self.is_playing = True
        self.playPauseButton.setIcon(QIcon("./images/icons/cil-media-pause.png"))
        self.player.play()

    def play_music(self):
        # if self.player.mediaStatus == QMediaPlayer.PlaybackState.PlayingState:
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def slider_changed(self, position_):
        self.player.setPosition(position_)

    def position_changed(self, position_):
        if self.slider.maximum() != self.player.duration():
            self.slider.setMaximum(self.player.duration())

        self.slider.setValue(position_)

        label = self.position_to_time_str(self.player.duration())
        if position_ != 0:
            label = self.position_to_time_str(position_) + " / " + label

        self.timeLabel.setText(label)

    def position_to_time_str(self, position_):
        seconds = (position_ / 1_000) % 60
        minutes = (position_ / 60_000) % 60
        hours = (position_ / 3_600_000)
        time = QTime(hours, minutes, seconds)
        time_str = time.toString()

        # remove 00: from beginning, if voice is below 1 hour
        if hours < 1:
            time_str = time_str[3:]

        return time_str

    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.playPauseButton.click()

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)


def short_text(text, length=20):
    the_text = text.replace("\n", " ")
    if len(the_text) > length:
        the_text = the_text[:length] + "..."
    return the_text


class VerticalLabel(QLabel):

    def __init__(self, *args):
        QLabel.__init__(self, *args)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(0, self.height())
        painter.rotate(-90)
        # calculate the size of the font
        fm = QFontMetrics(painter.font())
        xoffset = int(fm.boundingRect(self.text()).width() / 2)
        yoffset = int(fm.boundingRect(self.text()).height() / 2) - 5
        x = int(self.width() / 2) + yoffset
        y = int(self.height() / 2) - xoffset
        # because we rotated the label, x affects the vertical placement, and y affects the horizontal
        painter.drawText(y, x, self.text())
        painter.end()

    def minimumSizeHint(self):
        size = QLabel.minimumSizeHint(self)
        return QSize(size.height(), size.width())

    def sizeHint(self):
        size = QLabel.sizeHint(self)
        return QSize(size.height(), size.width())


class FileWidget(QFrame):
    def __init__(self, message_widget):
        super().__init__()
        self.message_widget = message_widget
        self.file_path = self.message_widget.message.file_path
        self.file_size = self.message_widget.message.file_size
        self.file_copy = self.message_widget.message.file_copy
        self.copy_pid = self.message_widget.message.copy_pid
        self.file_is_dir = self.message_widget.message.file_is_dir
        self.is_sender = (self.message_widget.message.sender_username == user.username)

        # preview file if it's an image
        self.is_image = (QImageReader.imageFormat(self.file_path) != '')
        if self.is_image:
            self.setToolTip(f'<img height="200"'
                            f'src="{self.file_path}">')
        else:
            self.setToolTip(self.file_path)

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(5)
        self.setLayout(self.hbox)

        self.type_label = VerticalLabel("COPY" if self.file_copy else "LINK")
        is_sender = (self.message_widget.message.sender_username == user.username)
        self.type_label.setObjectName("file-from-" + ("me" if is_sender else "them"))
        if is_sender:
            self.type_label.setStyleSheet("border-right: 2px solid hsl(270, 30%, 15%);")
        else: # 'hsl(270, 30%, 25%)'};")
            self.type_label.setStyleSheet("border-left: 2px solid hsl(270, 30%, 25%);")

        self.hbox.addWidget(self.type_label)

        self.fileButton = QPushButton(self)
        self.set_icon()
        self.fileButton.setStyleSheet("font: 35px; background-color: transparent;")
        if self.file_copy and psutil.pid_exists(self.copy_pid):
            self.fileButton.clicked.connect(self.cancel_copy)
        self.hbox.addWidget(self.fileButton)

        self.info = QFileInfo(self.file_path)
        self.fileNameLabel = QLabel(short_text(self.info.fileName(), length=20))
        self.fileNameLabel.setStyleSheet("font-weight: bold;")
        self.fileSizeLabel = QLabel(self.pretty_size(self.info.size()))
        self.fileSizeLabel.setStyleSheet("color: gray;")

        # # preview middle frame if file is a video
        # elif self.file_path[-3:] in ["mov", "mp4", "avi", "mpg"]: # player.hasVideo():
        #
        #     # create thumbnail of video, if not created already
        #     thumbnail_path = f"{self.file_path}.png"
        #     try:
        #         if not QFile.exists(thumbnail_path):
        #             image = self.thumbnail(self.file_path)
        #             image.save(thumbnail_path, "png", 10)
        #
        #         # show thumbnail as tooltip
        #         self.setToolTip(f'<img height="200"'
        #                         f'src="{self.file_path}.png">')
        #     except Exception as e:
        #         print(e)

        self.infoFrame = QFrame()
        self.infoFrame.mousePressEvent = self.myMousePressEvent
        self.infoFrame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.infoFrame.setLayout(self.vbox)
        self.vbox.addStretch()
        self.vbox.addWidget(self.fileNameLabel)
        self.vbox.addWidget(self.fileSizeLabel)
        self.vbox.addStretch()

        if is_sender:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

            self.infoFrame.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.vbox.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.fileNameLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.fileSizeLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.hbox.addWidget(self.infoFrame)
        self.hbox.addStretch()

    def extension(self):
        try:
            return self.file_path.split('.')[-1]
        except:
            return ''

    def set_icon(self):
        self.fileButton.setText("")
        self.fileButton.setIconSize(QSize(40, 40))
        extension = self.extension().lower()

        if self.file_is_dir:
            # self.fileButton.setText("📂")
            self.fileButton.setIcon(QIcon("./resources/icons/folder.png"))
        elif self.is_image or extension in ["jpg", "png", "bmp", "gif", "tiff", "webp", "svg", "ico", "jpeg"]:
            self.fileButton.setIcon(QIcon("./resources/icons/image.png"))
        elif extension in ["mp4", "mov", "avi", "wmv", "mkv", "flv", "webm", "m4v", "mpeg", "3gp"]:
            self.fileButton.setIcon(QIcon("./resources/icons/video.png"))
        elif extension in ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "ape", "alac", "aiff"]:
            self.fileButton.setIcon(QIcon("./resources/icons/audio.png"))
        elif extension in ["ma", "mb"]:
            self.fileButton.setIcon(QIcon("./resources/icons/maya.png"))
        elif extension in ["obj"]:
            self.fileButton.setIcon(QIcon("./resources/icons/obj.png"))
        elif extension in ["fbx"]:
            self.fileButton.setIcon(QIcon("./resources/icons/fbx.png"))
        elif extension in ["abc"]:
            self.fileButton.setIcon(QIcon("./resources/icons/abc.png"))
        elif extension in ["pdf"]:
            self.fileButton.setIcon(QIcon("./resources/icons/pdf.png"))
        elif extension in ["html", "htm"]:
            self.fileButton.setIcon(QIcon("./resources/icons/internet.png"))
        elif extension in ["txt"]:
            self.fileButton.setIcon(QIcon("./resources/icons/txt.png"))
        elif extension in ["exr"]:
            self.fileButton.setIcon(QIcon("./resources/icons/exr.png"))
        elif extension in ["docx", "doc"]:
            self.fileButton.setIcon(QIcon("./resources/icons/word.png"))
        elif extension in ["xlsx", "xls", "xlsm"]:
            self.fileButton.setIcon(QIcon("./resources/icons/excel.png"))
        elif extension in ["pptx", "pptm", "ppt"]:
            self.fileButton.setIcon(QIcon("./resources/icons/powerpoint.png"))
        elif extension in ["zip", "rar"]:
            self.fileButton.setIcon(QIcon("./resources/icons/archive.png"))
        elif extension in ["psd", "psb"]:
            self.fileButton.setIcon(QIcon("./resources/icons/photoshop.png"))
        elif extension in ["prproj", "prtl", "prm"]:
            self.fileButton.setIcon(QIcon("./resources/icons/premiere.png"))
        elif extension in ["aep", "aepx", "aet"]:
            self.fileButton.setIcon(QIcon("./resources/icons/ae.png"))
        elif extension in ["hip", "hipnc", "otl", "bgeos"]:
            self.fileButton.setIcon(QIcon("./resources/icons/houdini.png"))
        elif extension in ["exe"]:
            self.fileButton.setIcon(QIcon("./resources/icons/exe.png"))
        elif extension in ["3b", "3dclip"]:
            self.fileButton.setIcon(QIcon("./resources/icons/3dcoat.png"))

        elif self.file_copy:
            self.fileButton.setText("📋")
        else:
            self.fileButton.setText("🔗")

    def updateFileSize(self):
        # monitor the file size and compare it with what is should be
        new_size = FileWidget.fileSize(self.file_path)

        if new_size == self.file_size:
            self.clear_stop_button()
            self.fileSizeLabel.setText(self.pretty_size(new_size))

        elif self.file_size != 0:
            if self.is_sender and psutil.pid_exists(self.copy_pid):
                self.fileButton.setText("❌")
                self.fileButton.setIcon(QIcon(None))
            else:
                self.clear_stop_button()

            self.fileSizeLabel.setText(f"{self.pretty_size(new_size)} / {self.pretty_size(self.file_size)} "
                                       f"({new_size * 100 // self.file_size}%)")

    def cancel_copy(self):
        os.kill(self.copy_pid, signal.SIGTERM)
        self.message_widget.deleteMessage()

        try:
            if self.file_is_dir:
                os.rmdir(self.file_path)
                # delete_process = multiprocessing.Process(target=os.rmdir, args=(self.file_path,))
            else:
                os.remove(self.file_path)
                # delete_process = multiprocessing.Process(target=os.remove, args=(self.file_path,))
        except OSError as e:
            print(e)

    def clear_stop_button(self):
        try:
            self.fileButton.clicked.disconnect()
        except:
            pass
        self.set_icon()

    @classmethod
    def countItems(cls, folder_path):
        try:
            _, _, files = next(os.walk(folder_path))
            file_count = len(files)
            return file_count
        except:
            return 0

    @classmethod
    def fileSize(cls, file_path):
        if os.path.isdir(file_path):
            return FileWidget.countItems(file_path)
        else:
            return QFileInfo(file_path).size()

    def pretty_size(self, size: int):
        if self.file_is_dir:
            return f"{size} items"

        if size > 1_000_000_000:
            return str(round(size / 1_000_000_000, 3)) + " GB"
        if size > 1_000_000:
            return str(round(size / 1_000_000, 3)) + " MB"
        if size > 1_000:
            return str(round(size / 1_000, 3)) + " KB"
        else:
            return str(round(size / 1, 3)) + " B"

    def thumbnail(self, url) -> QPixmap:
        position = 0
        image = None
        loop = QEventLoop()
        QTimer.singleShot(15000, lambda: loop.exit(1))
        player = QMediaPlayer()
        sink = QVideoSink()
        player.setVideoSink(sink)
        player.setSource(url)

        def handle_status(status):
            nonlocal position
            print('status changed:', status.name)
            # if status == QMediaPlayer.MediaStatus.LoadedMedia:
            if status == QMediaPlayer.MediaStatus.BufferedMedia:
                position = player.duration() // 2
                player.setPosition(position)
                print('set position:', player.position())

        def handle_frame(frame):
            nonlocal image
            print('frame changed:', frame.startTime() // 1000)
            start = frame.startTime() // 1000
            if (start) and start >= position:
                sink.videoFrameChanged.disconnect()
                image = frame.toImage()
                print('save: exit')
                loop.exit()

        player.mediaStatusChanged.connect(handle_status)
        sink.videoFrameChanged.connect(handle_frame)
        player.durationChanged.connect(
            lambda value: print('duration changed:', value))
        player.play()
        if loop.exec() == 1:
            print('ERROR: process timed out')
        return image

    def myMousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            if self.parent().isBlur:
                self.parent().mousePressEvent(e)
            else:
                os.startfile(self.message_widget.message.file_path)
        else:
            super().mousePressEvent(e)


class ClickSlider(QSlider):
    """A slider with a signal that emits its position when it is pressed.
    Created to get around the slider only updating when the handle is dragged, but not when a new position is clicked"""

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            # Jump to click position
            value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), e.x(), self.width())
            self.setValue(value)
            self.sliderMoved.emit(value)


def enum_callback(hwnd, keyword):
    global count
    if win32gui.GetWindowText(hwnd).startswith(keyword):
        count += 1


def count_messenger_windows():
    global count
    count = 0
    win32gui.EnumWindows(enum_callback, "Message ")
    return count


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
    global target_username

    command = msg.split(" ")

    if command[0] == "new_message":
        if command[1] == user.username:
            if command[2] == target_username:
                print(f"new message... {command[3]}")
                newMessage(int(command[3]))
        if command[2] == user.username:
            if command[1] == target_username:
                newMessage(int(command[3]))

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
