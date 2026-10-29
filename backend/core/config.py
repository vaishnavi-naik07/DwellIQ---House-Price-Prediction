import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
ASSETS_DIR = PROJECT_ROOT / "assets"
FRONTEND_ASSETS_DIR = FRONTEND_DIR / "assets" / "images"

# Artifact and Database Paths
MODEL_PATH = MODELS_DIR / "best_model.joblib"
MODEL_BACKUP_PATH = MODELS_DIR / "best_model_uncompressed_backup.joblib"
REPORT_PATH = REPORTS_DIR / "model_comparison.csv"
RAW_DATA_PATH = DATA_DIR / "raw" / "house_prices.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_house_prices.csv"
DB_PATH = Path(os.environ.get("DB_PATH", str(DATA_DIR / "secure" / "users.db")))
HERO_IMG_PATH = FRONTEND_ASSETS_DIR / "luxury_home.jpg"
if not HERO_IMG_PATH.exists():
    HERO_IMG_PATH = ASSETS_DIR / "luxury_home.jpg"

FIG_FEAT_PATH = REPORTS_DIR / "figures" / "feature_importance.png"
FIG_COMP_PATH = REPORTS_DIR / "figures" / "model_comparison_mae.png"

# App & Security Settings
APP_ENV = os.environ.get("APP_ENV", "development")
PBKDF2_ITERATIONS = int(os.environ.get("PBKDF2_ITERATIONS", "200000"))
RATE_LIMIT_WINDOW_SEC = int(os.environ.get("RATE_LIMIT_WINDOW_SEC", "300"))
MAX_FAILED_ATTEMPTS = int(os.environ.get("MAX_FAILED_ATTEMPTS", "5"))

# API Keys (Optional live LLM integrations)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Verified Dataset Locations (Top 81 cities)
DATASET_LOCATIONS = [
    "Agra", "Ahmedabad", "Allahabad", "Aurangabad", "Badlapur", "Bangalore",
    "Belgaum", "Bhiwadi", "Bhiwandi", "Bhopal", "Bhubaneswar", "Chandigarh",
    "Chennai", "Coimbatore", "Dehradun", "Durgapur", "Ernakulam", "Faridabad",
    "Ghaziabad", "Goa", "Greater-Noida", "Guntur", "Gurgaon", "Guwahati",
    "Gwalior", "Haridwar", "Hyderabad", "Indore", "Jabalpur", "Jaipur",
    "Jamshedpur", "Jodhpur", "Kalyan", "Kanpur", "Kochi", "Kolkata",
    "Kozhikode", "Lucknow", "Ludhiana", "Madurai", "Mangalore", "Mohali",
    "Mumbai", "Mysore", "Nagpur", "Nashik", "Navi-Mumbai", "New-Delhi",
    "Noida", "Palghar", "Panchkula", "Patna", "Pondicherry", "Pune",
    "Raipur", "Rajahmundry", "Ranchi", "Shimla", "Siliguri", "Surat",
    "Thane", "Thrissur", "Tirupati", "Trichy", "Trivandrum", "Udaipur",
    "Vadodara", "Varanasi", "Vijayawada", "Visakhapatnam", "Zirakpur"
]

