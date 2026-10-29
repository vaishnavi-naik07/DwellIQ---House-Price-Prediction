import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np

from frontend.components.navbar import render_section_header
from frontend.components.property_card import render_valuation_card
from backend.services.prediction_service import predict_price, format_rupees
from backend.services.nearby_service import get_nearby_amenities
from backend.core.config import DATASET_LOCATIONS
from src.nearby_places import NEARBY_ESSENTIALS_OPTIONS, DISTANCE_PREFERENCES
from src.auth import save_user_estimation


def render_estimate_property_page(current_user=None):
    render_section_header(
        "ML Property Valuation",
        "Estimate a Residential Property",
        "Enter verified structural, locational, and amenity parameters to compute an instant valuation benchmark."
    )

    with st.form("property_estimation_form_redesign"):
        st.markdown("#### 1. Structural & Core Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            location = st.selectbox(
                "City / Locality Hub *",
                options=DATASET_LOCATIONS,
                index=DATASET_LOCATIONS.index("Mumbai") if "Mumbai" in DATASET_LOCATIONS else 0,
                help="Select from 81 verified cities with trained statistical representations.",
            )
            bhk = st.number_input("Bedrooms (BHK) *", min_value=1, max_value=10, value=3, step=1)
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=8, value=2, step=1)

        with col2:
            carpet_area = st.number_input(
                "Carpet Area (sq. ft) *",
                min_value=100.0,
                max_value=25000.0,
                value=1200.0,
                step=50.0,
                help="Usable net floor area within the property walls as per RERA standards.",
            )
            balconies = st.number_input("Balconies", min_value=0, max_value=6, value=2, step=1)
            floor_pref = st.selectbox(
                "Floor Level",
                ["Ground", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10+", "Top Floor"],
                index=5,
            )

        with col3:
            furnishing = st.selectbox(
                "Furnishing Status",
                ["Semi-Furnished", "Unfurnished", "Furnished"],
                index=0,
            )
            facing = st.selectbox(
                "Facing Direction",
                ["East", "North", "North-East", "West", "South", "North-West", "South-East", "South-West"],
                index=0,
            )
            parking = st.selectbox(
                "Car Parking Spaces",
                ["1", "2", "3", "4+", "None"],
                index=0,
            )

        st.markdown("#### 2. Legal, Transaction & Financial Preferences")
        col4, col5, col6 = st.columns(3)
        with col4:
            status = st.selectbox(
                "Construction Status",
                ["Ready to Move", "Under Construction"],
                index=0,
            )
        with col5:
            transaction = st.selectbox(
                "Transaction Type",
                ["Resale", "New Property"],
                index=0,
            )
        with col6:
            ownership = st.selectbox(
                "Ownership Title",
                ["Freehold", "Leasehold", "Power of Attorney", "Co-operative Society"],
                index=0,
            )

        st.markdown("#### 3. Nearby Essentials Preference (Optional Context)")
        col7, col8 = st.columns(2)
        with col7:
            essential_category = st.selectbox(
                "Check Nearby Infrastructure",
                options=NEARBY_ESSENTIALS_OPTIONS,
                index=0,
                help="Optionally search live OpenStreetMap POI records near this city's center.",
            )
        with col8:
            distance_radius = st.selectbox(
                "Max Radius Preference",
                options=list(DISTANCE_PREFERENCES.keys()),
                index=1,
            )

        submitted = st.form_submit_button(
            "⚡ Calculate Valuation Benchmark",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        input_data = {
            "BHK": bhk,
            "carpet_area_sqft": carpet_area,
            "Bathroom": bathrooms,
            "Balcony": balconies,
            "location": location.lower(),
            "Status": status,
            "Floor": floor_pref,
            "Transaction": transaction,
            "Furnishing": furnishing,
            "facing": facing,
            "Ownership": ownership,
            "Car Parking": parking,
        }

        try:
            with st.spinner("Executing Random Forest pipeline inference..."):
                predicted_val, meta = predict_price(input_data)

            # Store in session state for comparison and calculator reuse
            st.session_state["latest_estimate"] = {
                "title": f"{bhk} BHK in {location}",
                "price": predicted_val,
                "area": carpet_area,
                "bhk": bhk,
                "location": location,
                "bathrooms": bathrooms,
                "parking": parking,
                "furnishing": furnishing,
                "status": status,
            }

            # If user is logged in, record in persistence DB
            if current_user and "id" in current_user:
                save_user_estimation(
                    user_id=current_user["id"],
                    location=location,
                    bhk=bhk,
                    carpet_area=carpet_area,
                    estimated_price=predicted_val,
                )

            # Render Premium Valuation Card
            render_valuation_card(
                predicted_val=predicted_val,
                carpet_area=carpet_area,
                rate_per_sqft=meta.get("price_per_sqft"),
                specs={
                    "location": location,
                    "bhk": bhk,
                    "bathrooms": bathrooms,
                    "facing": facing,
                    "furnishing": furnishing,
                },
            )

            # Technical Transparency & Model Limitations Notice
            m_metrics = meta.get("metrics", {})
            mae_str = format_rupees(m_metrics.get("MAE_Rupees", 1816360))
            r2_val = m_metrics.get("R2", 0.026)

            st.warning(
                f"ℹ️ **Model Transparency & Limitation Notice:**\n\n"
                f"- **Active Estimator:** {meta.get('model_name', 'Random Forest Regressor')}\n"
                f"- **Reported Validation MAE:** ~{mae_str} (Mean Absolute Error on holdout test set)\n"
                f"- **Model R² Score:** {r2_val:.3f} — Real-estate price variation in pan-India open listings is wide due to hyper-local amenities, developer brand reputation, and road frontage not fully captured in tabular datasets.\n"
                f"- This figure should be used as a preliminary statistical benchmark alongside certified surveyor appraisal."
            )

            # Quick Navigation to EMI Calculator, Comparison, or DwellIQ AI Advisor
            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                if st.button("📊 Calculate Monthly EMI →", use_container_width=True):
                    st.session_state["prefill_price"] = predicted_val
                    st.session_state["page_nav"] = "EMI Calculator"
                    st.rerun()
            with col_act2:
                if st.button("⚖️ Compare Listing →", use_container_width=True):
                    st.session_state["page_nav"] = "Compare Properties"
                    st.rerun()
            with col_act3:
                if st.button("💬 Discuss with DwellIQ AI →", use_container_width=True, type="primary"):
                    st.session_state["active_property_context"] = st.session_state["latest_estimate"]
                    st.session_state["page_nav"] = "DwellIQ AI Advisor"
                    st.rerun()

            # Handle live Nearby Essentials if selected
            if essential_category and essential_category != "No preference":
                st.markdown("---")
                st.markdown(f"#### 📍 Nearby {essential_category} near {location}")
                radius_km = DISTANCE_PREFERENCES.get(distance_radius, 5.0)
                places_result = get_nearby_amenities(location, essential_category, radius_km)

                if places_result["status"] == "success":
                    st.success(places_result["message"])
                    for place in places_result["places"]:
                        st.markdown(
                            f"- **{place['name']}** (~{place['distance_km']} km away) · *{place['address']}*"
                        )
                elif places_result["status"] == "no_results":
                    st.info(places_result["message"])
                else:
                    st.info(
                        f"Live OSM service status: {places_result['message']} "
                        "(Local coordinate resolution fallback active)."
                    )

        except Exception as e:
            st.error(f"Prediction could not be completed: {str(e)}")


def render_estimate_page(current_user=None):
    """Alias for backwards compatibility."""
    render_estimate_property_page(current_user=current_user)


if __name__ == "__main__":
    render_estimate_property_page()
