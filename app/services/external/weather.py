import httpx
from app.core.config import settings

async def get_weather_conditions(lat: float, lng: float) -> dict:
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
            
            return {
                "condition": data["weather"][0]["main"],      # e.g. "Rain"
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "is_hazardous": data["weather"][0]["main"] in ["Thunderstorm", "Snow", "Fog"]
            }
            
    except Exception as e:
        # Temporary debug line to see the exact error
        return {"error_reason": str(e)}
