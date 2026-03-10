import json
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from batch.dml import mark_posted
from batch.scorer import extract_high_score_data
from batch.travellog.keywords import TRAVELLOG_ISSUE_KEYWORDS, TRAVELLOG_KEYWORDS
from batch.travellog.prompt import PROMPT, TEXT_INPUT
from batch.utils import extract_urls
from batch.variables import EXTRACTED_DATA_COUNT
from bot.services.core.openai_client import async_openai_response
from logger import logger


async def get_travellog_message(data: pd.DataFrame, tag: bool = True) -> list[str]:
    data = data[data["is_posted"] == 0].copy()
    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=TRAVELLOG_ISSUE_KEYWORDS,
        product_keywords=TRAVELLOG_KEYWORDS + ["트레블로그", "트레블고", "트레블GO"],
        extracted_data_count=EXTRACTED_DATA_COUNT,
    )

    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    refined_data["post_date"] = np.where(
        (refined_data["post_date"] == "") | (refined_data["post_date"].isna()),
        refined_data["scrap_date"].astype(str),
        refined_data["post_date"],
    )
    refined_data = refined_data.loc[refined_data["post_date"] >= yesterday]

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return "오늘은 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"

    content = json.dumps(
        refined_data[["title", "url", "description", "name"]].to_dict(orient="records"),
        ensure_ascii=False,
    )
    result = await async_openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(
            card_products=", ".join(TRAVELLOG_KEYWORDS),
            content=content,
        ),
    )

    entries = re.split(r"\n\s*\n|[-]{6,}", result.strip())
    entries = [e.strip() for e in entries if e.strip()]
    entries = [f"번호: {i + 1}\n{e}" for i, e in enumerate(entries)]

    urls = extract_urls(result)
    if len(urls) == 0:
        logger.warning(f"No URLs found in the message in {result}.")
        return ["오늘은 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"]
    else:
        logger.info(f"{len(urls)} found in the message.")
        if tag:
            mark_posted("travellog", urls)

    return entries
