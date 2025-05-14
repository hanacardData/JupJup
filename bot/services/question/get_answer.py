import json
from datetime import datetime

import pandas as pd
from fastapi_cache.decorator import cache

from bot.services.core.openai_client import async_openai_response
from bot.services.question.prompt import PROMPT
from data_collect.issue.make_message import extract_high_score_data
from data_collect.variables import DATA_PATH


@cache(expire=43_200)
async def get_prompt_content() -> str:
    data = pd.read_csv(DATA_PATH)
    refined_data = extract_high_score_data(data, extracted_data_count=10)
    content = json.dumps(
        refined_data[["title", "link", "description"]]
        .astype(str)
        .to_dict(orient="records"),
        ensure_ascii=False,
    )
    return (
        f"데이터 수집 날짜: {datetime.today().strftime('%Y년 %m월 %d일')}\n"
        + f"수집 데이터 수: {len(data)}\n"
        + f"수집 데이터 예시: {content}\n"
    )


async def get_answer(input: str) -> str:
    content = await get_prompt_content()
    return await async_openai_response(
        prompt=PROMPT.format(content=content),
        input=input,
    )
