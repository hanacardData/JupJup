import os

import pandas as pd
import requests
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

menu_df = pd.read_csv("data/menu.csv")


async def get_weather_info() -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?q=SEOUL&appid={OPENWEATHER_API_KEY}&lang=kr&units=metric"
    response = requests.get(url)
    data = response.json()

    weather_description = data["weather"][0]["description"]  # 예: "흐림", "비", "맑음"

    return weather_description
