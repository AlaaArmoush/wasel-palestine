import httpx
from app.core.config import settings

async def get_route(origin_lat, origin_lng, dest_lat, dest_lng) -> dict:
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
            return {
                "distance_km": summary["distance"] / 1000,
                "duration_minutes": int(summary["duration"] / 60)
            }
    except httpx.TimeoutException:
        return _heuristic_estimate(origin_lat, origin_lng, dest_lat, dest_lng)
    except Exception:
        return _heuristic_estimate(origin_lat, origin_lng, dest_lat, dest_lng)


def _heuristic_estimate(lat1, lng1, lat2, lng2) -> dict:
    from app.utils.geo import haversine_distance
    dist = haversine_distance(lat1, lng1, lat2, lng2)
    return {
        "distance_km": round(dist * 1.3, 2),
        "duration_minutes": int((dist * 1.3) / 40 * 60)
    }
