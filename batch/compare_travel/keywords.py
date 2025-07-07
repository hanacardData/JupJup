import itertools
import re

COMPARE_TRAVEL_KEYWORDS: list[str] = [
    "트래블로그",
    "쏠트래블",
    "트래블러스",
    "트래블월렛",
    "위비트래블",
]

COMPARE_TRAVEL_ISSUE_KEYWORDS: list[str] = [
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

COMPARE_TRAVEL_TREND_KEYWORDS: list[dict[str : str | list[str]]] = [
    {
        "groupName": "트래블로그",
        "keywords": [
            "트래블로그",
            "트레블로그",
        ],
    },
    {
        "groupName": "쏠트래블",
        "keywords": [
            "쏠트래블",
            "SOL트래블",
            "트래블쏠",
        ],
    },
    {
        "groupName": "트래블러스",
        "keywords": [
            "트래블러스",
            "트레블러스",
        ],
    },
    {
        "groupName": "트래블월렛",
        "keywords": [
            "트래블월렛",
            "트레블월렛",
        ],
    },
    {
        "groupName": "위비트래블",
        "keywords": [
            "위비트래블",
            "위비트레블",
        ],
    },
]

combinations = list(
    itertools.product(
        COMPARE_TRAVEL_KEYWORDS,
        COMPARE_TRAVEL_ISSUE_KEYWORDS,
    )
)
COMPARE_TRAVEL_QUERIES: list[str] = [
    re.sub(r"\s+", " ", f"{combination[0]} {combination[1]}").strip()
    for combination in combinations
]
