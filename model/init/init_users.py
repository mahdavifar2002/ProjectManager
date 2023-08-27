import json
import pathlib

from PySide6.QtCore import QDir

from model.user import User


def insert():
    # Load users from Works Manager
    accounts_path = pathlib.Path(QDir.toNativeSeparators("//alireza/E/Works Manager/List/Account.lst"))

    old_usernames = [user.username for user in User.users()]
    new_usernames = []

    with open(str(accounts_path), mode="r", encoding="utf-8") as accounts_file:
        accounts_str = accounts_file.read().replace('\'', "\"")
        accounts = json.loads(accounts_str)

        for account in accounts:
            account[3] = "F" + account[3][1:]

            fullname = account[0] + " " + account[1]
            share = account[2].lower()
            username = account[3][1:].lower()
            image_path = str(
                pathlib.Path(QDir.toNativeSeparators(f"//alireza/E/Works Manager/Pic/{account[3]}.png")))

            if username not in old_usernames:
                user = User(username=username, password="96321", fullname=fullname, share=share, image_path=image_path)
                user.save()
                new_usernames.append(username)

                print(f"{fullname} , {username}")

    return new_usernames
