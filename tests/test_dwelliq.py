
import pytest
import sqlite3
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from src.auth import (
    register_user,
    authenticate_user,
    hash_password,
    verify_password,
    validate_email,
    validate_password_strength,
    check_rate_limit,
    record_failed_attempt,
    clear_failed_attempts,
    save_user_estimation,
    get_user_estimations,
    init_auth_db,
    get_db_connection,
)
from src.data_preprocessing import convert_total_price, extract_bhk, convert_area

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.joblib"


# =====================================================================
# 1. AUTHENTICATION & SECURITY TESTS
# =====================================================================

class TestAuthenticationAndSecurity:

    def test_password_hashing_and_verification(self):
        password = "SecurePassword123!"
        h, s = hash_password(password)
        assert len(h) == 64  # SHA-256 output hex
        assert len(s) == 32  # 16 bytes salt in hex
        assert verify_password(password, h, s) is True
        assert verify_password("WrongPassword123!", h, s) is False

    def test_email_validation(self):
        assert validate_email("user@example.com") is True
        assert validate_email("john.doe+dwell@university.edu.in") is True
        assert validate_email("invalid-email") is False
        assert validate_email("@missinguser.com") is False
        assert validate_email("") is False

    def test_password_strength_rules(self):
        is_ok, msg = validate_password_strength("short")
        assert is_ok is False
        assert "at least 8" in msg

        is_ok, msg = validate_password_strength("alllettersonly")
        assert is_ok is False
        assert "number or special character" in msg

        is_ok, msg = validate_password_strength("ValidPassw0rd!")
        assert is_ok is True
        assert msg == ""

    def test_user_registration_and_duplicate_prevention(self, tmp_path, monkeypatch):
        test_db = tmp_path / "test_users.db"
        monkeypatch.setattr("src.auth.DB_PATH", test_db)
        init_auth_db()

        # Initial registration
        success, msg = register_user("Test User", "testuser@dwell.ai", "StrongPassword123!")
        assert success is True
        assert "successful" in msg.lower()

        # Duplicate registration attempt
        dup_success, dup_msg = register_user("Test User 2", "testuser@dwell.ai", "AnotherPassword999!")
        assert dup_success is False
        assert "already exists" in dup_msg.lower()

        # Case normalization check (UPPERCASE email)
        dup_success_upper, dup_msg_upper = register_user("Test User 3", "TESTUSER@DWELL.AI", "AnotherPassword999!")
        assert dup_success_upper is False
        assert "already exists" in dup_msg_upper.lower()

    def test_authentication_flow_success_and_failure(self, tmp_path, monkeypatch):
        test_db = tmp_path / "test_users.db"
        monkeypatch.setattr("src.auth.DB_PATH", test_db)
        init_auth_db()

        register_user("Alice Wonderland", "alice@example.com", "Wonderland2026!")

        # Success
        auth_ok, _, user_data = authenticate_user("alice@example.com", "Wonderland2026!")
        assert auth_ok is True
        assert user_data["full_name"] == "Alice Wonderland"
        assert user_data["email"] == "alice@example.com"

        # Failure: Wrong password
        auth_fail, fail_msg, _ = authenticate_user("alice@example.com", "WrongPassword!")
        assert auth_fail is False
        assert "invalid email or password" in fail_msg.lower()

        # Failure: Unregistered email
        auth_fail_user, _, _ = authenticate_user("nonexistent@example.com", "SomePassword123!")
        assert auth_fail_user is False

    def test_rate_limiting_after_repeated_failures(self):
        test_email = "ratelimit_tester@dwell.ai"
        clear_failed_attempts(test_email)

        is_blocked, _ = check_rate_limit(test_email)
        assert is_blocked is False

        # Simulate 5 failed attempts
        for _ in range(5):
            record_failed_attempt(test_email)

        is_blocked, wait_sec = check_rate_limit(test_email)
        assert is_blocked is True
        assert wait_sec > 0

        # Clear and check unblocked
        clear_failed_attempts(test_email)
        is_blocked_after, _ = check_rate_limit(test_email)
        assert is_blocked_after is False

    def test_saved_estimations_isolation(self, tmp_path, monkeypatch):
        test_db = tmp_path / "test_users.db"
        monkeypatch.setattr("src.auth.DB_PATH", test_db)
        init_auth_db()

        register_user("User One", "user1@dwell.ai", "Password123!")
        register_user("User Two", "user2@dwell.ai", "Password123!")

        _, _, u1 = authenticate_user("user1@dwell.ai", "Password123!")
        _, _, u2 = authenticate_user("user2@dwell.ai", "Password123!")

        save_user_estimation(u1["id"], "Mumbai", 3, 1200.0, 45000000.0)
        save_user_estimation(u2["id"], "Bangalore", 2, 950.0, 12000000.0)

        history_u1 = get_user_estimations(u1["id"])
        history_u2 = get_user_estimations(u2["id"])

        assert len(history_u1) == 1
        assert history_u1[0]["location"] == "Mumbai"
        assert len(history_u2) == 1
        assert history_u2[0]["location"] == "Bangalore"


