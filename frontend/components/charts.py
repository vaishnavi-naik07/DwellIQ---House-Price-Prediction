from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import streamlit as st


def render_emi_donut_chart(principal: float, total_interest: float):
    """Render an attractive payment breakdown donut chart."""
    if principal <= 0:
        return

    fig, ax = plt.subplots(figsize=(5, 3.2), facecolor="#FAF9F5")
    ax.set_facecolor("#FAF9F5")
    slices = [principal, total_interest]
    labels = ["Principal Loan", "Total Interest"]
    colors = ["#2D5A43", "#C59B27"]

    wedges, texts, autotexts = ax.pie(
        slices,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        textprops=dict(color="#18261E", fontweight="bold", fontsize=9),
        wedgeprops=dict(width=0.45, edgecolor="#FAF9F5", linewidth=2),
    )
    plt.setp(autotexts, size=9, weight="bold", color="white")
    ax.axis("equal")
    st.pyplot(fig)
    plt.close(fig)


def render_image_figure(fig_path: Path, caption: str, fallback_msg: str):
    """Safely render a figure image with fallback message."""
    if fig_path.exists():
        st.image(str(fig_path), caption=caption, use_container_width=True)
    else:
        st.info(fallback_msg)

