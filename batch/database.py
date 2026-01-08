import sqlite3


def init_database():
    with sqlite3.connect("jupjup.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geek_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                is_posted INTEGER DEFAULT 0,
                scrapped_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