# =====================================================================
# 2. DATA PREPROCESSING TESTS
# =====================================================================

class TestPreprocessing:

    def test_convert_total_price_lac_and_cr(self):
        assert convert_total_price("45 Lac") == 4_500_000
        assert convert_total_price("45.5 Lacs") == 4_550_000
        assert convert_total_price("1.2 Cr") == 12_000_000
        assert convert_total_price("3 Crore") == 30_000_000
        assert convert_total_price("₹ 2.50 crore") == 25_000_000
        assert convert_total_price(None) is None
        assert convert_total_price("Call for Price") is None
        assert convert_total_price("Invalid Text") is None

    def test_extract_bhk_from_titles(self):
        assert extract_bhk("3 BHK Flat in Andheri West") == 3
        assert extract_bhk("Luxury 4 BHK Penthouse") == 4
        assert extract_bhk("1BHK Studio Apartment") == 1
        assert extract_bhk("Commercial Shop for Sale") is None
        assert extract_bhk(np.nan) is None

    def test_convert_area_sqft(self):
        assert convert_area("1,200 sq.ft") == 1200.0
        assert convert_area("850 sqft") == 850.0
        assert convert_area("2500 square feet") == 2500.0
        assert convert_area("Unknown") is None
        assert convert_area(None) is None


# =====================================================================
# 3. MODEL INFERENCE & PIPELINE INTEGRITY TESTS
# =====================================================================

