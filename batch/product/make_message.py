import json
import os
from datetime import datetime, timedelta

import pandas as pd

from batch.product.keywords import BUTTON_TAG_MAP, CARD_COMPANIES, KEYWORDS_BY_BUTTON
from batch.product.prompt import OTHER_TEXT_INPUT, PROMPT, US_TEXT_INPUT
from batch.scorer import extract_high_score_data
from batch.utils import read_csv
from batch.variables import (
    EXTRACTED_DATA_COUNT,
    PRODUCT_SAVE_PATH,
)
from bot.services.core.openai_client import openai_response
from logger import logger


def identify_company(text: str) -> str:
    for company in CARD_COMPANIES:
        if company in text:
            return company
    return "기타"


def load_and_send_message(button_label: str) -> list[str]:
    """버튼 라벨에 따라 분기 처리"""
    if button_label in ["원더카드 고객반응", "JADE 고객반응"]:
        return _handle_our_product(button_label)
    else:
        return _handle_competitor_product(button_label)


def _handle_competitor_product(button_label: str) -> list[str]:
    keywords = KEYWORDS_BY_BUTTON[button_label]
    tag = BUTTON_TAG_MAP[button_label]
    extracted_data_count = EXTRACTED_DATA_COUNT
    dfs = _load_dataframes(tag)

    if not dfs:
        logger.warning("No data collected.")
        return [f"[{button_label}]\n오늘은 관련 소식이 없어요 😊"]

    data = pd.concat(dfs, ignore_index=True)
    total_count = len(data)

    refined_data = extract_high_score_data(
        data, keywords, CARD_COMPANIES, extracted_data_count
    )

    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    refined_data["post_date"] = (
        refined_data["post_date"].fillna(refined_data["scrap_date"]).astype(str)
    )
    refined_data = refined_data.loc[refined_data["post_date"] >= yesterday]

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return [
            "오늘은 보안과 관련한 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"
        ]

    refined_data["company"] = refined_data["title"].apply(identify_company)
    actual_count = len(refined_data)
    companies = ", ".join(sorted(set(refined_data["company"])))

    content = _to_json(refined_data)
    text_input = OTHER_TEXT_INPUT.format(
        count=actual_count, companies=companies, content=content
    )

    header = _make_header(
        button_label=button_label,
        expected=total_count,
        actual=actual_count,
    )

    result = openai_response(prompt=PROMPT, input=text_input)
    return [f"[{button_label}]\n{header}\n{result}"]


def _handle_our_product(button_label: str) -> list[str]:
    keywords = KEYWORDS_BY_BUTTON[button_label]
    tag = BUTTON_TAG_MAP[button_label]
    extracted_data_count = 12
    dfs = _load_dataframes(tag)

    if not dfs:
        logger.warning("No data collected.")
        return [f"[{button_label}]\n오늘은 관련 소식이 없어요 😊"]

    data = pd.concat(dfs, ignore_index=True)
    total_count = len(data)

    refined_data = extract_high_score_data(
        data, keywords, CARD_COMPANIES, extracted_data_count
    )
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    refined_data["post_date"] = (
        refined_data["post_date"].fillna(refined_data["scrap_date"]).astype(str)
    )
    refined_data = refined_data.loc[refined_data["post_date"] >= yesterday]

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return [
            "오늘은 보안과 관련한 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"
        ]

    refined_data["company"] = refined_data["title"].apply(identify_company)
    actual_count = len(refined_data)
    product_name = button_label.replace(" 고객반응", "")

    content = _to_json(refined_data)
    text_input = US_TEXT_INPUT.format(
        date=datetime.today().strftime("%Y년 %m월 %d일"),
        product_name=product_name,
        count=actual_count,
        content=content,
    )

    header = _make_header(
        button_label=button_label,
        expected=total_count,
        actual=actual_count,
    )

    result = openai_response(prompt=US_TEXT_INPUT, input=text_input)
    return [f"[{button_label}]\n{header}\n{result}"]


def _load_dataframes(tag: str) -> list[pd.DataFrame]:
    sources = ["news", "blog"]
    dfs = []
    for source in sources:
        path = os.path.join(PRODUCT_SAVE_PATH, f"{source}_{tag}.csv")
        df = read_csv(path)
        if df is not None and not df.empty:
            dfs.append(df)
    return dfs


def _to_json(df: pd.DataFrame) -> str:
    return json.dumps(
        df[["company", "title", "link", "description"]].to_dict(orient="records"),
        ensure_ascii=False,
    )


def _make_header(button_label: str, expected: int, actual: int) -> str:
    date = datetime.today().strftime("%Y년 %m월 %d일")

    if button_label in ["신용카드 신상품", "체크카드 신상품"]:
        product_type = "경쟁사 신상품"
        title = product_type
    elif button_label in ["원더카드 고객반응", "JADE 고객반응"]:
        product_type = "자사 중점상품"
        title = button_label.replace(" 고객반응", "")

    return (
        f"안녕하세요, 줍줍이입니다. {date} "
        f'줍줍한 {product_type} "{title}" 고객 반응을 공유드릴게요.\n\n'
        f"수집한 문서 {expected}개 중 의미 있는 {actual}개를 집중 분석한 결과입니다.\n"
    )
