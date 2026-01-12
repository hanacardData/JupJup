from __future__ import annotations

import re
from dataclasses import dataclass

# 1차(규칙) 키워드 가중치
KEYWORD_WEIGHTS: dict[str, int] = {
    # ===== 최상위: 금융·보안·개인정보 =====
    "금융": 22,
    "카드": 22,
    "결제": 18,
    "핀테크": 20,
    "fraud": 20,
    "보안": 20,
    "해킹": 20,
    "개인정보": 25,
    "유출": 25,
    "누출": 25,
    # ===== 국내 이슈 / 기업 =====
    "카카오": 13,
    "네이버": 13,
    "토스": 16,
    "삼성": 15,
    "신한": 15,
    "현대카드": 15,
    "KB": 15,
    # ===== AI / LLM (중간 포인트) =====
    "ai": 8,
    "llm": 8,
    "gpt": 6,
    "rag": 6,
    "embedding": 4,
    "prompt": 4,
    "inference": 4,
    "agent": 5,
    # ===== 업무·자동화, 데이터 (후순위) =====
    "자동화": 2,
    "workflow": 2,
    "pipeline": 2,
    "devops": 2,
    "mcp": 1,
    "cli": 1,
    "api": 1,
    "data": 2,
    "데이터": 2,
    "sql": 2,
    "ml": 1,
    "machine learning": 1,
    "업무": 1,
}

WORD_RE = re.compile(r"[A-Za-z0-9가-힣]+")


@dataclass
class GeekRow:
    id: int
    title: str
    url: str
    content: str


def _keyword_score(text: str) -> float:
    t = (text or "").lower()
    score = 0.0
    for kw, w in KEYWORD_WEIGHTS.items():
        if kw.lower() in t:
            score += float(w)
    return score


def rule_score_from_text(title: str, content: str) -> float:
    """
    fetch 시점에 넣을 rule_score
    - 방금 수집된 데이터이므로 5점 고정
    """
    recency = 5.0
    kw = _keyword_score(f"{title}\n{content}")
    return recency + kw
