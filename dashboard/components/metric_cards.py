"""
metric_cards.py — Premium banners, KPI cards, section headers, and glossary expanders.
"""
import os
import base64
import streamlit as st
from utils.data_loader import get_project_paths
from utils.formatting import METRIC_GLOSSARY


@st.cache_data(show_spinner=False)
def get_image_b64(filename: str) -> str:
    img_path = os.path.join(get_project_paths()["assets"], "images", filename)
    if not os.path.exists(img_path):
        return ""
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def render_hero_banner(eyebrow: str, title: str, subtitle: str, description: str, image_name: str = "hero_stadium.jpg", author: str = "Developed by Eko_Dev"):
    b64 = get_image_b64(image_name)
    bg_style = f"background-image: url('data:image/jpeg;base64,{b64}');" if b64 else "background: linear-gradient(135deg, #211B36 0%, #101426 100%);"
    author_html = (
        f'<div class="hero-author">✦ {author}</div>'
        if author
        else ""
    )
    st.markdown(
        f"""
        <div class="hero-banner" style="{bg_style}">
            <div class="hero-overlay">
                <div class="hero-eyebrow">{eyebrow}</div>
                <h1 class="hero-title">{title}</h1>
                {author_html}
                <div class="hero-subtitle">{subtitle}</div>
                <p class="hero-desc">{description}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_banner(title: str, subtitle: str, image_name: str = "tactical_analytics_bg.jpg", accent: str = "#EA3D91"):
    b64 = get_image_b64(image_name)
    bg_style = f"background-image: url('data:image/jpeg;base64,{b64}');" if b64 else "background: #211B36;"
    st.markdown(
        f"""
        <div class="page-banner" style="{bg_style} border-left: 4px solid {accent};">
            <div class="page-banner-overlay">
                <h1 class="page-banner-title">{title}</h1>
                <p class="page-banner-sub">{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, sub: str = "", accent: str = "pink"):
    accent_cls = {"pink": "kpi-accent-pink", "gold": "kpi-accent-gold", "teal": "kpi-accent-teal"}.get(accent, "kpi-accent-pink")
    st.markdown(
        f"""
        <div class="kpi-card {accent_cls}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, accent: str = "pink"):
    bar_cls = {"pink": "section-bar-pink", "gold": "section-bar-gold", "teal": "section-bar-teal"}.get(accent, "section-bar-pink")
    st.markdown(
        f"""
        <div class="section-header">
            <div class="{bar_cls}"></div>
            <h2 class="section-title">{title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(title: str, body: str, accent: str = "teal"):
    cls = "insight-card"
    if accent == "pink":
        cls += " insight-card-pink"
    elif accent == "gold":
        cls += " insight-card-gold"
    st.markdown(
        f"""
        <div class="{cls}">
            <h4>{title}</h4>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_glossary(keys: list, title: str = "Metric Definitions & Direction Guide"):
    with st.expander(title, expanded=False):
        rows_md = ["| Metric | Definition | Unit | Direction |", "| :--- | :--- | :--- | :--- |"]
        for k in keys:
            if k in METRIC_GLOSSARY:
                m = METRIC_GLOSSARY[k]
                rows_md.append(f"| **{m['label']}** | {m['definition']} | `{m['unit']}` | {m['direction']} |")
        st.markdown("\n".join(rows_md))


def render_footer(mode: str):
    st.markdown(
        """
        <div class="app-footer">
            T20 Pressure Analytics &amp; Scouting Platform &nbsp;•&nbsp;
            <strong style="color:#F4C542;">Developed by Eko_Dev</strong> &nbsp;•&nbsp;
            Built with Streamlit, Plotly &amp; Empirical Bayes Statistical Modeling
        </div>
        """,
        unsafe_allow_html=True,
    )
