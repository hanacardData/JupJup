import itertools
import re

TRAVELLOG_KEYWORDS: list[str] = [
    "트래블로그",
    "트래블고",
    "트래블GO",
    "하나머니",
]

TRAVELLOG_ISSUE_KEYWORDS: list[str] = [
    "ATM 오류",
    "ATM 에러",
    "거절",
    "불편",
    "불가",
]

combinations = list(itertools.product(TRAVELLOG_KEYWORDS, TRAVELLOG_ISSUE_KEYWORDS))
TRAVELLOG_QUERIES: list[str] = [
    re.sub(r"\s+", " ", f"{combination[0]} {combination[1]}").strip()
    for combination in combinations
]
