import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from frontend.components.navbar import render_section_header
from backend.services.comparison_service import compare_properties
from backend.services.prediction_service import format_rupees


def render_compare_properties_page():
    render_section_header(
        "Side-by-Side Analysis",
        "Property Comparison Matrix",
        "Evaluate two or three properties side-by-side on carpet area, unit rate (₹/sq.ft), configuration, and amenities."
    )

    st.write(
        "You can compare either your recent estimation, custom user-entered options, or sample verified market listings."
    )

    # Allow loading recent estimation if available
    latest_est = st.session_state.get("latest_estimate")

    num_props = st.radio("Number of properties to compare:", [2, 3], horizontal=True)

    if num_props == 3:
        col1, col2, col3 = st.columns(3)
    else:
        col1, col2 = st.columns(2)
        col3 = None

    prop1_data = {}
    prop2_data = {}
    prop3_data = {}

    with col1:
        st.markdown("#### Property A")
        default_title_a = latest_est.get("title", "3 BHK in Andheri West") if latest_est else "3 BHK in Andheri West"
        default_price_a = float(latest_est.get("price", 18500000.0)) if latest_est else 18500000.0
        default_area_a = float(latest_est.get("area", 1150.0)) if latest_est else 1150.0

        p1_title = st.text_input("Property Label / Name", value=default_title_a, key="cmp_p1_title")
        p1_price = st.number_input("Total Price (₹)", value=default_price_a, min_value=100000.0, step=100000.0, key="cmp_p1_price")
        p1_area = st.number_input("Carpet Area (sq. ft)", value=default_area_a, min_value=100.0, step=50.0, key="cmp_p1_area")
        p1_bhk = st.number_input("Bedrooms (BHK)", value=3, min_value=1, max_value=8, key="cmp_p1_bhk")
        p1_baths = st.number_input("Bathrooms", value=2, min_value=1, max_value=6, key="cmp_p1_baths")
        p1_furn = st.selectbox("Furnishing", ["Semi-Furnished", "Unfurnished", "Furnished"], key="cmp_p1_furn")
        p1_parking = st.selectbox("Car Parking", ["1", "2", "3+", "None"], key="cmp_p1_park")
        prop1_data = {
            "title": p1_title,
            "price": p1_price,
            "area": p1_area,
            "bhk": p1_bhk,
            "bathrooms": p1_baths,
            "furnishing": p1_furn,
            "parking": p1_parking,
        }

    with col2:
        st.markdown("#### Property B")
        p2_title = st.text_input("Property Label / Name", value="2 BHK in Powai Greens", key="cmp_p2_title")
        p2_price = st.number_input("Total Price (₹)", value=14200000.0, min_value=100000.0, step=100000.0, key="cmp_p2_price")
        p2_area = st.number_input("Carpet Area (sq. ft)", value=890.0, min_value=100.0, step=50.0, key="cmp_p2_area")
        p2_bhk = st.number_input("Bedrooms (BHK)", value=2, min_value=1, max_value=8, key="cmp_p2_bhk")
        p2_baths = st.number_input("Bathrooms", value=2, min_value=1, max_value=6, key="cmp_p2_baths")
        p2_furn = st.selectbox("Furnishing", ["Furnished", "Semi-Furnished", "Unfurnished"], key="cmp_p2_furn")
        p2_parking = st.selectbox("Car Parking", ["1", "2", "3+", "None"], key="cmp_p2_park")
        prop2_data = {
            "title": p2_title,
            "price": p2_price,
            "area": p2_area,
            "bhk": p2_bhk,
            "bathrooms": p2_baths,
            "furnishing": p2_furn,
            "parking": p2_parking,
        }

    if num_props == 3 and col3 is not None:
        with col3:
            st.markdown("#### Property C")
            p3_title = st.text_input("Property Label / Name", value="3.5 BHK in Whitefield Bangalore", key="cmp_p3_title")
            p3_price = st.number_input("Total Price (₹)", value=12500000.0, min_value=100000.0, step=100000.0, key="cmp_p3_price")
            p3_area = st.number_input("Carpet Area (sq. ft)", value=1450.0, min_value=100.0, step=50.0, key="cmp_p3_area")
            p3_bhk = st.number_input("Bedrooms (BHK)", value=3, min_value=1, max_value=8, key="cmp_p3_bhk")
            p3_baths = st.number_input("Bathrooms", value=3, min_value=1, max_value=6, key="cmp_p3_baths")
            p3_furn = st.selectbox("Furnishing", ["Semi-Furnished", "Unfurnished", "Furnished"], key="cmp_p3_furn")
            p3_parking = st.selectbox("Car Parking", ["2", "1", "3+", "None"], key="cmp_p3_park")
            prop3_data = {
                "title": p3_title,
                "price": p3_price,
                "area": p3_area,
                "bhk": p3_bhk,
                "bathrooms": p3_baths,
                "furnishing": p3_furn,
                "parking": p3_parking,
            }

    property_list = [prop1_data, prop2_data]
    if num_props == 3 and prop3_data:
        property_list.append(prop3_data)

    comparison_results = compare_properties(property_list)

    st.markdown("---")
    st.markdown("### Comparison Results Matrix")

    # Render structured comparison table
    items = comparison_results["items"]
    table_data = {
        "Metric": [
            "Total Price",
            "Carpet Area (sq. ft)",
            "Price per sq. ft",
            "Configuration",
            "Bathrooms",
            "Furnishing Status",
            "Car Parking",
        ]
    }

    for item in items:
        table_data[item["title"]] = [
            format_rupees(item["price"]),
            f"{item['area']:,.0f} sq.ft",
            f"₹{item['rate_sqft']:,.0f} / sq.ft",
            f"{item['bhk']} BHK",
            f"{item['bathrooms']} Baths",
            item["furnishing"],
            f"{item['parking']} slot(s)",
        ]

    df_cmp = pd.DataFrame(table_data)
    st.dataframe(df_cmp.set_index("Metric"), use_container_width=True)

    # Strategic Highlights Box
    h1, h2, h3 = st.columns(3)
    with h1:
        st.success(f"🏆 **Lowest Total Outlay:**\n\n{comparison_results['best_price']}")
    with h2:
        st.info(f"💎 **Best Value Rate (Lowest ₹/sq.ft):**\n\n{comparison_results['best_rate_sqft']}")
    with h3:
        st.warning(f"📐 **Largest Usable Space:**\n\n{comparison_results['largest_area']}")


def render_comparison_page():
    """Alias for backwards compatibility."""
    render_compare_properties_page()


if __name__ == "__main__":
    render_compare_properties_page()
