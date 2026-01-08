import sqlite3
import xml.etree.ElementTree as ET

import requests
from pydantic import BaseModel

from logger import logger


class GeekNewsItem(BaseModel):
    title: str
    url: str


def get_latest_url_from_db() -> str:
    with sqlite3.connect("jupjup.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT url FROM geek_news
            ORDER BY url ASC
            LIMIT 1
        """)
        result = cursor.fetchone()
        return result[0] if result else ""


def save_news_item(item: GeekNewsItem):
    with sqlite3.connect("jupjup.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO geek_news (title, url)
                VALUES (?, ?)
            """,
                (item.title, item.url),
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB save error: {e}")


def collect_load_geek_news():
    RSS_URL = "https://feeds.feedburner.com/geeknews-feed"
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"GeekNews RSS fetch error: {e}")
        return

    last_url = get_latest_url_from_db()
    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    for entry in reversed(entries):
        if (url := entry.find("atom:id", ns).text) >= last_url:
            save_news_item(
                GeekNewsItem(
                    title=entry.find("atom:title", ns).text,
                    url=url,
                )
            )


if __name__ == "__main__":
    collect_load_geek_news()
