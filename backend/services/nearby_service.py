from typing import Dict, Any
from src.nearby_places import (
    fetch_nearby_essentials,
    NEARBY_ESSENTIALS_OPTIONS,
    DISTANCE_PREFERENCES,
    CITY_COORDINATES,
)


def get_nearby_amenities(city: str, category: str, max_distance_km: float = 5.0) -> Dict[str, Any]:
    """
    Query real nearby amenities using OpenStreetMap public POI endpoints.
    Provides verified place names, distances in km, and graceful offline handling.
    """
    return fetch_nearby_essentials(
        city_name=city,
        essential_type=category,
        max_distance_km=max_distance_km,
        max_results=8,
    )
