import datetime
import json
import pathlib
from time import sleep

import jdatetime
from PySide6 import QtGui
from PySide6.QtCore import QDir

from model import conf
from model.message import Message
from model.task import Task
from model.user import User

# conf.drop_db()
conf.init_db()

# user = User(username="mahdavifar", password="96321", fullname="علی مهدوی فر", image_path="\\\\khakbaz\\E\\ProjectManager\\WorksManager\\Pic\\FMahdavifar.jpg")
# user.save()

# Load users from Works Manager
accounts_path = pathlib.Path(QDir.toNativeSeparators("//alireza/E/Works Manager/List/Account.lst"))

with open(str(accounts_path), mode="r", encoding="utf-8") as accounts_file:
    accounts_str = accounts_file.read().replace('\'', "\"")
    accounts = json.loads(accounts_str)

    for account in accounts:
        account[3] = "F" + account[3][1:]

        fullname = account[0] + " " + account[1]
        share = username = account[2].lower()
        username = account[3][1:].lower()
        image_path = str(
            pathlib.Path(QDir.toNativeSeparators(f"//khakbaz/E/ProjectManager/WorksManager/Pic/{account[3]}.png")))

        user = User(username=username, password="96321", fullname=fullname, share=share, image_path=image_path)
        user.save()

        print(f"{fullname} , {username}")

usernames = [user.username for user in User.users()]

# Add dummy rows for messages and tasks table
# message1 = Message(sender_username="alireza", receiver_username="pc25", text="Hello! How are you?")
# message1.save()
# message2 = Message(sender_username="pc25", receiver_username="alireza", text="I'm fine, thank you.", reply_to=message1.id)
# message2.save()

# for i in range(100):
#     message1 = Message(sender_username="alireza", receiver_username="pc25", text=str(2*i + 1),
#                        time_created=datetime.datetime.now() - datetime.timedelta(seconds=200 - (2*i + 1)))
#     message1.save()
#     message2 = Message(sender_username="pc25", receiver_username="alireza", text=str(2*i + 2),
#                        time_created=datetime.datetime.now() - datetime.timedelta(seconds=200 - (2*i + 2)), reply_to=message1.id)
#     message2.save()

task = Task(assigner_username="alireza", assignee_username="pc25", description="Creating project management program.")
task.save()

# import old messages
directory = 'E:\\ProjectManager\\Chat'

files = pathlib.Path(directory).glob('*')
for contact in files:
    with open(contact, mode="r", encoding="utf-8") as file:
        messages = [list(eval(file.read()))][0]
        print(f"\n{contact}: {len(messages)}")

        for args in messages[:20]:
            try:
                sender = args[0].lower()
                receiver = args[1].lower()
                text = args[2]
                _datetime = args[3].replace(".", ":")
                file_path = args[4].replace("/", "\\")
                file_size = args[5]
                file_type = args[6]
                percent = args[7]
                widget_size = args[8]
                has_been_seen = args[9]
                file_source = args[10].replace("/", "\\")
            except:
                pass

            _datetime = _datetime.split("      ", maxsplit=1)[1]
            time_created = jdatetime.datetime.strptime(_datetime, "%Y-%m-%d      %H:%M:%S").togregorian()
            doc = QtGui.QTextDocument()
            doc.setHtml(text)
            text = doc.toPlainText()
            while '\n\n' in text:
                text = text.replace("\n\n", "\n")

            try:
                if sender in usernames and receiver in usernames:
                    message = Message(sender_username=sender, receiver_username=receiver, text=text,
                                      time_created=time_created, file_path=file_path, has_been_seen=has_been_seen)
                    message.save()
            except Exception as e:
                raise e
