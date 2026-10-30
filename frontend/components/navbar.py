import streamlit as st


def render_brand_header(current_user=None):
    """Render top brand bar with logo, brand title, and personalised user profile badge."""
    user_html = ""
    if current_user:
        user_name = current_user.get("full_name", "Verified Member")
        first_name = user_name.split()[0] if user_name else "User"
        user_html = f"""
        <div style="display: flex; align-items: center; gap: 10px; background: #EEF3ED; border: 1px solid #D8E2D7; padding: 6px 14px; border-radius: 24px;">
            <div style="width: 26px; height: 26px; border-radius: 50%; background: #2D5A43; color: white; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 800;">
                {first_name[0].upper()}
            </div>
            <div style="font-size: 0.85rem; font-weight: 700; color: #18261E;">
                {user_name}
            </div>
        </div>
        """

    st.markdown(
        f"""<div class="dwell-brand-bar"><div class="dwell-brand-left"><div class="dwell-logo-box">🏡</div><div><div class="dwell-brand-title">Dwell<span>IQ</span></div><div class="dwell-brand-tagline">Smart Property Estimates · Real Estate AI Platform</div></div></div><div>{user_html}</div></div>""",
        unsafe_allow_html=True,
    )


def render_navbar(current_user=None):
    """Alias for render_brand_header."""
    render_brand_header(current_user=current_user)


def render_footer():
    """Render professional footer across all pages."""
    st.markdown(
        """
        <div class="dwell-footer">
            <div>
                <strong>DwellIQ</strong> — Intelligent Property Decision & Valuation System
                <div style="font-size: 0.76rem; color: #8C9E94; margin-top: 3px;">
                    Built with Streamlit & Scikit-learn · Academic Demonstration Platform
                </div>
            </div>
            <div style="display: flex; gap: 18px; font-size: 0.8rem; margin-top: 8px;">
                <span>🔒 PBKDF2 Secure Auth</span>
                <span>📊 Verified RF Pipeline</span>
                <span>🗺️ OpenStreetMap POI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(eyebrow: str, title: str, description: str = ""):
    """Render standard editorial section heading."""
    desc_html = f'<div class="section-description-text">{description}</div>' if description else ''
    st.markdown(
        f"""
        <div class="section-header-box">
            <div class="section-eyebrow-text">{eyebrow}</div>
            <div class="section-heading-text">{title}</div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
