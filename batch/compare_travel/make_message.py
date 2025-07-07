import json
import re
from datetime import datetime, timedelta

import pandas as pd

from batch.compare_travel.keywords import (
    COMPARE_TRAVEL_ISSUE_KEYWORDS,
    COMPARE_TRAVEL_KEYWORDS,
    COMPARE_TRAVEL_TREND_KEYWORDS,
)
from batch.compare_travel.prompt import PROMPT, TEXT_INPUT
from batch.fetch import fetch_trend_data
from batch.scorer import extract_high_score_data
from batch.utils import extract_urls
from batch.variables import EXTRACTED_DATA_COUNT, TRAVELLOG_DATA_PATH
from bot.services.core.openai_client import openai_response
from logger import logger


def _get_trend_message():
    today = datetime.today().strftime("%Y-%m-%d")
    one_week_ago = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    trend_response = fetch_trend_data(
        startDate=one_week_ago,
        endDate=today,
        timeUnit="date",
        keywordGroups=COMPARE_TRAVEL_TREND_KEYWORDS,
    )
    return openai_response(
        prompt="트래블카드의 최근 7일간의 트렌드 데이터 정보를 분석해줘.",
        input=f"""트래블카드의 최근 7일간 검색어 트렌드 정보를 토대로 카드를 비교해줘. {trend_response.to_results()}""",
    )


def get_compare_travel_message(data: pd.DataFrame, tag: bool = True) -> list[str]:
    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=COMPARE_TRAVEL_ISSUE_KEYWORDS,
        product_keywords=COMPARE_TRAVEL_KEYWORDS,
        extracted_data_count=EXTRACTED_DATA_COUNT,
    )
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    refined_data["post_date"] = (
        refined_data["post_date"].fillna(refined_data["scrap_date"]).astype(str)
    )
    refined_data = refined_data.loc[refined_data["post_date"] >= yesterday]

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return "오늘은 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"

    content = json.dumps(
        refined_data[["title", "link", "description", "name"]].to_dict(
            orient="records"
        ),
        ensure_ascii=False,
    )
    result = openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(
            card_products=", ".join(COMPARE_TRAVEL_KEYWORDS),
            content=content,
        ),
    )
    message = [
        f"안녕하세요! 줍줍이입니다 🤗\n{datetime.today().strftime('%Y년 %m월 %d일')} 줍줍한 트래블카드 정보를 공유드릴게요!\n",
        _get_trend_message(),
    ]

    entries = re.split(r"\n\s*\n|[-]{6,}", result.strip())
    entries = [e.strip() for e in entries if e.strip()]
    entries = [f"번호: {i + 1}\n{e}" for i, e in enumerate(entries)]

    urls = extract_urls(result)
    if len(urls) == 0:
        logger.warning("No URLs found in the message.")
        return [
            "오늘은 주목할만한 이슈가 없거나 ChatGPT 쪽 문제가 있는거 같아요. 확인하고 다시 찾아올게요 😊"
        ]
    else:
        logger.info(f"{len(urls)} found in the message.")
        if tag:
            data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(TRAVELLOG_DATA_PATH, index=False, encoding="utf-8")
    return message + entries
