import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.components.navbar import render_section_header
from frontend.components.charts import render_emi_donut_chart
from backend.services.finance_service import calculate_home_loan_emi, calculate_affordability
from backend.services.prediction_service import format_rupees


def render_emi_calculator_page():
    render_section_header(
        "Financial Analytics",
        "EMI & Home Loan Affordability Calculator",
        "Evaluate monthly outflow, interest obligations, and maximum borrowing capacity tailored to Indian mortgage terms."
    )

    # Prefill price if coming from Estimate page
    default_price = float(st.session_state.get("prefill_price", 7500000.0))

    tab1, tab2 = st.tabs(["📊 Loan EMI & Repayment Schedule", "💼 Income & Affordability Check"])

    with tab1:
        col1, col2 = st.columns([1.1, 1.4], gap="large")

        with col1:
            st.markdown("#### Loan Parameters")
            price = st.number_input(
                "Property Price (₹)",
                min_value=500000.0,
                max_value=1000000000.0,
                value=default_price,
                step=100000.0,
                format="%.0f",
            )
            down_payment_pct = st.slider("Down Payment Percentage (%)", min_value=10, max_value=80, value=20, step=5)
            down_payment = (price * down_payment_pct) / 100.0
            st.caption(f"Down Payment Amount: **{format_rupees(down_payment)}**")

            interest_rate = st.slider("Annual Interest Rate (%)", min_value=6.0, max_value=15.0, value=8.5, step=0.1)
            tenure_years = st.slider("Loan Tenure (Years)", min_value=5, max_value=30, value=20, step=1)

            emi_result = calculate_home_loan_emi(
                property_price=price,
                down_payment=down_payment,
                annual_interest_rate=interest_rate,
                tenure_years=tenure_years,
            )

        with col2:
            st.markdown("#### Repayment Breakdown")
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 20px; padding: 26px; box-shadow: 0 4px 12px rgba(24,38,30,0.04);">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #3B7A5C; text-transform: uppercase; letter-spacing: 1px;">Monthly Repayment</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #2D5A43; line-height: 1.1; margin: 8px 0 16px 0;">
                        {format_rupees(emi_result['monthly_emi'])} <span style="font-size: 1rem; color: #6B7C72; font-weight: 500;">/ month</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; border-top: 1px solid #EEF3ED; padding-top: 16px;">
                        <div>
                            <div style="font-size: 0.78rem; color: #6B7C72;">Principal Loan Amount</div>
                            <div style="font-weight: 700; font-size: 1.1rem; color: #18261E;">{format_rupees(emi_result['principal'])}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.78rem; color: #6B7C72;">Total Interest Payable</div>
                            <div style="font-weight: 700; font-size: 1.1rem; color: #B35C1E;">{format_rupees(emi_result['total_interest'])}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.78rem; color: #6B7C72;">Total Repayment (P + I)</div>
                            <div style="font-weight: 700; font-size: 1.1rem; color: #18261E;">{format_rupees(emi_result['total_repayment'])}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.78rem; color: #6B7C72;">Down Payment Paid</div>
                            <div style="font-weight: 700; font-size: 1.1rem; color: #2D5A43;">{format_rupees(emi_result['down_payment'])}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Chart
            render_emi_donut_chart(emi_result["principal"], emi_result["total_interest"])

    with tab2:
        st.markdown("#### Affordability Eligibility Check")
        st.write("Banks in India generally mandate that your total EMI outgo should not exceed 40% to 50% of your gross monthly take-home income (FOIR).")

        c_inc1, c_inc2 = st.columns(2)
        with c_inc1:
            monthly_income = st.number_input(
                "Net Monthly Household Income (₹)",
                min_value=25000.0,
                max_value=10000000.0,
                value=150000.0,
                step=10000.0,
            )
        with c_inc2:
            existing_emis = st.number_input(
                "Existing Monthly EMIs / Obligations (₹)",
                min_value=0.0,
                max_value=5000000.0,
                value=15000.0,
                step=5000.0,
            )

        afford = calculate_affordability(monthly_income, existing_emis)

        st.markdown(
            f"""
            <div style="background: #EEF3ED; border: 1px solid #D8E2D7; border-radius: 18px; padding: 24px; margin-top: 16px;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #2D5A43; text-transform: uppercase;">Affordability Assessment</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 14px;">
                    <div>
                        <div style="font-size: 0.8rem; color: #6B7C72;">Max Recommended EMI</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #2D5A43;">{format_rupees(afford['max_recommended_emi'])} / mo</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #6B7C72;">Max Loan Borrowing Capacity</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #18261E;">{format_rupees(afford['max_loan_capacity'])}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #6B7C72;">Recommended Property Budget (with 20% down)</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #3B7A5C;">{format_rupees(afford['max_recommended_property_budget'])}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_emi_page():
    """Alias for backwards compatibility."""
    render_emi_calculator_page()


if __name__ == "__main__":
    render_emi_calculator_page()
