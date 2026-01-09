import sqlite3

from logger import logger


def _add_column_if_not_exists(
    conn: sqlite3.Connection, table: str, col: str, col_def: str
):
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if col not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
        conn.commit()
        logger.info(f"[DB] Added column {table}.{col}")


def init_database():
    with sqlite3.connect("jupjup.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geeknews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                is_posted INTEGER DEFAULT 0,
                scrapped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                rule_score REAL,
                gpt_score REAL,
                scored_at DATETIME
            )
        """)
        conn.commit()

        _add_column_if_not_exists(conn, "geeknews", "rule_score", "REAL")
        _add_column_if_not_exists(conn, "geeknews", "gpt_score", "REAL")
        _add_column_if_not_exists(conn, "geeknews", "scored_at", "DATETIME")
