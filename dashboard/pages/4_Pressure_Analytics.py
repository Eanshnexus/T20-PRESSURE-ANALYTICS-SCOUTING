"""
4_Pressure_Analytics.py — PAGE 5: PRESSURE ANALYTICS
Explains high-pressure T20 situations, provides a live interactive pre-delivery CPI simulator,
and displays verified aggregate distributions by over, innings, match state, format, and knockout stakes.
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Pressure Analytics | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
    render_kpi_card,
    render_section_header,
    render_insight_card,
    render_metric_glossary,
    render_footer,
)
from components.charts import (
    make_cpi_histogram,
    make_over_pressure_chart,
    make_chase_heatmap,
    style_plotly_fig,
)
from utils.data_loader import get_active_data
from utils.calculations import compute_live_cpi
from utils.formatting import PALETTE

mode = render_sidebar_and_mode()
data = get_active_data()
agg = data["pressure_agg"]
kpis = agg["kpis"]

render_page_banner(
    title="Pre-Delivery Pressure Analytics (CPI)",
    subtitle="Quantifying High-Leverage T20 Match States Strictly Prior to Ball Release — Zero Outcome Leakage",
    image_name="tactical_analytics_bg.jpg",
    accent=PALETTE["pink"],
)

# Summary KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("High Pressure (>=0.60)", f"{kpis['hp_deliveries']:,}", f"{kpis['hp_pct']:.2f}% of all contested balls", "pink")
with c2:
    render_kpi_card("Medium Pressure (0.35–0.60)", f"{kpis['med_deliveries']:,}", f"{kpis['med_deliveries']/kpis['total_deliveries']*100:.2f}% of deliveries", "gold")
with c3:
    render_kpi_card("Low / Ordinary (<0.35)", f"{kpis['low_deliveries']:,}", f"{kpis['low_deliveries']/kpis['total_deliveries']*100:.2f}% of deliveries", "teal")
with c4:
    render_kpi_card("Model A vs B Agreement", "86.40%", "Jaccard 0.591 • Cohen's Kappa 0.651", "gold")

# Interactive Live Pre-Delivery CPI Simulator
render_section_header("Interactive Pre-Delivery CPI Scenario Simulator", accent="gold")
st.caption("Adjust pre-delivery match state below to compute the exact Composite Pressure Index (Model B) used in the official rankings.")

sim_left, sim_right = st.columns([1.4, 1.0])
with sim_left:
    s1, s2, s3 = st.columns(3)
    with s1:
        sim_inn = st.selectbox("Innings", [2, 1], format_func=lambda x: "2nd Innings (Chase)" if x == 2 else "1st Innings (Target Setting)", key="sim_inn")
        sim_ko = st.checkbox("Knockout Match (1.15× Stakes)", value=False, key="sim_ko")
        sim_so = st.checkbox("Super Over (CPI = 1.00)", value=False, key="sim_so")
    with s2:
        sim_over = st.slider("Over Number", min_value=1, max_value=20, value=18, key="sim_over")
        sim_wkts = st.slider("Wickets in Hand", min_value=1, max_value=10, value=4, key="sim_wkts")
    with s3:
        if sim_inn == 2:
            sim_rrr = st.slider("Required Run Rate (RRR)", min_value=3.0, max_value=24.0, value=12.0, step=0.5, key="sim_rrr")
            sim_crr = st.slider("Current Run Rate (CRR)", min_value=3.0, max_value=15.0, value=8.5, step=0.5, key="sim_crr")
        else:
            sim_rrr, sim_crr = 9.0, 8.0
            st.info("1st Innings CPI depends on innings progression (balls bowled), wickets remaining, death phase (overs 16–20), and early collapse crisis.")

res = compute_live_cpi(sim_inn, sim_over, sim_wkts, sim_rrr, sim_crr, sim_ko, sim_so)
with sim_right:
    cat_color = PALETTE["pink"] if res["category"] == "High Pressure" else (PALETTE["gold"] if res["category"] == "Medium Pressure" else PALETTE["teal"])
    runs_needed_est = int(round(sim_rrr * res["balls_remaining"] / 6.0)) if sim_inn == 2 else None
    chase_line = f"Est. Runs Needed: <strong>{runs_needed_est}</strong> off <strong>{res['balls_remaining']}</strong> balls" if runs_needed_est is not None else f"Balls Remaining: <strong>{res['balls_remaining']}</strong>"
    st.markdown(
        f"""
        <div class="profile-card" style="border-color:{cat_color};text-align:center;padding:1.4rem;">
            <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#A7AEC0;">Computed Pre-Delivery CPI</div>
            <div style="font-family:'Outfit',sans-serif;font-size:3.1rem;font-weight:800;color:{cat_color};line-height:1.1;margin:6px 0;">{res['cpi']:.3f}</div>
            <div style="display:inline-block;padding:0.25rem 0.85rem;border-radius:999px;background:rgba(255,255,255,0.08);color:{cat_color};font-weight:700;font-size:0.86rem;margin-bottom:10px;">
                {res['category']}
            </div>
            <div style="font-size:0.82rem;color:#CBD5E1;">
                Base CPI: <strong>{res['cpi_base']:.3f}</strong> &nbsp;|&nbsp; Stakes Multiplier: <strong>{res['stakes_multiplier']:.2f}×</strong><br>
                {chase_line}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Interactive Visualizations from Verified Aggregates
