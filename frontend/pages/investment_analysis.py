import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from frontend.components.navbar import render_section_header
from backend.services.investment_service import (
    calculate_rental_yield,
    simulate_property_appreciation,
    analyze_rental_cash_flow,
    calculate_overall_roi,
    calculate_break_even_period,
    compare_investment_properties,
)
from backend.services.prediction_service import format_rupees


def render_investment_analysis_page():
    # Page Header
    render_section_header(
        "Real Estate Wealth & Yield Analytics",
        "Investment Analysis Dashboard",
        "Comprehensive residential investment evaluation: rental yields, capital appreciation scenarios, net cash flow, and holding ROI.",
    )

    # Academic Disclaimer Notice
    st.info(
        "ℹ️ **Decision-Support & Academic Disclaimer:** All calculations are analytical models based on user-entered assumptions and scenario parameters. "
        "Appreciation rates, tax allowances, and yields do not represent guaranteed financial returns or AI price predictions. "
        "Applicable stamp duty, local property taxes, registration fees, maintenance, and vacancy periods must be accounted for in real-world transactions."
    )

    # Check for prefilled data from Estimate Property or session
    prefill = st.session_state.get("prefill_investment", {})
    latest_est = st.session_state.get("latest_estimate", {})

    default_price = float(prefill.get("price") or latest_est.get("price") or 7500000.0)
    default_name = str(prefill.get("title") or latest_est.get("title") or "Estimated Property")
    default_rent = float(prefill.get("rent") or round(default_price * 0.003, 0)) # rule-of-thumb ~0.3% monthly rent in Indian metros

    # Tabs for modules
    tab_single, tab_compare, tab_methodology = st.tabs([
        "📊 Property Investment Simulator",
        "⚖️ Multi-Property Investment Comparison",
        "📖 Formulas & Methodology",
    ])

    # =========================================================================
    # TAB 1: SINGLE PROPERTY SIMULATOR
    # =========================================================================
    with tab_single:
        if default_name != "Estimated Property":
            st.markdown(
                f"""
                <div style="background: #EEF3ED; border: 1px solid #D8E2D7; border-radius: 12px; padding: 10px 16px; margin-bottom: 16px; font-size: 0.88rem; color: #18261E;">
                    📍 <strong>Imported Context:</strong> {default_name} · Baseline Price: <strong>{format_rupees(default_price)}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        col_in1, col_in2 = st.columns(2)

        with col_in1:
            st.markdown("##### 1. Property Acquisition & Rental Terms")
            purchase_price = st.number_input(
                "Property Purchase Price (₹) *",
                min_value=100000.0,
                max_value=1000000000.0,
                value=float(default_price),
                step=100000.0,
                key="inv_purchase_price",
                help="Baseline purchase price or estimated property value.",
            )
            additional_costs = st.number_input(
                "Additional Acquisition Costs (₹)",
                min_value=0.0,
                max_value=50000000.0,
                value=round(purchase_price * 0.07, 0), # ~7% stamp duty & registration
                step=25000.0,
                key="inv_additional_costs",
                help="Estimated stamp duty, registration fees, legal fees, brokerage (typically 6-8%).",
            )
            monthly_rent = st.number_input(
                "Expected Monthly Rent (₹) *",
                min_value=0.0,
                max_value=2000000.0,
                value=float(default_rent),
                step=1000.0,
                key="inv_monthly_rent",
                help="Gross monthly rental income receivable from tenant.",
            )

        with col_in2:
            st.markdown("##### 2. Expenses & Holding Assumptions")
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                monthly_maint = st.number_input(
                    "Monthly Society Maintenance (₹)",
                    min_value=0.0,
                    max_value=200000.0,
                    value=3000.0,
                    step=500.0,
                    key="inv_monthly_maint",
                )
                annual_tax = st.number_input(
                    "Annual Property Tax (₹)",
                    min_value=0.0,
                    max_value=500000.0,
                    value=10000.0,
                    step=1000.0,
                    key="inv_annual_tax",
                )
            with col_exp2:
                monthly_emi = st.number_input(
                    "Monthly Loan EMI (₹)",
                    min_value=0.0,
                    max_value=1000000.0,
                    value=round(purchase_price * 0.007, 0), # rough estimate if financed
                    step=2000.0,
                    key="inv_monthly_emi",
                    help="Enter 0 if purchasing with 100% equity (all-cash).",
                )
                other_annual_exp = st.number_input(
                    "Other Annual Expenses (₹)",
                    min_value=0.0,
                    max_value=500000.0,
                    value=15000.0,
                    step=2000.0,
                    key="inv_other_annual_exp",
                    help="Insurance, annual maintenance, minor repairs.",
                )

            st.markdown("##### 3. Growth & Horizon Scenarios")
            col_scen1, col_scen2 = st.columns(2)
            with col_scen1:
                appreciation_rate = st.slider(
                    "Annual Appreciation Rate Assumption (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=6.0,
                    step=0.5,
                    key="inv_appreciation_rate",
                    help="Historical Indian urban residential real estate appreciation spans 4% - 8% depending on micro-market.",
                )
            with col_scen2:
                duration_years = st.select_slider(
                    "Investment Horizon (Years)",
                    options=[1, 3, 5, 10, 15],
                    value=5,
                    key="inv_duration_years",
                )

        # Execute Service Calculations
        yield_data = calculate_rental_yield(
            purchase_price=purchase_price,
            monthly_rent=monthly_rent,
            monthly_maintenance=monthly_maint,
            annual_property_tax=annual_tax,
            other_annual_expenses=other_annual_exp,
        )

        cashflow_data = analyze_rental_cash_flow(
            monthly_rent=monthly_rent,
            monthly_emi=monthly_emi,
            monthly_maintenance=monthly_maint,
            monthly_property_management=0.0,
            other_monthly_expenses=other_annual_exp / 12.0,
        )

        apprec_data = simulate_property_appreciation(
            current_value=purchase_price,
            annual_appreciation_rate_pct=appreciation_rate,
            years=duration_years,
        )

        roi_data = calculate_overall_roi(
            purchase_price=purchase_price,
            additional_purchase_costs=additional_costs,
            annual_rental_income=yield_data["annual_rental_income"],
            annual_operating_expenses=yield_data["annual_operating_expenses"],
            estimated_resale_value=apprec_data["future_value"],
            investment_duration_years=duration_years,
        )

        be_data = calculate_break_even_period(
            total_investment=roi_data["total_initial_investment"],
            net_annual_rental_income=yield_data["net_annual_rental_income"],
        )

        # ---------------------------------------------------------------------
        # KEY PERFORMANCE METRIC TILES
        # ---------------------------------------------------------------------
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🎯 Investment Performance Summary")

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric(
                label="Gross Rental Yield",
                value=f"{yield_data['gross_rental_yield_pct']:.2f}%",
                help="Annual Gross Rent / Purchase Price. Indian metros typically average 2.5% - 4.0%.",
            )
            st.caption(f"Net Yield: **{yield_data['net_rental_yield_pct']:.2f}%**")

        with m2:
            cf_sign = "+" if cashflow_data["is_positive"] else ""
            st.metric(
                label="Monthly Net Cash Flow",
                value=f"{cf_sign}{format_rupees(cashflow_data['monthly_net_cash_flow'])}",
                delta="Positive Cash Flow" if cashflow_data["is_positive"] else "Negative Cash Flow",
                delta_color="normal" if cashflow_data["is_positive"] else "inverse",
            )
            st.caption(f"Annual Cash Flow: {format_rupees(cashflow_data['annual_net_cash_flow'])}")

        with m3:
            st.metric(
                label=f"Projected Resale ({duration_years}Y)",
                value=format_rupees(apprec_data["future_value"]),
                delta=f"+{apprec_data['appreciation_pct']:.1f}% Total Gain",
            )
            st.caption(f"Assumed @ {appreciation_rate}% p.a.")

        with m4:
            st.metric(
                label=f"Total Investment ROI ({duration_years}Y)",
                value=f"{roi_data['roi_pct']:.1f}%",
                delta=f"{roi_data['annualized_roi_pct']:.1f}% Annualized",
            )
            st.caption(f"Total Profit: {format_rupees(roi_data['total_profit_or_loss'])}")

        # ---------------------------------------------------------------------
        # DETAILED MODULE BREAKDOWNS (Yield & Cash Flow + Capital Growth)
        # ---------------------------------------------------------------------
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        col_det1, col_det2 = st.columns([1.1, 1])

        with col_det1:
            st.markdown("##### 📈 Projected Property Valuation Trajectory")
            traj = apprec_data["trajectory"]
            traj_df = pd.DataFrame(traj)
            traj_df["Year"] = traj_df["year"].apply(lambda y: f"Year {y}")

            fig, ax = plt.subplots(figsize=(7, 3.8), dpi=140)
            ax.plot(
                traj_df["year"],
                traj_df["projected_value"] / 100000.0,
                marker="o",
                color="#2D5A43",
                linewidth=2.5,
                markersize=6,
                label="Property Valuation",
            )
            ax.fill_between(
                traj_df["year"],
                purchase_price / 100000.0,
                traj_df["projected_value"] / 100000.0,
                color="#3B7A5C",
                alpha=0.15,
                label="Capital Gain",
            )
            ax.axhline(purchase_price / 100000.0, color="#6B7C72", linestyle="--", linewidth=1.2, label="Base Cost")
            ax.set_title(f"Valuation Projection ({appreciation_rate}% p.a. Growth)", fontsize=11, fontweight="bold", pad=10, color="#18261E")
            ax.set_xlabel("Years Elapsed", fontsize=9, color="#18261E")
            ax.set_ylabel("Property Value (₹ in Lakhs)", fontsize=9, color="#18261E")
            ax.grid(axis="y", linestyle=":", alpha=0.6)
            ax.legend(frameon=True, facecolor="#FAF9F5", edgecolor="#E2E8E2", fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col_det2:
            st.markdown("##### 💵 Monthly Cash Inflow vs Outflow")
            inc = cashflow_data["total_monthly_income"]
            exp = cashflow_data["total_monthly_expenses"]
            net_cf = cashflow_data["monthly_net_cash_flow"]

            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 14px; padding: 18px 20px; box-shadow: 0 4px 12px rgba(24,38,30,0.03);">
                    <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid #EEF3ED;">
                        <span style="color: #6B7C72; font-size: 0.9rem;">Gross Monthly Rent</span>
                        <span style="font-weight: 700; color: #2D5A43; font-size: 0.95rem;">+{format_rupees(inc)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #EEF3ED;">
                        <span style="color: #6B7C72; font-size: 0.9rem;">- Monthly Loan EMI</span>
                        <span style="font-weight: 600; color: #18261E; font-size: 0.9rem;">-{format_rupees(monthly_emi)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #EEF3ED;">
                        <span style="color: #6B7C72; font-size: 0.9rem;">- Society Maintenance</span>
                        <span style="font-weight: 600; color: #18261E; font-size: 0.9rem;">-{format_rupees(monthly_maint)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #EEF3ED;">
                        <span style="color: #6B7C72; font-size: 0.9rem;">- Tax & Misc Reserve (Monthly Eqv.)</span>
                        <span style="font-weight: 600; color: #18261E; font-size: 0.9rem;">-{format_rupees((annual_tax + other_annual_exp) / 12.0)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-top: 10px; font-size: 1.05rem; font-weight: 800;">
                        <span style="color: #18261E;">Net Monthly Cash Flow</span>
                        <span style="color: {'#2D5A43' if net_cf >= 0 else '#C0392B'};">{'+' if net_cf >= 0 else ''}{format_rupees(net_cf)}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Cash Flow Explanation Note
            if cashflow_data["is_positive"]:
                st.success("✅ **Positive Cash Flow:** Rental receipts exceed monthly loan debt service and maintenance. The property provides passive monthly surplus.")
            else:
                st.warning("⚠️ **Negative Cash Flow:** Monthly expenses exceed rental income. You must contribute out-of-pocket funds each month to service the loan and property upkeep.")

            # Break-Even Analysis Box
            st.markdown("##### ⏱️ Equity Break-Even Period")
            if be_data["is_reachable"]:
                st.markdown(
                    f"""
                    <div style="background: #F4F7F3; border: 1px solid #D8E2D7; border-radius: 12px; padding: 12px 16px;">
                        <div style="font-size: 0.8rem; color: #6B7C72;">Time to recover initial acquisition cost ({format_rupees(roi_data['total_initial_investment'])}) via net rent:</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #2D5A43;">{be_data['message']}</div>
                        <div style="font-size: 0.75rem; color: #6B7C72; margin-top: 4px;">Based on Net Annual Rent of {format_rupees(yield_data['net_annual_rental_income'])}/year. Capital appreciation is evaluated separately.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background: #FDEDEC; border: 1px solid #F5B7B1; border-radius: 12px; padding: 12px 16px; color: #78281F; font-size: 0.88rem;">
                        <strong>Break-even unreachable from rental income alone:</strong> {be_data['message']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ---------------------------------------------------------------------
        # ROI & COMPREHENSIVE CASH BALANCE
        # ---------------------------------------------------------------------
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        st.markdown(f"#### 📊 Comprehensive {duration_years}-Year Holding Period Balance Sheet")

        c_roi1, c_roi2, c_roi3, c_roi4 = st.columns(4)
        c_roi1.metric("Initial Total Outlay", format_rupees(roi_data["total_initial_investment"]))
        c_roi2.metric("Cumulative Net Rent Collected", format_rupees(roi_data["cumulative_net_rent"]))
        c_roi3.metric(f"Projected Resale Value ({duration_years}Y)", format_rupees(roi_data["estimated_resale_value"]))
        c_roi4.metric(
            f"Net Investment Profit",
            format_rupees(roi_data["total_profit_or_loss"]),
            f"{roi_data['roi_pct']:.1f}% ROI",
        )

    # =========================================================================
    # TAB 2: MULTI-PROPERTY INVESTMENT COMPARISON
    # =========================================================================
    with tab_compare:
        st.markdown("#### ⚖️ Compare Investment Potential Across Properties")
        st.write("Benchmark 2 or 3 property scenarios side-by-side on yield, cash flow, and ROI.")

        num_compare = st.radio("Number of properties to evaluate:", [2, 3], horizontal=True, key="inv_cmp_count")

        comp_props = []

        if num_compare == 3:
            col_p1, col_p2, col_p3 = st.columns(3)
        else:
            col_p1, col_p2 = st.columns(2)
            col_p3 = None

        with col_p1:
            st.markdown("##### Property 1")
            name1 = st.text_input("Name / Title", value="Property A (Core City)", key="cmp_name1")
            price1 = st.number_input("Purchase Price (₹)", value=float(default_price), step=100000.0, key="cmp_pr1")
            rent1 = st.number_input("Monthly Rent (₹)", value=float(default_rent), step=1000.0, key="cmp_rt1")
            emi1 = st.number_input("Monthly EMI (₹)", value=round(price1 * 0.007, 0), step=1000.0, key="cmp_emi1")
            rate1 = st.slider("Appreciation (% p.a.)", 0.0, 15.0, 6.0, 0.5, key="cmp_rate1")
            comp_props.append({
                "name": name1,
                "purchase_price": price1,
                "monthly_rent": rent1,
                "monthly_emi": emi1,
                "monthly_maintenance": 3000.0,
                "annual_property_tax": 10000.0,
                "other_annual_expenses": 12000.0,
                "additional_purchase_costs": price1 * 0.07,
                "appreciation_rate_pct": rate1,
                "duration_years": 5,
            })

        with col_p2:
            st.markdown("##### Property 2")
            name2 = st.text_input("Name / Title", value="Property B (Suburban Growth)", key="cmp_name2")
            price2 = st.number_input("Purchase Price (₹)", value=float(max(default_price * 0.75, 2500000.0)), step=100000.0, key="cmp_pr2")
            rent2 = st.number_input("Monthly Rent (₹)", value=float(round(price2 * 0.0035, 0)), step=1000.0, key="cmp_rt2")
            emi2 = st.number_input("Monthly EMI (₹)", value=round(price2 * 0.007, 0), step=1000.0, key="cmp_emi2")
            rate2 = st.slider("Appreciation (% p.a.)", 0.0, 15.0, 8.0, 0.5, key="cmp_rate2")
            comp_props.append({
                "name": name2,
                "purchase_price": price2,
                "monthly_rent": rent2,
                "monthly_emi": emi2,
                "monthly_maintenance": 2500.0,
                "annual_property_tax": 8000.0,
                "other_annual_expenses": 10000.0,
                "additional_purchase_costs": price2 * 0.07,
                "appreciation_rate_pct": rate2,
                "duration_years": 5,
            })

        if col_p3:
            with col_p3:
                st.markdown("##### Property 3")
                name3 = st.text_input("Name / Title", value="Property C (High-Yield Studio)", key="cmp_name3")
                price3 = st.number_input("Purchase Price (₹)", value=float(max(default_price * 0.5, 2000000.0)), step=100000.0, key="cmp_pr3")
                rent3 = st.number_input("Monthly Rent (₹)", value=float(round(price3 * 0.0045, 0)), step=1000.0, key="cmp_rt3")
                emi3 = st.number_input("Monthly EMI (₹)", value=round(price3 * 0.007, 0), step=1000.0, key="cmp_emi3")
                rate3 = st.slider("Appreciation (% p.a.)", 0.0, 15.0, 5.0, 0.5, key="cmp_rate3")
                comp_props.append({
                    "name": name3,
                    "purchase_price": price3,
                    "monthly_rent": rent3,
                    "monthly_emi": emi3,
                    "monthly_maintenance": 1800.0,
                    "annual_property_tax": 5000.0,
                    "other_annual_expenses": 8000.0,
                    "additional_purchase_costs": price3 * 0.07,
                    "appreciation_rate_pct": rate3,
                    "duration_years": 5,
                })

        # Run Comparison Engine
        cmp_results = compare_investment_properties(comp_props)
        cmp_rows = cmp_results["rows"]
        best = cmp_results["best_in_metric"]

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 📊 Comparative Investment Matrix (5-Year Horizon)")

        # Build clean comparison table
        display_data = []
        for r in cmp_rows:
            display_data.append({
                "Property": r["name"],
                "Purchase Price": format_rupees(r["purchase_price"]),
                "Monthly Rent": format_rupees(r["monthly_rent"]),
                "Gross Yield": f"{r['gross_rental_yield']:.2f}%",
                "Net Yield": f"{r['net_rental_yield']:.2f}%",
                "Monthly Cash Flow": f"{'+' if r['monthly_cash_flow'] >= 0 else ''}{format_rupees(r['monthly_cash_flow'])}",
                "Projected 5Y Resale": format_rupees(r["estimated_future_value"]),
                "Total 5Y ROI": f"{r['total_roi']:.1f}%",
            })

        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

        # Highlight Strongest Results
        st.markdown("##### 🏆 Metric Highlights")
        h_col1, h_col2, h_col3 = st.columns(3)
        with h_col1:
            st.markdown(f"• **Highest Gross Yield:** {best.get('highest_gross_yield')}")
            st.markdown(f"• **Highest Net Yield:** {best.get('highest_net_yield')}")
        with h_col2:
            st.markdown(f"• **Highest Cash Flow:** {best.get('highest_cash_flow')}")
            st.markdown(f"• **Lowest Purchase Price:** {best.get('lowest_price')}")
        with h_col3:
            st.markdown(f"• **Highest Future Resale:** {best.get('highest_future_value')}")
            st.markdown(f"• **Highest Total ROI:** {best.get('highest_roi')}")

        st.caption("Note: Metric highlights reflect the mathematical maximum for each attribute. Investors should weigh cash-flow needs against long-term capital growth.")

    # =========================================================================
    # TAB 3: FORMULAS & METHODOLOGY
    # =========================================================================
    with tab_methodology:
        st.markdown("#### 📖 Mathematical Formulas & Real-Estate Assumptions")
        st.markdown(
            r"""
            ##### 1. Rental Yield
            $$\text{Gross Rental Yield} = \left(\frac{\text{Monthly Rent} \times 12}{\text{Purchase Price}}\right) \times 100$$
            
            $$\text{Net Rental Yield} = \left(\frac{(\text{Monthly Rent} \times 12) - \text{Annual Operating Expenses}}{\text{Purchase Price}}\right) \times 100$$
            
            Operating expenses include regular society maintenance fees, municipal property taxes, insurance, and maintenance provisions.
            
            ##### 2. Property Appreciation (Compound Value)
            $$\text{Future Value} = \text{Current Value} \times (1 + r)^n$$
            *(where $r$ is the annual assumed appreciation rate and $n$ is the number of years).*
            
            ##### 3. Monthly Net Cash Flow
            $$\text{Net Cash Flow} = \text{Gross Rent} - (\text{Monthly Loan EMI} + \text{Maintenance} + \text{Monthly Reserves})$$
            
            ##### 4. Total Return on Investment (ROI)
            $$\text{Total Inflows} = \text{Resale Value} + \text{Cumulative Net Rent Collected}$$
            $$\text{Total Outflows} = \text{Purchase Price} + \text{Additional Acquisition Costs (Stamp Duty, Reg)}$$
            $$\text{Total Net Profit} = \text{Total Inflows} - \text{Total Outflows}$$
            $$\text{Total ROI (\%)} = \left(\frac{\text{Total Net Profit}}{\text{Total Outflows}}\right) \times 100$$
            """
        )


def render_investment_page():
    """Alias for backwards compatibility."""
    render_investment_analysis_page()


if __name__ == "__main__":
    render_investment_analysis_page()

