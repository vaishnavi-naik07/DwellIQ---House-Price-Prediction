from pathlib import Path
from typing import Dict, Any, Optional
import joblib
from backend.core.config import MODEL_PATH


def load_model_bundle() -> Dict[str, Any]:
    """
    Load the trained joblib model bundle and verify structure.
    Returns the dictionary containing 'model', 'feature_columns', 'metrics', etc.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model artifact not found at: {MODEL_PATH}. "
            "Please ensure models/best_model.joblib is present."
        )

    bundle = joblib.load(MODEL_PATH)
    if not isinstance(bundle, dict):
        return {
            "model": bundle,
            "model_name": "Trained Estimator",
            "feature_columns": [],
            "metrics": {},
        }

    if "model" not in bundle:
        raise KeyError("Model bundle does not contain required 'model' pipeline.")

    return bundle
