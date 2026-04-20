import json
import httpx
from app.core.config import settings
from app.utils.cache import get_redis

ROUTE_TTL = 3600  # 1 hour — road geometry doesn't change frequently


async def get_route(origin_lat, origin_lng, dest_lat, dest_lng) -> dict:
    cache_key = f"route:{origin_lat}:{origin_lng}:{dest_lat}:{dest_lng}"
    r = get_redis()

    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": settings.OPENROUTESERVICE_API_KEY}
    body = {
        "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]]
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
            summary = data["routes"][0]["summary"]
            result = {
                "distance_km": summary["distance"] / 1000,
                "duration_minutes": int(summary["duration"] / 60)
            }
    except httpx.TimeoutException:
        result = _heuristic_estimate(origin_lat, origin_lng, dest_lat, dest_lng)
    except Exception:
        result = _heuristic_estimate(origin_lat, origin_lng, dest_lat, dest_lng)

    r.setex(cache_key, ROUTE_TTL, json.dumps(result))
    return result


def _heuristic_estimate(lat1, lng1, lat2, lng2) -> dict:
    from app.utils.geo import haversine_distance
    dist = haversine_distance(lat1, lng1, lat2, lng2)
    return {
        "distance_km": round(dist * 1.3, 2),
        "duration_minutes": int((dist * 1.3) / 40 * 60)
    }
