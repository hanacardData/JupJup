"""검색어에 사용되는 키워드 모음"""

CARD_COMPANIES: list[str] = [
    "신한카드",
    "하나카드",
    "국민카드",
    "우리카드",
    "롯데카드",
    "현대카드",
    "삼성카드",
    "비씨카드",
]

CREDIT_CARD_KEYWORDS: list[str] = [
    '"신한카드" +출시 -체크 +신용 -삼성 -현대 -KB -우리 -롯데',
    '"삼성카드" +출시 -체크 +신용 -신한 -현대 -KB -우리 -롯데',
    '"현대카드" +출시 -체크 +신용 -삼성 -신한 -KB -우리 -롯데',
    '"KB국민카드" +출시 -체크 +신용 -삼성 -현대 -신한 -우리 -롯데',
    '"우리카드" +출시 -체크 +신용 -삼성 -현대 -KB -신한 -롯데',
    '"롯데카드" +출시 -체크 +신용 -삼성 -현대 -KB -우리 -신한',
]

DEBIT_CARD_KEYWORDS: list[str] = [
    '"신한카드" +출시 +체크 -신용 -삼성 -현대 -KB -우리 -롯데',
    '"삼성카드" +출시 +체크 -신용 -신한 -현대 -KB -우리 -롯데',
    '"현대카드" +출시 +체크 -신용 -삼성 -신한 -KB -우리 -롯데',
    '"KB국민카드" +출시 +체크 -신용 -삼성 -현대 -신한 -우리 -롯데',
    '"우리카드" +출시 +체크 -신용 -삼성 -현대 -KB -신한 -롯데',
    '"롯데카드" +출시 +체크 -신용 -삼성 -현대 -KB -우리 -신한',
]

WONDER_CARD_FEEDBACK_KEYWORDS: list[str] = [
    '"카드" 원더||하나',
]

JADE_CARD_FEEDBACK_KEYWORDS: list[str] = ['"카드" 제이드||JADE']

KEYWORDS_BY_BUTTON = {
    "신용카드 신상품": CREDIT_CARD_KEYWORDS,
    "체크카드 신상품": DEBIT_CARD_KEYWORDS,
    "원더카드 고객반응": WONDER_CARD_FEEDBACK_KEYWORDS,
    "JADE 고객반응": JADE_CARD_FEEDBACK_KEYWORDS,
}
