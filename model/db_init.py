from time import sleep

from model import conf
from model.message import Message
from model.user import User

# conf.drop_db()
conf.init_db()

user = User(username="alireza", password="96321", fullname="علیرضا زارع")
user.save()
user = User(username="hossein", password="96321", fullname="حسین قاسمی")
user.save()
user = User(username="mahdavifar", password="96321", fullname="علی مهدوی فر")
user.save()

message = Message(sender_username="alireza", receiver_username="mahdavifar", text="Hello! How are you?")
message.save()
sleep(1)
message = Message(sender_username="mahdavifar", receiver_username="alireza", text="I'm fine, thank you.")
message.save()
sleep(1)
message = Message(sender_username="alireza", receiver_username="mahdavifar", text="Line 1.\nLine 2.\nLine 3.")
message.save()
