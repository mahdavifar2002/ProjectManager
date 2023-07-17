from time import sleep

from model import conf
from model.message import Message
from model.task import Task
from model.user import User

# conf.drop_db()
conf.init_db()

user = User(username="alireza", password="96321", fullname="علیرضا زارع")
user.save()
user = User(username="hossein", password="96321", fullname="حسین قاسمی")
user.save()
user = User(username="mahdavifar", password="96321", fullname="علی مهدوی فر")
user.save()

message1 = Message(sender_username="alireza", receiver_username="mahdavifar", text="Hello! How are you?\n"
                                                                                   "Second line.\n"
                                                                                   "Third line.\n"
                                                                                   "Forth line.\n"
                                                                                   "Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very long line.")
message1.save()
sleep(1)
message2 = Message(sender_username="mahdavifar", receiver_username="alireza", text="I'm fine, thank you.", reply_to=message1.id)
message2.save()
sleep(1)
task = Task(assigner_username="alireza", assignee_username="mahdavifar", description="Creating project management program.")
task.save()
