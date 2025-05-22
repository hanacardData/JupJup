from datetime import datetime

from fastapi_cache.decorator import cache
from korean_lunar_calendar import KoreanLunarCalendar

from bot.services.core.openai_client import async_openai_response
from bot.services.fortune.prompt import PROMPT_FORTUNE, TEXT_INPUT
from bot.services.fortune.variables import (
    BRANCH_TO_ELEMENT,
    FIVE_ELEMENTS,
    STEM_TO_ELEMENT,
)


@cache(expire=86400)
async def parse_date(date_str: str) -> tuple[int, int, int]:
    if len(date_str) != 8:
        raise ValueError("Date string must be in YYYYMMDD format.")

    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    return year, month, day


async def update_five_elements(
    pillar: str, element_scores: dict[str, int]
) -> dict[str, int]:
    stem, branch = pillar[0], pillar[1]
    element_scores[STEM_TO_ELEMENT[stem]] += 1  # 천간의 기여도
    element_scores[BRANCH_TO_ELEMENT[branch]] += 1  # 지지의 기여도
    return element_scores


@cache(expire=86400)
async def calculate_four_pillars_with_elements(
    birthday: str,
) -> dict[str, str | dict[str, int]]:
    """만세력 측정 함수"""
    calendar = KoreanLunarCalendar()

    year, month, day = await parse_date(birthday)
    calendar.setSolarDate(year, month, day)

    _gapja_string = calendar.getGapJaString()
    pillars = [_[:2] for _ in _gapja_string.split(" ")]
    year_pillar = pillars[0]
    month_pillar = pillars[1]
    day_pillar = pillars[2]

    element_scores = FIVE_ELEMENTS.copy()
    element_scores = await update_five_elements(year_pillar, element_scores)
    element_scores = await update_five_elements(month_pillar, element_scores)
    element_scores = await update_five_elements(day_pillar, element_scores)

    return {
        "연주": year_pillar,
        "월주": month_pillar,
        "일주": day_pillar,
        "오행 점수": element_scores,
    }


async def get_fortune_comment(input: str) -> str:
    user_manse = await calculate_four_pillars_with_elements(birthday=input)
    today_manse = await calculate_four_pillars_with_elements(
        birthday=datetime.today().strftime("%Y%m%d")
    )
    text_input = TEXT_INPUT.format(manse=user_manse, today_manse=today_manse)
    return await async_openai_response(prompt=PROMPT_FORTUNE, input=text_input)
