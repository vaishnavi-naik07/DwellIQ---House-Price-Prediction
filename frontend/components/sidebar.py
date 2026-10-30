import streamlit as st
from backend.auth.auth_service import get_user_estimations
from backend.services.prediction_service import format_rupees

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
    current_user = st.session_state.get("authenticated_user")

    with st.sidebar:
        # 1. Brand Logo & Title
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

        # 2. Personalized User Profile Box
        if current_user:
            user_name = current_user.get("full_name", "Verified Member")
            user_email = current_user.get("email", "")
            first_name = user_name.split()[0] if user_name else "User"

            st.markdown(
                f"""
                <div style="background: #F4F7F3; border: 1px solid #D8E2D7; border-radius: 14px; padding: 14px 16px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 36px; height: 36px; border-radius: 50%; background: #2D5A43; color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.95rem;">
                            {first_name[0].upper()}
                        </div>
                        <div style="overflow: hidden;">
                            <div style="font-size: 0.72rem; color: #6B7C72; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700;">Signed in as</div>
                            <div style="font-weight: 800; font-size: 0.95rem; color: #18261E; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;" title="{user_name}">
                                {user_name}
                            </div>
                            <div style="font-size: 0.76rem; color: #6B7C72; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;" title="{user_email}">
                                {user_email}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 3. Navigation Links
        st.markdown("##### Navigation")

        # Migrate legacy routes if found
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

        # 4. User Saved Estimates History
        if current_user and current_user.get("id"):
            try:
                history = get_user_estimations(current_user["id"])
                if history:
                    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"##### Saved Valuations ({len(history)})")
                    for h in history[:3]:
                        st.markdown(
                            f"""
                            <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 10px; padding: 8px 12px; margin-bottom: 8px; font-size: 0.8rem;">
                                <div style="font-weight: 700; color: #18261E;">{h['bhk']} BHK in {h['location']}</div>
                                <div style="color: #2D5A43; font-weight: 800;">{format_rupees(h['estimated_price'])}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            except Exception:
                pass

        # 5. Sign Out Button
        if current_user:
            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            if st.button("Sign Out 🚪", key="btn_sidebar_logout", use_container_width=True):
                st.session_state["authenticated_user"] = None
                st.session_state["auth_view_mode"] = "login"
                st.session_state["page_nav"] = "Overview Dashboard"
                st.rerun()

        return st.session_state["page_nav"], current_user
