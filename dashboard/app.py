"""
app.py — PAGE 1: HOME / ANALYTICS OVERVIEW
T20 Pressure Analytics & Scouting Platform (SupeRR Selector Season 2).
"""
import os
import sys
import streamlit as st

# Ensure dashboard root is on sys.path for clean imports across multipage runs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="T20 Pressure Analytics | Scouting Platform",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_hero_banner,
    render_kpi_card,
    render_section_header,
    render_insight_card,
    render_metric_glossary,
    render_footer,
)
from components.charts import (
    make_top10_bar,
    make_season_format_chart,
    make_cpi_histogram,
)
from utils.data_loader import get_active_data
from utils.formatting import PALETTE

# Render Sidebar & Active Mode
mode = render_sidebar_and_mode()
data = get_active_data()
kpis = data["pressure_agg"]["kpis"]

# 1. Hero Banner
eyebrow = "SUPERR SELECTOR SEASON 2  •  T20 PRESSURE ANALYTICS" if mode == "LOCAL_COMPETITION" else "PUBLIC DEMO MODE  •  SYNTHETIC DATA"
render_hero_banner(
    eyebrow=eyebrow,
    title="T20 Pressure Analytics",
    subtitle="Identifying Reliable T20 Performers Under Pressure",
    description=(
        "A quantitative cricket scouting and performance-evaluation platform separating true high-pressure match-winners "
        "from low-leverage compilers and small-sample anomalies. Built on pre-delivery leverage modeling (CPI), "
        "match-grouped out-of-fold ML baselines, Empirical Bayes shrinkage, and strict 3-way competition separation."
    ),
    image_name="hero_stadium.jpg",
)

# 2. Verified Dataset KPI Cards
render_section_header("Verified Dataset & Analytical Coverage", accent="gold")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Deliveries Analysed", f"{kpis['total_deliveries']:,}", f"{kpis['legal_deliveries']:,} legal deliveries", "pink")
with c2:
    render_kpi_card("High-Pressure Crucible", f"{kpis['hp_deliveries']:,}", f"{kpis['hp_pct']:.2f}% of all balls (CPI >= 0.60)", "gold")
with c3:
    render_kpi_card("Contested Matches", f"{kpis['total_matches']:,}", f"Across {kpis['total_competitions']} competitions (2022–2026)", "teal")
with c4:
    render_kpi_card("Players Evaluated", f"{kpis['unique_players']:,}", f"{kpis['qualified_batters']} qual. batters • {kpis['qualified_bowlers']} qual. bowlers", "pink")
with c5:
    render_kpi_card("3-Way Format Split", f"{kpis['ipl_deliveries']:,} IPL", f"{kpis['t20i_deliveries']:,} T20I • {kpis['other_t20_deliveries']:,} Other T20", "teal")

# 3. Quick Navigation Cards
render_section_header("Explore Platform Modules", accent="pink")
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    render_insight_card("Batter Analytics", "Explore the Global Top 10 & full qualifying pool with dynamic filters, 3-way format splits, and 10-part player profiles.", "pink")
    if st.button("Open Batter Analytics →", width='stretch', key="nav_bat"):
        st.switch_page("pages/1_Batter_Analytics.py")
with nav2:
    render_insight_card("Bowler Analytics", "Audit defensive run prevention (RPA), pressure economy, wickets above expectation, and IPL vs T20I bowling splits.", "teal")
    if st.button("Open Bowler Analytics →", width='stretch', key="nav_bowl"):
        st.switch_page("pages/2_Bowler_Analytics.py")
with nav3:
    render_insight_card("Head-to-Head Comparison", "Compare 2 or 3 batters or bowlers side-by-side with normalized radar charts, KPI cards, and bar breakdowns.", "gold")
    if st.button("Open Player Comparison →", width='stretch', key="nav_comp"):
        st.switch_page("pages/3_Player_Comparison.py")
with nav4:
    render_insight_card("Pressure & Methodology", "Simulate live match-state CPI, inspect over-by-over leverage, review exact formulas, and verify sensitivity checks.", "pink")
    if st.button("Open Pressure Analytics →", width='stretch', key="nav_press"):
        st.switch_page("pages/4_Pressure_Analytics.py")

# 4. Introductory Top 10 Previews
render_section_header("Official Global Top 10 Pressure Leaders", accent="gold")
col_b, col_bw = st.columns(2)
with col_b:
    fig_bat = make_top10_bar(
        data["top10_bat"], "Player name", "Auction Rating", "Rank", PALETTE["pink"],
        title="Global Top 10 Batters Under Pressure (>=120 HP BF)",
        x_range=[80, 100],
        extra_hover_cols=[("HP Balls Faced", "Pressure balls faced"), ("HP Strike Rate", "Pressure strike rate"), ("RAA", "Runs above expectation"), ("Consistency", "Match consistency")],
    )
    st.plotly_chart(fig_bat, width='stretch')

with col_bw:
    fig_bowl = make_top10_bar(
        data["top10_bowl"], "Player name", "Auction Rating", "Rank", PALETTE["teal"],
        title="Global Top 10 Bowlers Under Pressure (>=150 HP Legal Balls)",
        x_range=[55, 90],
        extra_hover_cols=[("HP Legal Balls", "Pressure legal balls"), ("HP Economy", "Pressure economy"), ("RPA", "Runs prevented above expectation"), ("Wickets", "Wickets")],
    )
    st.plotly_chart(fig_bowl, width='stretch')

# 5. Framework & Coverage Visuals
render_section_header("Dataset Coverage & Pre-Delivery Pressure Architecture", accent="teal")
vc1, vc2 = st.columns(2)
with vc1:
    st.plotly_chart(make_season_format_chart(data["pressure_agg"]["by_season_format"]), width='stretch')
with vc2:
    st.plotly_chart(make_cpi_histogram(data["pressure_agg"]["cpi_hist"]), width='stretch')

# 6. Methodology Highlights
render_section_header("Core Methodological Pillars", accent="pink")
m1, m2, m3 = st.columns(3)
with m1:
    render_insight_card(
        "1. Zero-Leakage Ex-Ante Pressure (CPI)",
        "Every delivery is scored strictly on pre-delivery scoreboard state (RRR, wickets remaining, balls left, collapse state, knockout multiplier) with zero outcome leakage.",
        "pink",
    )
with m2:
    render_insight_card(
        "2. Context-Adjusted ML Baselines",
        "5-fold match-grouped HistGradientBoosting models estimate expected runs and dismissal/wicket probabilities, isolating true Runs Added (RAA) and Runs Prevented (RPA) above expectation.",
        "teal",
    )
with m3:
    render_insight_card(
        "3. Shrinkage & 3-Way Format Separation",
        "Empirical Bayes shrinkage (K_bat=150, K_bowl=200) curbs small-sample volatility, while strict 3-way competition separation ensures Other T20 tournaments never contaminate IPL or T20I metrics.",
        "gold",
    )

render_metric_glossary(["Auction Rating", "Pressure Impact Score", "Runs Above Expectation (RAA)", "Runs Prevented Above Expectation (RPA)", "CPI", "Ranking Stability"])
render_footer(mode)
