import math
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any, Optional

# Verified coordinate anchors for Indian urban centers (lat, lon)
CITY_COORDINATES: Dict[str, tuple] = {
    "Mumbai": (19.0760, 72.8777),
    "New-Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946),
    "Pune": (18.5204, 73.8567),
    "Thane": (19.2183, 72.9781),
    "Navi-Mumbai": (19.0330, 73.0297),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Gurgaon": (28.4595, 77.0266),
    "Noida": (28.5355, 77.3910),
    "Greater-Noida": (28.4744, 77.5040),
    "Faridabad": (28.4089, 77.3178),
    "Ghaziabad": (28.6692, 77.4538),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Chandigarh": (30.7333, 76.7794),
    "Kochi": (9.9312, 76.2673),
    "Goa": (15.2993, 74.1240),
    "Surat": (21.1702, 72.8311),
    "Vadodara": (22.3072, 73.1812),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126),
    "Coimbatore": (11.0168, 76.9558),
    "Visakhapatnam": (17.6868, 83.2185),
    "Patna": (25.5941, 85.1376),
    "Bhubaneswar": (20.2961, 85.8245),
}

# Nominatim search keywords mapping
ESSENTIAL_SEARCH_TERMS: Dict[str, str] = {
    "Supermarket / Grocery Store": "supermarket",
    "Hospital / Clinic": "hospital",
    "School / College": "school",
    "Railway Station": "railway station",
    "Metro Station": "metro station",
    "Bus Stop": "bus station",
    "Shopping Mall": "shopping mall",
    "Pharmacy": "pharmacy",
    "Park / Garden": "park",
    "Gym / Fitness Centre": "fitness centre gym",
    "Restaurant / Café": "restaurant",
    "Airport": "airport",
}

NEARBY_ESSENTIALS_OPTIONS: List[str] = [
    "No preference",
    "Supermarket / Grocery Store",
    "Hospital / Clinic",
    "School / College",
    "Railway Station",
    "Metro Station",
    "Bus Stop",
    "Shopping Mall",
    "Pharmacy",
    "Park / Garden",
    "Gym / Fitness Centre",
    "Restaurant / Café",
    "Airport",
]

DISTANCE_PREFERENCES: Dict[str, float] = {
    "Within 1 km": 1.0,
    "Within 3 km": 3.0,
    "Within 5 km": 5.0,
    "Within 10 km": 10.0,
}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in km between two coordinate points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_city_coordinates(city_name: str) -> Optional[tuple]:
    """Retrieve city anchor coordinates."""
    norm_city = city_name.strip().title()
    if norm_city in CITY_COORDINATES:
        return CITY_COORDINATES[norm_city]

    for k, v in CITY_COORDINATES.items():
        if k.lower() == city_name.strip().lower() or k.replace("-", " ").lower() == city_name.strip().lower():
            return v

    try:
        clean = urllib.parse.quote(city_name.replace("-", " "))
        url = f"https://nominatim.openstreetmap.org/search?city={clean}&country=India&format=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "DwellIQ-RealEstateApp/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass

    return None


def fetch_nearby_essentials(
    city_name: str,
    essential_type: str,
    max_distance_km: float = 5.0,
    max_results: int = 5,
) -> Dict[str, Any]:
    """
    Query real nearby places using OpenStreetMap Nominatim POI indexing without requiring private API keys.
    Returns:
        {
            "status": "success" | "no_results" | "unavailable" | "none",
            "message": str,
            "places": [{"name": str, "distance_km": float, "category": str, "address": str}, ...]
        }
    """
    if essential_type == "No preference":
        return {"status": "none", "places": [], "message": ""}

    coords = get_city_coordinates(city_name)
    if not coords:
        return {
            "status": "unavailable",
            "places": [],
            "message": f"Geographic center coordinates are unavailable for '{city_name}'.",
        }

    center_lat, center_lon = coords
    term = ESSENTIAL_SEARCH_TERMS.get(essential_type)
    if not term:
        return {
            "status": "unavailable",
            "places": [],
            "message": f"No keyword mapping configured for '{essential_type}'.",
        }

    city_clean = city_name.replace("-", " ").strip()
    query_str = f"{term} in {city_clean}"
    encoded_query = urllib.parse.quote(query_str)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&addressdetails=1&limit=15"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DwellIQ-RealEstateApp/1.0"})
        with urllib.request.urlopen(req, timeout=7) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                
                places = []
                seen_names = set()

                for item in data:
                    display_parts = item.get("display_name", "").split(",")
                    name = item.get("name") or (display_parts[0] if display_parts else "")
                    clean_name = name.strip()
                    
                    if not clean_name or clean_name.lower() in seen_names:
                        continue

                    item_lat = float(item.get("lat", 0))
                    item_lon = float(item.get("lon", 0))

                    if item_lat and item_lon:
                        dist = haversine_distance_km(center_lat, center_lon, item_lat, item_lon)
                        if dist <= max_distance_km:
                            seen_names.add(clean_name.lower())
                            address_snippet = ", ".join([p.strip() for p in display_parts[1:3]]) if len(display_parts) > 1 else city_name
                            places.append({
                                "name": clean_name,
                                "distance_km": round(dist, 2),
                                "category": essential_type,
                                "address": address_snippet,
                            })

                places.sort(key=lambda x: x["distance_km"])
                trimmed_places = places[:max_results]

                if not trimmed_places:
                    return {
                        "status": "no_results",
                        "places": [],
                        "message": f"No verified '{essential_type}' listings found within {int(max_distance_km)} km of {city_name} center in public map records.",
                    }

                return {
                    "status": "success",
                    "places": trimmed_places,
                    "message": f"Found {len(trimmed_places)} verified nearby places for '{essential_type}' in {city_name}.",
                }

    except Exception as e:
        return {
            "status": "unavailable",
            "places": [],
            "message": f"Live public map service was unreachable ({type(e).__name__}). Please check internet connectivity.",
        }

    return {
        "status": "no_results",
        "places": [],
        "message": f"No places found within {int(max_distance_km)} km.",
    }
