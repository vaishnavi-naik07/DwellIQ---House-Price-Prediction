
import base64
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# --------------------------------------------------
# 1. PROJECT SETTINGS & CONSTANTS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.joblib"
REPORT_PATH = PROJECT_ROOT / "reports" / "model_comparison.csv"
HERO_IMG_PATH = PROJECT_ROOT / "assets" / "luxury_home.jpg"
FIG_FEAT_PATH = PROJECT_ROOT / "reports" / "figures" / "feature_importance.png"
FIG_COMP_PATH = PROJECT_ROOT / "reports" / "figures" / "model_comparison_mae.png"

st.set_page_config(
    page_title="DwellIQ | Smart Property Estimates",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Pre-known top locations from the 187k+ records dataset
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


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def format_rupees(amount: float) -> str:
    """Format an amount in Indian Rupees (Crores, Lakhs, or full amount)."""
    if amount >= 10_000_000:
        cr = amount / 10_000_000
        return f"₹{cr:.2f} Cr"
    elif amount >= 100_000:
        lakh = amount / 100_000
        return f"₹{lakh:.2f} Lakh"
    return f"₹{amount:,.0f}"


def get_image_as_base64(path: Path) -> str:
    """Encode local image to base64 for reliable display."""
    if path.exists():
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""


hero_base64 = get_image_as_base64(HERO_IMG_PATH)


# --------------------------------------------------
# 3. DWELLIQ DESIGN SYSTEM (PREMIUM SAGE & FOREST THEME)
# --------------------------------------------------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    :root {{
        --cream: #FAF9F5;
        --card-bg: #FFFFFF;
        --green: #2D5A43;
        --green-hover: #1E3D2D;
        --emerald: #3B7A5C;
        --sage-light: #EEF3ED;
        --sage-border: #D8E2D7;
        --ink: #18261E;
        --ink-light: #4A5B51;
        --muted: #6B7C72;
        --border-color: #E2E8E2;
        --shadow-sm: 0 4px 12px rgba(24, 38, 30, 0.04);
        --shadow-md: 0 10px 28px rgba(24, 38, 30, 0.07);
        --shadow-lg: 0 16px 40px rgba(24, 38, 30, 0.11);
    }}

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: var(--ink);
    }}

    .stApp {{
        background: var(--cream);
    }}

    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1360px;
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
    }}

    /* Typography */
    h1, h2, h3, .serif-heading {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800;
        color: var(--ink);
        letter-spacing: -0.6px;
    }}

    /* Top Brand Bar */
    .brand-container {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 10px 0;
    }}

    .brand-logo-badge {{
        background: linear-gradient(135deg, var(--green), var(--emerald));
        color: white;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        box-shadow: 0 4px 12px rgba(45, 90, 67, 0.25);
    }}

    .brand-title {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 1.65rem;
        letter-spacing: -0.8px;
        color: var(--ink);
        line-height: 1.1;
    }}

    .brand-title span {{
        color: var(--emerald);
    }}

    .brand-tag {{
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }}

    /* Auth status chip */
    .user-chip {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--sage-light);
        border: 1px solid var(--sage-border);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.83rem;
        font-weight: 700;
        color: var(--green);
    }}

    /* Hero Banner with Modern Indian Luxury Villa */
    .hero-banner {{
        position: relative;
        border-radius: 28px;
        overflow: hidden;
        margin: 18px 0 32px 0;
        background: #15241C;
        box-shadow: var(--shadow-lg);
        border: 1px solid rgba(216, 226, 215, 0.6);
        min-height: 440px;
        display: flex;
        align-items: center;
    }}

    .hero-bg-img {{
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background-image: linear-gradient(to right, rgba(17, 31, 23, 0.94) 0%, rgba(17, 31, 23, 0.82) 42%, rgba(17, 31, 23, 0.35) 75%, rgba(17, 31, 23, 0.15) 100%),
                          url('data:image/jpeg;base64,{hero_base64}');
        background-size: cover;
        background-position: center right;
        z-index: 1;
    }}

    .hero-content {{
        position: relative;
        z-index: 2;
        padding: 56px 52px;
        max-width: 680px;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(238, 243, 237, 0.18);
        border: 1px solid rgba(216, 226, 215, 0.35);
        backdrop-filter: blur(8px);
        color: #D6E8D8;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }}

    .hero-badge-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #52C480;
        box-shadow: 0 0 10px #52C480;
    }}

    .hero-headline {{
        color: #FFFFFF;
        font-size: clamp(2.2rem, 4.2vw, 3.4rem);
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -1.2px;
        margin-bottom: 16px;
    }}

    .hero-headline span {{
        color: #A3D4B6;
    }}

    .hero-desc {{
        color: #CAD5CE;
        font-size: 1.05rem;
        line-height: 1.65;
        font-weight: 400;
        margin-bottom: 24px;
    }}

    /* Stat Cards */
    .stat-pill-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin: 24px 0 10px 0;
    }}

    .stat-pill {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 20px 24px;
        flex: 1;
        min-width: 200px;
        box-shadow: var(--shadow-sm);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}

    .stat-pill:hover {{
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--sage-border);
    }}

    .stat-num {{
        font-size: 1.95rem;
        font-weight: 800;
        color: var(--green);
        letter-spacing: -1px;
        line-height: 1.1;
    }}

    .stat-label {{
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--ink);
        margin-top: 4px;
    }}

    .stat-sub {{
        font-size: 0.77rem;
        color: var(--muted);
        margin-top: 3px;
    }}

    /* Section Headers */
    .section-title-wrap {{
        margin: 36px 0 18px 0;
    }}

    .section-eyebrow {{
        font-size: 0.74rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        color: var(--emerald);
        margin-bottom: 6px;
    }}

    .section-title {{
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        color: var(--ink);
        margin-bottom: 6px;
    }}

    .section-sub {{
        font-size: 0.95rem;
        color: var(--muted);
        line-height: 1.6;
    }}

    /* Premium Feature Cards */
    .premium-card {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 26px;
        height: 100%;
        box-shadow: var(--shadow-sm);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        display: flex;
        flex-direction: column;
    }}

    .premium-card:hover {{
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
        border-color: var(--sage-border);
    }}

    .premium-card-icon {{
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: var(--sage-light);
        color: var(--green);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        margin-bottom: 16px;
        border: 1px solid var(--sage-border);
    }}

    .premium-card-title {{
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--ink);
        margin-bottom: 8px;
    }}

    .premium-card-desc {{
        font-size: 0.91rem;
        color: var(--ink-light);
        line-height: 1.65;
        flex-grow: 1;
    }}

    /* How It Works Steps */
    .step-card {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 22px;
        box-shadow: var(--shadow-sm);
        height: 100%;
        position: relative;
    }}

    .step-num {{
        display: inline-block;
        background: var(--sage-light);
        color: var(--green);
        border: 1px solid var(--sage-border);
        font-size: 0.76rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 12px;
    }}

    .step-title {{
        font-size: 1.02rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 6px;
    }}

    .step-desc {{
        font-size: 0.86rem;
        color: var(--muted);
        line-height: 1.6;
    }}

    /* Form Container */
    div[data-testid="stForm"] {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 34px 36px;
        box-shadow: var(--shadow-md);
    }}

    .form-section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.08rem;
        font-weight: 800;
        color: var(--ink);
        margin: 18px 0 14px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--sage-light);
    }}

    .form-step-badge {{
        background: var(--sage-light);
        color: var(--green);
        border: 1px solid var(--sage-border);
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 800;
    }}

    /* Inputs Styling */
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] > div {{
        background: #F8FAF7 !important;
        border-radius: 12px !important;
        border-color: var(--border-color) !important;
        color: var(--ink) !important;
        font-weight: 500 !important;
    }}

    div[data-baseweb="input"] input:focus {{
        border-color: var(--emerald) !important;
        box-shadow: 0 0 0 2px rgba(59, 122, 92, 0.15) !important;
    }}

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, var(--green) 0%, var(--emerald) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        min-height: 52px !important;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 6px 18px rgba(45, 90, 67, 0.25) !important;
        transition: all 0.25s ease !important;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: linear-gradient(135deg, var(--green-hover) 0%, var(--green) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(45, 90, 67, 0.35) !important;
    }}

    /* Navigation Radio Group */
    div[role="radiogroup"] {{
        background: #EEF3ED;
        padding: 5px;
        border-radius: 16px;
        gap: 6px;
        border: 1px solid var(--sage-border);
    }}

    div[role="radiogroup"] label {{
        background: transparent !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 9px 18px !important;
        font-weight: 600 !important;
        color: var(--ink-light) !important;
        transition: all 0.2s ease !important;
    }}

    div[role="radiogroup"] label[data-checked="true"],
    div[role="radiogroup"] label:has(input:checked) {{
        background: #FFFFFF !important;
        color: var(--green) !important;
        box-shadow: 0 2px 8px rgba(24, 38, 30, 0.08) !important;
    }}

    /* Prediction Result Showcase Card */
    .prediction-showcase {{
        background: linear-gradient(135deg, #F0F6F1 0%, #E6EFE8 100%);
        border: 1.5px solid var(--sage-border);
        border-radius: 26px;
        padding: 38px 40px;
        margin: 28px 0 20px 0;
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }}

    .prediction-showcase::after {{
        content: "🏡";
        position: absolute;
        right: 28px;
        bottom: 12px;
        font-size: 8rem;
        opacity: 0.08;
        pointer-events: none;
    }}

    .pred-eyebrow {{
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        color: var(--emerald);
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .pred-price-primary {{
        font-size: clamp(2.4rem, 5.5vw, 3.8rem);
        font-weight: 800;
        letter-spacing: -1.6px;
        color: var(--green);
        line-height: 1.1;
        margin: 12px 0 6px 0;
    }}

    .pred-price-secondary {{
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--muted);
        margin-bottom: 14px;
    }}

    .pred-range-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid var(--sage-border);
        padding: 7px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--ink);
    }}

    /* Summary Matrix Card */
    .summary-card {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px;
        box-shadow: var(--shadow-sm);
        margin-top: 14px;
    }}

    .summary-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 16px;
        margin-top: 10px;
    }}

    .summary-item {{
        background: var(--sage-light);
        border-radius: 12px;
        padding: 12px 14px;
    }}

    .summary-item-label {{
        font-size: 0.74rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
    }}

    .summary-item-val {{
        font-size: 1.02rem;
        font-weight: 800;
        color: var(--ink);
        margin-top: 2px;
    }}

    /* Academic Banner */
    .academic-banner {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 22px;
        padding: 30px 32px;
        box-shadow: var(--shadow-sm);
        margin: 20px 0;
    }}

    /* Clean Footer */
    .dwell-footer {{
        border-top: 1px solid var(--border-color);
        margin-top: 48px;
        padding-top: 32px;
        text-align: center;
    }}

    .footer-brand {{
        font-weight: 800;
        font-size: 1.2rem;
        color: var(--green);
        letter-spacing: -0.4px;
    }}

    .footer-text {{
        color: var(--muted);
        font-size: 0.84rem;
        margin-top: 6px;
        line-height: 1.6;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 4. LOAD SAVED MODEL BUNDLE CORRECTLY
# --------------------------------------------------

@st.cache_resource
def load_model_bundle():
    """
    Load the saved dictionary and extract the trained ML pipeline.
    Preserves train_model.py compatibility where pipeline is under 'model'.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Saved model not found at: {MODEL_PATH}. "
            "Please run src/train_model.py first."
        )

    model_data = joblib.load(MODEL_PATH)

    if not isinstance(model_data, dict):
        return {
            "model": model_data,
            "model_name": "Saved ML Model",
            "metrics": {},
            "feature_columns": [],
        }

    if "model" not in model_data:
        raise KeyError("The saved model dictionary does not contain a 'model' key.")

    return model_data


try:
    model_bundle = load_model_bundle()
    model = model_bundle["model"]
    model_name = model_bundle.get("model_name", "Random Forest Regressor")
    model_metrics = model_bundle.get("metrics", {})
    expected_features = model_bundle.get("feature_columns", [])
    model_error = None
except Exception as error:
    model = None
    model_name = "Unavailable"
    model_metrics = {}
    expected_features = []
    model_error = str(error)


# --------------------------------------------------
# 5. NAVIGATION OPTIONS
# --------------------------------------------------

nav_options = ["Overview", "Estimate a Property", "About the Project"]

if "page_nav" not in st.session_state or st.session_state["page_nav"] not in nav_options:
    st.session_state["page_nav"] = "Overview"

# --------------------------------------------------
# 6. HEADER AND NAVIGATION
# --------------------------------------------------

nav_left, nav_right = st.columns([1.1, 1.9], gap="medium")

with nav_left:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-logo-badge">🏡</div>
            <div>
                <div class="brand-title">Dwell<span>IQ</span></div>
                <div class="brand-tag">Smart Property Estimates · Real Estate AI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_right:
    selected_page = st.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state["page_nav"]),
        horizontal=True,
        label_visibility="collapsed",
        key="app_navigation_radio",
    )
    if selected_page != st.session_state["page_nav"]:
        st.session_state["page_nav"] = selected_page
        st.rerun()


# --------------------------------------------------
# 7. OVERVIEW / HOMEPAGE
# --------------------------------------------------

if st.session_state["page_nav"] == "Overview":

    # --- Hero Section with Modern Indian Luxury Villa ---
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-bg-img"></div>
            <div class="hero-content">
                <div class="hero-badge">
                    <span class="hero-badge-dot"></span>
                    Machine Learning Valuation Engine
                </div>
                <div class="hero-headline">
                    Find your place.<br><span>Understand its value.</span>
                </div>
                <div class="hero-desc">
                    Explore transparent residential property price estimates powered by
                    trained regression algorithms, 80+ cities across India, and comprehensive
                    architectural parameters.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hero Action Bar
    cta_col1, cta_col2 = st.columns([1, 1], gap="medium")
    with cta_col1:
        if st.button("✨  Estimate Property Price Now  →", key="btn_hero_estimate", use_container_width=True):
            st.session_state["page_nav"] = "Estimate a Property"
            st.rerun()
    with cta_col2:
        if st.button("📊  View Model Metrics & Architecture  →", key="btn_hero_about", use_container_width=True):
            st.session_state["page_nav"] = "About the Project"
            st.rerun()

    # --- Dataset Highlights & Statistics ---
    st.markdown(
        """
        <div class="stat-pill-row">
            <div class="stat-pill">
                <div class="stat-num">187,500+</div>
                <div class="stat-label">Housing Listings</div>
                <div class="stat-sub">Validated raw housing records</div>
            </div>
            <div class="stat-pill">
                <div class="stat-num">80+</div>
                <div class="stat-label">Indian Cities</div>
                <div class="stat-sub">Tier-1, Tier-2, & Metro markets</div>
            </div>
            <div class="stat-pill">
                <div class="stat-num">12</div>
                <div class="stat-label">Feature Signals</div>
                <div class="stat-sub">BHK, area, floor, facing, parking</div>
            </div>
            <div class="stat-pill">
                <div class="stat-num">Random Forest</div>
                <div class="stat-label">Ensemble Regressor</div>
                <div class="stat-sub">Non-linear feature interaction</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Feature Cards ---
    st.markdown(
        """
        <div class="section-title-wrap">
            <div class="section-eyebrow">Intelligent Capabilities</div>
            <div class="section-title">Property insights, engineered for clarity.</div>
            <div class="section-sub">
                Designed to make residential price discovery intuitive, transparent, and academically sound.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3, gap="medium")

    with f1:
        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-icon">⚡</div>
                <div class="premium-card-title">Instant ML Inference</div>
                <div class="premium-card-desc">
                    Generates instantaneous predictions using a Scikit-Learn pipeline
                    trained on thousands of validated real estate listings.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-icon">📐</div>
                <div class="premium-card-title">Multi-Signal Attributes</div>
                <div class="premium-card-desc">
                    Accounts for carpet area, floor height, vastu facing, furnishing
                    state, balconies, and parking accommodations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-icon">🎯</div>
                <div class="premium-card-title">Dual-Unit Formatting</div>
                <div class="premium-card-desc">
                    Outputs estimations clearly in Indian denominations (Lakhs and Crores)
                    along with empirical variance ranges.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- How It Works Section ---
    st.markdown(
        """
        <div class="section-title-wrap">
            <div class="section-eyebrow">Step-By-Step Workflow</div>
            <div class="section-title">How DwellIQ calculates estimates</div>
            <div class="section-sub">
                From raw property inputs to normalized price predictions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    h1, h2, h3, h4 = st.columns(4, gap="medium")

    with h1:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">STEP 01</div>
                <div class="step-title">Specify Parameters</div>
                <div class="step-desc">Select location, bedroom configuration, carpet area, and building specifics.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h2:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">STEP 02</div>
                <div class="step-title">Data Transformation</div>
                <div class="step-desc">Categorical columns are one-hot encoded and missing numeric inputs are median-imputed.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h3:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">STEP 03</div>
                <div class="step-title">Ensemble Evaluation</div>
                <div class="step-desc">The Random Forest ensemble evaluates feature trees to compute a target estimate.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h4:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">STEP 04</div>
                <div class="step-title">Summary & Valuation</div>
                <div class="step-desc">Delivers standard Indian Rupee figures (₹ Lakh / ₹ Cr) with full summary metrics.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Project Scope Disclaimer
    st.markdown(
        """
        <div class="academic-banner" style="margin-top: 36px;">
            <div style="font-weight: 800; font-size: 1.05rem; color: #18261E; margin-bottom: 6px;">
                🎓 Academic Project & Exploration Scope
            </div>
            <p style="color: #6B7C72; margin: 0; line-height: 1.7; font-size: 0.91rem;">
                DwellIQ was created as an educational machine learning project exploring property valuation
                models. Real-estate values are subject to micro-market variables, builder reputation, legal
                clearances, and negotiation dynamics. Estimates should be treated as experimental analytical
                approximations rather than certified real-estate appraisals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# 8. ESTIMATE A PROPERTY PAGE
# --------------------------------------------------

elif st.session_state["page_nav"] == "Estimate a Property":

    st.markdown(
        """
        <div class="section-title-wrap" style="margin-top: 10px;">
            <div class="section-eyebrow">Valuation Calculator</div>
            <div class="section-title">Estimate your property value</div>
            <div class="section-sub">
                Fill in the property specifics below. Each attribute feeds directly into our trained machine learning pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if model_error:
        st.error(
            "⚠️ The saved model pipeline could not be loaded. "
            "Please ensure 'models/best_model.joblib' exists."
        )
        with st.expander("Technical Error Details"):
            st.code(model_error)

    else:
        with st.form("property_estimation_form"):

            # Section 1
            st.markdown(
                """
                <div class="form-section-header">
                    <span class="form-step-badge">1</span>
                    Location & Structural Essentials
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2, gap="large")

            with col1:
                default_loc_index = (
                    DATASET_LOCATIONS.index("Mumbai")
                    if "Mumbai" in DATASET_LOCATIONS else 0
                )
                location = st.selectbox(
                    "City / Location",
                    DATASET_LOCATIONS,
                    index=default_loc_index,
                    help="Select the city where the residential property is situated.",
                )

                bhk = st.selectbox(
                    "Bedrooms Configuration (BHK)",
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    index=1,
                    help="Number of bedrooms (hall & kitchen).",
                )

                carpet_area = st.number_input(
                    "Carpet Area (sq. ft.)",
                    min_value=100,
                    max_value=25000,
                    value=950,
                    step=50,
                    help="Usable net floor area inside the walls.",
                )

            with col2:
                bathrooms = st.selectbox(
                    "Number of Bathrooms",
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    index=1,
                )

                balconies = st.selectbox(
                    "Number of Balconies",
                    [0, 1, 2, 3, 4, 5],
                    index=1,
                )

                floor = st.selectbox(
                    "Floor Level",
                    [
                        "1", "2", "3", "4", "5", "6", "7", "8",
                        "9", "10", "11", "12", "13", "14", "15",
                        "16", "17", "18", "19", "20", "Ground",
                        "Upper Basement", "Lower Basement", "Other",
                    ],
                    index=4,
                )

            # Section 2
            st.markdown(
                """
                <div class="form-section-header" style="margin-top: 26px;">
                    <span class="form-step-badge">2</span>
                    Property Characteristics & Vastu
                </div>
                """,
                unsafe_allow_html=True,
            )

            col3, col4 = st.columns(2, gap="large")

            with col3:
                furnishing = st.selectbox(
                    "Furnishing State",
                    ["Unfurnished", "Semi-Furnished", "Furnished"],
                    index=1,
                )

                status = st.selectbox(
                    "Construction Status",
                    ["Ready to Move", "Under Construction"],
                    index=0,
                )

                transaction = st.selectbox(
                    "Transaction Type",
                    ["Resale", "New Property"],
                    index=0,
                )

            with col4:
                facing = st.selectbox(
                    "Property Facing (Direction)",
                    [
                        "East", "West", "North", "South",
                        "North-East", "North-West", "South-East",
                        "South-West", "Unknown",
                    ],
                    index=0,
                )

                ownership = st.selectbox(
                    "Ownership Title",
                    [
                        "Freehold", "Co-operative Society", "Leasehold",
                        "Power of Attorney", "Other",
                    ],
                    index=0,
                )

                parking = st.selectbox(
                    "Car Parking Provision",
                    ["0", "1", "2", "3", "4", "Covered", "Open", "None"],
                    index=1,
                )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button(
                "⚡  Calculate Valuation Estimate",
                use_container_width=True,
            )

        if submitted:
            input_values = {
                "BHK": bhk,
                "carpet_area_sqft": carpet_area,
                "Bathroom": bathrooms,
                "Balcony": balconies,
                "location": str(location).strip().lower(),
                "Status": status,
                "Floor": str(floor),
                "Transaction": transaction,
                "Furnishing": furnishing,
                "facing": facing,
                "Ownership": ownership,
                "Car Parking": str(parking),
            }

            if expected_features:
                input_data = pd.DataFrame(
                    [[input_values.get(col) for col in expected_features]],
                    columns=expected_features,
                )
            else:
                input_data = pd.DataFrame([input_values])

            try:
                prediction = float(model.predict(input_data)[0])

                if not pd.notna(prediction) or prediction <= 0:
                    st.error(
                        "The model returned an out-of-bounds estimate for this combination. "
                        "Please adjust area or location attributes."
                    )
                else:
                    formatted_rupees = format_rupees(prediction)
                    mae_val = model_metrics.get("MAE_Rupees", 1816360)
                    lower_bound = max(100_000, prediction - float(mae_val))
                    upper_bound = prediction + float(mae_val)

                    st.markdown(
                        f"""
                        <div class="prediction-showcase">
                            <div class="pred-eyebrow">
                                <span>✦</span> Estimated Market Value
                            </div>
                            <div class="pred-price-primary">
                                {formatted_rupees}
                            </div>
                            <div class="pred-price-secondary">
                                Exact computation: ₹{prediction:,.0f}
                            </div>
                            <div class="pred-range-pill">
                                📊 Empirical Variance Range (±MAE): {format_rupees(lower_bound)} — {format_rupees(upper_bound)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )



                    # Neat Property Specification Matrix
                    st.markdown(
                        f"""
                        <div class="summary-card">
                            <div style="font-weight: 800; font-size: 1.05rem; color: #18261E; margin-bottom: 4px;">
                                📋 Evaluated Property Profile
                            </div>
                            <div style="font-size: 0.84rem; color: #6B7C72; margin-bottom: 12px;">
                                Configuration inputs processed by {model_name}
                            </div>
                            <div class="summary-grid">
                                <div class="summary-item">
                                    <div class="summary-item-label">City</div>
                                    <div class="summary-item-val">{location}</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Configuration</div>
                                    <div class="summary-item-val">{bhk} BHK</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Carpet Area</div>
                                    <div class="summary-item-val">{carpet_area:,} sq.ft.</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Bathrooms</div>
                                    <div class="summary-item-val">{bathrooms} Baths</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Balconies</div>
                                    <div class="summary-item-val">{balconies}</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Floor</div>
                                    <div class="summary-item-val">Floor {floor}</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Furnishing</div>
                                    <div class="summary-item-val">{furnishing}</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Status</div>
                                    <div class="summary-item-val">{status}</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Facing</div>
                                    <div class="summary-item-val">{facing}</div>
                                </div>
                                <div class="summary-item">
                                    <div class="summary-item-label">Parking</div>
                                    <div class="summary-item-val">{parking}</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            except Exception as error:
                st.error("Prediction failed. Please verify the input values.")
                with st.expander("Technical details"):
                    st.code(str(error))


# --------------------------------------------------
# 9. ABOUT THE PROJECT PAGE
# --------------------------------------------------

elif st.session_state["page_nav"] == "About the Project":

    st.markdown(
        """
        <div class="section-title-wrap" style="margin-top: 10px;">
            <div class="section-eyebrow">Project Architecture & Evaluation</div>
            <div class="section-title">Behind DwellIQ</div>
            <div class="section-sub">
                An academic machine learning project exploring property price modeling across Indian metropolitan regions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="academic-banner">
            <div class="hero-badge" style="background:#EEF3ED; color:#2D5A43; border-color:#D8E2D7;">
                College Mini-Project
            </div>
            <div style="font-size:1.35rem; font-weight:800; color:#18261E; margin: 10px 0 8px 0;">
                House Price Prediction Using Linear Regression and Random Forest
            </div>
            <p style="color:#4A5B51; line-height:1.75; font-size:0.95rem; margin:0;">
                DwellIQ leverages high-dimensional listing features (geography, floor space, architectural layout,
                and amenities) to train and compare predictive regression algorithms. The objective is to evaluate
                the performance, limitations, and variance patterns of machine learning applied to diverse housing markets.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Technical Workflow
    st.markdown("#### 🛠️ Pipeline Architecture")

    p1, p2 = st.columns(2, gap="medium")

    with p1:
        st.markdown(
            """
            <div class="premium-card" style="margin-bottom: 16px;">
                <div class="premium-card-icon">1</div>
                <div class="premium-card-title">Data Preprocessing & Cleaning</div>
                <div class="premium-card-desc">
                    Extracts BHK configurations using regular expressions, standardizes Indian Rupee pricing
                    (Cr and Lac conversions), filters duplicate records, and normalizes carpet area definitions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-icon">2</div>
                <div class="premium-card-title">Feature Engineering & Encoding</div>
                <div class="premium-card-desc">
                    Employs Scikit-Learn ColumnTransformer with SimpleImputer (median for numericals, most frequent
                    for categoricals) and OneHotEncoder with handle_unknown='ignore' to gracefully handle novel locations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div class="premium-card" style="margin-bottom: 16px;">
                <div class="premium-card-icon">3</div>
                <div class="premium-card-title">Model Training & Evaluation</div>
                <div class="premium-card-desc">
                    Compares a baseline Linear Regression against a multi-estimator Random Forest Regressor
                    evaluated on a standard 80/20 train-test partition using MAE, RMSE, and R² scores.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-icon">4</div>
                <div class="premium-card-title">Deployment & Interactive UI</div>
                <div class="premium-card-desc">
                    Serializes the complete transformer-regressor pipeline via Joblib, served through
                    a reactive Streamlit web application with custom HSL styling and responsive inputs.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Technology Stack
    st.markdown("#### 💻 Technology Stack")

    t1, t2, t3, t4 = st.columns(4, gap="medium")

    with t1:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size:1.8rem; margin-bottom:8px;">🐍</div>
                <div class="step-title">Python 3.10+</div>
                <div class="step-desc">Core language for pipelines and inference.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with t2:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size:1.8rem; margin-bottom:8px;">🐼</div>
                <div class="step-title">Pandas & NumPy</div>
                <div class="step-desc">Data wrangling, regex parsing, and arrays.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with t3:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size:1.8rem; margin-bottom:8px;">🤖</div>
                <div class="step-title">Scikit-Learn</div>
                <div class="step-desc">Pipelines, OneHotEncoder, and Random Forest.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with t4:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size:1.8rem; margin-bottom:8px;">🌿</div>
                <div class="step-title">Streamlit</div>
                <div class="step-desc">Modern web dashboard with custom CSS.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Model Evaluation Metrics & Visual Explainability
    st.markdown("#### 📊 Model Performance & Explainability")

    if model is not None:
        mae_value = model_metrics.get("MAE_Rupees")
        rmse_value = model_metrics.get("RMSE_Rupees")
        r2_value = model_metrics.get("R2")

        metric1, metric2, metric3 = st.columns(3, gap="medium")

        with metric1:
            st.metric(
                "Mean Absolute Error (MAE)",
                format_rupees(float(mae_value)) if mae_value else "Unavailable",
                help="Average magnitude of errors in Indian Rupees on test split.",
            )

        with metric2:
            st.metric(
                "Root Mean Squared Error (RMSE)",
                format_rupees(float(rmse_value)) if rmse_value else "Unavailable",
                help="Penalizes larger prediction errors proportionally.",
            )

        with metric3:
            st.metric(
                "R² Determination Score",
                f"{float(r2_value):.4f}" if r2_value is not None else "Unavailable",
                help="Proportion of variance explained by model features.",
            )

        # Charts Section
        st.markdown("##### 📈 Empirical Visual Insights")
        chart_col1, chart_col2 = st.columns(2, gap="medium")

        with chart_col1:
            if FIG_FEAT_PATH.exists():
                st.image(str(FIG_FEAT_PATH), caption="Top Feature Importances (Tree Impurity Reduction)", use_container_width=True)
            else:
                st.info("Feature importance visual will generate upon running 'python src/evaluate_model.py'.")

        with chart_col2:
            if FIG_COMP_PATH.exists():
                st.image(str(FIG_COMP_PATH), caption="Comparative Model Error (MAE in ₹ Lakhs)", use_container_width=True)
            else:
                st.info("Comparative evaluation visual will generate upon running 'python src/evaluate_model.py'.")

        st.caption(
            "📌 **Explainability Note:** Feature importance indicates statistical association within the tabular listing sample, "
            "not direct causality. Factors such as local infrastructure and builder pedigree remain unobserved tabular variables."
        )

        if REPORT_PATH.exists():
            st.markdown("##### Comparative Model Evaluation Table")
            try:
                comparison = pd.read_csv(REPORT_PATH)
                st.dataframe(comparison, use_container_width=True, hide_index=True)
            except Exception as e:
                st.caption(f"Could not load report: {e}")

        st.warning(
            "📌 **Academic Discussion & Variance Note:** "
            "Real estate datasets possess significant inherent variance due to hyper-local amenities, "
            "luxury finishes, and builder branding not fully captured in tabular records. "
            "The low R² score reflects this real-world variance across disparate cities. "
            "Estimates should be interpreted as exploratory baseline approximations."
        )


# --------------------------------------------------
# 12. FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="dwell-footer">
        <div class="footer-brand">DwellIQ 🏡</div>
        <div class="footer-text">
            Smart Property Estimates · Real Estate Machine Learning Project<br>
            Designed with natural aesthetics, Scikit-Learn pipelines, and Streamlit.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
