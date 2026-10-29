from typing import List, Dict, Any


def compare_properties(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare 2 or 3 property records side by side.
    Computes key metrics such as Price per sq.ft and identifies the best value metrics.
    """
    if not properties:
        return {"items": [], "metrics": {}}

    processed = []
    for idx, p in enumerate(properties):
        price = float(p.get("price", 0))
        area = float(p.get("area", 0))
        rate_sqft = round(price / area, 1) if area > 0 else 0
        bhk = int(p.get("bhk", 1))

        processed.append({
            "id": idx + 1,
            "title": p.get("title", f"Property {idx + 1}"),
            "location": p.get("location", "N/A"),
            "price": price,
            "area": area,
            "rate_sqft": rate_sqft,
            "bhk": bhk,
            "bathrooms": p.get("bathrooms", 1),
            "parking": p.get("parking", "1"),
            "furnishing": p.get("furnishing", "Unfurnished"),
            "status": p.get("status", "Ready to Move"),
            "amenities": p.get("amenities", []),
        })

    # Find benchmark highlights
    min_price_item = min(processed, key=lambda x: x["price"]) if processed else None
    min_rate_item = min(
        [x for x in processed if x["rate_sqft"] > 0],
        key=lambda x: x["rate_sqft"],
        default=None,
    )
    max_area_item = max(processed, key=lambda x: x["area"]) if processed else None

    return {
        "items": processed,
        "best_price": min_price_item["title"] if min_price_item else None,
        "best_rate_sqft": min_rate_item["title"] if min_rate_item else None,
        "largest_area": max_area_item["title"] if max_area_item else None,
    }
