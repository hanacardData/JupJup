import json
import re
from datetime import datetime, timedelta

import pandas as pd

from bot.services.core.openai_client import openai_response
from data_collect.scorer import extract_high_score_data
from data_collect.travellog.keywords import TRAVELLOG_ISSUE_KEYWORDS, TRAVELLOG_KEYWORDS
from data_collect.travellog.prompt import PROMPT, TEXT_INPUT
from data_collect.utils import extract_urls
from data_collect.variables import EXTRACTED_DATA_COUNT, TRAVELLOG_DATA_PATH
from logger import logger


def get_travellog_message(data: pd.DataFrame, tag: bool = True) -> list[str]:
    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=TRAVELLOG_ISSUE_KEYWORDS,
        product_keywords=TRAVELLOG_KEYWORDS,
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
            card_products=", ".join(TRAVELLOG_KEYWORDS),
            content=content,
        ),
    )
    message = [
        f"안녕하세요! 줍줍이입니다 🤗\n{datetime.today().strftime('%Y년 %m월 %d일')} 줍줍한 트래블로그 이슈를 공유드릴게요!\n"
    ]
    entries = re.split(r"\n\s*\n|[-]{6,}", result.strip())
    entries = [e.strip() for e in entries if e.strip()]
    entries = [f"번호: {i + 1}\n{e}" for i, e in enumerate(entries)]

    urls = extract_urls(result)
    if len(urls) == 0:
        logger.warning("No URLs found in the message.")
    else:
        if len(urls) != 2:
            logger.warning("Not expected number of URLs found in the message.")
        if tag:
            data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(TRAVELLOG_DATA_PATH, index=False, encoding="utf-8")
    return message + entries