class TestModelInference:

    @pytest.fixture(scope="class")
    def model_bundle(self):
        assert MODEL_PATH.exists(), f"Missing model bundle at {MODEL_PATH}"
        bundle = joblib.load(MODEL_PATH)
        assert isinstance(bundle, dict)
        assert "model" in bundle
        assert "feature_columns" in bundle
        return bundle

    def test_model_loading_and_pipeline_structure(self, model_bundle):
        pipe = model_bundle["model"]
        assert hasattr(pipe, "predict")
        assert "preprocessor" in pipe.named_steps
        assert "model" in pipe.named_steps

    def test_prediction_on_typical_input(self, model_bundle):
        pipe = model_bundle["model"]
        cols = model_bundle["feature_columns"]

        sample = pd.DataFrame([{
            "BHK": 3,
            "carpet_area_sqft": 1100,
            "Bathroom": 2,
            "Balcony": 1,
            "location": "mumbai",
            "Status": "Ready to Move",
            "Floor": "5",
            "Transaction": "Resale",
            "Furnishing": "Semi-Furnished",
            "facing": "East",
            "Ownership": "Freehold",
            "Car Parking": "1"
        }])[cols]

        pred = pipe.predict(sample)
        assert len(pred) == 1
        assert float(pred[0]) > 0
        assert not np.isnan(pred[0])

    def test_unseen_location_and_categories_handling(self, model_bundle):
        pipe = model_bundle["model"]
        cols = model_bundle["feature_columns"]

        sample = pd.DataFrame([{
            "BHK": 2,
            "carpet_area_sqft": 800,
            "Bathroom": 2,
            "Balcony": 1,
            "location": "unseen_exotic_city_xyz_99",
            "Status": "Under Construction",
            "Floor": "Top Floor Penthouse Unknown",
            "Transaction": "Special Transfer",
            "Furnishing": "Ultra Luxury Custom",
            "facing": "North-East",
            "Ownership": "Ancestral Trust",
            "Car Parking": "Underground Valet"
        }])[cols]

        # OneHotEncoder(handle_unknown='ignore') must gracefully handle unseen categories without crashing
        pred = pipe.predict(sample)
        assert len(pred) == 1
        assert float(pred[0]) > 0

    def test_missing_and_zero_inputs_robustness(self, model_bundle):
        pipe = model_bundle["model"]
        cols = model_bundle["feature_columns"]

        sample = pd.DataFrame([{
            "BHK": np.nan,
            "carpet_area_sqft": np.nan,
            "Bathroom": np.nan,
            "Balcony": np.nan,
            "location": np.nan,
            "Status": np.nan,
            "Floor": np.nan,
            "Transaction": np.nan,
            "Furnishing": np.nan,
            "facing": np.nan,
            "Ownership": np.nan,
            "Car Parking": np.nan
        }])[cols]

        # Preprocessor imputers should substitute missing values
        pred = pipe.predict(sample)
        assert len(pred) == 1
        assert float(pred[0]) > 0

    def test_extreme_luxury_scale_property(self, model_bundle):
        pipe = model_bundle["model"]
        cols = model_bundle["feature_columns"]

        sample = pd.DataFrame([{
            "BHK": 8,
            "carpet_area_sqft": 15000,
            "Bathroom": 8,
            "Balcony": 5,
            "location": "mumbai",
            "Status": "Ready to Move",
            "Floor": "20",
            "Transaction": "New Property",
            "Furnishing": "Furnished",
            "facing": "North",
            "Ownership": "Freehold",
            "Car Parking": "4"
        }])[cols]

        pred = pipe.predict(sample)
        assert float(pred[0]) >= 10_000_000  # Should be luxury scale (> ₹1 Cr)


# =====================================================================
# 4. NEARBY ESSENTIALS SERVICE TESTS
# =====================================================================

class TestNearbyPlaces:
    def test_haversine_distance_calculation(self):
        from src.nearby_places import haversine_distance_km
        # Distance between Mumbai center (19.0760, 72.8777) and nearby point should be ~0 when identical
        assert haversine_distance_km(19.0760, 72.8777, 19.0760, 72.8777) == 0.0

        # Distance between Mumbai and Pune is ~120-150 km
        dist = haversine_distance_km(19.0760, 72.8777, 18.5204, 73.8567)
        assert 110.0 <= dist <= 160.0

    def test_nearby_options_and_distance_definitions(self):
        from src.nearby_places import NEARBY_ESSENTIALS_OPTIONS, DISTANCE_PREFERENCES
        assert "No preference" in NEARBY_ESSENTIALS_OPTIONS
        assert "Supermarket / Grocery Store" in NEARBY_ESSENTIALS_OPTIONS
        assert "Hospital / Clinic" in NEARBY_ESSENTIALS_OPTIONS
        assert "Airport" in NEARBY_ESSENTIALS_OPTIONS
        assert len(NEARBY_ESSENTIALS_OPTIONS) == 13

        assert "Within 1 km" in DISTANCE_PREFERENCES
        assert "Within 3 km" in DISTANCE_PREFERENCES
        assert "Within 5 km" in DISTANCE_PREFERENCES
        assert "Within 10 km" in DISTANCE_PREFERENCES

    def test_fetch_nearby_essentials_no_preference(self):
        from src.nearby_places import fetch_nearby_essentials
        res = fetch_nearby_essentials("Mumbai", "No preference")
        assert res["status"] == "none"
        assert res["places"] == []

    def test_fetch_nearby_essentials_unknown_city(self):
        from src.nearby_places import fetch_nearby_essentials
        res = fetch_nearby_essentials("AtlantisCityXYZ", "Hospital / Clinic")
        assert res["status"] == "unavailable"
        assert res["places"] == []

