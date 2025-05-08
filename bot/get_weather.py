import httpx
from fastapi_cache.decorator import cache

from secret import OPENWEATHER_API_KEY


@cache(expire=3600)
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
