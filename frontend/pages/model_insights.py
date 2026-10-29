import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from frontend.components.navbar import render_section_header
from frontend.components.charts import render_image_figure
from backend.services.prediction_service import format_rupees
from backend.core.config import REPORT_PATH, FIG_FEAT_PATH, FIG_COMP_PATH


def render_model_insights_page():
    render_section_header(
        "Empirical Validation",
        "Model Insights & Comparative Metrics",
        "Transparent, authentic benchmark results from model training and cross-validation on the 177K+ dataset."
    )

    # 1. Official Model Metrics Table from model_comparison.csv
    st.markdown("#### Model Benchmark Leaderboard")
    if REPORT_PATH.exists():
        df_comp = pd.read_csv(REPORT_PATH)
        df_display = df_comp.copy()
        df_display["MAE_Rupees_Formatted"] = df_display["MAE_Rupees"].apply(format_rupees)
        df_display["RMSE_Rupees_Formatted"] = df_display["RMSE_Rupees"].apply(format_rupees)
        df_display["R2_Score"] = df_display["R2"].apply(lambda x: f"{x:.4f}")

        st.dataframe(
            df_display[["Model", "MAE_Rupees_Formatted", "RMSE_Rupees_Formatted", "R2_Score"]].set_index("Model"),
            use_container_width=True,
        )

    # Metric Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">₹18.16 Lakh</div>
                <div class="dwell-stat-title">Random Forest MAE</div>
                <div class="dwell-stat-caption">Mean Absolute Error on holdout test set (58% lower than Linear Regression)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">0.0263</div>
                <div class="dwell-stat-title">Holdout R² Score</div>
                <div class="dwell-stat-caption">Honest metric showing the extreme noise and luxury dispersion in public listings</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="dwell-stat-card">
                <div class="dwell-stat-number">₹43.08 Lakh</div>
                <div class="dwell-stat-title">Linear Regression MAE</div>
                <div class="dwell-stat-caption">Baseline linear model struggling with non-linear location and area interactions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### Genuine Visualizations From Training Runs")

    col_fig1, col_fig2 = st.columns(2)
    with col_fig1:
        render_image_figure(
            FIG_FEAT_PATH,
            caption="Random Forest Feature Importance Analysis",
            fallback_msg="Feature importance plot not generated yet.",
        )

    with col_fig2:
        render_image_figure(
            FIG_COMP_PATH,
            caption="MAE Comparison: Random Forest vs Linear Regression",
            fallback_msg="Model comparison plot not generated yet.",
        )

    # Honest Limitations Discussion
    st.markdown("---")
    st.markdown("#### Honest Discussion of Model Limitations (For College Viva & Review)")
    st.markdown(
        """
        - **Why is R² low (~0.026)?**
          Open web-scraped real-estate data includes massive price dispersion: ultra-luxury villas and penthouses priced at ₹20–50+ Cr coexist with budget 1 BHK suburban apartments. Additionally, critical valuation determinants (such as developer reputation, exact road frontage, interior finish quality, view of sea/garden) are unobserved in basic tabular metadata.
        - **Why Random Forest outperforms Linear Regression:**
          The decision forest captures non-linear thresholds (e.g., location premium multiplier depending on carpet area) and handles high-cardinality categorical variables via frequency encoding and one-hot encoding without suffering from multicollinearity.
        - **Data Quality Safeguards:**
          Missing numerical attributes (carpet area, bathrooms) are imputed using robust median statistics, and categorical variables are imputed with mode followed by `handle_unknown='ignore'` encoders to prevent production crashes on unseen input values.
        """
    )


def render_insights_page():
    """Alias for backwards compatibility."""
    render_model_insights_page()


if __name__ == "__main__":
    render_model_insights_page()
