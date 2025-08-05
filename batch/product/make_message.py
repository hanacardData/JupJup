import json
from datetime import datetime

import pandas as pd

from batch.product.keywords import CARD_COMPANIES
from batch.product.prompt import PROMPT, TEXT_INPUT
from batch.scorer import extract_high_score_data
from batch.utils import extract_urls
from batch.variables import DATA_PATH, EXTRACTED_DATA_COUNT
from bot.services.core.openai_client import openai_response
from logger import logger


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

    result = openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(
            count=len(refined_data),
            companies=", ".join(sorted(set(refined_data["company"]))),
            content=content,
        ),
    )

    message = (
        f"[{button_label}]\n"
        f"{datetime.today().strftime('%Y년 %m월 %d일')} 카드 관련 뉴스를 분석했어요.\n\n"
        + result
    )
    urls = extract_urls(result)

    if len(urls) == 0:
        logger.warning("No URLs found in the message.")
        return "오늘은 주목할만한 이슈가 없거나 ChatGPT 쪽 문제가 있는거 같아요. 확인하고 다시 찾아올게요 😊"
    else:
        if len(urls) != 2:
            logger.warning("Not expected number of URLs found in the message.")
        if tag:
            data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(DATA_PATH, index=False, encoding="utf-8")
    return [message]
