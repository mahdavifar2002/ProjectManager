import pathlib
import datetime
import jdatetime
import html2text


from PySide6 import QtGui

from tqdm import tqdm

from model import conf
from model.message import Message
from model.user import User


def insert():
    # import old messages
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True

    users = User.users()
    usernames = [user.username for user in users]

    users = [User.find_by_username("shabani"), User.find_by_username("pc25")
             , User.find_by_username("hossein"), User.find_by_username("alireza")]

    for user in users:
        try:
            print(f"\nloading chats of user {user.username}...\n")
            directory = f"\\\\{user.share}\\E\\Works Manager\\Chat"
            files = pathlib.Path(directory).glob('*')

            files_list = []
            for contact in files:
                files_list.append(contact)

            for contact in tqdm(files_list):

                contact_username = str(contact).replace("\\", ".").split(".")[-2].lower()

                if contact_username not in usernames:
                    continue
                if len(user.ten_messages(contact_username)) > 0:
                    continue

                with open(contact, mode="r", encoding="utf-8") as file:

                    messages_list = [list(eval(file.read()))][0]
                    messages = []

                    for args in messages_list[-100:]:

                        try:
                            sender = args[0].lower()
                            receiver = args[1].lower()
                            text = args[2]
                            _datetime = args[3].replace(".", ":")
                            file_path = str(args[4].replace("/", "\\")).strip()
                            file_size = args[5]
                            file_type = str(args[6])
                            if file_type not in ["Link", "Copy"]:
                                file_type = ""
                            percent = args[7]
                            widget_size = args[8]
                            has_been_seen = bool(args[9])
                            file_source = args[10].replace("/", "\\")

                            _datetime = _datetime.split("      ", maxsplit=1)[1]
                            time_created = jdatetime.datetime.strptime(_datetime, "%Y-%m-%d      %H:%M:%S").togregorian()
                            # doc = QtGui.QTextDocument()
                            # doc.setHtml(text)
                            # text = doc.toPlainText() + file_type
                            text = h.handle(text)

                            while '\n\n' in text:
                                text = text.replace("\n\n", "\n")
                            text = text.replace("\n", " ")
                            text = text.strip()

                            try:
                                # if sender in usernames and receiver in usernames:
                                if user.username in [sender, receiver] and contact_username in [sender, receiver]:
                                    message = Message(sender_username=sender, receiver_username=receiver, text=text,
                                                      time_created=time_created, file_path=file_path,
                                                      file_copy=(file_type == "Copy"), has_been_seen=has_been_seen)
                                    messages.append(message)

                            except Exception as e:
                                print(e)

                        except:
                            pass

                    conf.bulk_save_to_db(messages)
        except:
            print(f"failed to enter share {user.share}")


if __name__ == "__main__":
    insert()