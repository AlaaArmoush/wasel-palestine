from pydantic import BaseModel


class RouteRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    avoid_checkpoints: bool = False
    avoid_area_lat: float | None = None
    avoid_area_lng: float | None = None
    avoid_area_radius_km: float | None = None


class RouteResponse(BaseModel):
    distance_km: float
    estimated_duration_minutes: int
    affecting_factors: list[str]
    checkpoints_on_route: list
    warnings: list[str]
    weather: dict | None = None
