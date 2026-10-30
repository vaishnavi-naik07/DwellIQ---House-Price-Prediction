import streamlit as st

from backend.auth.auth_service import (
    register_user,
    authenticate_user,
    validate_email,
    validate_password_strength,
    check_rate_limit,
    record_failed_attempt,
    clear_failed_attempts,
)


def render_full_auth_page():
    """
    Renders a centered, clean Signup & Login card without distracting broken split elements.
    First-time visitors see Signup by default.
    Returning users can switch seamlessly to Login.
    """
    if "auth_view_mode" not in st.session_state:
        st.session_state["auth_view_mode"] = "signup"

    if "show_pwd" not in st.session_state:
        st.session_state["show_pwd"] = False
    if "show_reg_pwd" not in st.session_state:
        st.session_state["show_reg_pwd"] = False

    mode = st.session_state["auth_view_mode"]

    # Centered container layout
    _, col_center, _ = st.columns([1, 1.8, 1])

    with col_center:
        # Brand Header
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px; padding-top: 10px;">
                <div style="display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2D5A43, #3B7A5C); color: white; width: 56px; height: 56px; border-radius: 16px; font-size: 1.8rem; box-shadow: 0 8px 20px rgba(45,90,67,0.22); margin-bottom: 12px;">🏡</div>
                <div style="font-weight: 800; font-size: 1.9rem; color: #18261E; letter-spacing: -0.6px; line-height: 1.2;">
                    Dwell<span style="color: #3B7A5C;">IQ</span>
                </div>
                <div style="font-size: 0.9rem; color: #6B7C72; margin-top: 4px; font-weight: 500;">
                    Find Your Place. Understand Its Value.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if mode == "signup":
            _render_signup_form()
        else:
            _render_login_form()


def _render_signup_form():
    """Renders the Clean Registration Card."""
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 20px; padding: 26px 30px 10px 30px; box-shadow: 0 10px 28px rgba(24,38,30,0.06); margin-bottom: 20px;">
            <div style="font-size: 1.4rem; font-weight: 800; color: #18261E; margin-bottom: 4px;">
                Create Your Account ✨
            </div>
            <div style="font-size: 0.88rem; color: #6B7C72; margin-bottom: 16px; line-height: 1.5;">
                Join DwellIQ to access personalised property estimates, save valuations, and consult the AI Property Advisor.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show/hide password checkbox
    show_pwd = st.checkbox("👁️ Show password", value=st.session_state["show_reg_pwd"], key="chk_show_reg_pwd")
    st.session_state["show_reg_pwd"] = show_pwd
    pwd_type = "default" if show_pwd else "password"

    with st.form("dwell_clean_signup_form"):
        reg_name = st.text_input("Full Name *", placeholder="e.g. Vaishnavi Naik", key="clean_reg_name").strip()
        reg_email = st.text_input("Email Address *", placeholder="name@example.com", key="clean_reg_email").strip()

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            reg_pwd = st.text_input(
                "Password *",
                type=pwd_type,
                placeholder="Min 8 chars, 1 number/symbol",
                key="clean_reg_pwd",
                help="Requires minimum 8 characters with at least one number or special character.",
            )
        with col_p2:
            reg_confirm = st.text_input(
                "Confirm Password *",
                type=pwd_type,
                placeholder="Re-enter password",
                key="clean_reg_confirm",
            )

        submit_btn = st.form_submit_button("Create Account & Sign In →", type="primary", use_container_width=True)

    if submit_btn:
        if not reg_name:
            st.error("Please enter your Full Name.")
        elif not reg_email:
            st.error("Please enter your Email Address.")
        elif not validate_email(reg_email):
            st.error("Please provide a valid email address (e.g. name@domain.com).")
        elif not reg_pwd:
            st.error("Password is required.")
        elif reg_pwd != reg_confirm:
            st.error("Passwords do not match. Please verify and re-type.")
        else:
            is_valid_pw, pw_err = validate_password_strength(reg_pwd)
            if not is_valid_pw:
                st.error(pw_err)
            else:
                with st.spinner("Creating your secure account..."):
                    success, msg = register_user(reg_name, reg_email, reg_pwd)
                if success:
                    st.success("🎉 Registration successful! Logging you in...")
                    # Automatically log user in
                    auth_ok, _, user_data = authenticate_user(reg_email, reg_pwd)
                    if auth_ok and user_data:
                        st.session_state["authenticated_user"] = user_data
                        st.session_state["page_nav"] = "Overview Dashboard"
                        st.rerun()
                    else:
                        st.session_state["auth_view_mode"] = "login"
                        st.rerun()
                else:
                    st.error(f"Registration failed: {msg}")

    # Switch to Login Option
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        st.markdown("<span style='font-size: 0.88rem; color: #6B7C72;'>Already have an account?</span>", unsafe_allow_html=True)
    with col_r:
        if st.button("Sign In →", key="btn_switch_to_login", use_container_width=True):
            st.session_state["auth_view_mode"] = "login"
            st.rerun()


def _render_login_form():
    """Renders the Clean Login Card."""
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 20px; padding: 26px 30px 10px 30px; box-shadow: 0 10px 28px rgba(24,38,30,0.06); margin-bottom: 20px;">
            <div style="font-size: 1.4rem; font-weight: 800; color: #18261E; margin-bottom: 4px;">
                Welcome Back 🔑
            </div>
            <div style="font-size: 0.88rem; color: #6B7C72; margin-bottom: 16px; line-height: 1.5;">
                Enter your credentials to access your saved valuations, model insights & AI property advice.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show/hide password checkbox
    show_pwd = st.checkbox("👁️ Show password", value=st.session_state["show_pwd"], key="chk_show_login_pwd")
    st.session_state["show_pwd"] = show_pwd
    pwd_type = "default" if show_pwd else "password"

    with st.form("dwell_clean_login_form"):
        login_email = st.text_input("Email Address *", placeholder="name@example.com", key="clean_login_email").strip()
        login_pwd = st.text_input("Password *", type=pwd_type, placeholder="Enter your password", key="clean_login_pwd")
        submit_btn = st.form_submit_button("Sign In to Dashboard →", type="primary", use_container_width=True)

    if submit_btn:
        if not login_email or not login_pwd:
            st.error("Please enter both your email address and password.")
        else:
            is_blocked, wait_sec = check_rate_limit(login_email)
            if is_blocked:
                st.error(f"Too many failed login attempts. Account temporarily locked for {wait_sec} seconds.")
            else:
                with st.spinner("Authenticating credentials..."):
                    success, msg, user_data = authenticate_user(login_email, login_pwd)
                if success and user_data:
                    clear_failed_attempts(login_email)
                    st.session_state["authenticated_user"] = user_data
                    st.session_state["page_nav"] = "Overview Dashboard"
                    st.success(f"Welcome back, {user_data['full_name']}!")
                    st.rerun()
                else:
                    record_failed_attempt(login_email)
                    st.error(msg or "Invalid email or password. Please check your credentials.")

    # Switch to Signup Option
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        st.markdown("<span style='font-size: 0.88rem; color: #6B7C72;'>New to DwellIQ?</span>", unsafe_allow_html=True)
    with col_r:
        if st.button("Create an Account ✨", key="btn_switch_to_signup", use_container_width=True):
            st.session_state["auth_view_mode"] = "signup"
            st.rerun()
