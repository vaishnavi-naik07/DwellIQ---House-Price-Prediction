import streamlit as st
from frontend.components.auth_modal import render_auth_modal_or_tab

PAGE_ROUTES = [
    "Overview Dashboard",
    "Estimate a Property",
    "DwellIQ AI Advisor",
    "Nearby Essentials",
    "Compare Properties",
    "EMI Calculator",
    "Model Insights",
]


def render_sidebar():
    """
    Renders the consistent navigation sidebar across all pages.
    Returns:
        (active_page, current_user)
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                <div style="background: linear-gradient(135deg, #2D5A43, #3B7A5C); color: white; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">🏡</div>
                <div>
                    <div style="font-weight: 800; font-size: 1.35rem; color: #18261E; line-height: 1.1;">Dwell<span style="color: #3B7A5C;">IQ</span></div>
                    <div style="font-size: 0.74rem; color: #6B7C72;">Smart Valuation & Advisory</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### Navigation")

        # Migrate legacy routes
        route_migration = {
            "AI Property Assistant": "DwellIQ AI Advisor",
            "AI Property Advisor": "DwellIQ AI Advisor",
            "About the Project": "Overview Dashboard",
            "About": "Overview Dashboard",
        }
        current_nav = st.session_state.get("page_nav", "Overview Dashboard")
        if current_nav in route_migration:
            st.session_state["page_nav"] = route_migration[current_nav]

        if "page_nav" not in st.session_state or st.session_state["page_nav"] not in PAGE_ROUTES:
            st.session_state["page_nav"] = "Overview Dashboard"

        current_idx = PAGE_ROUTES.index(st.session_state["page_nav"])
        selected_page = st.radio(
            "Navigation",
            options=PAGE_ROUTES,
            index=current_idx,
            label_visibility="collapsed",
            key="app_sidebar_navigation",
        )

        if selected_page != st.session_state["page_nav"]:
            st.session_state["page_nav"] = selected_page
            st.rerun()

        st.markdown("---")
        st.markdown("##### Account & Saved Records")
        current_user = render_auth_modal_or_tab()

    return selected_page, current_user