render_section_header("Pressure Distributions Across Overs, Innings & Match Situations", accent="pink")
v1, v2 = st.columns(2)
with v1:
    st.plotly_chart(make_cpi_histogram(agg["cpi_hist"]), width='stretch')
with v2:
    st.plotly_chart(make_over_pressure_chart(agg["by_over_innings"]), width='stretch')

v3, v4 = st.columns(2)
with v3:
    st.plotly_chart(make_chase_heatmap(agg["chase_heatmap"]), width='stretch')
with v4:
    # Pressure by 3-Way Format & Phase
    fpdf = pd.DataFrame(agg["by_format_phase"])
    phase_order = ["Powerplay", "Middle", "Death"]
    fig_fp = go.Figure()
    for cat, color in [("IPL", PALETTE["pink"]), ("International T20I", PALETTE["teal"]), ("Other T20", PALETTE["gold"])]:
        sub = fpdf[fpdf["comp_category"] == cat].set_index("innings_phase").reindex(phase_order).reset_index()
        fig_fp.add_trace(
            go.Bar(
                name=cat, x=sub["innings_phase"], y=sub["hp_pct"],
                marker_color=color,
                text=[f"{v:.1f}%" for v in sub["hp_pct"]],
                textposition="outside",
            )
        )
    fig_fp.update_layout(barmode="group")
    style_plotly_fig(fig_fp, title="High-Pressure Delivery Share (%) by Phase & 3-Way Format", height=390)
    fig_fp.update_yaxes(title_text="High-Pressure Share (%)", range=[0, 100])
    st.plotly_chart(fig_fp, width='stretch')

# Knockout & Model Architecture Explanation
render_section_header("Knockout Stakes & Dual Model Architecture", accent="teal")
ko_df = pd.DataFrame(agg["by_knockout"])
e1, e2 = st.columns(2)
with e1:
    ko_row = ko_df[ko_df["is_knockout"] == True].iloc[0]
    lg_row = ko_df[ko_df["is_knockout"] == False].iloc[0]
    render_insight_card(
        "Knockout Match Stakes Modifier (1.15×)",
        f"In knockout matches ({int(ko_row['deliveries']):,} deliveries), applying a 1.15× stakes multiplier increases mean CPI to "
        f"<strong>{ko_row['mean_cpi']:.4f}</strong> (vs <strong>{lg_row['mean_cpi']:.4f}</strong> in league/group games) and raises High-Pressure "
        f"classification to <strong>{ko_row['hp_pct']:.2f}%</strong> (vs {lg_row['hp_pct']:.2f}%). Sensitivity checks confirm removing this modifier "
        f"retains <strong>99.64%</strong> delivery agreement and rank correlation <strong>&rho; &ge; 0.994</strong>.",
        "gold",
    )
with e2:
    render_insight_card(
        "Model B (Continuous CPI) vs Model A (Rule-Based Benchmark)",
        "Official rankings use <strong>exclusively Model B (Continuous CPI &ge; 0.60)</strong>. Model A (discrete cricket rules for high RRR, "
        "death finishes, and wicket collapses) serves strictly as an independent sensitivity benchmark (86.40% agreement, Cohen's Kappa = 0.651). "
        "Note on collinearity: In Innings 2, RRR and (RRR − CRR) correlate at r = 0.9786; dropping the acceleration term maintains 99.11% delivery agreement (&rho; &ge; 0.9895).",
        "teal",
    )

render_metric_glossary(["CPI", "Pressure Impact Score", "Ranking Stability"])
render_footer(mode)
