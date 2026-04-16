import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "eds.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario  TEXT,       -- 'client' or 'server'
                message   TEXT,
                signature TEXT,
                verified  INTEGER,    -- 1 or 0
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
