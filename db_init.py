import json
import pathlib
from time import sleep

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
        # username = account[2].lower()
        username = account[3][1:].lower()
        image_path = str(pathlib.Path(QDir.toNativeSeparators(f"//khakbaz/E/ProjectManager/WorksManager/Pic/{account[3]}.png")))

        user = User(username=username, password="96321", fullname=fullname, image_path=image_path)
        user.save()

        print(f"{fullname} , {username}")


# Add dummy rows for messages and tasks table
message1 = Message(sender_username="alireza", receiver_username="pc25", text="Hello! How are you?")
message1.save()
message2 = Message(sender_username="pc25", receiver_username="alireza", text="I'm fine, thank you.", reply_to=message1.id)
message2.save()

for i in range(10):
    message1 = Message(sender_username="alireza", receiver_username="pc25", text=str(2*i + 1))
    message1.save()
    message2 = Message(sender_username="pc25", receiver_username="alireza", text=str(2*i + 2),
                       reply_to=message1.id)
    message2.save()

task = Task(assigner_username="alireza", assignee_username="pc25", description="Creating project management program.")
task.save()