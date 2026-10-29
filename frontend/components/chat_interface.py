from typing import List, Dict, Any, Callable, Optional
import streamlit as st


PROMPT_CARDS = [
    {
        "icon": "🔍",
        "title": "Explain My Price",
        "desc": "Understand how inputs drive property estimates",
        "prompt": "Explain how my estimated property valuation is calculated and what features drive the price.",
    },
    {
        "icon": "💰",
        "title": "Can I Afford It?",
        "desc": "Evaluate property price against your income",
        "prompt": "Can I afford a ₹80 lakh home with a ₹1.5 lakh monthly income? Break down the numbers.",
    },
    {
        "icon": "📊",
        "title": "Calculate My EMI",
        "desc": "Mortgage calculation for principal & interest",
        "prompt": "Calculate EMI for a ₹60 lakh home loan at 8.5% interest for 20 years.",
    },
    {
        "icon": "⚖️",
        "title": "Compare Properties",
        "desc": "Trade-offs between different BHKs and locations",
        "prompt": "What are the key trade-offs between a 2 BHK in city center vs a 3 BHK in suburbs?",
    },
    {
        "icon": "📍",
        "title": "Find Nearby Essentials",
        "desc": "Civic amenities and public transit benchmarks",
        "prompt": "What essential infrastructure should I check around a residential society in Mumbai?",
    },
    {
        "icon": "📋",
        "title": "Home-Buying Checklist",
        "desc": "Crucial legal and RERA checks before purchase",
        "prompt": "Give me the essential checklist of legal documents before buying a flat in India.",
    },
    {
        "icon": "📐",
        "title": "Understand Property Terms",
        "desc": "Carpet area vs super built-up area and titles",
        "prompt": "Explain the difference between carpet area, built-up area, and super built-up area.",
    },
]


def render_quick_action_cards(on_select_callback: Callable[[str], None]):
    """Render the 7 modern clickable prompt cards in an attractive grid."""
    st.markdown("##### 💡 Suggested Actions & Questions")

    # Render first row of 4 cards
    row1_cols = st.columns(4)
    for idx, card in enumerate(PROMPT_CARDS[:4]):
        with row1_cols[idx]:
            btn_label = f"{card['icon']} **{card['title']}**\n\n{card['desc']}"
            if st.button(btn_label, key=f"quick_card_{idx}", use_container_width=True):
                on_select_callback(card["prompt"])

    # Render second row of 3 cards
    row2_cols = st.columns(3)
    for idx, card in enumerate(PROMPT_CARDS[4:]):
        with row2_cols[idx]:
            btn_label = f"{card['icon']} **{card['title']}**\n\n{card['desc']}"
            if st.button(btn_label, key=f"quick_card_{idx+4}", use_container_width=True):
                on_select_callback(card["prompt"])


def render_prompt_chips(on_select_callback: Callable[[str], None]):
    """Compact chip version of suggestions."""
    render_quick_action_cards(on_select_callback)


def render_property_context_banner(
    context: Optional[Dict[str, Any]],
    on_discuss_callback: Callable[[str], None],
    on_clear_callback: Callable[[], None],
):
    """Render high-visibility banner when an active estimation is attached to the session."""
    if not context or not context.get("price"):
        return

    title = context.get("title", "Estimated Property")
    loc = context.get("location", "Selected City")
    bhk = context.get("bhk", 3)
    area = context.get("area", 1200)

    # Format price safely
    price_val = context.get("price", 0)
    if price_val >= 10_000_000:
        price_str = f"₹{price_val / 10_000_000:.2f} Cr"
    elif price_val >= 100_000:
        price_str = f"₹{price_val / 100_000:.2f} Lakh"
    else:
        price_str = f"₹{price_val:,.0f}"

    c_left, c_right1, c_right2 = st.columns([3, 1.2, 0.8])
    with c_left:
        st.markdown(
            f"""
            <div style="background: #EEF3ED; border: 1px solid #D8E2D7; border-radius: 12px; padding: 10px 16px; display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.4rem;">🏡</span>
                <div>
                    <div style="font-size: 0.76rem; font-weight: 700; color: #3B7A5C; text-transform: uppercase;">Active Property Context Attached</div>
                    <div style="font-weight: 800; font-size: 1.0rem; color: #18261E;">{title} ({bhk} BHK · {area:,.0f} sq.ft in {loc})</div>
                    <div style="font-size: 0.82rem; color: #2D5A43;">Estimated Valuation: <strong>{price_str}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_right1:
        if st.button("💬 Discuss Estimate", key="btn_discuss_ctx", use_container_width=True, type="primary"):
            on_discuss_callback(f"Can you explain the valuation estimate of {price_str} for my {bhk} BHK in {loc} ({area:,.0f} sq.ft)?")
    with c_right2:
        if st.button("Detach ✕", key="btn_detach_ctx", use_container_width=True):
            on_clear_callback()


def render_chat_messages(messages: List[Dict[str, Any]]):
    """Render conversation message history with timestamps, source labels & feedback."""
    if "message_feedback" not in st.session_state:
        st.session_state["message_feedback"] = {}

    st.markdown('<div class="chat-container-dwell">', unsafe_allow_html=True)

    for idx, msg in enumerate(messages):
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        time_str = msg.get("timestamp", "")
        source = msg.get("source", "DwellIQ Advisor")
        calc_note = msg.get("calculation_note", "")

        if role == "user":
            st.markdown(
                f"""
                <div class="chat-bubble-user">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; font-size: 0.82rem; color: #2D5A43;">👤 You</span>
                        <span style="font-size: 0.72rem; color: #6B7C72;">{time_str}</span>
                    </div>
                    <div>{content}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            calc_badge = f'<div style="font-size: 0.74rem; color: #3B7A5C; margin-top: 4px;">📊 <em>{calc_note}</em></div>' if calc_note else ''
            st.markdown(
                f"""
                <div class="chat-bubble-ai">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 800; font-size: 0.88rem; color: #2D5A43;">🏡 DwellIQ AI Advisor</span>
                        <span style="font-size: 0.72rem; color: #8C9E94;">{time_str}</span>
                    </div>
                    <div>{content}</div>
                    <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #EEF3ED; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div style="font-size: 0.74rem; color: #6B7C72;">Source: <strong>{source}</strong>{calc_badge}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Interactive feedback buttons for assistant messages
            fb_key = f"fb_{idx}"
            cur_fb = st.session_state["message_feedback"].get(fb_key)
            c_fb1, c_fb2, c_spacer = st.columns([1, 1, 8])
            with c_fb1:
                if st.button("👍 Helpful", key=f"btn_up_{idx}", use_container_width=True):
                    st.session_state["message_feedback"][fb_key] = "up"
                    st.rerun()
            with c_fb2:
                if st.button("👎 Not Helpful", key=f"btn_down_{idx}", use_container_width=True):
                    st.session_state["message_feedback"][fb_key] = "down"
                    st.rerun()

            if cur_fb == "up":
                st.caption("✓ Thanks for your positive feedback!")
            elif cur_fb == "down":
                st.caption("✓ Thank you. We'll refine future responses.")

    st.markdown('</div>', unsafe_allow_html=True)
