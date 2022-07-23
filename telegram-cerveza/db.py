import json


class Status:
    FOUND = 1
    NOT_FOUND = 2


def save_user(id):
    users = []
    with open("users.json", "r") as f:
        users = json.load(f)

    if id not in [x["id"] for x in users]:
        users.append({"id": id, "malta_last_status": Status.NOT_FOUND, "cerveza_last_status": Status.NOT_FOUND})
        with open("users.json", "w") as f:
            json.dump(users, f)


def remove_user(id):
    users = []
    with open("users.json", "r") as f:
        users = json.load(f)

    ids = [x["id"] for x in users]
    if id in ids:
        users = [x for x in users if x["id"] != id]
        with open("users.json", "w") as f:
            json.dump(users, f)


def bulk_save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)


def get_users():
    users = []
    with open("users.json", "r") as f:
        users = json.load(f)
    return users
