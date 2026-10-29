import streamlit as st
from src.auth import (
    register_user,
    authenticate_user,
    validate_email,
    validate_password_strength,
    check_rate_limit,
    record_failed_attempt,
    clear_failed_attempts,
    init_auth_db,
    get_user_estimations,
)
from backend.services.prediction_service import format_rupees


def render_auth_modal_or_tab():
    """Render Login / Register tabbed card in sidebar or modal."""
    init_auth_db()

    current_user = st.session_state.get("authenticated_user")

    if current_user:
        st.markdown(
            f"""
            <div style="background: #EEF3ED; border: 1px solid #D8E2D7; border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 0.8rem; color: #6B7C72;">Signed in as</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #2D5A43;">{current_user.get('full_name')}</div>
                <div style="font-size: 0.8rem; color: #18261E;">{current_user.get('email')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Show estimation history
        history = get_user_estimations(current_user["id"])
        if history:
            st.markdown(f"**Saved Valuations ({len(history)}):**")
            for h in history[:4]:
                st.markdown(
                    f"- **{h['bhk']} BHK in {h['location']}** ({h['carpet_area']:,.0f} sq.ft) → **{format_rupees(h['estimated_price'])}**"
                )

        if st.button("Sign Out 🚪", key="btn_signout", use_container_width=True):
            st.session_state["authenticated_user"] = None
            st.rerun()

        return current_user

    # Not signed in: provide login / register tabs
    auth_tab1, auth_tab2 = st.tabs(["Sign In 🔑", "Create Account ✨"])

    with auth_tab1:
        with st.form("auth_login_form"):
            login_email = st.text_input("Email Address", key="login_email_input").strip()
            login_pwd = st.text_input("Password", type="password", key="login_pwd_input")
            login_btn = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if login_btn:
            if not login_email or not login_pwd:
                st.error("Please enter both email and password.")
            else:
                is_blocked, wait_sec = check_rate_limit(login_email)
                if is_blocked:
                    st.error(f"Too many failed login attempts. Please wait {wait_sec} seconds before trying again.")
                else:
                    success, msg, user_data = authenticate_user(login_email, login_pwd)
                    if success:
                        clear_failed_attempts(login_email)
                        st.session_state["authenticated_user"] = user_data
                        st.success(f"Welcome back, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        record_failed_attempt(login_email)
                        st.error(msg)

    with auth_tab2:
        with st.form("auth_reg_form"):
            reg_name = st.text_input("Full Name", key="reg_name_input").strip()
            reg_email = st.text_input("Email Address", key="reg_email_input").strip()
            reg_pwd = st.text_input("Password (min 8 chars, 1 number/special)", type="password", key="reg_pwd_input")
            reg_btn = st.form_submit_button("Register Account", use_container_width=True)

        if reg_btn:
            if not reg_name or not reg_email or not reg_pwd:
                st.error("All registration fields are required.")
            elif not validate_email(reg_email):
                st.error("Please enter a valid email address.")
            else:
                is_strong, pwd_err = validate_password_strength(reg_pwd)
                if not is_strong:
                    st.error(pwd_err)
                else:
                    reg_success, reg_msg = register_user(reg_name, reg_email, reg_pwd)
                    if reg_success:
                        st.success("Account created successfully! You can now log in.")
                    else:
                        st.error(reg_msg)

    return None
