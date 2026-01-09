from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

DB_PATH = "jupjup.db"

# 1차(규칙) 키워드 가중치
KEYWORD_WEIGHTS: dict[str, int] = {
    "업무": 3,
    "자동화": 5,
    "workflow": 5,
    "pipeline": 6,
    "devops": 3,
    "mcp": 6,
    "agent": 6,
    "cli": 5,
    "api": 3,
    "ai": 8,
    "llm": 8,
    "gpt": 4,
    "rag": 4,
    "embedding": 3,
    "prompt": 3,
    "inference": 3,
    "금융": 10,
    "카드": 13,
    "결제": 10,
    "핀테크": 12,
    "fraud": 12,
    "보안": 12,
    "해킹": 12,
    "개인정보": 15,
    "유출": 15,
    "data": 3,
    "데이터": 3,
    "sql": 3,
    "ml": 3,
    "machine learning": 3,
}

WORD_RE = re.compile(r"[A-Za-z0-9가-힣]+")


@dataclass
class GeekRow:
    id: int
    title: str
    url: str
    content: str
    is_posted: int
    scrapped_at: str  # sqlite datetime text


def _fetch_unposted(limit: int = 200) -> list[GeekRow]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, url, content, is_posted, scrapped_at
            FROM geeknews
            WHERE is_posted = 0
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        GeekRow(
            id=int(r["id"]),
            title=str(r["title"]),
            url=str(r["url"]),
            content=str(r["content"]),
            is_posted=int(r["is_posted"]),
            scrapped_at=str(r["scrapped_at"]),
        )
        for r in rows
    ]


def _recency_score(scrapped_at: str) -> float:
    """
    scrapped_at이 '최근'일수록 점수 높게.
    (sqlite CURRENT_TIMESTAMP는 보통 'YYYY-MM-DD HH:MM:SS')
    """
    try:
        dt = datetime.strptime(scrapped_at, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except Exception:
        return 0.0

    now = datetime.now(timezone.utc)
    hours = max((now - dt).total_seconds() / 3600.0, 0.0)

    # 0시간=5점, 24시간≈1.67점, 72시간≈0.56점
    return 5.0 / (1.0 + (hours / 12.0))


def _keyword_score(text: str) -> float:
    """
    title+content에서 키워드가 발견되면 가중치 합산.
    """
    t = (text or "").lower()
    score = 0.0

    for kw, w in KEYWORD_WEIGHTS.items():
        if kw.lower() in t:
            score += float(w)

    return score


def rule_score(row: GeekRow) -> float:
    base = 0.0
    base += _recency_score(row.scrapped_at)
    base += _keyword_score(f"{row.title}\n{row.content}")
    return base


def select_top_by_rule(rows: list[GeekRow], top_m: int = 30) -> list[GeekRow]:
    scored = [(rule_score(r), r) for r in rows]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_m]]


def update_rule_scores(limit: int = 2000) -> None:
    """
    rows에 대해 rule_score를 계산해서 DB geeknews.rule_score에 저장한다.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, url, content, is_posted, scrapped_at
            FROM geeknews
            WHERE is_posted = 0
              AND rule_score IS NULL
            ORDER BY id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        targets = [
            GeekRow(
                id=int(r["id"]),
                title=str(r["title"]),
                url=str(r["url"]),
                content=str(r["content"]),
                is_posted=int(r["is_posted"]),
                scrapped_at=str(r["scrapped_at"]),
            )
            for r in rows
        ]

        if not targets:
            return 0

        scored = [(float(rule_score(r)), int(r.id)) for r in targets]

        conn.executemany(
            """
            UPDATE geeknews
            SET rule_score = ?, scored_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            scored,
        )
        conn.commit()
        return len(scored)
