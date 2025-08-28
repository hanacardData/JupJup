import json
import os
from datetime import datetime

import pandas as pd

from batch.product.keywords import BUTTON_TAG_MAP, CARD_COMPANIES, KEYWORDS_BY_BUTTON
from batch.product.prompt import (
    OTHER_PROMPT,
    OTHER_TEXT_INPUT,
    US_PROMPT,
    US_TEXT_INPUT,
)
from batch.product.utils import (
    fill_postdate_from_pubdate,
    filter_last_n_days_postdate,
)
from batch.scorer import extract_high_score_data
from batch.utils import read_csv
from batch.variables import (
    EXTRACTED_DATA_COUNT,
    PRODUCT_SAVE_PATH,
)
from bot.services.core.openai_client import openai_response
from logger import logger


def _identify_company(text: str) -> str:
    for company in CARD_COMPANIES:
        if company in text:
            return company
    return "기타"


def _to_json(df: pd.DataFrame) -> str:
    return json.dumps(
        df[["company", "title", "link", "description"]].to_dict(orient="records"),
        ensure_ascii=False,
    )


def _make_header(button_label: str, expected: int, actual: int) -> str:
    date = datetime.today().strftime("%Y년 %m월 %d일")
    button_label_map: dict[str, tuple[str, str]] = {
        "신용카드 신상품": ("경쟁사 신상품", ""),
        "체크카드 신상품": ("경쟁사 신상품", ""),
        "원더카드 고객반응": ("자사 중점상품", "원더카드"),
        "JADE 고객반응": ("자사 중점상품", "JADE"),
    }
    product_type, title = button_label_map[button_label]
    return (
        f"안녕하세요, 줍줍이입니다. {date} "
        f"줍줍한 {product_type} {title} 고객 반응을 공유드릴게요.\n\n"
        f"수집한 문서 {expected}개 중 의미 있는 {actual}개를 집중 분석한 결과입니다.\n"
    ).replace("  ", " ")


def _load_dataframes(tag: str) -> list[pd.DataFrame]:
    sources = ["news", "blog"]
    dfs: list[pd.DataFrame] = []

    for source in sources:
        path = os.path.join(PRODUCT_SAVE_PATH, f"{source}_{tag}.csv")
        if not os.path.exists(path):
            continue

        df = read_csv(path)
        if df is not None and not df.empty:
            df = fill_postdate_from_pubdate(df)
            dfs.append(df)

    return dfs


def _update_is_posted(tag: str, used_links: list[str]) -> None:
    if not used_links:
        return

    for source in ("news", "blog"):
        fpath = os.path.join(PRODUCT_SAVE_PATH, f"{source}_{tag}.csv")
        if not os.path.exists(fpath):
            continue

        df = read_csv(fpath)
        if df is None or df.empty or "link" not in df.columns:
            continue

        if "is_posted" not in df.columns:
            df["is_posted"] = 0

        mask = df["link"].astype(str).isin([str(u) for u in used_links])
        changed = int(mask.sum())
        if changed:
            df.loc[mask, "is_posted"] = 1
            try:
                df["is_posted"] = df["is_posted"].astype(int)
            except Exception:
                pass
            df.to_csv(fpath, index=False, encoding="utf-8")
        logger.info(f"{os.path.basename(fpath)}: is_posted updated {changed} rows")


def load_and_send_message(button_label: str) -> list[str]:
    """버튼 라벨에 따라 분기 처리"""
    if button_label in ["원더카드 고객반응", "JADE 고객반응"]:
        return _handle_our_product(button_label)
    else:
        return _handle_competitor_product(button_label)


def _handle_competitor_product(button_label: str) -> list[str]:
    keywords = KEYWORDS_BY_BUTTON[button_label]
    tag = BUTTON_TAG_MAP[button_label]
    dfs = _load_dataframes(tag)

    if not dfs:
        logger.warning("No source files found.")
        return [f"[{button_label}]\n최근 7일 내 소식이 없어요 😊"]

    data = pd.concat(dfs, ignore_index=True)
    data = filter_last_n_days_postdate(data, 7)

    if data.empty:
        logger.warning("No data after 7-day postdate filter.")
        return [f"[{button_label}]\n최근 7일 내 소식이 없어요 😊"]
    total_count = len(data)

    data = data.rename(columns={"postdate": "post_date"})

    refined_data = extract_high_score_data(
        data, keywords, CARD_COMPANIES, EXTRACTED_DATA_COUNT
    )
    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return [
            "오늘은 타사 신상품 관련 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"
        ]

    refined_data["company"] = refined_data["title"].apply(_identify_company)
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

    result = openai_response(prompt=OTHER_PROMPT, input=text_input)

    used_links = ...  # result 에서 url 식별
    try:
        _update_is_posted(tag, used_links)
    except Exception as e:
        logger.warning(f"update_is_posted failed ({tag}): {e}")

    return [f"[{button_label}]\n{header}\n{result}"]


def _handle_our_product(button_label: str) -> list[str]:
    keywords = KEYWORDS_BY_BUTTON[button_label]
    tag = BUTTON_TAG_MAP[button_label]
    extracted_data_count = 12
    dfs = _load_dataframes(tag)

    if not dfs:
        logger.warning("No source files found.")
        return [f"[{button_label}]\n최근 7일 내 소식이 없어요 😊"]

    data = pd.concat(dfs, ignore_index=True)
    data = filter_last_n_days_postdate(data, 7)

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

    refined_data["company"] = refined_data["title"].apply(_identify_company)
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

    result = openai_response(prompt=US_PROMPT, input=text_input)

    used_links = ...  ## FIXME
    try:
        _update_is_posted(tag, used_links)
    except Exception as e:
        logger.warning(f"update_is_posted failed ({tag}): {e}")

    return [f"[{button_label}]\n{header}\n{result}"]
