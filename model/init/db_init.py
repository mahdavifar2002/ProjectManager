import datetime
import json
import pathlib
from time import sleep

from PySide6 import QtGui
from PySide6.QtCore import QDir
from tqdm import tqdm

from model import conf
from model.init import users
from model.init import messages
from model.message import Message
from model.task import Task
from model.user import User

# conf.drop_db()
conf.init_db()

# user = User(username="mahdavifar", password="96321", fullname="علی مهدوی فر", image_path="\\\\khakbaz\\E\\ProjectManager\\WorksManager\\Pic\\FMahdavifar.jpg")
# user.save()

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

# task = Task(assigner_username="alireza", assignee_username="pc25", description="Creating project management program.")
# task.save()

users.insert()
messages.insert()
