import re
from typing import Tuple, Dict, Any


def validate_email(email: str) -> bool:
    """Validate RFC 5322 standard email address format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength requirements:
    - Minimum 8 characters
    - At least one number or special symbol
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[\d\W_]", password):
        return False, "Password must contain at least one number or special character."
    return True, ""


def validate_property_input(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate property prediction form inputs."""
    carpet_area = data.get("carpet_area_sqft")
    if carpet_area is None or float(carpet_area) <= 0:
        return False, "Carpet area must be a positive number."
    if float(carpet_area) > 50000:
        return False, "Carpet area exceeds reasonable residential limits (50,000 sq.ft)."

    bhk = data.get("BHK")
    if bhk is None or int(bhk) < 1:
        return False, "BHK must be at least 1."

    return True, ""


def validate_emi_inputs(
    price: float,
    down_payment: float,
    rate: float,
    tenure_years: int,
) -> Tuple[bool, str]:
    """Validate home loan EMI calculation parameters."""
    if price <= 0:
        return False, "Property price must be greater than zero."
    if down_payment < 0:
        return False, "Down payment cannot be negative."
    if down_payment >= price:
        return False, "Down payment cannot equal or exceed property price."
    if rate <= 0 or rate > 30:
        return False, "Annual interest rate must be between 0.1% and 30%."
    if tenure_years <= 0 or tenure_years > 40:
        return False, "Loan tenure must be between 1 and 40 years."
    return True, ""

