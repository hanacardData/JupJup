from datetime import datetime

from bot.services.core.openai_client import async_openai_response
from bot.services.fortune.get_fortune import (
    calculate_four_pillars_with_elements,
    is_valid_date_input,
)
from bot.services.harmony.prompt import PROMPT_FORTUNE, TEXT_INPUT


async def get_harmony_comment(input1: str, input2: str) -> str:
    if not is_valid_date_input(input1) or not is_valid_date_input(input2):
        return "날짜 형식이 잘못되었어요! YYYYMMDD 혹은 YYYYMMDDHHmm 형식으로 다시 입력해주세요."
    try:
        year1 = int(input1[:4])
        month1 = int(input1[4:6])
        day1 = int(input1[6:8])
        hour1 = int(input1[8:10]) if len(input1) == 10 else None
        datetime(year1, month1, day1)

        year2 = int(input2[:4])
        month2 = int(input2[4:6])
        day2 = int(input2[6:8])
        hour2 = int(input2[8:10]) if len(input2) == 10 else None
        datetime(year2, month2, day2)
    except ValueError:
        return "존재하지 않는 날짜예요. 올바른 날짜를 입력해주세요 (예: 20230230은 잘못된 날짜입니다)."

    today = datetime.today()
    user1_manse = await calculate_four_pillars_with_elements(
        year=year1, month=month1, day=day1, hour=hour1
    )
    user2_manse = await calculate_four_pillars_with_elements(
        year=year2, month=month2, day=day2, hour=hour2
    )
    today_manse = await calculate_four_pillars_with_elements(
        year=today.year, month=today.month, day=today.day
    )
    text_input = TEXT_INPUT.format(
        user1_birthday=input1,
        user1_manse=user1_manse,
        user2_bitrhday=input2,
        user2_manse=user2_manse,
        today=today.strftime("%Y%m%d"),
        today_manse=today_manse,
    )
    return await async_openai_response(prompt=PROMPT_FORTUNE, input=text_input)
