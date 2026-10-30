from pathlib import Path
import streamlit as st

# Configure page early
def setup_page():
    try:
        st.set_page_config(
            page_title="DwellIQ | AI Real Estate Decision Platform",
            page_icon="🏡",
            layout="wide",
            initial_sidebar_state="expanded",
        )
    except Exception:
        # Ignore if set_page_config was already invoked by entrypoint
        pass

    # Load CSS Stylesheet
    css_path = Path(__file__).resolve().parent / "styles" / "main.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


from frontend.components.navbar import render_brand_header, render_footer
from frontend.components.sidebar import render_sidebar
from frontend.pages.auth import render_full_auth_page
from frontend.pages.dashboard import render_dashboard_page
from frontend.pages.estimate_property import render_estimate_property_page
from frontend.pages.ai_assistant import render_ai_assistant_page
from frontend.pages.nearby_essentials import render_nearby_essentials_page
from frontend.pages.compare_properties import render_compare_properties_page
from frontend.pages.emi_calculator import render_emi_calculator_page
from frontend.pages.investment_analysis import render_investment_analysis_page
from frontend.pages.model_insights import render_model_insights_page


def main():
    setup_page()

    # 1. Check Authentication Gate
    current_user = st.session_state.get("authenticated_user")

    if not current_user:
        # User is not logged in: display dedicated Full-Page Signup/Login experience
        render_full_auth_page()
        render_footer()
        return

    # 2. Authenticated: Render Sidebar Navigation & Account Widget
    active_page, current_user = render_sidebar()

    # 3. Top Brand Header / Navbar with Personalized User Profile
    render_brand_header(current_user=current_user)

    # 4. Route to active protected page
    if active_page == "Overview Dashboard":
        render_dashboard_page(current_user=current_user)
    elif active_page == "Estimate a Property":
        render_estimate_property_page(current_user=current_user)
    elif active_page in ["DwellIQ AI Advisor", "AI Property Assistant"]:
        render_ai_assistant_page(current_user=current_user)
    elif active_page == "Nearby Essentials":
        render_nearby_essentials_page()
    elif active_page == "Compare Properties":
        render_compare_properties_page()
    elif active_page == "EMI Calculator":
        render_emi_calculator_page()
    elif active_page == "Investment Analysis":
        render_investment_analysis_page()
    elif active_page == "Model Insights":
        render_model_insights_page()

    # 5. Global Footer
    render_footer()


if __name__ == "__main__":
    main()
