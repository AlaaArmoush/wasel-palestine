from sqlalchemy.orm import Session
from app.models.checkpoint import Checkpoint
from app.utils.geo import is_within_radius
from app.services.external import routing, weather
from app.schemas.route import RouteRequest


async def estimate_route(db: Session, payload: RouteRequest) -> dict:
    route_data = await routing.get_route(
        payload.origin_lat, payload.origin_lng,
        payload.destination_lat, payload.destination_lng
    )

    weather_data = await weather.get_weather_conditions(
        payload.destination_lat, payload.destination_lng
    )

    mid_lat = (payload.origin_lat + payload.destination_lat) / 2
    mid_lng = (payload.origin_lng + payload.destination_lng) / 2
    checkpoints = db.query(Checkpoint).filter(Checkpoint.is_active == True).all()
    nearby = [c for c in checkpoints if is_within_radius(mid_lat, mid_lng, c.latitude, c.longitude, 5)]

    factors = []
    warnings = []
    if nearby:
        factors.append(f"{len(nearby)} checkpoint(s) near route")
    if weather_data.get("is_hazardous"):
        factors.append(f"Hazardous weather: {weather_data.get('description')}")
        warnings.append("Drive carefully due to weather conditions")

    return {
        "distance_km": route_data["distance_km"],
        "estimated_duration_minutes": route_data["duration_minutes"],
        "affecting_factors": factors,
        "checkpoints_on_route": [str(c.id) for c in nearby],
        "warnings": warnings,
        "weather": weather_data
    }
