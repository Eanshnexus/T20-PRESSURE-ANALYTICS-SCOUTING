"""
sidebar.py — Clean, top-anchored branded sidebar with Material icon navigation
(Dashboard instead of 'app'), 'Developed by Eko_Dev' attribution, and zero clutter.
"""
import os
import base64
import streamlit as st
from utils.data_loader import get_project_paths


@st.cache_data(show_spinner=False)
def _load_css_text() -> str:
    css_path = os.path.join(get_project_paths()["assets"], "styles", "custom.css")
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()


@st.cache_data(show_spinner=False)
def _load_svg_b64(filename: str) -> str:
    svg_path = os.path.join(get_project_paths()["assets"], "icons", filename)
    if not os.path.exists(svg_path):
        return ""
    with open(svg_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def inject_global_styles():
    st.markdown(f"<style>{_load_css_text()}</style>", unsafe_allow_html=True)


def render_sidebar_and_mode() -> str:
    """Render top-aligned branded sidebar with interactive icon navigation and return active mode."""
    inject_global_styles()
    mode = "LOCAL_COMPETITION"
    st.session_state["app_mode"] = mode

    with st.sidebar:
        # 1. Brand Crest + Title + Developer Credit at VERY TOP
        icon_b64 = _load_svg_b64("cricket_crest.svg")
        icon_html = (
            f'<img src="data:image/svg+xml;base64,{icon_b64}" width="44" style="border-radius:10px;flex-shrink:0;"/>'
            if icon_b64
            else ""
        )
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:11px;margin-bottom:2px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.09);">
                {icon_html}
                <div>
                    <div style="font-family:'Outfit',sans-serif;font-size:1.10rem;font-weight:800;color:#F5F6FA;line-height:1.12;letter-spacing:0.01em;">
                        T20 PRESSURE
                    </div>
                    <div style="font-size:0.68rem;font-weight:700;color:#EA3D91;letter-spacing:0.09em;margin-top:2px;">
                        ANALYTICS &amp; SCOUTING
                    </div>
                    <div style="font-size:0.69rem;color:#F4C542;font-weight:600;margin-top:2px;">
                        Developed by Eko_Dev
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Structured Interactive Icon Navigation
        def _nav_link(page: str, label: str, icon: str):
            try:
                st.page_link(page, label=label, icon=icon)
            except KeyError:
                pass  # Isolated AppTest single-file runs without multipage router

        st.markdown("<div class='sidebar-nav-label' style='padding-top:4px;'>Overview</div>", unsafe_allow_html=True)
        _nav_link("app.py", label="Dashboard", icon=":material/space_dashboard:")

        st.markdown("<div class='sidebar-nav-label'>Player Intelligence</div>", unsafe_allow_html=True)
        _nav_link("pages/1_Batter_Analytics.py", label="Batter Analytics", icon=":material/sports_cricket:")
        _nav_link("pages/2_Bowler_Analytics.py", label="Bowler Analytics", icon=":material/target:")
        _nav_link("pages/3_Player_Comparison.py", label="Player Comparison", icon=":material/compare_arrows:")
        _nav_link("pages/7_Scouting_Insights.py", label="Scouting Insights", icon=":material/radar:")

        st.markdown("<div class='sidebar-nav-label'>Statistical Engine</div>", unsafe_allow_html=True)
        _nav_link("pages/4_Pressure_Analytics.py", label="Pressure Analytics", icon=":material/speed:")
        _nav_link("pages/5_Methodology.py", label="Methodology", icon=":material/functions:")
        _nav_link("pages/6_Format_Robustness.py", label="Format & Robustness", icon=":material/verified:")

        # 3. Compact Framework Summary Card
        st.markdown(
            """
            <div style="margin-top:12px;padding:10px 12px;border-radius:10px;background:rgba(33,27,54,0.72);border:1px solid rgba(255,255,255,0.08);font-size:0.72rem;color:#A7AEC0;line-height:1.5;">
                <div style="color:#F5F6FA;font-weight:700;font-size:0.73rem;margin-bottom:3px;letter-spacing:0.04em;">
                    MODEL HIGHLIGHTS
                </div>
                • Ex-Ante CPI Pressure (&ge; 0.60)<br>
                • 5-Fold Match-Grouped ML<br>
                • Empirical Bayes Shrinkage<br>
                • <span style="color:#EA3D91;">IPL</span> · <span style="color:#35C6B5;">T20I</span> · <span style="color:#F4C542;">Other T20</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return mode
