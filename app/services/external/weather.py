import json
import httpx
from app.core.config import settings
from app.utils.cache import get_redis

WEATHER_TTL = 600


async def get_weather_conditions(lat: float, lng: float) -> dict:
    lat_r, lng_r = round(lat, 2), round(lng, 2)
    cache_key = f"weather:{lat_r}:{lng_r}"
    r = get_redis()

    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            result = {
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "is_hazardous": data["weather"][0]["main"] in ["Thunderstorm", "Snow", "Fog"]
            }
    except Exception as e:
        return {"error_reason": str(e)}

    r.setex(cache_key, WEATHER_TTL, json.dumps(result))
    return result
