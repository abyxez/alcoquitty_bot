import datetime
import sqlite3
from sqlite3 import IntegrityError


def get_initialization(username, first_name):
    connection = sqlite3.connect("alcodabatase.sql")
    cur = connection.cursor()

    cur.execute(
        """
                CREATE TABLE IF NOT EXISTS users 
                (id INTEGER PRIMARY KEY, 
                username varchar(50) UNIQUE, first_name varchar(50),
                penalty INTEGER DEFAULT 1, drunk_times INTEGER DEFAULT 0,
                last_drank varchar(30))
                """
    )

    try:
        cur.execute(
            "INSERT INTO users( username, first_name)"
            "VALUES"
            f'("{username}", "{first_name}")'
        )
    except IntegrityError:
        pass

    connection.commit()
    cur.close()
    connection.close()


def get_user(username):
    connection = sqlite3.connect("alcodabatase.sql")
    cur = connection.cursor()
    user = [
        user
        for user in cur.execute("SELECT * FROM users " f"WHERE username = '{username}'")
    ]
    return user[0]


def update_user(username):
    connection = sqlite3.connect("alcodabatase.sql")
    cur = connection.cursor()
    timestamp = datetime.datetime.now()

    cur.execute(
        "UPDATE users SET penalty = penalty + 1, "
        f"drunk_times = drunk_times + 1, last_drank = '{timestamp}' "
        f"WHERE username = '{username}'"
    )
    connection.commit()
    cur.close()
    connection.close()
