import json
import os
from datetime import datetime, timedelta
from typing import Literal

import pandas as pd

from batch.product.keywords import BUTTON_TAG_MAP, CARD_COMPANIES, KEYWORDS_BY_BUTTON
from batch.product.prompt import (
    OTHER_PROMPT,
    OTHER_TEXT_INPUT,
    US_PROMPT,
    US_TEXT_INPUT,
)
from batch.scorer import extract_high_score_data
from batch.utils import extract_urls, read_csv
from batch.variables import (
    EXTRACTED_DATA_COUNT,
    PRODUCT_SAVE_PATH,
)
from bot.services.core.openai_client import async_openai_response
from logger import logger


async def process_generate_message(
    button_label: Literal[
        "원더카드 고객반응", "JADE 고객반응", "경쟁사신용", "경쟁사체크"
    ],
) -> list[str]:
    try:
        keywords = KEYWORDS_BY_BUTTON[button_label]
        tag = BUTTON_TAG_MAP[button_label]
        is_our_product: bool = button_label in ["원더카드 고객반응", "JADE 고객반응"]
        extracted_data_count = 12 if is_our_product else EXTRACTED_DATA_COUNT
        file_name = os.path.join(PRODUCT_SAVE_PATH, f"{tag}.csv")
        data = read_csv(file_name)
        data = _filter_last_n_days_postdate(data, 7)

        if data.empty:
            logger.warning("No data after 7-day postdate filter.")
            return [f"[{button_label}]\n최근 7일 내 소식이 없어요 😊"]

        total_count = len(data)
        refined_data = extract_high_score_data(
            data, keywords, CARD_COMPANIES, extracted_data_count
        )

        actual_count = len(refined_data)
        if actual_count == 0:
            logger.warning("No data found after filtering.")
            return [
                f"오늘은 {button_label} 관련 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"
            ]
        refined_data["companies"] = refined_data.apply(
            lambda r: _identify_companies(
                f"{r.get('title', '')} {r.get('description', '')}"
            ),
            axis=1,
        )
        content = json.dumps(
            refined_data[["companies", "title", "link", "description"]].to_dict(
                orient="records"
            ),
            ensure_ascii=False,
        )
        if is_our_product:
            product_name = button_label.replace(" 고객반응", "")
            text_input = US_TEXT_INPUT.format(
                date=datetime.today().strftime("%Y년 %m월 %d일"),
                product_name=product_name,
                count=actual_count,
                content=content,
            )
        else:
            companies = ", ".join(
                sorted(
                    {
                        company
                        for company_list in refined_data["companies"]
                        for company in company_list
                    }
                )
            )
            text_input = OTHER_TEXT_INPUT.format(
                count=actual_count, companies=companies, content=content
            )
        header = _make_header(
            button_label=button_label,
            expected=total_count,
            actual=actual_count,
        )

        result = await async_openai_response(
            prompt=US_PROMPT if is_our_product else OTHER_PROMPT, input=text_input
        )
        urls = extract_urls(result)
        data.loc[data["link"].isin(urls), "is_posted"] = 1
        data.to_csv(file_name, index=False, encoding="utf-8")
        return [f"[{button_label}]\n{header}\n{result}"]
    except Exception as e:
        logger.error(f"Error in process_generate_message for {button_label}: {e}")
        return [
            f"[{button_label}]\n 메시지 생성 중 오류가 발생했어요. 관리자에게 문의해주세요."
        ]


def _identify_companies(text: str) -> list[str]:
    return [company for company in CARD_COMPANIES if company in text]


def _filter_last_n_days_postdate(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    if df is None or df.empty or "post_date" not in df.columns:
        logger.error("post_date not in column!")
        raise Exception("post_date not in column!")
    dt = pd.to_datetime(df["post_date"], format="%Y%m%d", errors="coerce")
    cutoff = (datetime.now() - timedelta(days=days)).date()
    mask = dt.dt.date >= cutoff
    return df.loc[mask].copy()


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
