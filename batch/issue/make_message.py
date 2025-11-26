import json
from datetime import datetime

import pandas as pd

from batch.issue.keywords import CARD_PRODUCTS, ISSUE_KEYWORDS
from batch.issue.prompt import PROMPT, TEXT_INPUT
from batch.scorer import extract_high_score_data
from batch.utils import extract_urls
from batch.variables import DATA_PATH, EXTRACTED_DATA_COUNT
from bot.services.core.openai_client import async_openai_response
from logger import logger


async def get_issue_message(data: pd.DataFrame, tag: bool = True) -> list[str]:
    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=ISSUE_KEYWORDS,
        product_keywords=CARD_PRODUCTS,
        extracted_data_count=EXTRACTED_DATA_COUNT,
    )
    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return ["오늘은 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"]

    content = json.dumps(
        refined_data[["title", "link", "description"]].to_dict(orient="records"),
        ensure_ascii=False,
    )
    result = await async_openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(
            card_products=", ".join(CARD_PRODUCTS),
            content=content,
        ),
    )
    message = (
        f"안녕하세요! 줍줍이입니다 🤗\n{datetime.today().strftime('%Y년 %m월 %d일')} 줍줍한 이슈를 공유드릴게요!\n수집한 총 {len(data)}개의 문서 중 {EXTRACTED_DATA_COUNT}개를 집중 분석한 결과입니다!\n"
        + result
    )
    urls = extract_urls(result)

    if len(urls) == 0:
        logger.warning("No URLs found in the message.")
        return ["오늘은 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"]
    else:
        if len(urls) != 2:
            logger.warning("Not expected number of URLs found in the message.")
        if tag:
            data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(DATA_PATH, index=False, encoding="utf-8")
    return [message]
