import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "cnb.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS rates (
                date     TEXT,
                currency TEXT,
                amount   INTEGER,
                rate     REAL,
                PRIMARY KEY (date, currency)
            )
        """)
