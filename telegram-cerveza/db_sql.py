import os
import sqlite3
from dataclasses import dataclass

import psycopg2


class Status:
    FOUND = 1
    NOT_FOUND = 2


INITIAL_STATE = Status.NOT_FOUND


@dataclass
class User:
    id: int
    malta_last_status: int
    cerveza_last_status: int
    cerveza_bucanero_last_status: int


class SQLiteDB:
    def __init__(self, dbname="db.sqlite") -> None:
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def exec(self, stmt, args=(), commit=True):
        result = self.conn.execute(stmt, args)
        if commit:
            self.commit()

        return result

    def commit(self):
        self.conn.commit()

    def select(self, stmt):
        return self.exec(stmt, commit=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, malta_last_status INTEGER, cerveza_last_status INTEGER)"
        self.exec(stmt)


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
        stmt = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, malta_last_status INTEGER, cerveza_last_status INTEGER, cerveza_bucanero_last_status INTEGER)"
        self.exec(stmt)


class DB(PostgreSqlDB):
    def add_user(self, id):
        stmt = "INSERT INTO users SELECT ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = ?)"
        args = (id, INITIAL_STATE, INITIAL_STATE, INITIAL_STATE, id)
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
            stmt = "UPDATE users SET malta_last_status = ?, cerveza_last_status = ?, cerveza_bucanero_last_status = ? WHERE id = ?"
            args = (user.malta_last_status, user.cerveza_last_status, user.cerveza_bucanero_last_status, user.id)
            self.exec(stmt, args, commit=False)
        self.commit()
        self.conn.close()


user = os.environ.get("POSTGRES_USER")
passw = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DBNAME", "micerveza")

database_url = os.environ.get("DATABASE_URL", f"postgresql://{user}:{passw}@localhost:5432/{dbname}")
db = DB(database_url)
