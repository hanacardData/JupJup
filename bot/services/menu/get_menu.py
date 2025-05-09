import httpx
import pandas as pd
from fastapi_cache.decorator import cache

from bot.services.core.openai_client import async_openai_response
from bot.services.menu.prompt import PROMPT_MENU
from secret import OPENWEATHER_API_KEY

menu_df = pd.read_csv("data/menu.csv")
required_columns = ["상호", "메뉴", "위치", "전화번호", "거리(도보)"]
menu_df = menu_df.dropna(subset=required_columns)


@cache(expire=10800)
async def _get_weather_info() -> str:
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "SEOUL",
        "appid": OPENWEATHER_API_KEY,
        "lang": "kr",
        "units": "metric",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    weather_description = data["weather"][0]["description"]
    return weather_description


@cache(expire=10800)
async def select_random_menu_based_on_weather() -> str:
    weather = await _get_weather_info()

    # 모든 음식점 목록 가져오기 (필터 없이)
    selected_data = menu_df.reset_index(drop=True)[required_columns].to_dict(
        orient="records"
    )

    # 음식점 리스트를 문자열로 변환
    restaurants_string = "\n".join(
        f"- 식당 이름: {item['상호']}\n"
        f"  - 메뉴: {item['메뉴']}\n"
        f"  - 위치: {item['위치']}\n"
        f"  - 거리(도보): {int(item['거리(도보)'])}분\n"
        f"  - 전화번호: {item['전화번호']}"
        for item in selected_data
    )

    prompt_instruction = "당신은 날씨에 어울리는 식당을 추천하는 하나카드 챗봇입니다."

    prompt_input = PROMPT_MENU.format(weather=weather, menu_list=restaurants_string)

    return await async_openai_response(prompt=prompt_instruction, input=prompt_input)
