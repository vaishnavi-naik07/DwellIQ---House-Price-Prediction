import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.components.navbar import render_section_header
from frontend.components.chat_interface import (
    render_quick_action_cards,
    render_chat_messages,
    render_property_context_banner,
)
from backend.services.chatbot_service import (
    ask_property_advisor,
    get_ai_service_status,
)


def render_ai_assistant_page():
    # 1. Page Header & AI Status Indicator
    render_section_header(
        "DwellIQ AI Platform",
        "DwellIQ AI — Your Personal Property Advisor",
        "Empowering your real-estate decisions with automated valuation explainability, mortgage calculations, legal due diligence & personalized market guidance."
    )

    ai_status = get_ai_service_status()

    # AI Status & Connectivity Card
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 14px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; box-shadow: 0 2px 8px rgba(24,38,30,0.03);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2rem;">🤖</span>
                <div>
                    <div style="font-weight: 700; font-size: 0.88rem; color: #18261E;">Engine Status: <span style="color: {ai_status['badge_color']}; font-weight: 800;">{ai_status['badge_text']}</span></div>
                    <div style="font-size: 0.78rem; color: #6B7C72;">{ai_status['description']}</div>
                </div>
            </div>
            <div>
                <span style="background: #EEF3ED; border: 1px solid #D8E2D7; color: #2D5A43; padding: 4px 10px; border-radius: 12px; font-size: 0.76rem; font-weight: 700;">
                    {ai_status['provider']}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Initialize Session State
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "👋 Welcome! I am **DwellIQ AI — Your Personal Property Advisor**.\n\n"
                    "I can help you navigate Indian residential real estate:\n"
                    "• **Break down and explain property valuations**\n"
                    "• **Assess personal budget & affordability (30/40 rule)**\n"
                    "• **Calculate home loan EMIs & total interest amortisation**\n"
                    "• **Compare multiple properties side-by-side**\n"
                    "• **Review essential legal & RERA buying checklists**\n\n"
                    "How may I assist your property journey today?"
                ),
                "source": ai_status["badge_text"],
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "calculation_note": "Grounded in verified real-estate principles.",
            }
        ]

    if "confirm_clear_chat" not in st.session_state:
        st.session_state["confirm_clear_chat"] = False

    # 3. Active Property Context (passed from Estimate page)
    active_ctx = st.session_state.get("active_property_context") or st.session_state.get("latest_estimate")

    def handle_discuss_context(prompt_text: str):
        _send_message(prompt_text)

    def handle_detach_context():
        st.session_state["active_property_context"] = None
        st.session_state["latest_estimate"] = None
        st.rerun()

    if active_ctx:
        render_property_context_banner(active_ctx, handle_discuss_context, handle_detach_context)

    # 4. Message Submission Handler
    def _send_message(user_msg: str):
        now_time = datetime.now().strftime("%I:%M %p")
        st.session_state["chat_messages"].append({
            "role": "user",
            "content": user_msg,
            "timestamp": now_time,
        })

        with st.spinner("DwellIQ AI is analyzing real-estate data & calculations..."):
            response = ask_property_advisor(
                user_prompt=user_msg,
                history=st.session_state["chat_messages"][:-1],
                property_context=active_ctx,
            )

        st.session_state["chat_messages"].append({
            "role": "assistant",
            "content": response["reply"],
            "source": response["source"],
            "timestamp": response.get("timestamp", datetime.now().strftime("%I:%M %p")),
            "calculation_note": response.get("calculation_note", ""),
        })
        st.rerun()

    # 5. Conversation Control Toolbar
    col_t1, col_t2, col_t3 = st.columns([1.5, 1.5, 5])
    with col_t1:
        if st.button("➕ New Conversation", key="btn_new_chat", use_container_width=True):
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": "Fresh session started. How can I assist your real estate planning today?",
                    "source": ai_status["badge_text"],
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                }
            ]
            st.session_state["confirm_clear_chat"] = False
            st.rerun()

    with col_t2:
        if not st.session_state["confirm_clear_chat"]:
            if st.button("🗑️ Clear Chat", key="btn_req_clear", use_container_width=True):
                st.session_state["confirm_clear_chat"] = True
                st.rerun()
        else:
            if st.button("⚠️ Confirm Clear?", key="btn_confirm_clear", use_container_width=True, type="primary"):
                st.session_state["chat_messages"] = [
                    {
                        "role": "assistant",
                        "content": "Chat history has been cleared.",
                        "source": ai_status["badge_text"],
                        "timestamp": datetime.now().strftime("%I:%M %p"),
                    }
                ]
                st.session_state["confirm_clear_chat"] = False
                st.rerun()

    with col_t3:
        # Retry last query button (if there is at least one user query)
        user_queries = [m["content"] for m in st.session_state["chat_messages"] if m["role"] == "user"]
        if user_queries:
            if st.button("🔄 Regenerate / Retry Last Query", key="btn_retry_last"):
                last_q = user_queries[-1]
                # Remove last assistant response
                if st.session_state["chat_messages"][-1]["role"] == "assistant":
                    st.session_state["chat_messages"].pop()
                # Remove last user message
                if st.session_state["chat_messages"] and st.session_state["chat_messages"][-1]["role"] == "user":
                    st.session_state["chat_messages"].pop()
                _send_message(last_q)

    # 6. Render Suggested Prompt Cards
    # Render prompt cards when conversation is fresh (<= 1 message) or in an expander
    if len(st.session_state["chat_messages"]) <= 1:
        render_quick_action_cards(on_select_callback=_send_message)
    else:
        with st.expander("💡 View Quick Prompt Suggestions", expanded=False):
            render_quick_action_cards(on_select_callback=_send_message)

    # 7. Render Conversation History
    render_chat_messages(st.session_state["chat_messages"])

    # 8. Interactive Message Input Box (Mobile-friendly with Enter-to-send support)
    user_input = st.chat_input(
        placeholder="Ask about property valuation, affordability, home loans, comparison, or RERA legal checks...",
        key="dwell_advisor_chat_input",
    )

    if user_input and user_input.strip():
        _send_message(user_input.strip())


def render_chatbot_page():
    """Alias for backwards compatibility."""
    render_ai_assistant_page()


if __name__ == "__main__":
    render_ai_assistant_page()
