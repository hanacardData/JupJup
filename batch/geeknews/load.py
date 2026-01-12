from __future__ import annotations

import html
import re
import sqlite3
import xml.etree.ElementTree as ET

import requests
from pydantic import BaseModel

from batch.geeknews.rank import rule_score_from_text
from logger import logger

DB_PATH = "jupjup.db"
RSS_URL = "https://feeds.feedburner.com/geeknews-feed"


class GeekNewsItem(BaseModel):
    title: str
    url: str
    content: str


def remove_html(raw_html: str) -> str:
    clean_text = re.sub("<.*?>", "", raw_html or "")
    clean_text = html.unescape(clean_text)
    return clean_text.strip()


def save_news_item(item: GeekNewsItem) -> None:
    score = float(rule_score_from_text(item.title, item.content))

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO geeknews (title, url, content, rule_score, scored_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (item.title, item.url, item.content, score),
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB save error: {e}")


def collect_load_geeknews() -> None:
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"GeekNews RSS fetch error: {e}")
        return

    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)

    for entry in reversed(entries):
        url = (entry.find("atom:id", ns).text or "").strip()
        title = remove_html(entry.find("atom:title", ns).text or "")
        content = remove_html(entry.find("atom:content", ns).text or "")

        if not url or not title:
            continue

        save_news_item(
            GeekNewsItem(
                title=title,
                url=url,
                content=content,
            )
        )
