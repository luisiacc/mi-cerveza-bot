import json
import os
from dataclasses import dataclass

import psycopg2
from typing_extensions import TypedDict


class Status:
    FOUND = 1
    NOT_FOUND = 2


INITIAL_STATE = Status.NOT_FOUND

UserStatus = TypedDict(
    "UserStatus",
    {
        "malta_last_status": int,
        "cerveza_last_status": int,
        "cerveza_bucanero_last_status": int,
    },
)

initial_status: UserStatus = {
    "malta_last_status": Status.NOT_FOUND,
    "cerveza_last_status": Status.NOT_FOUND,
    "cerveza_bucanero_last_status": Status.NOT_FOUND,
}


@dataclass
class User:
    id: int
    status: UserStatus


class PostgreSqlDB:
    def __init__(self, database_url) -> None:
        self.database_url = database_url
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(self.database_url, sslmode="require")

    def exec(self, stmt, args=(), commit=True):
        stmt = stmt.replace("?", "%s")
        self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(stmt, args)
            if commit:
                self.commit()
            result = cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        finally:
            cursor.close()
            if commit:
                self.conn.close()

    def commit(self):
        self.conn.commit()

    def select(self, stmt):
        return self.exec(stmt, commit=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, status JSON)"
        self.exec(stmt)


class DB(PostgreSqlDB):
    def add_user(self, id):
        stmt = "INSERT INTO users SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = ?)"
        args = (id, json.dumps(initial_status), id)
        print("adding user", id)
        self.exec(stmt, args)

    def remove_user(self, id):
        stmt = "DELETE FROM users WHERE id = (?)"
        print("removing user", id)
        self.exec(stmt, (id,))

    def get_users(self):
        items = self.select("SELECT * FROM users")
        if not items:
            return []
        return [User(*item) for item in items]

    def bulk_update_users(self, users):
        for user in users:
            stmt = "UPDATE users SET status = ? WHERE id = ?"
            args = (json.dumps(user.status), user.id)
            self.exec(stmt, args, commit=False)
        self.commit()
        self.conn.close()


user = os.environ.get("POSTGRES_USER")
passw = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DBNAME", "micerveza")

database_url = os.environ.get("DATABASE_URL", f"postgresql://{user}:{passw}@localhost:5432/{dbname}")
db = DB(database_url)
