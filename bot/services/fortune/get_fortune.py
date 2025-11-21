import re
from datetime import datetime

from fastapi_cache.decorator import cache
from korean_lunar_calendar import KoreanLunarCalendar

from bot.services.core.openai_client import async_openai_response
from bot.services.fortune.prompt import PROMPT_FORTUNE, TEXT_INPUT
from bot.services.fortune.variables import (
    BRANCH_TO_ELEMENT,
    FIVE_ELEMENTS,
    HOUR_BRANCHES,
    HOUR_STEM_TABLE,
    STEM_TO_ELEMENT,
)


async def update_five_elements(
    pillar: str, element_scores: dict[str, int]
) -> dict[str, int]:
    stem, branch = pillar[0], pillar[1]
    element_scores[STEM_TO_ELEMENT[stem]] += 1  # 천간의 기여도
    element_scores[BRANCH_TO_ELEMENT[branch]] += 1  # 지지의 기여도
    return element_scores


async def _calculate_hour_pillar(hour: int, day_stem: str) -> str:
    # 시간에 따라 시지를 결정
    for start, end, branch in HOUR_BRANCHES:
        if start <= hour < end:
            hour_branch = branch
            break

    # 일간에 따라 천간 결정
    hour_stem_index = HOUR_BRANCHES.index((start, end, branch))  # 시지의 인덱스
    hour_stem = HOUR_STEM_TABLE[day_stem][hour_stem_index]

    # 시주 (천간 + 지지) 반환
    return f"{hour_stem}{hour_branch}"


@cache(expire=86400)
async def calculate_four_pillars_with_elements(
    year: int,
    month: int,
    day: int,
    hour: int | None = None,
) -> dict[str, str | dict[str, int]]:
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)

    gapja_string = calendar.getGapJaString()
    pillars = gapja_string.split(" ")
    year_pillar = pillars[0]
    month_pillar = pillars[1]
    day_pillar = pillars[2]

    element_scores = FIVE_ELEMENTS.copy()
    element_scores = await update_five_elements(year_pillar, element_scores)
    element_scores = await update_five_elements(month_pillar, element_scores)
    element_scores = await update_five_elements(day_pillar, element_scores)
    result = {
        "사주": gapja_string,
        "연주": year_pillar,
        "월주": month_pillar,
        "일주": day_pillar,
    }
    if hour is None:
        result.update({"오행 점수": element_scores})
        return result

    hour_pillar = await _calculate_hour_pillar(hour, day_pillar[0])
    element_scores = await update_five_elements(day_pillar, element_scores)
    result.update(
        {
            "시주": hour_pillar,
            "오행 점수": element_scores,
        }
    )
    return result


async def get_fortune_comment(input: str) -> str:
    if not re.match(r"^\d{8}$|^\d{10}$", input):
        return "날짜 형식이 잘못되었어요! YYYYMMDDHH 형식으로 다시 입력해주세요."
    try:
        year = int(input[:4])
        month = int(input[4:6])
        day = int(input[6:8])
        hour = int(input[8:10]) if len(input) == 10 else None
        datetime(year, month, day)
        today = datetime.today()
    except ValueError:
        return "존재하지 않는 날짜예요. 올바른 날짜를 입력해주세요 (예: 20230230은 잘못된 날짜입니다)."

    user_manse = await calculate_four_pillars_with_elements(
        year=year, month=month, day=day, hour=hour
    )
    today_manse = await calculate_four_pillars_with_elements(
        year=today.year, month=today.month, day=today.day
    )
    text_input = TEXT_INPUT.format(
        manse=user_manse,
        birthday=input,
        today_manse=today_manse,
        today=today.strftime("%Y%m%d"),
    )
    return await async_openai_response(prompt=PROMPT_FORTUNE, input=text_input)
