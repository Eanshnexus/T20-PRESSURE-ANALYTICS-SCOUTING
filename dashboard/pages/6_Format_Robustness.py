"""
6_Format_Robustness.py — PAGE 7: FORMAT & ROBUSTNESS
Strict 3-way competition separation (IPL, International T20I, Other T20), sensitivity audits
(wicket value, shrinkage, 4 CPI specs), model validation, calibration, and statistical limitations.
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Format & Robustness | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
    render_kpi_card,
    render_section_header,
    render_insight_card,
    render_footer,
)
from components.charts import style_plotly_fig
from components.tables import render_clean_table
from utils.data_loader import get_active_data
from utils.formatting import PALETTE

mode = render_sidebar_and_mode()
data = get_active_data()
agg = data["pressure_agg"]

render_page_banner(
    title="3-Way Format Separation, Robustness & Model Calibration",
    subtitle="Auditing IPL vs International T20I vs Other T20 Exposure, Sensitivity Diagnostics & Honest Statistical Limitations",
    image_name="tactical_analytics_bg.jpg",
    accent=PALETTE["teal"],
)

# 1. Strict 3-Way Competition Separation
render_section_header("1. Strict 3-Way Competition Classification (IPL vs International T20I vs Other T20)", accent="pink")
fmt_df = pd.DataFrame(agg["by_format"])
fc1, fc2, fc3 = st.columns(3)
for col_obj, cat, acc in [(fc1, "IPL", "pink"), (fc2, "International T20I", "teal"), (fc3, "Other T20", "gold")]:
    sub = fmt_df[fmt_df["comp_category"] == cat]
    if len(sub) > 0:
        r = sub.iloc[0]
        with col_obj:
            render_kpi_card(
                cat,
                f"{int(r['deliveries']):,} balls",
                f"{int(r['matches'])} matches ({int(r['competitions'])} comps) • HP: {r['hp_pct']:.2f}%",
                accent=acc,
            )

render_insight_card(
    "Why Other T20 Is Never Classified as IPL (and Why T20I != Proven IPL)",
    "Two ACC emerging tournaments (<em>Mens T20 Emerging Teams Asia Cup 2024</em> & <em>Asia Cup Rising Stars 2025</em>, 6,985 deliveries) "
    "carry <code>match_format == 'T20'</code> in source metadata. Separating them strictly into <strong>Other T20</strong> prevents non-IPL "
    "emerging fixtures from inflating IPL format scores (e.g. Sufiyan Muqeem has <strong>0 IPL</strong>, <strong>134 T20I</strong>, and "
    "<strong>65 Other T20</strong> HP balls). Furthermore, bowlers with 0 IPL balls (Abrar Ahmed, Shaheen Afridi, Mohammad Nawaz, Muqeem) "
    "receive <code>IPL Wt Comp = 0.00</code> — elite international performance must not automatically be equated with proven IPL venue performance.",
    "gold",
)

# Stacked 3-way sample chart for Top 10 Batters & Bowlers
t1, t2 = st.columns(2)
with t1:
    tb = data["top10_bat"]
    fig_tb = go.Figure()
    fig_tb.add_trace(go.Bar(name="IPL", x=tb["Player name"], y=tb["ipl_bf"], marker_color=PALETTE["pink"]))
    fig_tb.add_trace(go.Bar(name="International T20I", x=tb["Player name"], y=tb["t20i_bf"], marker_color=PALETTE["teal"]))
    fig_tb.add_trace(go.Bar(name="Other T20", x=tb["Player name"], y=tb["other_t20_bf"], marker_color=PALETTE["gold"]))
    fig_tb.update_layout(barmode="stack")
    style_plotly_fig(fig_tb, title="Top 10 Batters: 3-Way High-Pressure Ball Breakdown", height=370)
    fig_tb.update_xaxes(tickangle=-30)
    fig_tb.update_yaxes(title_text="HP Balls Faced")
    st.plotly_chart(fig_tb, width='stretch')

with t2:
    tbw = data["top10_bowl"]
    fig_tbw = go.Figure()
    fig_tbw.add_trace(go.Bar(name="IPL", x=tbw["Player name"], y=tbw["ipl_balls"], marker_color=PALETTE["pink"]))
    fig_tbw.add_trace(go.Bar(name="International T20I", x=tbw["Player name"], y=tbw["t20i_balls"], marker_color=PALETTE["teal"]))
    fig_tbw.add_trace(go.Bar(name="Other T20", x=tbw["Player name"], y=tbw["other_t20_balls"], marker_color=PALETTE["gold"]))
    fig_tbw.update_layout(barmode="stack")
    style_plotly_fig(fig_tbw, title="Top 10 Bowlers: 3-Way High-Pressure Legal Ball Breakdown", height=370)
    fig_tbw.update_xaxes(tickangle=-30)
    fig_tbw.update_yaxes(title_text="HP Legal Balls")
    st.plotly_chart(fig_tbw, width='stretch')

# 2. Ranking Sensitivity Across 4 CPI Specifications
render_section_header("2. Ranking Stability Across 4 Pressure Definitions", accent="gold")
sens = data["sensitivity"].copy()
sens_disc = st.radio("View Sensitivity Table For:", ["Batting", "Bowling"], horizontal=True, key="sens_disc_radio")
sens_sub = sens[sens["Discipline"] == sens_disc].sort_values("Primary_Rank")
render_clean_table(sens_sub, height=385)

# 3. Wicket-Value, Shrinkage & CPI Assumption Sensitivity Summary
render_section_header("3. Parameter Sensitivity: Wicket Valuation, Shrinkage & CPI Assumptions", accent="teal")
param_sens_df = pd.DataFrame([
    {"Test Dimension": "Wicket Value: 6 vs 8 runs/wkt", "Batters Spearman rho": "0.9993", "Batters Top-10 Overlap": "9 / 10", "Bowlers Spearman rho": "0.9988", "Bowlers Top-10 Overlap": "10 / 10"},
    {"Test Dimension": "Wicket Value: 10 vs 8 runs/wkt", "Batters Spearman rho": "0.9994", "Batters Top-10 Overlap": "10 / 10", "Bowlers Spearman rho": "0.9992", "Bowlers Top-10 Overlap": "10 / 10"},
    {"Test Dimension": "Wicket Value: 12 vs 8 runs/wkt", "Batters Spearman rho": "0.9986", "Batters Top-10 Overlap": "10 / 10", "Bowlers Spearman rho": "0.9979", "Bowlers Top-10 Overlap": "10 / 10"},
    {"Test Dimension": "Empirical Bayes K (MoM: 205.2 / 343.3 vs 150 / 200)", "Batters Spearman rho": "0.9997", "Batters Top-10 Overlap": "10 / 10", "Bowlers Spearman rho": "0.9996", "Bowlers Top-10 Overlap": "10 / 10"},
    {"Test Dimension": "Remove Knockout Modifier (1.0x vs 1.15x)", "Batters Spearman rho": "0.9959", "Batters Top-10 Overlap": "99.64% ball agree", "Bowlers Spearman rho": "0.9942", "Bowlers Top-10 Overlap": "99.64% ball agree"},
    {"Test Dimension": "Remove Collinear RRR-CRR Term (0.55 RRR)", "Batters Spearman rho": "0.9942", "Batters Top-10 Overlap": "99.11% ball agree", "Bowlers Spearman rho": "0.9895", "Bowlers Top-10 Overlap": "99.11% ball agree"},
])
render_clean_table(param_sens_df, height=255)

# 4. Match-Grouped ML Validation & Probability Calibration
render_section_header("4. Match-Grouped 5-Fold Validation & Probability Calibration", accent="pink")
mv1, mv2 = st.columns([1.1, 1.0])
with mv1:
    st.markdown("**Out-of-Fold Model Diagnostics (All 200,999 Deliveries, Match-Grouped 5-Fold GroupKFold):**")
    render_clean_table(data["model_val"], height=315)
with mv2:
    # Calibration decile reliability chart (verified from local audit)
    cal_deciles = pd.DataFrame({
        "Decile": list(range(1, 11)),
        "Dismissal Pred": [0.0361, 0.0401, 0.0423, 0.0442, 0.0461, 0.0484, 0.0517, 0.0574, 0.0713, 0.1085],
        "Dismissal Obs": [0.0341, 0.0401, 0.0424, 0.0425, 0.0462, 0.0511, 0.0529, 0.0589, 0.0700, 0.1038],
        "Wicket Pred": [0.0347, 0.0386, 0.0407, 0.0426, 0.0445, 0.0468, 0.0499, 0.0554, 0.0676, 0.0942],
        "Wicket Obs": [0.0346, 0.0375, 0.0413, 0.0413, 0.0440, 0.0490, 0.0486, 0.0572, 0.0680, 0.0894],
    })
    fig_cal = go.Figure()
    fig_cal.add_trace(go.Scatter(x=cal_deciles["Dismissal Pred"], y=cal_deciles["Dismissal Obs"], mode="lines+markers", name="Dismissal Prob (ECE=0.0015)", line=dict(color=PALETTE["pink"], width=2.5)))
    fig_cal.add_trace(go.Scatter(x=cal_deciles["Wicket Pred"], y=cal_deciles["Wicket Obs"], mode="lines+markers", name="Bowler Wicket Prob (ECE=0.0014)", line=dict(color=PALETTE["teal"], width=2.5)))
    fig_cal.add_trace(go.Scatter(x=[0.03, 0.115], y=[0.03, 0.115], mode="lines", name="Perfect Calibration", line=dict(dash="dash", color="rgba(255,255,255,0.4)")))
    style_plotly_fig(fig_cal, title="Out-of-Fold Probability Calibration Curve (10 Deciles)", height=315)
    fig_cal.update_xaxes(title_text="Mean Predicted Probability")
    fig_cal.update_yaxes(title_text="Observed Event Frequency")
    st.plotly_chart(fig_cal, width='stretch')

# 5. Statistical Limitations
render_section_header("5. Key Statistical Limitations & Disclosures", accent="gold")
l1, l2 = st.columns(2)
with l1:
    render_insight_card(
        "Cross-Validation & Single-Ball Variance",
        "1. 5-Fold GroupKFold is <strong>match-grouped (non-chronological)</strong> rather than walk-forward across future seasons.<br>"
        "2. Per-delivery MAE gains over simple cell baselines are modest (+0.0105 runs/ball batters [95% CI: +0.0076, +0.0138]; "
        "+0.0116 runs/ball bowlers [95% CI: +0.0085, +0.0150]) due to high single-ball outcome variance, though consistently positive in all 5/5 folds.",
        "pink",
    )
with l2:
    render_insight_card(
        "Sample Uncertainty & Missing Covariates",
        "1. Moderate-volume players (Jurel 283 BF, Pant 266 BF, Malik 170 balls, Nawaz 175 balls) show higher rank sensitivity at CPI &ge; 0.70.<br>"
        "2. Ball-level dew, pitch moisture, boundary dimensions, and reliable speed-gun values are absent from the source dataset.<br>"
        "3. The 70/30 format blend is a domain-chosen weighting, not an empirically fitted regression parameter.",
        "teal",
    )

render_footer(mode)
