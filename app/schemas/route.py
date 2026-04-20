from typing import Optional, List
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


class WeatherData(BaseModel):
    """Weather conditions returned by the OpenWeather integration."""
    condition: str
    description: str
    temperature: float
    is_hazardous: bool
    error_reason: Optional[str] = None  # populated when the external API fails


class RouteResponse(BaseModel):
    distance_km: float
    estimated_duration_minutes: int
    affecting_factors: List[str]
    checkpoints_on_route: List[str]   # list of checkpoint UUIDs (as strings)
    warnings: List[str]
    weather: Optional[WeatherData] = None
