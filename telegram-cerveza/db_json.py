import json
from dataclasses import asdict, dataclass


@dataclass
class User:
    id: int
    malta_last_status: int
    cerveza_last_status: int


class Status:
    FOUND = 1
    NOT_FOUND = 2


class DB:
    def add_user(self, id):
        return save_user(id)

    def remove_user(self, id):
        return remove_user(id)

    def get_users(self):
        return get_users()

    def bulk_update_users(self, users):
        return bulk_save_users(users)


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
    users = asdict(users)
    with open("users.json", "w") as f:
        json.dump(users, f)


def get_users():
    users = []
    with open("users.json", "r") as f:
        users = json.load(f)
    return [User(**data) for data in users]


db = DB()
