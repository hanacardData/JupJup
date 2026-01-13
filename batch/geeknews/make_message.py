import sqlite3

from batch.database import DB_PATH
from logger import logger


def update_posted_status(id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE geeknews SET is_posted = 1 WHERE id = ?", (id,))
        conn.commit()


def get_geeknews_message() -> list[str]:
    """DB에서 미발송건만 찾아 전달"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT id, title, content, url
            FROM geeknews
            WHERE is_posted = 0
            ORDER BY gpt_score DESC
            """
        )
        unposted = cursor.fetchall()
        messages: list[str] = ["geeknews"]
        for row in unposted[:10]:
            try:
                message = (
                    f"제목:{row['title']}\n내용:{row['content']}\n링크:{row['url']}"
                )
                messages.append(message)
                update_posted_status(row["id"])
            except Exception as e:
                logger.error(f"Poster Error (ID {row['id']}): {e}")

    return messages
