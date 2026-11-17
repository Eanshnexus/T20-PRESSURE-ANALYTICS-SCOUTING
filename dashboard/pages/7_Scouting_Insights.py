"""
7_Scouting_Insights.py — PAGE 8: SCOUTING & RECRUITMENT INSIGHTS
Translates verified statistical profiles into evidence-based cricketing roles using
observed batting order, phase ball-shares, and bowling style (never name/reputation).
Preserves global statistical rankings across all nationalities without exclusion.
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Scouting & Recruitment | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
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

render_page_banner(
    title="Scouting & Tactical Role Insights",
    subtitle="Evidence-Based Cricketing Role Classification Derived Strictly from Batting Order, Phase Ball Shares & Bowling Style",
    image_name="hero_stadium.jpg",
    accent=PALETTE["gold"],
)

st.info(
    "**Scouting & Eligibility Transparency Notice:** All role classifications below are derived strictly from empirical match evidence "
    "(median batting order, Powerplay/Middle/Death ball shares, and recorded pace/spin style) — never from player reputation. "
    "Global statistical rankings include players of every nationality. Recruitment considerations are strictly conditional on player availability, "
    "eligibility, retention rules, and squad requirements; no claims of confirmed IPL 2027 auction participation are made."
)

tab_bat_roles, tab_bowl_roles, tab_ar = st.tabs([
    "Batting Roles Under Pressure",
    "Bowling Roles Under Pressure",
    "Multi-Skill / All-Rounder Profiles",
])

with tab_bat_roles:
    render_section_header("Evidence-Based Batting Role Profiles (Qualifying Pool >=120 HP BF)", accent="pink")
    st.caption("Classification Criteria: Top-Order (median batting order <= 3), Finisher (Death share >= 45% or median order >= 5.5), Power Hitter (boundary % >= 22% & Death share >= 30%), Middle-Order (remaining batters).")

    eb = data["elig_bat"].copy()
    bat_roles = ["Top-Order Batter", "Middle-Order Batter", "Finisher", "Power Hitter"]
    role_counts = eb["inferred_batting_role"].value_counts()

    r_cols = st.columns(4)
    for i, rname in enumerate(bat_roles):
        sub_r = eb[eb["inferred_batting_role"] == rname].sort_values("Global_Rank")
        top_p = f"Leader: {sub_r.iloc[0]['name']} (#{int(sub_r.iloc[0]['Global_Rank'])}, {sub_r.iloc[0]['auction_rating']:.1f})" if len(sub_r) > 0 else "No qualifying players"
        with r_cols[i]:
            render_insight_card(f"{rname} ({int(role_counts.get(rname, 0))})", top_p, accent="pink" if i % 2 == 0 else "gold")

    sel_bat_role = st.selectbox("Filter Qualifying Batters by Inferred Role", ["All Roles"] + bat_roles, key="scout_bat_role")
    sub_b = eb if sel_bat_role == "All Roles" else eb[eb["inferred_batting_role"] == sel_bat_role]
    sub_b = sub_b.sort_values("Global_Rank").head(20)

    if len(sub_b) == 0:
        st.warning("No qualifying batters match this role category.")
    else:
        disp_b = pd.DataFrame({
            "Global Rank": sub_b["Global_Rank"],
            "Player Name": sub_b["name"],
            "Player ID": sub_b["striker_id"],
            "Team": sub_b["team"],
            "Inferred Role": sub_b["inferred_batting_role"],
            "Median Order": sub_b["median_batting_order"].round(1),
            "Death Share %": sub_b["death_share_pct"].round(1),
            "Auction Rating": sub_b["auction_rating"].round(1),
            "HP BF": sub_b["hp_bf"].astype(int),
            "HP SR": sub_b["hp_sr"].round(1),
            "RAA": sub_b["hp_raa"].round(1),
            "Consistency %": sub_b["consistency_pct"].round(1),
        })
        render_clean_table(disp_b, height=390)

        # Phase distribution chart for top 8 in role
        top_viz = sub_b.head(8)
        fig_pb = go.Figure()
        fig_pb.add_trace(go.Bar(name="Powerplay (1–6)", x=top_viz["name"], y=top_viz["pp_share_pct"], marker_color=PALETTE["teal"]))
        fig_pb.add_trace(go.Bar(name="Middle (7–15)", x=top_viz["name"], y=top_viz["mid_share_pct"], marker_color=PALETTE["gold"]))
        fig_pb.add_trace(go.Bar(name="Death (16–20)", x=top_viz["name"], y=top_viz["death_share_pct"], marker_color=PALETTE["pink"]))
        fig_pb.update_layout(barmode="stack")
        style_plotly_fig(fig_pb, title=f"Innings Phase Ball-Share Breakdown — Top Leaders ({sel_bat_role})", height=350)
        fig_pb.update_yaxes(title_text="Share of Total Balls Faced (%)", range=[0, 102])
        st.plotly_chart(fig_pb, width='stretch')

with tab_bowl_roles:
    render_section_header("Evidence-Based Bowling Role Profiles (Qualifying Pool >=150 HP Legal Balls)", accent="teal")
    st.caption("Classification Criteria: Spin Bowler (recorded pace_or_spin == Spin), Death-Over Specialist (Pace with Death share >= 38%), Powerplay Bowler (Pace with Powerplay share >= 42%), Middle-Over Specialist (remaining pace bowlers).")

    ebw = data["elig_bowl"].copy()
    bowl_roles = ["Spin Bowler", "Death-Over Specialist", "Powerplay Bowler", "Middle-Over Specialist"]
    b_counts = ebw["inferred_bowling_role"].value_counts()

    r_cols = st.columns(4)
    for i, rname in enumerate(bowl_roles):
        sub_r = ebw[ebw["inferred_bowling_role"] == rname].sort_values("Global_Rank")
        top_p = f"Leader: {sub_r.iloc[0]['name']} (#{int(sub_r.iloc[0]['Global_Rank'])}, {sub_r.iloc[0]['auction_rating']:.1f})" if len(sub_r) > 0 else "No qualifying players"
        with r_cols[i]:
            render_insight_card(f"{rname} ({int(b_counts.get(rname, 0))})", top_p, accent="teal" if i % 2 == 0 else "gold")

    sel_bowl_role = st.selectbox("Filter Qualifying Bowlers by Inferred Role", ["All Roles"] + bowl_roles, key="scout_bowl_role")
    sub_bw = ebw if sel_bowl_role == "All Roles" else ebw[ebw["inferred_bowling_role"] == sel_bowl_role]
    sub_bw = sub_bw.sort_values("Global_Rank").head(20)

    if len(sub_bw) == 0:
        st.warning("No qualifying bowlers match this role category.")
    else:
        disp_bw = pd.DataFrame({
            "Global Rank": sub_bw["Global_Rank"],
            "Player Name": sub_bw["name"],
            "Player ID": sub_bw["bowler_id"],
            "Team": sub_bw["team"],
            "Inferred Role": sub_bw["inferred_bowling_role"],
            "Style": sub_bw["primary_style"],
            "Death Share %": sub_bw["death_share_pct"].round(1),
            "Auction Rating": sub_bw["auction_rating"].round(1),
            "HP Balls": sub_bw["hp_balls"].astype(int),
            "HP Econ": sub_bw["hp_econ"].round(2),
            "RPA": sub_bw["hp_rpa"].round(1),
            "Wkts": sub_bw["hp_wkts"].astype(int),
            "IPL HP Balls": sub_bw["ipl_balls"].astype(int),
        })
        render_clean_table(disp_bw, height=390)

        top_viz = sub_bw.head(8)
        fig_pbw = go.Figure()
        fig_pbw.add_trace(go.Bar(name="Powerplay (1–6)", x=top_viz["name"], y=top_viz["pp_share_pct"], marker_color=PALETTE["gold"]))
        fig_pbw.add_trace(go.Bar(name="Middle (7–15)", x=top_viz["name"], y=top_viz["mid_share_pct"], marker_color=PALETTE["teal"]))
        fig_pbw.add_trace(go.Bar(name="Death (16–20)", x=top_viz["name"], y=top_viz["death_share_pct"], marker_color=PALETTE["pink"]))
        fig_pbw.update_layout(barmode="stack")
        style_plotly_fig(fig_pbw, title=f"Innings Phase Workload Breakdown — Top Leaders ({sel_bowl_role})", height=350)
        fig_pbw.update_yaxes(title_text="Share of Legal Balls Bowled (%)", range=[0, 102])
        st.plotly_chart(fig_pbw, width='stretch')

with tab_ar:
    render_section_header("Dual-Discipline High-Pressure All-Rounders", accent="gold")
    comb = data["combined"]
    if len(comb) > 0 and "Is_AllRounder" in comb.columns:
        ar_df = comb[comb["Is_AllRounder"] == True].sort_values("Combined_Pressure_Value", ascending=False).head(15)
        st.caption("Players appearing with meaningful pressure exposure across both batting and bowling disciplines in `combined_player_analysis.csv`.")
        render_clean_table(ar_df, height=380)
    else:
        # In Public Demo Mode, show intersection or informative note
        st.info("In Public Demo Mode, batting and bowling demo pools are generated independently. Switch to Local Competition Mode to inspect the 160-player combined all-rounder index.")

render_section_header("Evidence-Based Recruitment Considerations (Conditional on Availability)", accent="pink")
c1, c2 = st.columns(2)
with c1:
    render_insight_card(
        "Batting Considerations (Role Fit & Sample Caveats)",
        "• <strong>High-Volume Pressure Anchors/Finishers:</strong> Suryakumar Yadav (453 HP BF), Tristan Stubbs (529 HP BF, +12.48 WAA), "
        "Tilak Varma (675 HP BF, +12.69 WAA), and Tim David (680 HP BF, +15.65 WAA) combine elite scoring with large multi-season samples.<br>"
        "• <strong>Moderate-Volume Domestic Finishers:</strong> Dhruv Jurel (283 HP BF, 70.4% consistency), Ashutosh Sharma (283 HP BF), "
        "and Naman Dhir (209 HP BF) show strong pressure strike rates but carry wider rank uncertainty under strict CPI &ge; 0.70 cutoffs.",
        "pink",
    )
with c2:
    render_insight_card(
        "Bowling Considerations (Format Exposure & Uncertainty)",
        "• <strong>Proven High-Volume IPL + T20I Benchmarks:</strong> Sunil Narine (376 IPL balls), Jasprit Bumrah (404 IPL / 193 T20I), "
        "and Matheesha Pathirana (422 IPL / 180 T20I) provide the deepest demonstrated IPL pressure records.<br>"
        "• <strong>Spin Control & Domestic Depth:</strong> Mitchell Santner (92 IPL / 319 T20I), Kuldeep Yadav (385 IPL / 140 T20I), and "
        "Mohsin Khan (167 IPL) offer verified IPL pressure records, whereas Akeal Hosein (29 IPL / 157 T20I) and international-only stars "
        "carry limited or zero IPL sample.",
        "teal",
    )

render_footer(mode)
