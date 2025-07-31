"""검색어에 사용되는 키워드 모음"""

import itertools
import re

CARD_PRODUCTS: list[str] = [
    "하나카드",
]

ISSUE_KEYWORDS: list[str] = [
    "개인정보",
    "고객정보",
    "유출",
    "랜섬웨어",
    "해킹",
]

combinations = list(itertools.product(CARD_PRODUCTS, ISSUE_KEYWORDS))
SECURITY_QUERIES: list[str] = [
    re.sub(r"\s+", " ", f"{product} {issue}").strip() for product, issue in combinations
]
