"""
2_Bowler_Analytics.py — PAGE 3: BOWLER ANALYTICS
Interactive bowling leaderboard, dynamic filters, verified Global Top 10, and 10-part bowler profile.
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Bowler Analytics | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
    render_kpi_card,
    render_section_header,
    render_metric_glossary,
    render_footer,
)
from components.charts import make_impact_vs_volume_scatter, style_plotly_fig
from components.player_profiles import render_bowler_profile
from components.tables import render_clean_table
from utils.data_loader import get_active_data
from utils.formatting import PALETTE

mode = render_sidebar_and_mode()
data = get_active_data()

render_page_banner(
    title="Bowler Pressure Analytics",
    subtitle="Official Global Top 10 Bowling Leaderboard, Qualifying Pool Explorer & 10-Point Defensive Profiles",
    image_name="bowling_action.jpg",
    accent=PALETTE["teal"],
)

top10 = data["top10_bowl"].copy()
elig = data["elig_bowl"].copy()

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("#1 Pressure Bowler", top10.iloc[0]["Player name"], f"Rating: {top10.iloc[0]['Auction Rating']:.1f} • ID {int(top10.iloc[0]['Player ID'])}", "gold")
with k2:
    render_kpi_card("Top 10 Avg HP Econ", f"{top10['Pressure economy'].mean():.2f}", "Runs conceded per over (lower is better)", "teal")
with k3:
    render_kpi_card("Qualifying Bowler Pool", f"{len(elig):,}", "Minimum >=150 HP legal balls bowled", "pink")
with k4:
    render_kpi_card("Highest Top-10 RPA", f"+{top10['Runs prevented above expectation'].max():.1f}", f"{top10.loc[top10['Runs prevented above expectation'].idxmax(), 'Player name']}", "gold")

tab_top10, tab_ipl_view, tab_pool = st.tabs([
    "Official Global Top 10 Bowlers",
    "Separate IPL-Relevant Top 10 (Scouting View)",
    "Interactive Full Qualifying Pool (111 Bowlers)",
])

with tab_top10:
    render_section_header("Official Global Top 10 Bowlers (Verified Final CSV)", accent="gold")
    display_top10 = pd.DataFrame({
        "Global Rank": top10["Rank"],
        "Player Name": top10["Player name"],
        "Player ID": top10["Player ID"],
        "Primary Team": top10["Primary team/affiliation"],
        "Auction Rating": top10["Auction Rating"],
        "Pressure Impact (P)": top10["Pressure impact score"],
        "HP Balls": top10["Pressure legal balls"],
        "HP Econ": top10["Pressure economy"],
        "Dot %": top10["Dot-ball percentage"],
        "Wkts": top10["Wickets"],
        "RPA": top10["Runs prevented above expectation"],
        "WAA": top10["Wickets above expectation"],
        "Consistency": top10["Match consistency"],
        "IPL Bls": top10["ipl_balls"].astype(int),
        "T20I Bls": top10["t20i_balls"].astype(int),
        "Other T20 Bls": top10["other_t20_balls"].astype(int),
        "Stability": top10["Ranking stability"],
    })
    render_clean_table(display_top10, height=395)
    st.caption(
        "Note: Global rankings objectively preserve all nationalities across the full supplied dataset. "
        "Ranks #3–#5 and #10 have 0 genuine IPL balls; Sufiyan Muqeem's 65 Emerging/Rising Stars Asia Cup deliveries are classified strictly as Other T20."
    )

with tab_ipl_view:
    render_section_header("Separate IPL-Relevant Top 10 Bowlers (Secondary Scouting View)", accent="teal")
    st.info(
        "**Secondary View Notice:** Does NOT replace the primary Global Top 10. Screens for practical IPL recruitment availability "
        "based on historical IPL participation precedent since 2008. Distinct from confirmed IPL 2027 auction release/retention status."
    )
    render_clean_table(data["top10_bowl_ipl"], height=395)

with tab_pool:
    render_section_header("Search & Filter Qualifying Bowlers (Original Global Rank Preserved)", accent="teal")
    if st.button("Reset Bowler Filters", key="reset_bowl_filters"):
        for k in ["bowl_search", "bowl_rating_rng", "bowl_min_balls", "bowl_fmt_filter", "bowl_role_filter", "bowl_sort_by"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    fc1, fc2, fc3, fc4, fc5 = st.columns([1.4, 1.2, 1.1, 1.1, 1.1])
    with fc1:
        search_q = st.text_input("Search Bowler or Team", placeholder="e.g. Bumrah, Narine, CSK...", key="bowl_search")
    with fc2:
        r_min, r_max = float(elig["auction_rating"].min()), float(elig["auction_rating"].max())
        rating_rng = st.slider("Auction Rating Range", min_value=round(r_min, 1), max_value=round(r_max, 1), value=(round(r_min, 1), round(r_max, 1)), key="bowl_rating_rng")
    with fc3:
        min_b = st.slider("Min Pressure Legal Balls", min_value=150, max_value=int(elig["hp_balls"].max()), value=150, step=15, key="bowl_min_balls")
    with fc4:
        fmt_choice = st.selectbox("Competition Exposure", ["All Qualifying", "Has IPL (>=60 HP Balls)", "Has T20I (>=60 HP Balls)", "Both IPL & T20I", "Has Other T20"], key="bowl_fmt_filter")
    with fc5:
        role_opts = ["All Roles"] + sorted([r for r in elig["inferred_bowling_role"].dropna().unique().tolist()])
        role_choice = st.selectbox("Bowling Role", role_opts, key="bowl_role_filter")

    filtered = elig.copy()
    if search_q.strip():
        q = search_q.strip().lower()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(q, na=False)
            | filtered["team"].str.lower().str.contains(q, na=False)
            | filtered["bowler_id"].astype(str).str.contains(q, na=False)
        ]
    filtered = filtered[(filtered["auction_rating"] >= rating_rng[0]) & (filtered["auction_rating"] <= rating_rng[1])]
    filtered = filtered[filtered["hp_balls"] >= min_b]
    if fmt_choice == "Has IPL (>=60 HP Balls)":
        filtered = filtered[filtered["ipl_balls"] >= 60]
    elif fmt_choice == "Has T20I (>=60 HP Balls)":
        filtered = filtered[filtered["t20i_balls"] >= 60]
    elif fmt_choice == "Both IPL & T20I":
        filtered = filtered[(filtered["ipl_balls"] >= 60) & (filtered["t20i_balls"] >= 60)]
    elif fmt_choice == "Has Other T20":
        filtered = filtered[filtered["other_t20_balls"] > 0]
    if role_choice != "All Roles":
        filtered = filtered[filtered["inferred_bowling_role"] == role_choice]

    sort_col_map = {
        "Original Global Rank (Auction Rating)": ("auction_rating", False),
        "Pressure Impact Score (P)": ("pressure_impact_score", False),
        "Runs Prevented Above Expectation (RPA)": ("hp_rpa", False),
        "Pressure Economy (Lowest First)": ("hp_econ", True),
        "Pressure Wickets": ("hp_wkts", False),
        "Match Consistency (%)": ("consistency_pct", False),
    }
    sort_label = st.selectbox("Sort Filtered View By", list(sort_col_map.keys()), key="bowl_sort_by")
    scol, sasc = sort_col_map[sort_label]
    filtered = filtered.sort_values(scol, ascending=sasc).reset_index(drop=True)

    is_filtered_view = (len(filtered) != len(elig)) or (sort_label != "Original Global Rank (Auction Rating)")
    if len(filtered) == 0:
        st.warning("No bowlers match your current filters. Click **Reset Bowler Filters** above to restore the full pool.")
    else:
        if is_filtered_view:
            st.info(f"**Filtered View ({len(filtered)} of {len(elig)} qualifying bowlers):** Sorted by *{sort_label}*; authoritative **`Global Rank`** is preserved.")
        disp_pool = pd.DataFrame({
            "Filtered Pos": range(1, len(filtered) + 1),
            "Global Rank": filtered["Global_Rank"],
            "Player Name": filtered["name"],
            "Player ID": filtered["bowler_id"],
            "Primary Team": filtered["team"],
            "Role": filtered["inferred_bowling_role"].fillna("N/A"),
            "Auction Rating": filtered["auction_rating"].round(1),
            "Pressure Impact (P)": filtered["pressure_impact_score"].round(1),
            "HP Balls": filtered["hp_balls"].astype(int),
            "HP Econ": filtered["hp_econ"].round(2),
            "Wkts": filtered["hp_wkts"].astype(int),
            "RPA": filtered["hp_rpa"].round(1),
            "Consistency (%)": filtered["consistency_pct"].round(1),
            "IPL Bls": filtered["ipl_balls"].astype(int),
            "T20I Bls": filtered["t20i_balls"].astype(int),
            "Other T20 Bls": filtered["other_t20_balls"].astype(int),
        })
        render_clean_table(disp_pool, height=390)

# Visual Exploration: RPA vs Volume & Economy Pressure vs Ordinary
render_section_header("Bowling Defensive Landscape", accent="teal")
sc1, sc2 = st.columns(2)
with sc1:
    fig_vol = make_impact_vs_volume_scatter(
        elig, set(top10["Player ID"].tolist()),
        x_col="hp_balls", y_col="hp_rpa", name_col="name", id_col="bowler_id",
        threshold_x=150,
        title="Runs Prevented Above Expectation (RPA) vs High-Pressure Legal Balls",
        x_label="High-Pressure Legal Balls Bowled", y_label="Runs Prevented Above Expectation (RPA)",
        accent_color=PALETTE["teal"],
    )
    st.plotly_chart(fig_vol, width='stretch')

with sc2:
    fig_ec = go.Figure()
    fig_ec.add_trace(
        go.Scatter(
            x=top10["ord_econ"], y=top10["Pressure economy"],
            mode="markers+text",
            text=[n.split()[-1] for n in top10["Player name"]],
            textposition="top center",
            marker=dict(size=13, color=PALETTE["teal"], line=dict(width=2, color=PALETTE["gold"])),
            customdata=top10[["Player name", "Player ID", "Pressure uplift/deterioration"]].values,
            hovertemplate="<b>%{customdata[0]}</b> (ID: %{customdata[1]})<br>Ordinary Econ: %{x:.2f}<br>Pressure Econ: %{y:.2f}<br>Econ Saved (Ord-HP): %{customdata[2]:+.2f}<extra></extra>",
            name="Top 10 Bowlers",
        )
    )
    fig_ec.add_trace(
        go.Scatter(x=[4.5, 10.2], y=[4.5, 10.2], mode="lines", name="Equal Economy Line (Below = Tighter Under Pressure)",
                   line=dict(dash="dash", color="rgba(255,255,255,0.35)", width=1.5))
    )
    style_plotly_fig(fig_ec, title="Top 10 Bowlers: High-Pressure Economy vs Ordinary Economy", height=420)
    fig_ec.update_xaxes(title_text="Ordinary Situation Economy (RPO)")
    fig_ec.update_yaxes(title_text="High-Pressure Economy (RPO — Lower is Better)")
    st.plotly_chart(fig_ec, width='stretch')

# Detailed 10-Part Bowler Profile Selector
render_section_header("Interactive Bowler Scouting Profile", accent="teal")
elig_sorted = elig.sort_values("Global_Rank").reset_index(drop=True)
id_to_label = {
    int(r["bowler_id"]): f"#{int(r['Global_Rank'])} {r['name']} ({r['team']}) — ID: {int(r['bowler_id'])} | Rating: {r['auction_rating']:.1f}"
    for _, r in elig_sorted.iterrows()
}
selected_pid = st.selectbox(
    "Select a Qualifying Bowler to Inspect Full 10-Point Profile",
    options=list(id_to_label.keys()),
    format_func=lambda pid: id_to_label[pid],
    key="selected_bowler_pid",
)
sel_row = elig_sorted[elig_sorted["bowler_id"] == selected_pid].iloc[0]
render_bowler_profile(sel_row)

render_metric_glossary(["Auction Rating", "Pressure Impact Score", "Ordinary Performance Score", "Runs Prevented Above Expectation (RPA)", "Wickets Above Expectation (Bowling WAA)", "Pressure Economy", "Dot-Ball Percentage", "Match Consistency", "Ranking Stability"])
render_footer(mode)
