import math
from typing import Dict, Any, List, Optional


def calculate_rental_yield(
    purchase_price: float,
    monthly_rent: float,
    monthly_maintenance: float = 0.0,
    annual_property_tax: float = 0.0,
    other_annual_expenses: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate gross and net rental yield.
    
    Gross Rental Yield = (Annual Rental Income / Property Purchase Price) * 100
    Net Rental Yield = (Net Annual Rental Income / Property Purchase Price) * 100
    where:
    Annual Rental Income = monthly_rent * 12
    Annual Operating Expenses = (monthly_maintenance * 12) + annual_property_tax + other_annual_expenses
    Net Annual Rental Income = Annual Rental Income - Annual Operating Expenses
    """
    if purchase_price <= 0:
        return {
            "purchase_price": purchase_price,
            "monthly_rent": monthly_rent,
            "annual_rental_income": 0.0,
            "annual_operating_expenses": 0.0,
            "net_annual_rental_income": 0.0,
            "gross_rental_yield_pct": 0.0,
            "net_rental_yield_pct": 0.0,
        }

    annual_rental_income = monthly_rent * 12.0
    annual_operating_expenses = (monthly_maintenance * 12.0) + annual_property_tax + other_annual_expenses
    net_annual_rental_income = annual_rental_income - annual_operating_expenses

    gross_yield = (annual_rental_income / purchase_price) * 100.0
    net_yield = (net_annual_rental_income / purchase_price) * 100.0

    return {
        "purchase_price": purchase_price,
        "monthly_rent": monthly_rent,
        "annual_rental_income": round(annual_rental_income, 2),
        "annual_operating_expenses": round(annual_operating_expenses, 2),
        "net_annual_rental_income": round(net_annual_rental_income, 2),
        "gross_rental_yield_pct": round(gross_yield, 2),
        "net_rental_yield_pct": round(net_yield, 2),
    }


def simulate_property_appreciation(
    current_value: float,
    annual_appreciation_rate_pct: float,
    years: int,
) -> Dict[str, Any]:
    """
    Simulate future property appreciation over a specified horizon.
    
    Formula:
    Future Value = Current Value * (1 + annual_rate)^years
    Total Appreciation = Future Value - Current Value
    Appreciation Percentage = ((Future Value - Current Value) / Current Value) * 100
    """
    rate = max(annual_appreciation_rate_pct / 100.0, -1.0)
    years = max(years, 0)

    yearly_trajectory: List[Dict[str, Any]] = []
    running_val = current_value

    for y in range(0, years + 1):
        if y == 0:
            val = current_value
        else:
            val = current_value * math.pow(1.0 + rate, y)
        yearly_trajectory.append({
            "year": y,
            "projected_value": round(val, 2),
            "gain": round(val - current_value, 2),
        })

    future_val = current_value * math.pow(1.0 + rate, years) if years > 0 else current_value
    total_appreciation = future_val - current_value
    appreciation_pct = (total_appreciation / current_value * 100.0) if current_value > 0 else 0.0

    return {
        "current_value": current_value,
        "annual_appreciation_rate_pct": annual_appreciation_rate_pct,
        "years": years,
        "future_value": round(future_val, 2),
        "total_appreciation": round(total_appreciation, 2),
        "appreciation_pct": round(appreciation_pct, 2),
        "trajectory": yearly_trajectory,
    }


def analyze_rental_cash_flow(
    monthly_rent: float,
    monthly_emi: float = 0.0,
    monthly_maintenance: float = 0.0,
    monthly_property_management: float = 0.0,
    other_monthly_expenses: float = 0.0,
) -> Dict[str, Any]:
    """
    Analyze monthly and annual rental cash flow.
    """
    total_monthly_income = max(monthly_rent, 0.0)
    total_monthly_expenses = max(monthly_emi, 0.0) + max(monthly_maintenance, 0.0) + max(monthly_property_management, 0.0) + max(other_monthly_expenses, 0.0)
    monthly_net_cash_flow = total_monthly_income - total_monthly_expenses
    annual_net_cash_flow = monthly_net_cash_flow * 12.0
    is_positive = monthly_net_cash_flow >= 0.0

    return {
        "total_monthly_income": round(total_monthly_income, 2),
        "total_monthly_expenses": round(total_monthly_expenses, 2),
        "monthly_net_cash_flow": round(monthly_net_cash_flow, 2),
        "annual_net_cash_flow": round(annual_net_cash_flow, 2),
        "is_positive": is_positive,
        "expense_breakdown": {
            "monthly_emi": round(monthly_emi, 2),
            "monthly_maintenance": round(monthly_maintenance, 2),
            "property_management": round(monthly_property_management, 2),
            "other_expenses": round(other_monthly_expenses, 2),
        },
    }


def calculate_overall_roi(
    purchase_price: float,
    additional_purchase_costs: float,
    annual_rental_income: float,
    annual_operating_expenses: float,
    estimated_resale_value: float,
    investment_duration_years: int,
) -> Dict[str, Any]:
    """
    Calculate comprehensive total ROI and annualized ROI over an investment holding period.
    
    Total Initial Outlay = purchase_price + additional_purchase_costs
    Cumulative Net Rental Income = (annual_rental_income - annual_operating_expenses) * years
    Capital Gains = estimated_resale_value - purchase_price
    Total Net Profit = (estimated_resale_value + (annual_rental_income * years)) - (Total Initial Outlay + (annual_operating_expenses * years))
    ROI % = (Total Net Profit / Total Initial Outlay) * 100
    Annualized ROI = ((1 + Total ROI / 100) ^ (1 / years) - 1) * 100 (if profitable)
    """
    total_initial_investment = purchase_price + additional_purchase_costs
    years = max(investment_duration_years, 1)

    cumulative_rental_income = annual_rental_income * years
    cumulative_expenses = annual_operating_expenses * years
    cumulative_net_rent = cumulative_rental_income - cumulative_expenses

    total_inflows = estimated_resale_value + cumulative_rental_income
    total_outflows = total_initial_investment + cumulative_expenses
    total_profit_or_loss = total_inflows - total_outflows

    if total_initial_investment > 0:
        roi_pct = (total_profit_or_loss / total_initial_investment) * 100.0
    else:
        roi_pct = 0.0

    # Compound Annual Growth / Annualized ROI
    if total_initial_investment > 0 and (total_inflows - cumulative_expenses) > 0:
        multiplier = max(1.0 + (roi_pct / 100.0), 0.0)
        annualized_roi = (math.pow(multiplier, 1.0 / years) - 1.0) * 100.0
    else:
        annualized_roi = roi_pct / years

    return {
        "purchase_price": purchase_price,
        "additional_purchase_costs": additional_purchase_costs,
        "total_initial_investment": round(total_initial_investment, 2),
        "investment_duration_years": years,
        "cumulative_rental_income": round(cumulative_rental_income, 2),
        "cumulative_operating_expenses": round(cumulative_expenses, 2),
        "cumulative_net_rent": round(cumulative_net_rent, 2),
        "estimated_resale_value": round(estimated_resale_value, 2),
        "capital_gain": round(estimated_resale_value - purchase_price, 2),
        "total_profit_or_loss": round(total_profit_or_loss, 2),
        "roi_pct": round(roi_pct, 2),
        "annualized_roi_pct": round(annualized_roi, 2),
    }


def calculate_break_even_period(
    total_investment: float,
    net_annual_rental_income: float,
) -> Dict[str, Any]:
    """
    Calculate the time required to recover the initial investment through net rental income.
    Returns years and months, or unreachable flag.
    """
    if total_investment <= 0:
        return {
            "years": 0,
            "months": 0,
            "decimal_years": 0.0,
            "is_reachable": True,
            "message": "Immediate (Zero initial outlay)",
        }

    if net_annual_rental_income <= 0:
        return {
            "years": None,
            "months": None,
            "decimal_years": None,
            "is_reachable": False,
            "message": "Break-even is unreachable under negative or zero net rental income.",
        }

    decimal_years = total_investment / net_annual_rental_income
    whole_years = int(decimal_years)
    remaining_months = int(round((decimal_years - whole_years) * 12))

    if remaining_months == 12:
        whole_years += 1
        remaining_months = 0

    return {
        "years": whole_years,
        "months": remaining_months,
        "decimal_years": round(decimal_years, 1),
        "is_reachable": True,
        "message": f"{whole_years} years, {remaining_months} months",
    }


def compare_investment_properties(
    properties: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compare up to 3 properties across yield, cash flow, future value, and ROI.
    Identifies the strongest result for each metric without declaring an absolute winner.
    """
    if not properties:
        return {"rows": [], "best_in_metric": {}}

    rows = []
    for p in properties:
        price = float(p.get("purchase_price", 0.0))
        rent = float(p.get("monthly_rent", 0.0))
        maint = float(p.get("monthly_maintenance", 0.0))
        tax = float(p.get("annual_property_tax", 0.0))
        other_exp = float(p.get("other_annual_expenses", 0.0))
        emi = float(p.get("monthly_emi", 0.0))
        appreciation_rate = float(p.get("appreciation_rate_pct", 6.0))
        duration = int(p.get("duration_years", 5))
        additional_costs = float(p.get("additional_purchase_costs", 0.0))

        # 1. Rental Yield
        y_res = calculate_rental_yield(price, rent, maint, tax, other_exp)
        # 2. Appreciation
        app_res = simulate_property_appreciation(price, appreciation_rate, duration)
        # 3. Cash Flow
        cf_res = analyze_rental_cash_flow(rent, emi, maint, 0.0, other_exp / 12.0)
        # 4. ROI
        roi_res = calculate_overall_roi(
            purchase_price=price,
            additional_purchase_costs=additional_costs,
            annual_rental_income=y_res["annual_rental_income"],
            annual_operating_expenses=y_res["annual_operating_expenses"],
            estimated_resale_value=app_res["future_value"],
            investment_duration_years=duration,
        )

        rows.append({
            "name": p.get("name", "Property"),
            "purchase_price": price,
            "monthly_rent": rent,
            "gross_rental_yield": y_res["gross_rental_yield_pct"],
            "net_rental_yield": y_res["net_rental_yield_pct"],
            "monthly_cash_flow": cf_res["monthly_net_cash_flow"],
            "estimated_future_value": app_res["future_value"],
            "total_roi": roi_res["roi_pct"],
        })

    # Find highest in each metric
    best = {}
    if rows:
        best["lowest_price"] = min(rows, key=lambda r: r["purchase_price"])["name"]
        best["highest_monthly_rent"] = max(rows, key=lambda r: r["monthly_rent"])["name"]
        best["highest_gross_yield"] = max(rows, key=lambda r: r["gross_rental_yield"])["name"]
        best["highest_net_yield"] = max(rows, key=lambda r: r["net_rental_yield"])["name"]
        best["highest_cash_flow"] = max(rows, key=lambda r: r["monthly_cash_flow"])["name"]
        best["highest_future_value"] = max(rows, key=lambda r: r["estimated_future_value"])["name"]
        best["highest_roi"] = max(rows, key=lambda r: r["total_roi"])["name"]

    return {
        "rows": rows,
        "best_in_metric": best,
    }

