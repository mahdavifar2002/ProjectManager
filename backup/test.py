# import required module
import json
import pathlib

import jdatetime
from PySide6 import QtGui
from PySide6.QtCore import QDir

from model.message import Message

usernames = []

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

        usernames.append(username)




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
            except Exception as e:
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
                    print(time_created)
                    message = Message(sender_username=sender, receiver_username=receiver, text=text,
                                      time_created=time_created, file_path=file_path, has_been_seen=has_been_seen)
                    # message.save()
            except Exception as e:
                raise e
