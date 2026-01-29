import sqlite3

DB_PATH = "jupjup.db"


def init_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # 트래블로그
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS travellog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                title TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                post_date TEXT,
                scrap_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                name TEXT,
                is_posted INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 보안
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_monitor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                title TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                post_date TEXT,
                scrap_date TEXT,
                source TEXT,
                name TEXT,
                is_posted INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 긱뉴스
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geeknews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                is_posted INTEGER DEFAULT 0,
                scrapped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                gpt_score REAL,
                topic TEXT
            )
        """)
        conn.commit()

        # 나라사랑카드
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS narasarang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT,               -- 'hana' | 'shinhan'
                query TEXT,
                title TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                post_date TEXT,
                scrap_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                name TEXT,
                is_posted INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
