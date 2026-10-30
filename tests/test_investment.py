import pytest
from backend.services.investment_service import (
    calculate_rental_yield,
    simulate_property_appreciation,
    analyze_rental_cash_flow,
    calculate_overall_roi,
    calculate_break_even_period,
    compare_investment_properties,
)


class TestInvestmentService:
    def test_rental_yield_calculation(self):
        # 1 Crore property, 30k monthly rent
        res = calculate_rental_yield(
            purchase_price=10000000.0,
            monthly_rent=30000.0,
            monthly_maintenance=3000.0,
            annual_property_tax=12000.0,
            other_annual_expenses=12000.0,
        )
        assert res["annual_rental_income"] == 360000.0
        # Gross Yield = (360,000 / 10,000,000) * 100 = 3.6%
        assert res["gross_rental_yield_pct"] == 3.6
        # Annual operating expenses = (3000*12) + 12000 + 12000 = 60,000
        assert res["annual_operating_expenses"] == 60000.0
        # Net rent = 300,000 -> 3.0%
        assert res["net_annual_rental_income"] == 300000.0
        assert res["net_rental_yield_pct"] == 3.0

    def test_rental_yield_zero_price_safety(self):
        res = calculate_rental_yield(purchase_price=0.0, monthly_rent=25000.0)
        assert res["gross_rental_yield_pct"] == 0.0
        assert res["net_rental_yield_pct"] == 0.0

    def test_appreciation_simulator(self):
        # 50 Lakh property, 6% annual growth, 5 years
        res = simulate_property_appreciation(
            current_value=5000000.0,
            annual_appreciation_rate_pct=6.0,
            years=5,
        )
        assert res["years"] == 5
        # 50L * (1.06)^5 = ~66,91,127.89
        assert res["future_value"] > 6600000.0
        assert res["total_appreciation"] > 1600000.0
        assert len(res["trajectory"]) == 6  # Years 0 to 5

    def test_rental_cash_flow_positive_and_negative(self):
        # Case 1: Positive Cash Flow
        pos_res = analyze_rental_cash_flow(
            monthly_rent=40000.0,
            monthly_emi=25000.0,
            monthly_maintenance=3000.0,
            monthly_property_management=2000.0,
            other_monthly_expenses=2000.0,
        )
        assert pos_res["is_positive"] is True
        assert pos_res["monthly_net_cash_flow"] == 8000.0
        assert pos_res["annual_net_cash_flow"] == 96000.0

        # Case 2: Negative Cash Flow
        neg_res = analyze_rental_cash_flow(
            monthly_rent=30000.0,
            monthly_emi=38000.0,
            monthly_maintenance=4000.0,
        )
        assert neg_res["is_positive"] is False
        assert neg_res["monthly_net_cash_flow"] == -12000.0

    def test_overall_roi_calculation(self):
        # 60L property, 4L stamp duty/legal, 5Y holding
        res = calculate_overall_roi(
            purchase_price=6000000.0,
            additional_purchase_costs=400000.0,
            annual_rental_income=240000.0,
            annual_operating_expenses=40000.0,
            estimated_resale_value=8500000.0,
            investment_duration_years=5,
        )
        assert res["total_initial_investment"] == 6400000.0
        assert res["cumulative_rental_income"] == 1200000.0
        assert res["cumulative_operating_expenses"] == 200000.0
        # Inflows: 85L + 12L = 97L
        # Outflows: 64L + 2L = 66L
        # Profit: 31L
        assert res["total_profit_or_loss"] == 3100000.0
        # ROI %: (31L / 64L) * 100 = ~48.44%
        assert round(res["roi_pct"], 1) == 48.4
        assert res["annualized_roi_pct"] > 8.0

    def test_break_even_period(self):
        # 50 Lakh investment, 2.5 Lakh net rent per year -> 20.0 years
        res = calculate_break_even_period(
            total_investment=5000000.0,
            net_annual_rental_income=250000.0,
        )
        assert res["is_reachable"] is True
        assert res["years"] == 20
        assert res["months"] == 0

        # Unreachable when rent is negative or zero
        unreach = calculate_break_even_period(
            total_investment=5000000.0,
            net_annual_rental_income=-10000.0,
        )
        assert unreach["is_reachable"] is False

    def test_compare_investment_properties(self):
        props = [
            {
                "name": "Property Alpha",
                "purchase_price": 5000000.0,
                "monthly_rent": 22000.0,
                "monthly_emi": 20000.0,
                "monthly_maintenance": 2000.0,
                "appreciation_rate_pct": 5.0,
            },
            {
                "name": "Property Beta",
                "purchase_price": 8000000.0,
                "monthly_rent": 38000.0,
                "monthly_emi": 35000.0,
                "monthly_maintenance": 3000.0,
                "appreciation_rate_pct": 8.0,
            },
        ]
        cmp_res = compare_investment_properties(props)
        assert len(cmp_res["rows"]) == 2
        assert "best_in_metric" in cmp_res
        assert cmp_res["best_in_metric"]["lowest_price"] == "Property Alpha"
        assert cmp_res["best_in_metric"]["highest_monthly_rent"] == "Property Beta"

