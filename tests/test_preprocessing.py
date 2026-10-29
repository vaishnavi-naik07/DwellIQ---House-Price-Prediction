import pytest
import numpy as np
import pandas as pd

from src.data_preprocessing import convert_total_price, extract_bhk, convert_area
from backend.utils.validators import (
    validate_email,
    validate_password_strength,
    validate_property_input,
    validate_emi_inputs,
)
from backend.services.finance_service import calculate_home_loan_emi, calculate_affordability
from backend.services.comparison_service import compare_properties
from backend.services.prediction_service import format_rupees


class TestDataPreprocessingFunctions:
    def test_convert_total_price_various_formats(self):
        assert convert_total_price("50 Lac") == 5_000_000
        assert convert_total_price("1.5 Cr") == 15_000_000
        assert convert_total_price("₹ 2.25 Crore") == 22_500_000
        assert convert_total_price("75 Lakhs") == 7_500_000
        assert convert_total_price(None) is None
        assert convert_total_price("Contact Builder") is None
        assert convert_total_price(np.nan) is None

    def test_extract_bhk_patterns(self):
        assert extract_bhk("Spacious 2 BHK Apartment") == 2
        assert extract_bhk("Luxury 4 BHK Villa") == 4
        assert extract_bhk("1BHK Studio") == 1
        assert extract_bhk("Commercial Office") is None
        assert extract_bhk(None) is None

    def test_convert_area_sqft(self):
        assert convert_area("1,500 sq.ft") == 1500.0
        assert convert_area("950 sqft") == 950.0
        assert convert_area("3000 square feet") == 3000.0
        assert convert_area("N/A") is None
        assert convert_area(None) is None


class TestBackendValidators:
    def test_email_validation(self):
        assert validate_email("student@university.ac.in") is True
        assert validate_email("invalid-email") is False
        assert validate_email("") is False

    def test_password_strength(self):
        ok, _ = validate_password_strength("Short1!")
        assert ok is False

        ok, _ = validate_password_strength("validPassword123!")
        assert ok is True

    def test_property_input_validator(self):
        valid_input = {"carpet_area_sqft": 1200, "BHK": 3}
        ok, _ = validate_property_input(valid_input)
        assert ok is True

        invalid_area = {"carpet_area_sqft": -100, "BHK": 3}
        ok, err = validate_property_input(invalid_area)
        assert ok is False

    def test_emi_input_validator(self):
        ok, _ = validate_emi_inputs(price=8000000, down_payment=1600000, rate=8.5, tenure_years=20)
        assert ok is True

        # Invalid: down payment >= price
        ok, _ = validate_emi_inputs(price=5000000, down_payment=5000000, rate=8.5, tenure_years=20)
        assert ok is False


class TestFinanceAndComparisonServices:
    def test_emi_calculation_accuracy(self):
        # Loan: 80L home, 20% down (16L), principal = 64L, 8.5% for 20 years
        res = calculate_home_loan_emi(
            property_price=8000000,
            down_payment=1600000,
            annual_interest_rate=8.5,
            tenure_years=20,
        )
        assert res["principal"] == 6400000
        # Monthly EMI should be approximately ~55,500
        assert 54000 <= res["monthly_emi"] <= 57000
        assert res["total_repayment"] > res["principal"]

    def test_affordability_assessment(self):
        # 1.5 Lakh salary, 15k existing EMI
        afford = calculate_affordability(monthly_income=150000, existing_emis=15000)
        assert afford["max_recommended_emi"] == 45000.0
        assert afford["max_loan_capacity"] > 0
        assert afford["max_recommended_property_budget"] > afford["max_loan_capacity"]

    def test_property_comparison(self):
        p1 = {"title": "A", "price": 10000000, "area": 1000, "bhk": 2}
        p2 = {"title": "B", "price": 15000000, "area": 2000, "bhk": 3}
        cmp_res = compare_properties([p1, p2])

        assert cmp_res["best_price"] == "A"  # 1 Cr vs 1.5 Cr
        assert cmp_res["best_rate_sqft"] == "B"  # 7500/sqft vs 10000/sqft
        assert cmp_res["largest_area"] == "B"  # 2000 sqft vs 1000 sqft

    def test_format_rupees(self):
        assert format_rupees(25000000) == "₹2.50 Cr"
        assert format_rupees(7500000) == "₹75.00 Lakh"
        assert format_rupees(45000) == "₹45,000"

