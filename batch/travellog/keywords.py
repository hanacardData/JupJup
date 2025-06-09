import itertools
import re

TRAVELLOG_KEYWORDS: list[str] = [
    "트래블로그",
    "트래블고",
    "트래블GO",
    "하나머니",
]

TRAVELLOG_ADDTIONAL_KEYWORDS: list[str] = [
    "인출",
    "ATM",
    "출금",
    "질문",
    "수수료",
]

TRAVELLOG_ISSUE_KEYWORDS: list[str] = [
    "",
    "불편",
    "오류",
    "불가",
    "안돼요",
    "안되요",
    "불만",
    "문의",
    "도와주세요",
    "절대",
    "거절",
    "불안",
    "급해요",
]

combinations = list(
    itertools.product(
        TRAVELLOG_KEYWORDS, TRAVELLOG_ADDTIONAL_KEYWORDS, TRAVELLOG_ISSUE_KEYWORDS
    )
)
TRAVELLOG_QUERIES: list[str] = [
    re.sub(r"\s+", " ", f"{combination[0]} {combination[1]} {combination[2]}").strip()
    for combination in combinations
]
