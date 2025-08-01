import json
import re
from datetime import datetime, timedelta

import pandas as pd

from batch.scorer import extract_high_score_data
from batch.security_monitor.keywords import CARD_PRODUCTS, ISSUE_KEYWORDS
from batch.security_monitor.prompt import SECURITY_PROMPT, SECURITY_TEXT_INPUT
from batch.variables import EXTRACTED_DATA_COUNT, SECURITY_DATA_PATH
from bot.services.core.openai_client import openai_response
from logger import logger


def generate_security_alert_messages(data: pd.DataFrame, tag: bool = True) -> list[str]:
    refined_data = extract_high_score_data(
        data=data,
        issue_keywords=ISSUE_KEYWORDS,
        product_keywords=CARD_PRODUCTS,
        extracted_data_count=EXTRACTED_DATA_COUNT,
    )

    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    refined_data["post_date"] = (
        refined_data["post_date"].fillna(refined_data["scrap_date"]).astype(str)
    )
    refined_data = refined_data.loc[refined_data["post_date"] >= yesterday]

    if len(refined_data) == 0:
        logger.warning("No data found after filtering.")
        return "오늘은 보안과 관련한 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊"

    columns = ["title", "link", "description"]
    if "name" in refined_data.columns:
        columns.append("name")

    content = json.dumps(
        refined_data[columns].to_dict(orient="records"),
        ensure_ascii=False,
    )

    result = openai_response(
        prompt=SECURITY_PROMPT,
        input=SECURITY_TEXT_INPUT.format(
            card_products=", ".join(ISSUE_KEYWORDS),
            content=content,
        ),
    )

    messages: list[str] = []
    entries = re.split(r"\n\s*\n|[-]{6,}", result.strip())
    entries = [e.strip() for e in entries if e.strip()]
    entries = [f"번호: {i + 1}\n{e}" for i, e in enumerate(entries)]

    for _, row in refined_data.iterrows():
        content = f"- 제목: {row['title']}\n- 내용: {row['description']}\n- 링크: {row['link']}"
        prompt_input = SECURITY_TEXT_INPUT.format(content=content)
        result = openai_response(prompt=SECURITY_PROMPT, input=prompt_input)

        if result:
            messages.append(
                f"📌 {datetime.today().strftime('%Y-%m-%d')} 보안 이슈 알림\n\n{result}"
            )
            if tag:
                data.loc[data["link"] == row["link"], "is_posted"] = 1

    data.to_csv(SECURITY_DATA_PATH, index=False, encoding="utf-8")
    return messages
