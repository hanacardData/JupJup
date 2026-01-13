import asyncio
import html
import re
import sqlite3
import xml.etree.ElementTree as ET

import requests

from batch.database import DB_PATH
from batch.geeknews.gpt_rank import GeekNewsItem, gpt_score_from_items
from batch.geeknews.rank import rule_score_from_text
from logger import logger

RSS_URL = "https://feeds.feedburner.com/geeknews-feed"


def remove_html(raw_html: str) -> str:
    clean_text = re.sub("<.*?>", "", raw_html or "")
    clean_text = html.unescape(clean_text)
    return clean_text.strip()


def get_last_url() -> str:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT url
            FROM geeknews
            ORDER BY id DESC
            LIMIT 1
            """).fetchone()
    return (row[0] or "").strip()


def save_news_item(item: GeekNewsItem) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO geeknews (title, url, content, rule_score, gpt_score)
                VALUES (?, ?, ?, ?, ?)
                """,
                (item.title, item.url, item.content, item.rule_score, item.gpt_score),
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB save error: {e}")


def collect_load_geeknews(rule_top_n: int = 30, gpt_concurrency: int = 5) -> None:
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"GeekNews RSS fetch error: {e}")
        return

    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)

    last_url = get_last_url()

    items: list[GeekNewsItem] = []
    for entry in reversed(entries):
        if (url := entry.find("atom:id", ns).text) > last_url:
            title = remove_html(entry.find("atom:title", ns).text)
            content = remove_html(entry.find("atom:content", ns).text)
            if not url or not title:
                continue

            rule_score = rule_score_from_text(title, content)

            items.append(
                GeekNewsItem(
                    title=title,
                    url=url,
                    content=content,
                    rule_score=rule_score,
                    gpt_score=None,
                )
            )

    items_sorted = sorted(items, key=lambda x: x.rule_score, reverse=True)
    top_items = items_sorted[:rule_top_n]

    gpt_scores = asyncio.run(
        gpt_score_from_items(top_items, concurrency=gpt_concurrency)
    )
    score_map = {it.url: float(s) for it, s in zip(top_items, gpt_scores)}
    for it in items:
        if it.url in score_map:
            it.gpt_score = score_map[it.url]
        save_news_item(it)

    logger.info(
        f"[GeekNews] saved new items (looped insert): {len(items)} "
        f"(gpt_scored={len(score_map)}, rule_top_n={rule_top_n})"
    )
