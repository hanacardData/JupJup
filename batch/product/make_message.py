import json
import os
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

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


def normalize_source_fields(df: pd.DataFrame) -> pd.DataFrame:
    """뉴스 데이터(pubDate)를 YYYYMMDD → postdate 컬럼으로 변환"""
    if "pubDate" not in df.columns:
        return df

    def to_yyyymmdd(x):
        dt = pd.to_datetime(x, errors="coerce")
        if pd.isna(dt):
            dt = parsedate_to_datetime(str(x))
        return dt.strftime("%Y%m%d")

    df["postdate"] = df["pubDate"].map(to_yyyymmdd)
    df = df.drop(columns=["pubDate"])

    return df


def _filter_last_n_days_postdate(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if "postdate" not in df.columns:
        return pd.DataFrame(columns=df.columns)

    s = df["postdate"].astype(str).str.strip().str.replace(r"\D", "", regex=True)
    dt = pd.to_datetime(s, format="%Y%m%d", errors="coerce")
    cutoff = (datetime.now() - timedelta(days=days)).date()

    mask = dt.dt.date >= cutoff
    return df.loc[mask].copy()


def _handle_competitor_product(button_label: str) -> list[str]:
    keywords = KEYWORDS_BY_BUTTON[button_label]
    tag = BUTTON_TAG_MAP[button_label]
    extracted_data_count = EXTRACTED_DATA_COUNT
    dfs = _load_dataframes(tag)

    data = pd.concat(dfs, ignore_index=True)
    data = _filter_last_n_days_postdate(data, 7)

    if data.empty:
        logger.warning("No data after 7-day postdate filter.")
        return [f"[{button_label}]\n최근 7일 내 소식이 없어요 😊"]
    total_count = len(data)

    data = data.rename(columns={"postdate": "post_date"})

    refined_data = extract_high_score_data(
        data, keywords, CARD_COMPANIES, extracted_data_count
    )

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return [
            "오늘은 타사 신상품 관련 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"
        ]

    refined_data["company"] = refined_data["title"].apply(identify_company)
    actual_count = len(refined_data)
    companies = ", ".join(sorted(set(refined_data["company"])))

    content = json.dumps(
        refined_data[["company", "title", "link", "description"]].to_dict(
            orient="records"
        ),
        ensure_ascii=False,
    )
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

    data = pd.concat(dfs, ignore_index=True)

    data = _filter_last_n_days_postdate(data, 7)

    if data.empty:
        logger.warning("No data after 7-day postdate filter.")
        return [f"[{button_label}]\n최근 7일 내 소식이 없어요 😊"]
    total_count = len(data)

    data = data.rename(columns={"postdate": "post_date"})

    refined_data = extract_high_score_data(
        data, keywords, CARD_COMPANIES, extracted_data_count
    )

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return [
            "오늘은 자사 상품 반응 관련 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"
        ]

    refined_data["company"] = refined_data["title"].apply(identify_company)
    actual_count = len(refined_data)
    product_name = button_label.replace(" 고객반응", "")

    content = json.dumps(
        refined_data[["company", "title", "link", "description"]].to_dict(
            orient="records"
        ),
        ensure_ascii=False,
    )
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
    dfs: list[pd.DataFrame] = []

    for source in sources:
        path = os.path.join(PRODUCT_SAVE_PATH, f"{source}_{tag}.csv")

        if not os.path.exists(path):
            continue

        df = read_csv(path)

        if df is not None and not df.empty:
            df = normalize_source_fields(df)
            dfs.append(df)

    return dfs


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
