import json
from datetime import datetime

import pandas as pd

from batch.product.keywords import CARD_COMPANIES, KEYWORDS_BY_BUTTON
from batch.product.prompt import OTHER_TEXT_INPUT, PROMPT, US_TEXT_INPUT
from batch.scorer import extract_high_score_data
from batch.utils import read_csv
from batch.variables import (
    EXTRACTED_DATA_COUNT,
    PRODUCT_OTHER_DATA_PATH,
    PRODUCT_US_DATA_PATH,
)
from bot.services.core.openai_client import openai_response


def identify_company(text: str) -> str:
    for company in CARD_COMPANIES:
        if company in text:
            return company
    return "기타"


def get_product_message(
    data: pd.DataFrame,
    button_label: str,
    keywords: list[str],
    tag: bool = True,
    extracted_data_count: int = EXTRACTED_DATA_COUNT,
) -> list[str]:
    if len(data) == 0:
        return [f"[{button_label}]\n오늘은 관련 소식이 없어요 😊"]

    # 스코어링 적용
    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=keywords,
        product_keywords=CARD_COMPANIES,
        extracted_data_count=extracted_data_count,
    )

    if len(refined_data) == 0:
        return [
            f"[{button_label}]\n유의미한 문서를 찾지 못했어요. 다음에 다시 시도할게요."
        ]

    refined_data["company"] = refined_data["title"].apply(identify_company)

    content = json.dumps(
        refined_data[["company", "title", "link", "description"]].to_dict(
            orient="records"
        ),
        ensure_ascii=False,
    )

    if button_label in ["원더카드 고객반응", "JADE 고객반응"]:
        prompt = US_TEXT_INPUT
        text_input = US_TEXT_INPUT.format(
            date=datetime.today().strftime("%Y년 %m월 %d일"),
            product_name=button_label.replace(" 고객반응", ""),
            count=len(refined_data),
            content=content,
        )

        product_name = button_label[:4]

        header = (
            f"안녕하세요, 줍줍이입니다. "
            f"{datetime.today().strftime('%Y년 %m월 %d일')} "
            f'줍줍한 당사 중점상품 "{product_name}" 고객 반응을 공유드릴게요.\n\n'
            f"수집한 문서 {len(refined_data)}개를 집중 분석한 결과입니다.\n"
        )

    else:
        prompt = PROMPT
        text_input = OTHER_TEXT_INPUT.format(
            count=len(refined_data),
            companies=", ".join(sorted(set(refined_data["company"]))),
            content=content,
        )

        header = (
            f"안녕하세요, 줍줍이입니다. "
            f"{datetime.today().strftime('%Y년 %m월 %d일')} "
            f"줍줍한 경쟁사 신상품 고객 반응을 공유드릴게요.\n\n"
            f"수집한 문서 {len(refined_data)}개를 집중 분석한 결과입니다.\n"
        )

    result = openai_response(prompt=prompt, input=text_input)
    message = f"[{button_label}]\n{header}\n{result}"

    return [message]


def load_and_send_message(button_label: str) -> list[str]:
    """버튼 라벨에 따라 적절한 데이터 로드 및 메시지 생성"""
    keywords = KEYWORDS_BY_BUTTON[button_label]

    if button_label in ["원더카드 고객반응", "JADE 고객반응"]:
        data_path = PRODUCT_US_DATA_PATH
    else:
        data_path = PRODUCT_OTHER_DATA_PATH

    data = read_csv(data_path)

    return get_product_message(
        data=data,
        button_label=button_label,
        keywords=keywords,
    )
