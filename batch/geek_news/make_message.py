import sqlite3

from logger import logger


def update_posted_status(id: str):
    with sqlite3.connect("jupjup.db") as conn:
        conn.execute("UPDATE geek_news SET is_posted = 1 WHERE id = ?", (id,))
        conn.commit()


def get_geeknews_message() -> list[str]:
    """DB에서 미발송건만 찾아 전달"""
    with sqlite3.connect("jupjup.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT id, title, url FROM geek_news WHERE is_posted = 0 ORDER BY id ASC"
        )
        unposted = cursor.fetchall()
        messages: list[str] = []
        for row in unposted:
            try:
                message = f"📢 **GeekNews**\n\n{row['title']}\n{row['url']}"
                messages.append(message)
                update_posted_status(row["id"])
            except Exception as e:
                logger.error(f"Poster Error (ID {row['id']}): {e}")

    return messages
