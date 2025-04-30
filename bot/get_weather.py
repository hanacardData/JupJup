import os

import httpx
import pandas as pd
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

menu_df = pd.read_csv("data/menu.csv")


async def get_weather_info() -> str:
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
