import json
import re
from datetime import datetime, timedelta

import pandas as pd

from batch.dml import fetch_df, mark_posted
from batch.scorer import extract_high_score_data
from batch.security_monitor.keywords import ISSUE_KEYWORDS
from batch.security_monitor.prompt import SECURITY_PROMPT, SECURITY_TEXT_INPUT
from batch.utils import extract_urls
from batch.variables import EXTRACTED_DATA_COUNT
from bot.services.core.openai_client import async_openai_response
from logger import logger


async def get_security_messages(tag: bool = True) -> list[str]:
    data = fetch_df("security_monitor")

    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=ISSUE_KEYWORDS,
        product_keywords=["카드사", "카드업", "하나카드"],
        extracted_data_count=EXTRACTED_DATA_COUNT,
    )

    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    refined_data["post_date"] = refined_data["post_date"].fillna("").astype(str)

    refined_data["date_key"] = (
        refined_data["post_date"]
        .replace("", pd.NA)
        .fillna(refined_data["scrap_date"])
        .astype(str)
    )

    refined_data = refined_data.loc[refined_data["date_key"] >= yesterday]

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return []

    columns = ["title", "url", "description"]
    if "name" in refined_data.columns:
        columns.append("name")

    content = json.dumps(
        refined_data[columns].to_dict(orient="records"),
        ensure_ascii=False,
    )

    result = await async_openai_response(
        prompt=SECURITY_PROMPT,
        input=SECURITY_TEXT_INPUT.format(
            issue_keywords=", ".join(ISSUE_KEYWORDS),
            content=content,
        ),
    )

    entries = re.split(r"\n\s*\n|[-]{6,}", result.strip())
    entries = [e.strip() for e in entries if e.strip()]

    urls = extract_urls(result)
    if len(urls) == 0:
        return []

    logger.info(f"{len(urls)} found in the message.")
    if tag:
        mark_posted("security_monitor", urls)

    return entries
