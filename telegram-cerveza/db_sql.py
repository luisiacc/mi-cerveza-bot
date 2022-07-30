import contextlib
import json
import os
from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import register_adapter
from psycopg2.extras import Json, execute_values
from typing_extensions import TypedDict

register_adapter(dict, Json)


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

    @contextlib.contextmanager
    def prepare_connection(self, commit=True):
        self.connect()
        cursor = self.conn.cursor()
        try:
            yield cursor
            if commit:
                self.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        finally:
            cursor.close()
            if commit:
                self.conn.close()

    def exec(self, stmt, args=(), commit=True, return_results=False):
        stmt = stmt.replace("?", "%s")
        with self.prepare_connection(commit=commit) as cursor:
            cursor.execute(stmt, args)
            if return_results:
                return cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def select(self, stmt):
        return self.exec(stmt, commit=False, return_results=True)

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
        def user_row(user):
            return (user.id, user.status)

        stmt = "UPDATE users SET status = payload.status::json FROM (VALUES %s) as payload (id, status) WHERE users.id = payload.id"
        args = [user_row(user) for user in users]
        with self.prepare_connection() as cursor:
            execute_values(cursor, stmt, args)


user = os.environ.get("POSTGRES_USER")
passw = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DBNAME", "micerveza")

database_url = os.environ.get("DATABASE_URL", f"postgresql://{user}:{passw}@localhost:5432/{dbname}")
db = DB(database_url)
