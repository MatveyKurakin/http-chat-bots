import json
import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


def recreate_database() -> None:
    connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
    with connection:
        connection.execute("DROP TABLE IF EXISTS telegram_updates")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_updates
            (
                id INTEGER PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """,
        )
    connection.close()


def persist_updates(updates: dict) -> None:
    connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
    with connection:
        data = []
        for update in updates:
            data.append((json.dumps(update),))
        connection.executemany(
            "INSERT INTO telegram_updates (payload) VALUES (?)",
            data,
        )
    connection.close()
