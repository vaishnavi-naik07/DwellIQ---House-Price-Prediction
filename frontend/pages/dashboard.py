import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import base64
import streamlit as st
from frontend.components.navbar import render_section_header
from backend.services.prediction_service import format_rupees
from backend.core.config import HERO_IMG_PATH


def get_image_base64(path: Path) -> str:
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def render_dashboard_page(current_user=None):
    hero_b64 = get_image_base64(HERO_IMG_PATH)
    bg_style = (
        f"linear-gradient(to right, rgba(17, 31, 23, 0.94) 0%, rgba(17, 31, 23, 0.82) 42%, rgba(17, 31, 23, 0.35) 75%, rgba(17, 31, 23, 0.15) 100%), url('data:image/jpeg;base64,{hero_b64}')"
        if hero_b64
        else "linear-gradient(135deg, #15241C, #2D5A43)"
    )

    user_name = current_user.get("full_name") if current_user else ""
    first_name = user_name.split()[0] if user_name else ""
    greeting_pill = (
        f"""<div style="margin-bottom: 8px; font-size: 1.1rem; color: #A3D4B6; font-weight: 700;">Good day, {first_name} 👋</div>"""
        if first_name
        else ""
    )

    # 1. Landing Page Hero
    st.markdown(
        f"""
        <div class="hero-banner-dwell" style="background-image: {bg_style}; background-size: cover; background-position: center right;">
            <div class="hero-overlay-content">
                <div class="hero-pill-badge">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #52C480; box-shadow: 0 0 10px #52C480;"></span>
                    <span>AI-Powered Real Estate Intelligence</span>
                </div>
                {greeting_pill}
                <h1 class="hero-title-main">Find Your Place.<br><span>Understand Its Value.</span></h1>
                <p class="hero-sub-p">
                    DwellIQ combines machine learning on 177,000+ real estate transactions across 80+ Indian cities with comprehensive financial analytics, nearby infrastructure mapping, and an intelligent advisory assistant.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick Action Buttons
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("✨ Estimate Property", key="dash_btn_est", use_container_width=True):
            st.session_state["page_nav"] = "Estimate a Property"
            st.rerun()
    with c2:
        if st.button("⚖️ Compare Properties", key="dash_btn_comp", use_container_width=True):
            st.session_state["page_nav"] = "Compare Properties"
            st.rerun()
    with c3:
        if st.button("💬 Ask DwellIQ AI", key="dash_btn_chat", use_container_width=True):
            st.session_state["page_nav"] = "DwellIQ AI Advisor"
            st.rerun()
    with c4:
        if st.button("🏦 EMI Calculator", key="dash_btn_emi", use_container_width=True):
            st.session_state["page_nav"] = "EMI Calculator"
            st.rerun()

    # 2. Genuine Dataset & Market Statistics (From 177k cleaned records)
    render_section_header(
        "Market Dynamics",
        "Key Figures From Cleaned Real-Estate Data",
        "All figures reflect verified empirical statistics from the 177,000+ pan-India residential property dataset."
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">177,847</div>
                <div class="dwell-stat-title">Verified Listings</div>
                <div class="dwell-stat-caption">Scraped and curated across Indian metros & tier-1 cities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">₹78.0 Lakh</div>
                <div class="dwell-stat-title">Pan-India Median Price</div>
                <div class="dwell-stat-caption">Robust median pricing avoiding distortion from luxury outliers</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">81 Cities</div>
                <div class="dwell-stat-title">Geographic Coverage</div>
                <div class="dwell-stat-caption">Including Mumbai, Delhi NCR, Bangalore, Pune, Hyderabad & more</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s4:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">1,100 sq.ft</div>
                <div class="dwell-stat-title">Median Carpet Area</div>
                <div class="dwell-stat-caption">Most common configuration is 3 BHK family residences</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Interactive City Price Explorer
    render_section_header(
        "Interactive Discovery",
        "Property Search & City Benchmarks",
        "Explore real median prices by location before estimating specific units."
    )

    search_col1, search_col2, search_col3 = st.columns(3)
    with search_col1:
        selected_city = st.selectbox(
            "Select Target City / Hub",
            [
                "New-Delhi", "Mumbai", "Bangalore", "Pune", "Gurgaon", "Kolkata",
                "Ahmedabad", "Hyderabad", "Chennai", "Jaipur", "Thane", "Vadodara"
            ],
            key="dash_search_city",
        )
    with search_col2:
        budget_range = st.selectbox(
            "Budget Preference",
            ["Under ₹50 Lakh", "₹50 Lakh - ₹1 Cr", "₹1 Cr - ₹2.5 Cr", "Luxury (> ₹2.5 Cr)"],
            key="dash_search_budget",
        )
    with search_col3:
        prop_type = st.selectbox(
            "Configuration",
            ["1 BHK", "2 BHK", "3 BHK", "4+ BHK Penthouse"],
            key="dash_search_type",
        )

    city_medians = {
        "New-Delhi": (16000000, 24945, "₹1.60 Cr"),
        "Mumbai": (21000000, 1814, "₹2.10 Cr"),
        "Bangalore": (8500000, 23262, "₹85.0 Lakh"),
        "Pune": (7000000, 2177, "₹70.0 Lakh"),
        "Gurgaon": (15700000, 18846, "₹1.57 Cr"),
        "Kolkata": (5100000, 21605, "₹51.0 Lakh"),
        "Ahmedabad": (7000000, 12614, "₹70.0 Lakh"),
        "Hyderabad": (8180000, 11147, "₹81.8 Lakh"),
        "Chennai": (6900000, 10163, "₹69.0 Lakh"),
        "Jaipur": (5100000, 7867, "₹51.0 Lakh"),
        "Thane": (7000000, 1869, "₹70.0 Lakh"),
        "Vadodara": (3900000, 2361, "₹39.0 Lakh"),
    }

    if selected_city in city_medians:
        median_val, count, display_str = city_medians[selected_city]
        st.info(
            f"📍 **{selected_city} Market Snapshot:** Dataset records: **{count:,} listings** · "
            f"Median Price: **{display_str}** · Target Filter: **{budget_range} ({prop_type})**"
        )

    # 4. Platform Capabilities Grid
    render_section_header(
        "Platform Modules",
        "A Unified Suite for Real-Estate Decision Making"
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-icon-bubble">🎯</div>
                <div class="feature-title-dwell">Valuation Intelligence</div>
                <div class="feature-desc-dwell">
                    Ensemble Random Forest algorithm predicting fair market estimates based on 12 verified engineering and property parameters.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-icon-bubble">📍</div>
                <div class="feature-title-dwell">Nearby Essentials</div>
                <div class="feature-desc-dwell">
                    Integrated OpenStreetMap Nominatim search for hospitals, metro stations, schools, and supermarkets within 1km to 10km.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-icon-bubble">💬</div>
                <div class="feature-title-dwell">AI Real-Estate Advisor</div>
                <div class="feature-desc-dwell">
                    Intelligent consultation on property affordability rules, RERA compliance checklists, carpet area nuances, and loan approvals.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_overview_page():
    """Alias for backwards compatibility."""
    render_dashboard_page()


if __name__ == "__main__":
    render_dashboard_page()
