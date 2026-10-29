from typing import Dict, Any


def calculate_home_loan_emi(
    property_price: float,
    down_payment: float,
    annual_interest_rate: float,
    tenure_years: int,
) -> Dict[str, Any]:
    """
    Standard Equated Monthly Installment (EMI) Formula:
    EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]
    where:
    P = Principal loan amount (property_price - down_payment)
    R = Monthly interest rate (annual_interest_rate / 12 / 100)
    N = Number of monthly installments (tenure_years * 12)
    """
    principal = max(property_price - down_payment, 0.0)

    if principal <= 0 or tenure_years <= 0:
        return {
            "principal": principal,
            "monthly_emi": 0.0,
            "total_interest": 0.0,
            "total_repayment": 0.0,
            "down_payment_pct": round((down_payment / property_price) * 100, 1)
            if property_price > 0
            else 0.0,
        }

    monthly_rate = (annual_interest_rate / 100.0) / 12.0
    num_months = tenure_years * 12

    if monthly_rate == 0:
        emi = principal / num_months
        total_payment = principal
        total_interest = 0.0
    else:
        emi = (
            principal
            * monthly_rate
            * ((1 + monthly_rate) ** num_months)
            / (((1 + monthly_rate) ** num_months) - 1)
        )
        total_payment = emi * num_months
        total_interest = total_payment - principal

    return {
        "property_price": property_price,
        "down_payment": down_payment,
        "principal": principal,
        "monthly_emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_repayment": round(total_payment, 2),
        "down_payment_pct": round((down_payment / property_price) * 100, 1)
        if property_price > 0
        else 0.0,
        "tenure_months": num_months,
    }


def calculate_affordability(monthly_income: float, existing_emis: float = 0.0) -> Dict[str, Any]:
    """
    Calculate maximum recommended property price based on 40% FOIR (Fixed Obligation to Income Ratio).
    """
    available_emi = max((monthly_income * 0.40) - existing_emis, 0.0)
    # Estimate borrowing capacity at 8.5% for 20 years
    r = (8.5 / 100.0) / 12.0
    n = 20 * 12
    max_loan = available_emi * (((1 + r) ** n) - 1) / (r * ((1 + r) ** n)) if available_emi > 0 else 0
    # Assuming 80% LTV (Loan to Value)
    max_budget = max_loan / 0.80 if max_loan > 0 else 0

    return {
        "max_recommended_emi": round(available_emi, 2),
        "max_loan_capacity": round(max_loan, 2),
        "max_recommended_property_budget": round(max_budget, 2),
    }
