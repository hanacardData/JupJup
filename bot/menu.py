from functools import lru_cache

import pandas as pd

from bot.get_weather import get_weather_info
from bot.openai_client import async_openai_response
from bot.prompt import PROMPT_MENU

menu_df = pd.read_csv("data/menu.csv")


@lru_cache
async def select_random_menu_based_on_weather() -> str:
    weather = await get_weather_info()

    # 모든 음식점 목록 가져오기 (필터 없이)
    selected_data = (
        menu_df.sample(
            min(15, len(menu_df))
        )  # 전체에서 15개만 샘플링 (아주 많으면 조절)
        .reset_index(drop=True)[["상호", "메뉴", "위치", "전화번호", "가격대"]]
        .to_dict(orient="records")
    )

    # 음식점 리스트를 문자열로 변환
    restaurants_string = "\n".join(
        f"- {item['상호']} ({item['메뉴']}, {item['가격대']})" for item in selected_data
    )

    prompt_instruction = "당신은 날씨에 어울리는 식당을 추천하는 하나카드 챗봇입니다."

    prompt_input = PROMPT_MENU.format(weather=weather, menu_list=restaurants_string)

    return await async_openai_response(prompt=prompt_instruction, input=prompt_input)
