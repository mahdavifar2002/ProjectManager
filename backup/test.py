# import required module
import json
import pathlib

import jdatetime
from PySide6 import QtGui

# assign directory
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
            time_created = jdatetime.datetime.strptime(_datetime, "%Y-%m-%d      %H:%M:%S")
            doc = QtGui.QTextDocument()
            doc.setHtml(text)
            text = doc.toPlainText()
            while '\n\n' in text:
                text = text.replace("\n\n", "\n")

            try:
                print(text)
                # message = Message(sender_username=sender, receiver_username=receiver, text=text,
                #                    time_created=time_created)
                # messages.save()
            except Exception as e:
                print(e)
