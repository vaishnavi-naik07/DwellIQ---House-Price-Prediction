from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from backend.core.model_loader import load_model_bundle

# Cached or runtime bundle
_BUNDLE_CACHE: Dict[str, Any] = {}


def get_model_bundle() -> Dict[str, Any]:
    global _BUNDLE_CACHE
    if not _BUNDLE_CACHE:
        _BUNDLE_CACHE = load_model_bundle()
    return _BUNDLE_CACHE


def format_rupees(amount: float) -> str:
    """Format amount cleanly into Indian numbering system (Cr, Lakh, or raw)."""
    if amount is None or np.isnan(amount):
        return "N/A"
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Cr"
    elif amount >= 100_000:
        return f"₹{amount / 100_000:.2f} Lakh"
    return f"₹{amount:,.0f}"


def predict_price(input_features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Predict property price using the trained scikit-learn pipeline.
    Returns:
        (predicted_price_rupees, metadata_dict)
    """
    bundle = get_model_bundle()
    pipeline = bundle["model"]
    feature_cols = bundle.get("feature_columns", [])

    # Construct DataFrame aligned strictly to expected feature columns
    df = pd.DataFrame([input_features])
    if feature_cols:
        for col in feature_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df[feature_cols]

    pred = float(pipeline.predict(df)[0])
    # Safeguard against extreme negatives if any
    pred = max(pred, 100_000.0)

    metadata = {
        "model_name": bundle.get("model_name", "Random Forest Regressor"),
        "metrics": bundle.get("metrics", {}),
        "carpet_area": input_features.get("carpet_area_sqft", 0),
        "price_per_sqft": round(pred / input_features["carpet_area_sqft"], 1)
        if input_features.get("carpet_area_sqft", 0) > 0
        else None,
    }
    return pred, metadata
