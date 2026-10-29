import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from backend.services.finance_service import calculate_home_loan_emi, calculate_affordability
from backend.services.nearby_service import get_nearby_amenities
from backend.services.comparison_service import compare_properties
from backend.services.prediction_service import format_rupees
from backend.core.config import DATASET_LOCATIONS


SYSTEM_INSTRUCTION = (
    "You are DwellIQ AI, a practical and transparent real-estate assistant. "
    "Help users understand property estimates, affordability, home loans, property comparisons, "
    "location considerations, and home-buying checks. Use supplied project data and verified service "
    "results whenever available. Distinguish facts, calculations, model outputs, and general guidance. "
    "Never invent listings, property prices, nearby places, market statistics, legal guarantees, or model performance. "
    "State assumptions clearly, ask for missing information when necessary, and explain uncertainty in straightforward language. "
    "Do not claim to be a certified financial, legal, or real-estate professional. "
    "Format currency cleanly in Indian numbering (e.g. ₹78 Lakh or ₹78,00,000, ₹1.50 Cr)."
)


def get_configured_llm_credentials() -> Tuple[str, str]:
    """Retrieve OpenAI or Gemini API keys from Streamlit secrets or environment variables."""
    openai_key = ""
    gemini_key = ""

    # Try Streamlit secrets first
    try:
        import streamlit as st
        if "OPENAI_API_KEY" in st.secrets:
            openai_key = str(st.secrets["OPENAI_API_KEY"]).strip()
        if "GEMINI_API_KEY" in st.secrets:
            gemini_key = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    # Fall back to environment variables
    if not openai_key:
        openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not gemini_key:
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()

    return openai_key, gemini_key


def get_ai_service_status() -> Dict[str, Any]:
    """Return the active AI provider status for UI badge presentation."""
    openai_key, gemini_key = get_configured_llm_credentials()

    if openai_key:
        return {
            "is_live_llm": True,
            "provider": "OpenAI",
            "model": "gpt-4o-mini",
            "badge_color": "#2D5A43",
            "badge_text": "🟢 Live AI Active (OpenAI gpt-4o-mini)",
            "description": "Connected to OpenAI API for adaptive natural language reasoning.",
        }
    elif gemini_key:
        return {
            "is_live_llm": True,
            "provider": "Google Gemini",
            "model": "gemini-1.5-flash",
            "badge_color": "#2D5A43",
            "badge_text": "🟢 Live AI Active (Gemini 1.5 Flash)",
            "description": "Connected to Google Gemini API for adaptive real-estate consultation.",
        }
    else:
        return {
            "is_live_llm": False,
            "provider": "Offline Knowledge Engine",
            "model": "DwellIQ Real Estate Engine",
            "badge_color": "#C59B27",
            "badge_text": "🟡 DwellIQ Domain Engine (Deterministic Mode)",
            "description": "Running locally on verified formulas, Scikit-Learn predictions & domain knowledge. Add OPENAI_API_KEY or GEMINI_API_KEY in .env/secrets for LLM reasoning.",
        }


