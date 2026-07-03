from datetime import datetime, timedelta

from batch.compare_travel.keywords import (
    COMPARE_TRAVEL_TREND_KEYWORDS,
)
from batch.compare_travel.prompt import PROMPT, TEXT_INPUT
from batch.fetch import fetch_trend_data
from bot.services.core.openai_client import async_openai_response


async def _get_trend_message() -> str:
    today = datetime.today().strftime("%Y-%m-%d")
    one_week_ago = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    trend_response = fetch_trend_data(
        startDate=one_week_ago,
        endDate=today,
        timeUnit="date",
        keywordGroups=COMPARE_TRAVEL_TREND_KEYWORDS,
    )
    if not trend_response:
        return ""

    return await async_openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(content=trend_response.to_results()),
    )


async def get_compare_travel_message() -> list[str]:
    trend_message = await _get_trend_message()
    message = [
        "트래블카드의 최근 7일 간 네이버 검색어 트렌드 분석 결과를 확인해보세요! 📊\n",
        trend_message,
    ]
    return message
