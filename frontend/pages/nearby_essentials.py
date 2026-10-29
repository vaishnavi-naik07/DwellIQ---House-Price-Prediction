import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.components.navbar import render_section_header
from backend.services.nearby_service import get_nearby_amenities
from src.nearby_places import (
    NEARBY_ESSENTIALS_OPTIONS,
    DISTANCE_PREFERENCES,
    CITY_COORDINATES,
)


def render_nearby_essentials_page():
    render_section_header(
        "Infrastructure Mapping",
        "Nearby Essentials & POI Verification",
        "Search verified civic amenities, transportation hubs, hospitals, and schools around Indian cities via live OpenStreetMap geospatial data."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.selectbox(
            "Select City Anchor",
            options=sorted(list(CITY_COORDINATES.keys())),
            index=sorted(list(CITY_COORDINATES.keys())).index("Mumbai")
            if "Mumbai" in CITY_COORDINATES
            else 0,
        )
    with col2:
        category = st.selectbox(
            "Essential Amenity Type",
            options=[opt for opt in NEARBY_ESSENTIALS_OPTIONS if opt != "No preference"],
            index=0,
        )
    with col3:
        dist_pref = st.selectbox(
            "Search Radius",
            options=list(DISTANCE_PREFERENCES.keys()),
            index=1,
        )

    radius_km = DISTANCE_PREFERENCES[dist_pref]

    if st.button("🔍 Search Verified Nearby Places", type="primary", use_container_width=True):
        with st.spinner(f"Querying OpenStreetMap Nominatim for {category} within {radius_km} km of {city}..."):
            res = get_nearby_amenities(city, category, radius_km)

        if res["status"] == "success":
            st.success(res["message"])
            for idx, p in enumerate(res["places"], 1):
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8E2; border-radius: 14px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 700; font-size: 1.05rem; color: #18261E;">{idx}. {p['name']}</div>
                            <div style="font-size: 0.82rem; color: #6B7C72; margin-top: 2px;">{p['address']}</div>
                        </div>
                        <div style="background: #EEF3ED; border: 1px solid #D8E2D7; color: #2D5A43; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 0.82rem;">
                            📍 {p['distance_km']} km
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        elif res["status"] == "no_results":
            st.warning(res["message"])
        else:
            st.info(
                f"📡 **Live Provider Status:** {res['message']}\n\n"
                "When live OpenStreetMap Nominatim is rate-limited or offline, city centers fallback gracefully without application failure."
            )


def render_nearby_page():
    """Alias for backwards compatibility."""
    render_nearby_essentials_page()


if __name__ == "__main__":
    render_nearby_essentials_page()
