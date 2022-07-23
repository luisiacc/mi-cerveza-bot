import sqlite3
from dataclasses import dataclass


class Status:
    FOUND = 1
    NOT_FOUND = 2


@dataclass
class User:
    id: int
    malta_last_status: int
    cerveza_last_status: int


class DB:
    def __init__(self, dbname="db.sqlite") -> None:
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def exec(self, stmt, args=(), commit=True):
        result = self.conn.execute(stmt, args)
        if commit:
            self.conn.commit()

        return result

    def select(self, stmt):
        return self.exec(stmt, commit=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, malta_last_status INTEGER, cerveza_last_status INTEGER)"
        self.exec(stmt)

    def add_user(self, id):
        stmt = "INSERT INTO users SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = ?)"
        args = (id, 2, 2, id)
        self.exec(stmt, args)

    def remove_user(self, id):
        stmt = "DELETE FROM users WHERE id = (?)"
        self.exec(stmt, (id,))

    def get_users(self):
        items = self.select("SELECT * FROM users")
        if not items:
            return []
        return [User(*item) for item in items]

    def bulk_update_users(self, users):
        for user in users:
            stmt = "UPDATE users SET malta_last_status = ?, cerveza_last_status = ? WHERE id = ?"
            args = (user.malta_last_status, user.cerveza_last_status, user.id)
            self.exec(stmt, args, commit=False)
        self.conn.commit()


db = DB()
db.setup()
