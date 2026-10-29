from typing import Dict, Any, Optional
import streamlit as st
from backend.services.prediction_service import format_rupees


def render_valuation_card(
    predicted_val: float,
    carpet_area: float,
    rate_per_sqft: Optional[float],
    specs: Dict[str, Any],
):
    """Render the premium valuation summary hero card."""
    rate_display = f"₹{rate_per_sqft:,.0f} / sq. ft" if rate_per_sqft else "N/A"
    location = specs.get("location", "Selected Micro-market")
    bhk = specs.get("bhk", 3)
    baths = specs.get("bathrooms", 2)
    facing = specs.get("facing", "East")
    furnishing = specs.get("furnishing", "Semi-Furnished")

    st.markdown(
        f"""
        <div class="valuation-result-card">
            <div class="valuation-eyebrow">Estimated Fair Market Valuation</div>
            <div class="valuation-price-hero">{format_rupees(predicted_val)}</div>
            <div style="font-size: 0.95rem; color: #D6E8D8; margin-bottom: 8px;">
                Benchmark Rate: <strong>{rate_display}</strong> (Carpet Area)
            </div>
            <div class="valuation-specs-row">
                <div class="valuation-spec-pill">📍 {location}</div>
                <div class="valuation-spec-pill">🛏️ {bhk} BHK</div>
                <div class="valuation-spec-pill">📐 {carpet_area:,.0f} sq.ft</div>
                <div class="valuation-spec-pill">🚿 {baths} Baths</div>
                <div class="valuation-spec-pill">🧭 {facing} Facing</div>
                <div class="valuation-spec-pill">🛋️ {furnishing}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_property_card(property_data: Dict[str, Any], show_action: bool = True):
    """Render a clean card displaying a single property's core attributes."""
    title = property_data.get("title", "Residential Property")
    price = property_data.get("price", 0)
    area = property_data.get("area", 0)
    bhk = property_data.get("bhk", 2)
    loc = property_data.get("location", "Pan-India")
    status = property_data.get("status", "Ready to Move")
    rate = round(price / area, 0) if area > 0 else 0

    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 16px; padding: 20px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(24,38,30,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="font-size: 0.76rem; font-weight: 700; color: #3B7A5C; text-transform: uppercase;">{status}</div>
                    <div style="font-weight: 800; font-size: 1.15rem; color: #18261E; margin: 4px 0;">{title}</div>
                    <div style="font-size: 0.82rem; color: #6B7C72;">📍 {loc}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 800; font-size: 1.3rem; color: #2D5A43;">{format_rupees(price)}</div>
                    <div style="font-size: 0.78rem; color: #6B7C72;">₹{rate:,.0f}/sq.ft</div>
                </div>
            </div>
            <div style="display: flex; gap: 12px; margin-top: 14px; font-size: 0.82rem; color: #3D4F44; border-top: 1px solid #F4F7F3; padding-top: 10px;">
                <span>🛏️ {bhk} BHK</span>
                <span>📐 {area:,.0f} sq.ft</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

