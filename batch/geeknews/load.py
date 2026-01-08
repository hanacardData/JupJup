import html
import re
import sqlite3
import xml.etree.ElementTree as ET

import requests
from pydantic import BaseModel

from logger import logger


class GeekNewsItem(BaseModel):
    title: str
    url: str
    content: str


def remove_html(raw_html: str) -> str:
    clean_text = re.sub("<.*?>", "", raw_html)
    clean_text = html.unescape(clean_text)
    return clean_text.strip()


def get_latest_url_from_db() -> str:
    with sqlite3.connect("jupjup.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT url FROM geeknews
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
                INSERT OR IGNORE INTO geeknews (title, url, content)
                VALUES (?, ?, ?)
                """,
                (item.title, item.url, item.content),
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB save error: {e}")


def collect_load_geeknews():
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
    # items: list[GeekNewsItem] = []
    for entry in reversed(entries):
        if (url := entry.find("atom:id", ns).text) >= last_url:
            logger.info(f"Insert {url}")
            save_news_item(
                GeekNewsItem(
                    title=remove_html(entry.find("atom:title", ns).text),
                    url=url,
                    content=remove_html(entry.find("atom:content", ns).text),
                )
            )


if __name__ == "__main__":
    collect_load_geeknews()