def _call_openai_llm(
    api_key: str,
    user_prompt: str,
    history: List[Dict[str, Any]],
    property_context: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Execute live chat completion call to OpenAI API."""
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

    if property_context:
        ctx_desc = (
            f"Active Verified Property Estimation Context:\n"
            f"- Title: {property_context.get('title', 'N/A')}\n"
            f"- Location: {property_context.get('location', 'N/A')}\n"
            f"- Configuration: {property_context.get('bhk', 'N/A')} BHK, {property_context.get('bathrooms', 'N/A')} Baths\n"
            f"- Carpet Area: {property_context.get('area', 'N/A')} sq.ft\n"
            f"- Estimated Price: {format_rupees(property_context.get('price', 0))}\n"
            f"- Parking: {property_context.get('parking', 'N/A')}, Furnishing: {property_context.get('furnishing', 'N/A')}\n"
            f"Reference this verified valuation if the user asks about their estimate or property."
        )
        messages.append({"role": "system", "content": ctx_desc})

    # Add up to 6 previous history turns
    for turn in history[-6:]:
        role = "assistant" if turn.get("role") == "assistant" else "user"
        content = turn.get("content", "")
        if content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_prompt})

    req_data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.35,
        "max_tokens": 600,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(req_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        result = json.loads(response.read().decode())
        return result["choices"][0]["message"]["content"]


def _call_gemini_llm(
    api_key: str,
    user_prompt: str,
    history: List[Dict[str, Any]],
    property_context: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Execute live chat completion call to Google Gemini API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    contents = []
    # System instruction preamble
    sys_text = SYSTEM_INSTRUCTION
    if property_context:
        sys_text += (
            f"\n\nActive Verified Property Context:\n"
            f"- Title: {property_context.get('title')}, Location: {property_context.get('location')}, "
            f"Carpet Area: {property_context.get('area')} sq.ft, Price: {format_rupees(property_context.get('price', 0))}"
        )
    contents.append({"role": "user", "parts": [{"text": sys_text}]})
    contents.append({"role": "model", "parts": [{"text": "Understood. I will act strictly as DwellIQ AI with these guidelines."}]})

    for turn in history[-6:]:
        g_role = "model" if turn.get("role") == "assistant" else "user"
        contents.append({"role": g_role, "parts": [{"text": turn.get("content", "")}]})

    contents.append({"role": "user", "parts": [{"text": user_prompt}]})

    req_data = {
        "contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(req_data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        result = json.loads(response.read().decode())
        return result["candidates"][0]["content"]["parts"][0]["text"]


# =====================================================================
# DETERMINISTIC DOMAIN ADVISORY ENGINE (Offline Grounded Mode)
# =====================================================================

def _extract_monetary_amount(text: str) -> Optional[float]:
    """Extract currency figures like '80 lakh', '1.5 cr', '7500000'."""
    text_lower = text.lower().replace(",", "")

    # Look for Cr / Crore
    cr_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:cr|crore|crores)", text_lower)
    if cr_match:
        return float(cr_match.group(1)) * 10_000_000

    # Look for Lakh / Lac
    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)", text_lower)
    if lakh_match:
        return float(lakh_match.group(1)) * 100_000

    # Look for raw numbers > 10,000
    raw_match = re.search(r"\b(\d{5,10})\b", text_lower)
    if raw_match:
        return float(raw_match.group(1))

    return None


def _handle_price_explanation(
    property_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Explain predicted property valuation based on engineering features."""
    if property_context and property_context.get("price"):
        price = property_context.get("price", 0)
        area = property_context.get("area", 1000)
        loc = property_context.get("location", "Selected City")
        bhk = property_context.get("bhk", 2)
        rate = round(price / area, 0) if area > 0 else 0

        reply = (
            f"🔍 **Valuation Breakdown for Your {bhk} BHK in {loc}:**\n\n"
            f"- **Estimated Fair Market Value:** **{format_rupees(price)}** (Benchmark: **₹{rate:,.0f} / sq.ft** on usable carpet area).\n"
            f"- **Structural Drivers:** Carpet area of **{area:,.0f} sq.ft** and **{bhk} BHK** configuration represent the primary baseline cost of construction and land share.\n"
            f"- **Location Impact:** Historical market sales in **{loc}** calibrate the base square-foot rate within the trained Random Forest model.\n"
            f"- **Floor & Amenities:** Elevation, direction facing, and dedicated parking spaces provide micro-market liquidity adjustments.\n\n"
            f"📌 *Transparency Note:* This estimate reflects statistical patterns across 177,000+ pan-India listings with a holdout MAE of ~₹18.16 Lakh. "
            f"Treat this as a negotiation benchmark alongside an on-site physical structural survey."
        )
        return {
            "reply": reply,
            "calculation_note": f"Evaluated based on {area:,.0f} sq.ft at ₹{rate:,.0f}/sq.ft benchmark.",
        }

    reply = (
        "🔍 **How DwellIQ Computes Property Price Estimates:**\n\n"
        "Our valuation model utilizes a Scikit-Learn **Random Forest Regressor** trained on 177,000+ cleaned residential listings. The primary valuation drivers include:\n\n"
        "1. **Location Tier & Micro-market:** Dictates the baseline land cost index across 81 Indian cities.\n"
        "2. **Usable Carpet Area (sq.ft):** Primary physical cost determinant under RERA standards.\n"
        "3. **BHK & Bathroom Count:** Utility configuration driving space layout efficiency.\n"
        "4. **Floor Level & Facing:** Upper floors and East/North-East orientations historically command modest daylight and ventilation premiums.\n"
        "5. **Ownership & Transaction Type:** Freehold clear-title properties trade higher than unregularized power-of-attorney titles.\n\n"
        "💡 *Tip:* If you have generated an estimate on our **Estimate a Property** tab, click *'Discuss this Estimate with DwellIQ AI'* to inspect your exact breakdown!"
    )
    return {"reply": reply, "calculation_note": "Based on 12-feature Random Forest model architecture."}


def _handle_affordability(
    user_prompt: str,
    property_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Advise on budget and property price fit using the 30/40 rule."""
    amount_found = _extract_monetary_amount(user_prompt)

    # If user provided a salary or target price
    if amount_found and amount_found < 1_000_000:
        # User likely provided monthly income (e.g. 1.5 lakh)
        monthly_income = amount_found
        afford = calculate_affordability(monthly_income, existing_emis=0.0)
        max_emi = afford["max_recommended_emi"]
        max_loan = afford["max_loan_capacity"]
        max_budget = afford["max_recommended_property_budget"]

        reply = (
            f"💼 **Affordability Analysis for Monthly Income of {format_rupees(monthly_income)}:**\n\n"
            f"- **Safe Monthly EMI Cap (40% FOIR):** Up to **{format_rupees(max_emi)} / month**.\n"
            f"- **Estimated Loan Capacity (8.5% for 20 yrs):** ~**{format_rupees(max_loan)}**.\n"
            f"- **Recommended Property Budget (with 20% down payment):** Up to **{format_rupees(max_budget)}**.\n\n"
            f"📊 **Financial Checklist:**\n"
            f"1. Save at least **20% down payment** ({format_rupees(max_budget * 0.20)}).\n"
            f"2. Keep a contingency fund of **5-7%** for stamp duty, registration, and moving costs.\n"
            f"3. Ensure existing loan obligations (car, credit cards) remain under 10% of income."
        )
        return {
            "reply": reply,
            "calculation_note": f"FOIR: 40% of {format_rupees(monthly_income)} = {format_rupees(max_emi)}/mo cap.",
        }

    # If user asked about property price (e.g. 80 lakh home)
    target_price = amount_found if amount_found else (property_context.get("price", 8_000_000) if property_context else 8_000_000)
    down_payment = target_price * 0.20
    loan_amount = target_price * 0.80
    emi_calc = calculate_home_loan_emi(target_price, down_payment, annual_interest_rate=8.5, tenure_years=20)
    monthly_emi = emi_calc["monthly_emi"]
    min_income_needed = monthly_emi / 0.40

    reply = (
        f"💰 **Affordability Breakdown for a {format_rupees(target_price)} Home:**\n\n"
        f"1. **Upfront Capital Required (20% Down Payment):** **{format_rupees(down_payment)}**\n"
        f"   *(Plus ~6-7% or {format_rupees(target_price * 0.065)} for Stamp Duty & Registration charges).*\n"
        f"2. **Home Loan Principal (80% LTV):** **{format_rupees(loan_amount)}**\n"
        f"3. **Estimated Monthly EMI (8.5% over 20 years):** **{format_rupees(monthly_emi)} / month**\n"
        f"4. **Recommended Take-Home Household Income:** Minimum **{format_rupees(min_income_needed)} / month** "
        f"so that your housing EMI does not exceed 40% of net income (FOIR rule).\n\n"
        f"Would you like me to recalculate this with your exact monthly salary or down payment savings?"
    )
    return {
        "reply": reply,
        "calculation_note": f"Amortization: ₹{loan_amount/100000:,.1f}L loan @ 8.5% for 20 yrs -> EMI {format_rupees(monthly_emi)}.",
    }


def _handle_emi_guidance(user_prompt: str) -> Dict[str, Any]:
    """Calculate and explain EMI from user inputs."""
    amount = _extract_monetary_amount(user_prompt) or 5_000_000.0

    # Look for interest rate like 8.5% or 9%
    rate_match = re.search(r"(\d+(?:\.\d+)?)\s*%", user_prompt)
    rate = float(rate_match.group(1)) if rate_match else 8.5

    # Look for tenure years like 15 years, 20 yrs
    tenure_match = re.search(r"(\d+)\s*(?:years?|yrs?)", user_prompt.lower())
    tenure = int(tenure_match.group(1)) if tenure_match else 20

    emi_data = calculate_home_loan_emi(
        property_price=amount,
        down_payment=0.0,
        annual_interest_rate=rate,
        tenure_years=tenure,
    )

    monthly_emi = emi_data["monthly_emi"]
    total_repayment = emi_data["total_repayment"]
    total_interest = emi_data["total_interest"]

    reply = (
        f"📊 **Home Loan EMI Calculation Summary:**\n\n"
        f"- **Loan Amount:** **{format_rupees(amount)}**\n"
        f"- **Interest Rate:** **{rate}% per annum**\n"
        f"- **Tenure:** **{tenure} years** ({tenure * 12} monthly installments)\n\n"
        f"📌 **Repayment Breakdown:**\n"
        f"- **Monthly EMI:** **{format_rupees(monthly_emi)} / month**\n"
        f"- **Total Interest Payable:** **{format_rupees(total_interest)}**\n"
        f"- **Total Repayment (P + I):** **{format_rupees(total_repayment)}**\n\n"
        f"💡 *Amortization Insight:* Over a {tenure}-year horizon at {rate}%, total interest represents approximately "
        f"**{round((total_interest / total_repayment) * 100, 1)}%** of your total cumulative repayment."
    )
    return {
        "reply": reply,
        "calculation_note": f"Formula: P×R×(1+R)^N / [(1+R)^N - 1] -> EMI {format_rupees(monthly_emi)}.",
    }


def _handle_checklist() -> Dict[str, Any]:
    """Provide the legal & due diligence property checklist."""
    reply = (
        "📋 **Essential Home-Buying Due Diligence Checklist (India):**\n\n"
        "1. **RERA Registration Verification:** Check the state RERA portal (e.g. MahaRERA, HRERA, UP-RERA) for the sanctioned project end-date and litigation history.\n"
        "2. **Title Search & Encumbrance Certificate (EC):** Obtain an EC for the past 30 years from the sub-registrar office to verify clear ownership and no outstanding mortgages.\n"
        "3. **Sanctioned Building Plan & OC/CC:**\n"
        "   - **Commencement Certificate (CC):** Confirms builder has permission to construct.\n"
        "   - **Occupancy Certificate (OC):** Mandatory for ready flats confirming building is safe and compliant with municipal bye-laws.\n"
        "4. **Carpet Area Verification:** Verify the agreement explicitly states RERA usable carpet area, not just super built-up.\n"
        "5. **Undivided Share of Land (UDS):** Ensure the registered agreement allocates proportional UDS rights.\n"
        "6. **No-Objection Certificates (NOCs):** Verify clearance from Fire Safety, Airport Authority, Pollution Control Board, and Electricity Board.\n"
        "7. **Society Maintenance & Property Tax Receipts:** For resale units, confirm zero pending dues with the housing cooperative society.\n\n"
        "⚠️ *Disclaimer: Always engage an independent property lawyer to vet the original mother deed before signing the agreement.*"
    )
    return {"reply": reply, "calculation_note": "Compliant with Indian Real Estate (Regulation and Development) Act (RERA) standards."}


def _handle_property_terms() -> Dict[str, Any]:
    """Explain core real-estate terminology."""
    reply = (
        "📐 **Demystifying Real-Estate Property Terms:**\n\n"
        "1. **Carpet Area (RERA Standard):**\n"
        "   - The net usable floor area within inner walls where a carpet can physically be spread.\n"
        "   - Excludes external walls, service shafts, and balcony areas.\n\n"
        "2. **Built-Up Area:**\n"
        "   - Carpet area + thickness of inner and perimeter walls + balcony spaces (~10% to 15% larger than carpet area).\n\n"
        "3. **Super Built-Up Area:**\n"
        "   - Built-up area + proportional share of common areas (lift shafts, staircases, entrance lobby, club house).\n"
        "   - Usually 25% to 40% higher than usable carpet area. **Always negotiate price based on usable carpet area!**\n\n"
        "4. **Freehold vs Leasehold Title:**\n"
        "   - **Freehold:** You own both the structure and the underlying land indefinitely with full transfer rights.\n"
        "   - **Leasehold:** Ownership is granted for a fixed period (typically 99 years) leased from the government or municipal development authority.\n\n"
        "5. **Undivided Share of Land (UDS):**\n"
        "   - Your proportionate ownership share of the land parcel upon which the apartment complex is erected."
    )
    return {"reply": reply, "calculation_note": "RERA Section 2(k) statutory definitions."}


def _handle_nearby_amenities_query(user_prompt: str) -> Dict[str, Any]:
    """Extract location and category to query verified OpenStreetMap amenities."""
    detected_city = None
    for city in DATASET_LOCATIONS:
        if city.lower() in user_prompt.lower():
            detected_city = city
            break

    if not detected_city:
        detected_city = "Mumbai"

    # Identify category
    category = "Hospital / Clinic"
    if any(w in user_prompt.lower() for w in ["school", "college", "education"]):
        category = "School / College"
    elif any(w in user_prompt.lower() for w in ["metro", "subway", "train", "station"]):
        category = "Metro Station"
    elif any(w in user_prompt.lower() for w in ["supermarket", "grocery", "mall"]):
        category = "Supermarket / Grocery Store"
    elif any(w in user_prompt.lower() for w in ["park", "garden", "gym"]):
        category = "Park / Playground"

    places_res = get_nearby_amenities(detected_city, category, max_distance_km=5.0)

    if places_res.get("status") == "success" and places_res.get("places"):
        places = places_res["places"][:5]
        places_lines = "\n".join([f"- **{p['name']}** (~{p['distance_km']} km away) · *{p['address']}*" for p in places])
        reply = (
            f"📍 **Verified Nearby {category} near {detected_city} (via OpenStreetMap):**\n\n"
            f"{places_lines}\n\n"
            f"ℹ️ *Infrastructure Note:* Proximity within 1–3 km provides strong lifestyle convenience while maintaining a peaceful residential setback."
        )
        return {
            "reply": reply,
            "calculation_note": f"OpenStreetMap Nominatim geospatial query centered on {detected_city}.",
        }

    reply = (
        f"📍 **Nearby Infrastructure Checklist for {detected_city}:**\n\n"
        f"When evaluating residential micro-markets in **{detected_city}**, verify these benchmark radii:\n"
        f"- **Hospitals & Emergency Care:** Within 3 to 5 km.\n"
        f"- **Metro / Railway Transit Hubs:** Within 1.5 to 2.5 km (for commute without traffic congestion).\n"
        f"- **Daily Supermarkets & Groceries:** Within 500m to 1 km.\n"
        f"- **Schools & Playgrounds:** Within 2 to 4 km.\n\n"
        f"Use our dedicated **Nearby Essentials** tab to explore live OpenStreetMap POI pins across 81 cities!"
    )
    return {"reply": reply, "calculation_note": "Standard urban planning radius benchmarks."}


def _handle_comparison_query(
    user_prompt: str,
    property_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Provide property comparison framework and trade-off analysis."""
    reply = (
        "⚖️ **Property Comparison & Trade-off Framework:**\n\n"
        "When comparing two or three properties, evaluate these decisive dimensions:\n\n"
        "1. **Effective Price per Sq. Ft on Usable Carpet Area:**\n"
        "   Never compare gross prices directly without normalizing for usable carpet area (Total Price ÷ Carpet Sq.ft).\n"
        "2. **Location Premium vs Space:**\n"
        "   A 2 BHK in a prime urban core often equals the price of a 3 BHK in developing suburban corridors. Consider daily commute hours vs long-term family space requirements.\n"
        "3. **Ready to Move vs Under Construction:**\n"
        "   Ready properties carry zero construction delay risk and immediate tax depreciation benefits, but trade at an 8% to 15% price premium.\n"
        "4. **Maintenance Costs & Society Amenities:**\n"
        "   High-end clubhouses and extensive landscaping increase recurring monthly society maintenance charges by ₹4 to ₹8 per sq.ft.\n\n"
        "💡 *Action:* Navigate to our **Compare Properties** tab to enter your specific candidate listings side-by-side with automatic rate calculations!"
    )
    return {"reply": reply, "calculation_note": "Comparative multi-criteria valuation matrix."}


def _handle_general_advisory(user_prompt: str) -> Dict[str, Any]:
    """General helpful fallback for greetings or open queries."""
    reply = (
        "👋 **Welcome to DwellIQ AI — Your Personal Property Advisor!**\n\n"
        "I am here to guide you through every stage of your real-estate decision process:\n\n"
        "• **Valuation Breakdown:** Ask *'Explain my property estimate'* to understand how model features drove your price.\n"
        "• **Affordability & Budget Planning:** Ask *'Can I afford a ₹80 lakh home?'* or state your monthly salary.\n"
        "• **Loan & EMI Calculations:** Ask *'Calculate EMI for a ₹50 lakh loan at 8.5% for 20 years'*.\n"
        "• **Property Comparison:** Ask *'Compare a 2 BHK in city center vs a 3 BHK in suburbs'*.\n"
        "• **Due Diligence Checklist:** Ask *'What should I check before buying a flat?'* for the RERA legal guide.\n"
        "• **Property Terminology:** Ask *'What is the difference between carpet area and built-up area?'*.\n\n"
        "Select one of the quick prompt cards above or type your specific question below to begin!"
    )
    return {"reply": reply, "calculation_note": "DwellIQ Built-in Real Estate Knowledge Engine."}


# =====================================================================
# MAIN ADVISOR ENTRYPOINT
# =====================================================================

def ask_property_advisor(
    user_prompt: str,
    history: Optional[List[Dict[str, Any]]] = None,
    property_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main entrypoint for DwellIQ AI Property Advisor.
    1. Tries OpenAI or Gemini live LLM if API keys are configured in st.secrets or os.environ.
    2. Falls back seamlessly to the deterministic DwellIQ Real Estate Domain Engine.
    """
    if history is None:
        history = []

    cleaned = user_prompt.strip().lower()
    openai_key, gemini_key = get_configured_llm_credentials()
    timestamp_str = datetime.now().strftime("%I:%M %p")

    # 1. Attempt OpenAI live call
    if openai_key:
        try:
            llm_text = _call_openai_llm(openai_key, user_prompt, history, property_context)
            if llm_text:
                return {
                    "reply": llm_text,
                    "source": "OpenAI LLM (gpt-4o-mini)",
                    "is_live_llm": True,
                    "timestamp": timestamp_str,
                    "calculation_note": "Adaptive reasoning grounded in DwellIQ real-estate system instruction.",
                }
        except Exception as e:
            # Fall through gracefully to Gemini or Domain Engine
            pass

    # 2. Attempt Gemini live call
    if gemini_key:
        try:
            llm_text = _call_gemini_llm(gemini_key, user_prompt, history, property_context)
            if llm_text:
                return {
                    "reply": llm_text,
                    "source": "Google Gemini (gemini-1.5-flash)",
                    "is_live_llm": True,
                    "timestamp": timestamp_str,
                    "calculation_note": "Adaptive reasoning grounded in DwellIQ real-estate system instruction.",
                }
        except Exception as e:
            pass

    # 3. Deterministic Knowledge Engine (Offline Grounded Mode)
    # Detect user intent
    if any(w in cleaned for w in ["explain", "estimate", "valuation", "predicted", "model", "how is price", "why is price"]):
        res = _handle_price_explanation(property_context)
    elif any(w in cleaned for w in ["afford", "budget", "salary", "can i buy", "can i afford", "income", "eligible"]):
        res = _handle_affordability(user_prompt, property_context)
    elif any(w in cleaned for w in ["emi", "loan", "interest", "mortgage", "tenure", "down payment", "repayment"]):
        res = _handle_emi_guidance(user_prompt)
    elif any(w in cleaned for w in ["checklist", "legal", "documents", "before buying", "rera", "encumbrance", "oc", "cc"]):
        res = _handle_checklist()
    elif any(w in cleaned for w in ["carpet", "built-up", "super area", "builtup", "sqft", "uds", "freehold", "leasehold"]):
        res = _handle_property_terms()
    elif any(w in cleaned for w in ["nearby", "hospital", "school", "metro", "supermarket", "station", "amenities", "facilities"]):
        res = _handle_nearby_amenities_query(user_prompt)
    elif any(w in cleaned for w in ["compare", "comparison", "trade-off", "vs", "difference between"]):
        res = _handle_comparison_query(user_prompt, property_context)
    else:
        res = _handle_general_advisory(user_prompt)

    return {
        "reply": res["reply"],
        "source": "DwellIQ Real Estate Domain Engine (Deterministic Mode)",
        "is_live_llm": False,
        "timestamp": timestamp_str,
        "calculation_note": res.get("calculation_note", "Verified engineering & financial formulas."),
    }


def ask_assistant(user_prompt: str, session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Backward compatibility shim."""
    return ask_property_advisor(user_prompt=user_prompt, property_context=session_context)
