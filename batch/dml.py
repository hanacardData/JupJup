import sqlite3
from typing import Iterable

import pandas as pd

from batch.database import DB_PATH

COMMON_COLS = [
    "query",
    "title",
    "url",
    "description",
    "post_date",
    "scrap_date",
    "source",
    "name",
    "is_posted",
]

TABLE_COLS: dict[str, list[str]] = {
    "travellog": COMMON_COLS,
    "security_monitor": COMMON_COLS,
    "narasarang": ["brand"] + COMMON_COLS,
}


def fetch_df(table: str, cols: list[str] | None = None) -> pd.DataFrame:
    cols = cols or COMMON_COLS
    sql = f"SELECT {', '.join(cols)} FROM {table}"
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)


def insert_rows(table: str, rows: list[dict]) -> None:
    if not rows:
        return
    cols = TABLE_COLS.get(table, COMMON_COLS)
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"""
        INSERT OR IGNORE INTO {table} ({", ".join(cols)})
        VALUES ({placeholders})
    """

    values = []
    for r in rows:
        link = (r.get("url") or "").strip()
        if not link:
            continue
        values.append(tuple(r.get(c, "") for c in cols))

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(sql, values)
        conn.commit()


def mark_posted(table: str, urls: Iterable[str]) -> None:
    urls = [u.strip() for u in urls if u and u.strip()]
    if not urls:
        return
    placeholders = ",".join(["?"] * len(urls))
    sql = f"UPDATE {table} SET is_posted = 1 WHERE url IN ({placeholders})"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, urls)
        conn.commit()
