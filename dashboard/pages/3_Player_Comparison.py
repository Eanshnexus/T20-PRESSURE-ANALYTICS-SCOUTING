"""
3_Player_Comparison.py — PAGE 4: HEAD-TO-HEAD PLAYER COMPARISON
Compare 2 or 3 Batters or Bowlers side-by-side with normalized radar charts, KPI cards,
comparison bars, and scatter overlays. Strictly separates Batting and Bowling disciplines.
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Player Comparison | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
    render_kpi_card,
    render_section_header,
    render_metric_glossary,
    render_footer,
)
from components.charts import make_radar_chart, style_plotly_fig
from utils.data_loader import get_active_data
from utils.formatting import PALETTE, fmt_num
from utils.calculations import normalize_for_radar

mode = render_sidebar_and_mode()
data = get_active_data()

render_page_banner(
    title="Head-to-Head Player Comparison",
    subtitle="Compare 2 or 3 Qualifying Batters or Bowlers Side-by-Side Across Pressure Impact, Format Exposure & Reliability",
    image_name="cricket_pitch_ball.jpg",
    accent=PALETTE["gold"],
)

discipline = st.radio(
    "Select Comparison Discipline",
    ["Batters Comparison", "Bowlers Comparison"],
    horizontal=True,
    key="comp_discipline",
)

if discipline == "Batters Comparison":
    pool = data["elig_bat"].sort_values("Global_Rank").reset_index(drop=True)
    id_map = {int(r["striker_id"]): f"#{int(r['Global_Rank'])} {r['name']} ({r['team']}, ID {int(r['striker_id'])})" for _, r in pool.iterrows()}
    default_ids = [int(x) for x in pool["striker_id"].head(3).tolist()]
    sel_ids = st.multiselect(
        "Choose 2 or 3 Batters to Compare",
        options=list(id_map.keys()),
        default=default_ids,
        max_selections=3,
        format_func=lambda x: id_map[x],
        key="comp_bat_ids",
    )

    if len(sel_ids) < 2:
        st.warning("Please select **at least 2 batters** (up to 3) to generate side-by-side comparisons.")
    else:
        sub = pool[pool["striker_id"].isin(sel_ids)].copy()
        sub["order"] = sub["striker_id"].map({pid: i for i, pid in enumerate(sel_ids)})
        sub = sub.sort_values("order").reset_index(drop=True)

        # Side-by-Side KPI Cards
        render_section_header("Side-by-Side Batting Scorecard", accent="pink")
        cols = st.columns(len(sub))
        accents = ["pink", "teal", "gold"]
        for i, (_, r) in enumerate(sub.iterrows()):
            with cols[i]:
                render_kpi_card(
                    f"#{int(r['Global_Rank'])} {r['name']} (ID {int(r['striker_id'])})",
                    f"{r['auction_rating']:.1f}",
                    f"P-Score: {r['pressure_impact_score']:.1f} • HP SR: {r['hp_sr']:.1f} • RAA: {r['hp_raa']:+.1f} • Cons: {r['consistency_pct']:.1f}% • {int(r['hp_bf'])} HP BF",
                    accent=accents[i % 3],
                )

        # Radar & Comparison Bars
        ch1, ch2 = st.columns(2)
        with ch1:
            # Transparent pool-based 0-100 min-max normalization
            categories = ["Auction Rating", "Pressure Impact (P)", "HP Strike Rate", "RAA / 100", "Consistency (%)", "Pressure Volume"]
            norm_bounds = {
                "auction_rating": (float(pool["auction_rating"].min()), float(pool["auction_rating"].max())),
                "pressure_impact_score": (float(pool["pressure_impact_score"].min()), float(pool["pressure_impact_score"].max())),
                "hp_sr": (float(pool["hp_sr"].min()), float(pool["hp_sr"].max())),
                "hp_raa_per_100": (float(pool["hp_raa_per_100"].min()), float(pool["hp_raa_per_100"].max())),
                "consistency_pct": (0.0, 100.0),
                "hp_bf": (120.0, float(pool["hp_bf"].max())),
            }
            radar_players = []
            for _, r in sub.iterrows():
                vals = [
                    float(normalize_for_radar([r["auction_rating"]], bounds=norm_bounds["auction_rating"])[0]),
                    float(normalize_for_radar([r["pressure_impact_score"]], bounds=norm_bounds["pressure_impact_score"])[0]),
                    float(normalize_for_radar([r["hp_sr"]], bounds=norm_bounds["hp_sr"])[0]),
                    float(normalize_for_radar([r["hp_raa_per_100"]], bounds=norm_bounds["hp_raa_per_100"])[0]),
                    float(normalize_for_radar([r["consistency_pct"]], bounds=norm_bounds["consistency_pct"])[0]),
                    float(normalize_for_radar([r["hp_bf"]], bounds=norm_bounds["hp_bf"])[0]),
                ]
                raws = [
                    f"{r['auction_rating']:.1f}", f"{r['pressure_impact_score']:.1f}", f"{r['hp_sr']:.1f}",
                    f"{r['hp_raa_per_100']:+.1f}/100", f"{r['consistency_pct']:.1f}%", f"{int(r['hp_bf'])} BF"
                ]
                radar_players.append({"name": r["name"], "values": vals, "raw_labels": raws})
            st.plotly_chart(make_radar_chart(radar_players, categories, "Normalized Multi-Metric Profile (0–100 Across Qualifying Pool)"), width='stretch')
            st.caption("Radar Scale Note: Each axis is min-max normalized (0–100) relative to the full qualifying batter pool (>=120 HP BF). Hover points to inspect exact raw metrics.")

        with ch2:
            fig_bar = go.Figure()
            bar_colors = [PALETTE["pink"], PALETTE["teal"], PALETTE["gold"]]
            for i, (_, r) in enumerate(sub.iterrows()):
                fig_bar.add_trace(
                    go.Bar(
                        name=r["name"],
                        x=["IPL HP BF", "T20I HP BF", "Other T20 BF"],
                        y=[int(r["ipl_bf"]), int(r["t20i_bf"]), int(r["other_t20_bf"])],
                        marker_color=bar_colors[i % 3],
                        text=[int(r["ipl_bf"]), int(r["t20i_bf"]), int(r["other_t20_bf"])],
                        textposition="outside",
                    )
                )
            fig_bar.update_layout(barmode="group")
            style_plotly_fig(fig_bar, title="3-Way Format Sample Comparison (HP Balls Faced)", height=430)
            fig_bar.update_yaxes(title_text="High-Pressure Balls Faced")
            st.plotly_chart(fig_bar, width='stretch')

        # Detailed Comparison Table
        render_section_header("Exact Side-by-Side Metric Table", accent="gold")
        comp_tbl = pd.DataFrame({
            "Metric": [
                "Global Rank", "Player ID", "Primary Team", "Verified Auction Rating", "Pressure Impact Score (P)",
                "Ordinary Performance Score", "Pressure Strike Rate", "Runs Above Expectation (RAA)",
                "Dismissal Equity (WAA)", "Match Consistency (%)", "High-Pressure Balls Faced",
                "IPL HP BF (Raw RAA)", "T20I HP BF (Raw RAA)", "Other T20 HP BF (Raw RAA)"
            ],
            **{
                r["name"]: [
                    f"#{int(r['Global_Rank'])}", str(int(r["striker_id"])), r["team"], f"{r['auction_rating']:.1f}",
                    f"{r['pressure_impact_score']:.1f}", f"{r['ord_score']:.1f}", f"{r['hp_sr']:.1f}",
                    fmt_num(r["hp_raa"], 1, signed=True), fmt_num(r["hp_waa"], 2, signed=True),
                    f"{r['consistency_pct']:.1f}%", f"{int(r['hp_bf'])}",
                    f"{int(r['ipl_bf'])} ({r['ipl_raa']:+.1f})", f"{int(r['t20i_bf'])} ({r['t20i_raa']:+.1f})",
                    f"{int(r['other_t20_bf'])} ({r['other_t20_raa']:+.1f})",
                ]
                for _, r in sub.iterrows()
            }
        })
        st.dataframe(comp_tbl, width='stretch', hide_index=True)

else:
    pool = data["elig_bowl"].sort_values("Global_Rank").reset_index(drop=True)
    id_map = {int(r["bowler_id"]): f"#{int(r['Global_Rank'])} {r['name']} ({r['team']}, ID {int(r['bowler_id'])})" for _, r in pool.iterrows()}
    default_ids = [int(x) for x in pool["bowler_id"].head(3).tolist()]
    sel_ids = st.multiselect(
        "Choose 2 or 3 Bowlers to Compare",
        options=list(id_map.keys()),
        default=default_ids,
        max_selections=3,
        format_func=lambda x: id_map[x],
        key="comp_bowl_ids",
    )

    if len(sel_ids) < 2:
        st.warning("Please select **at least 2 bowlers** (up to 3) to generate side-by-side comparisons.")
    else:
        sub = pool[pool["bowler_id"].isin(sel_ids)].copy()
        sub["order"] = sub["bowler_id"].map({pid: i for i, pid in enumerate(sel_ids)})
        sub = sub.sort_values("order").reset_index(drop=True)

        render_section_header("Side-by-Side Bowling Scorecard", accent="teal")
        cols = st.columns(len(sub))
        accents = ["teal", "pink", "gold"]
        for i, (_, r) in enumerate(sub.iterrows()):
            with cols[i]:
                render_kpi_card(
                    f"#{int(r['Global_Rank'])} {r['name']} (ID {int(r['bowler_id'])})",
                    f"{r['auction_rating']:.1f}",
                    f"P-Score: {r['pressure_impact_score']:.1f} • Econ: {r['hp_econ']:.2f} • RPA: {r['hp_rpa']:+.1f} • Wkts: {int(r['hp_wkts'])} • {int(r['hp_balls'])} Bls",
                    accent=accents[i % 3],
                )

        ch1, ch2 = st.columns(2)
        with ch1:
            categories = ["Auction Rating", "Pressure Impact (P)", "Economy Control", "RPA / 6", "Consistency (%)", "Pressure Volume"]
            norm_bounds = {
                "auction_rating": (float(pool["auction_rating"].min()), float(pool["auction_rating"].max())),
                "pressure_impact_score": (float(pool["pressure_impact_score"].min()), float(pool["pressure_impact_score"].max())),
                "hp_econ": (float(pool["hp_econ"].min()), float(pool["hp_econ"].max())),
                "hp_rpa_per_6": (float(pool["hp_rpa_per_6"].min()), float(pool["hp_rpa_per_6"].max())),
                "consistency_pct": (0.0, 100.0),
                "hp_balls": (150.0, float(pool["hp_balls"].max())),
            }
            radar_players = []
            for _, r in sub.iterrows():
                vals = [
                    float(normalize_for_radar([r["auction_rating"]], bounds=norm_bounds["auction_rating"])[0]),
                    float(normalize_for_radar([r["pressure_impact_score"]], bounds=norm_bounds["pressure_impact_score"])[0]),
                    float(normalize_for_radar([r["hp_econ"]], lower_is_better=True, bounds=norm_bounds["hp_econ"])[0]),
                    float(normalize_for_radar([r["hp_rpa_per_6"]], bounds=norm_bounds["hp_rpa_per_6"])[0]),
                    float(normalize_for_radar([r["consistency_pct"]], bounds=norm_bounds["consistency_pct"])[0]),
                    float(normalize_for_radar([r["hp_balls"]], bounds=norm_bounds["hp_balls"])[0]),
                ]
                raws = [
                    f"{r['auction_rating']:.1f}", f"{r['pressure_impact_score']:.1f}", f"{r['hp_econ']:.2f} RPO (lower=better)",
                    f"{r['hp_rpa_per_6']:+.2f}/6", f"{r['consistency_pct']:.1f}%", f"{int(r['hp_balls'])} Balls"
                ]
                radar_players.append({"name": r["name"], "values": vals, "raw_labels": raws})
            st.plotly_chart(make_radar_chart(radar_players, categories, "Normalized Multi-Metric Profile (0–100 Across Qualifying Pool)"), width='stretch')
            st.caption("Radar Scale Note: Economy Control is inverted so lower pressure economy plots closer to 100. Hover points for exact raw metrics.")

        with ch2:
            fig_bar = go.Figure()
            bar_colors = [PALETTE["teal"], PALETTE["pink"], PALETTE["gold"]]
            for i, (_, r) in enumerate(sub.iterrows()):
                fig_bar.add_trace(
                    go.Bar(
                        name=r["name"],
                        x=["IPL HP Balls", "T20I HP Balls", "Other T20 Balls"],
                        y=[int(r["ipl_balls"]), int(r["t20i_balls"]), int(r["other_t20_balls"])],
                        marker_color=bar_colors[i % 3],
                        text=[int(r["ipl_balls"]), int(r["t20i_balls"]), int(r["other_t20_balls"])],
                        textposition="outside",
                    )
                )
            fig_bar.update_layout(barmode="group")
            style_plotly_fig(fig_bar, title="3-Way Format Sample Comparison (HP Legal Balls)", height=430)
            fig_bar.update_yaxes(title_text="High-Pressure Legal Balls Bowled")
            st.plotly_chart(fig_bar, width='stretch')

        render_section_header("Exact Side-by-Side Metric Table", accent="gold")
        comp_tbl = pd.DataFrame({
            "Metric": [
                "Global Rank", "Player ID", "Primary Team", "Verified Auction Rating", "Pressure Impact Score (P)",
                "Ordinary Performance Score", "Pressure Economy (RPO)", "Dot-Ball Percentage",
                "Pressure Wickets", "Runs Prevented (RPA)", "Wickets Above Exp (WAA)",
                "Match Consistency (%)", "High-Pressure Legal Balls",
                "IPL HP Balls (Raw RPA)", "T20I HP Balls (Raw RPA)", "Other T20 Balls (Raw RPA)"
            ],
            **{
                r["name"]: [
                    f"#{int(r['Global_Rank'])}", str(int(r["bowler_id"])), r["team"], f"{r['auction_rating']:.1f}",
                    f"{r['pressure_impact_score']:.1f}", f"{r['ord_score']:.1f}", f"{r['hp_econ']:.2f}",
                    f"{r['hp_dot_pct']:.1f}%", str(int(r["hp_wkts"])),
                    fmt_num(r["hp_rpa"], 1, signed=True), fmt_num(r["hp_waa"], 2, signed=True),
                    f"{r['consistency_pct']:.1f}%", f"{int(r['hp_balls'])}",
                    f"{int(r['ipl_balls'])} ({r['ipl_rpa']:+.1f})", f"{int(r['t20i_balls'])} ({r['t20i_rpa']:+.1f})",
                    f"{int(r['other_t20_balls'])} ({r['other_t20_rpa']:+.1f})",
                ]
                for _, r in sub.iterrows()
            }
        })
        st.dataframe(comp_tbl, width='stretch', hide_index=True)

render_metric_glossary(["Auction Rating", "Pressure Impact Score", "Runs Above Expectation (RAA)", "Runs Prevented Above Expectation (RPA)", "Pressure Strike Rate", "Pressure Economy", "Match Consistency"])
render_footer(mode)
