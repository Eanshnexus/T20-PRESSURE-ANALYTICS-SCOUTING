"""
1_Batter_Analytics.py — PAGE 2: BATTER ANALYTICS
Interactive batting leaderboard, dynamic filters, verified Global Top 10, and 10-part player profile.
"""
import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Batter Analytics | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
    render_kpi_card,
    render_section_header,
    render_metric_glossary,
    render_footer,
)
from components.charts import make_impact_vs_volume_scatter, style_plotly_fig
from components.player_profiles import render_batter_profile
from components.tables import render_clean_table
from utils.data_loader import get_active_data
from utils.formatting import PALETTE
import plotly.graph_objects as go

mode = render_sidebar_and_mode()
data = get_active_data()

render_page_banner(
    title="Batter Pressure Analytics",
    subtitle="Official Global Top 10 Batting Leaderboard, Qualifying Pool Explorer & 10-Point Scouting Profiles",
    image_name="batting_action.jpg",
    accent=PALETTE["pink"],
)

top10 = data["top10_bat"].copy()
elig = data["elig_bat"].copy()

# Top Summary KPIs
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("#1 Pressure Batter", top10.iloc[0]["Player name"], f"Rating: {top10.iloc[0]['Auction Rating']:.1f} • ID {int(top10.iloc[0]['Player ID'])}", "gold")
with k2:
    render_kpi_card("Top 10 Avg HP SR", f"{top10['Pressure strike rate'].mean():.1f}", "Runs per 100 high-pressure balls", "pink")
with k3:
    render_kpi_card("Qualifying Batter Pool", f"{len(elig):,}", "Minimum >=120 HP balls faced", "teal")
with k4:
    render_kpi_card("Highest Top-10 RAA", f"+{top10['Runs above expectation'].max():.1f}", f"{top10.loc[top10['Runs above expectation'].idxmax(), 'Player name']}", "pink")

# Tabs: Official Global Top 10 vs Interactive Full Pool Explorer
tab_top10, tab_pool = st.tabs(["Official Global Top 10 Batters", "Interactive Full Qualifying Pool Explorer"])

with tab_top10:
    render_section_header("Official Global Top 10 Batters (Verified Final CSV)", accent="gold")
    display_top10 = pd.DataFrame({
        "Global Rank": top10["Rank"],
        "Player Name": top10["Player name"],
        "Player ID": top10["Player ID"],
        "Primary Team": top10["Primary team/affiliation"],
        "Auction Rating": top10["Auction Rating"],
        "Pressure Impact (P)": top10["Pressure impact score"],
        "HP BF": top10["Pressure balls faced"],
        "HP SR": top10["Pressure strike rate"],
        "RAA": top10["Runs above expectation"],
        "WAA": top10["Dismissal performance"],
        "Consistency": top10["Match consistency"],
        "IPL HP BF": top10["ipl_bf"].astype(int),
        "T20I HP BF": top10["t20i_bf"].astype(int),
        "Other T20 BF": top10["other_t20_bf"].astype(int),
        "Stability": top10["Ranking stability"],
    })
    render_clean_table(display_top10, height=395)

with tab_pool:
    render_section_header("Search & Filter Qualifying Batters (Original Global Rank Preserved)", accent="pink")
    if st.button("Reset Batter Filters", key="reset_bat_filters"):
        for k in ["bat_search", "bat_rating_rng", "bat_min_bf", "bat_fmt_filter", "bat_role_filter", "bat_sort_by"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    fc1, fc2, fc3, fc4, fc5 = st.columns([1.4, 1.2, 1.1, 1.1, 1.1])
    with fc1:
        search_q = st.text_input("Search Batter or Team", placeholder="e.g. Suryakumar, Jurel, MI...", key="bat_search")
    with fc2:
        r_min, r_max = float(elig["auction_rating"].min()), float(elig["auction_rating"].max())
        rating_rng = st.slider("Auction Rating Range", min_value=round(r_min, 1), max_value=round(r_max, 1), value=(round(r_min, 1), round(r_max, 1)), key="bat_rating_rng")
    with fc3:
        min_bf = st.slider("Min Pressure Balls (HP BF)", min_value=120, max_value=int(elig["hp_bf"].max()), value=120, step=10, key="bat_min_bf")
    with fc4:
        fmt_choice = st.selectbox("Competition Exposure", ["All Qualifying", "Has IPL (>=50 HP BF)", "Has T20I (>=50 HP BF)", "Both IPL & T20I", "Has Other T20"], key="bat_fmt_filter")
    with fc5:
        role_opts = ["All Roles"] + sorted([r for r in elig["inferred_batting_role"].dropna().unique().tolist()])
        role_choice = st.selectbox("Batting Role", role_opts, key="bat_role_filter")

    filtered = elig.copy()
    if search_q.strip():
        q = search_q.strip().lower()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(q, na=False)
            | filtered["team"].str.lower().str.contains(q, na=False)
            | filtered["striker_id"].astype(str).str.contains(q, na=False)
        ]
    filtered = filtered[(filtered["auction_rating"] >= rating_rng[0]) & (filtered["auction_rating"] <= rating_rng[1])]
    filtered = filtered[filtered["hp_bf"] >= min_bf]
    if fmt_choice == "Has IPL (>=50 HP BF)":
        filtered = filtered[filtered["ipl_bf"] >= 50]
    elif fmt_choice == "Has T20I (>=50 HP BF)":
        filtered = filtered[filtered["t20i_bf"] >= 50]
    elif fmt_choice == "Both IPL & T20I":
        filtered = filtered[(filtered["ipl_bf"] >= 50) & (filtered["t20i_bf"] >= 50)]
    elif fmt_choice == "Has Other T20":
        filtered = filtered[filtered["other_t20_bf"] > 0]
    if role_choice != "All Roles":
        filtered = filtered[filtered["inferred_batting_role"] == role_choice]

    sort_col_map = {
        "Original Global Rank (Auction Rating)": ("auction_rating", False),
        "Pressure Impact Score (P)": ("pressure_impact_score", False),
        "Runs Above Expectation (RAA)": ("hp_raa", False),
        "Pressure Strike Rate": ("hp_sr", False),
        "Match Consistency (%)": ("consistency_pct", False),
        "High-Pressure Balls Faced": ("hp_bf", False),
    }
    sort_label = st.selectbox("Sort Filtered View By", list(sort_col_map.keys()), key="bat_sort_by")
    scol, sasc = sort_col_map[sort_label]
    filtered = filtered.sort_values(scol, ascending=sasc).reset_index(drop=True)

    is_filtered_view = (len(filtered) != len(elig)) or (sort_label != "Original Global Rank (Auction Rating)")
    if len(filtered) == 0:
        st.warning("No batters match your current filter selection. Click **Reset Batter Filters** above to restore the full qualifying pool.")
    else:
        if is_filtered_view:
            st.info(f"**Filtered View ({len(filtered)} of {len(elig)} qualifying batters):** Displayed `Filtered Position` is dynamically ordered by *{sort_label}*; the authoritative **`Global Rank`** column is strictly preserved.")
        disp_pool = pd.DataFrame({
            "Filtered Pos": range(1, len(filtered) + 1),
            "Global Rank": filtered["Global_Rank"],
            "Player Name": filtered["name"],
            "Player ID": filtered["striker_id"],
            "Primary Team": filtered["team"],
            "Role": filtered["inferred_batting_role"].fillna("N/A"),
            "Auction Rating": filtered["auction_rating"].round(1),
            "Pressure Impact (P)": filtered["pressure_impact_score"].round(1),
            "HP BF": filtered["hp_bf"].astype(int),
            "HP SR": filtered["hp_sr"].round(1),
            "RAA": filtered["hp_raa"].round(1),
            "Consistency (%)": filtered["consistency_pct"].round(1),
            "IPL BF": filtered["ipl_bf"].astype(int),
            "T20I BF": filtered["t20i_bf"].astype(int),
            "Other T20 BF": filtered["other_t20_bf"].astype(int),
        })
        render_clean_table(disp_pool, height=390)

# Visual Exploration: RAA vs Volume & Pressure vs Ordinary SR
render_section_header("Batting Pressure Landscape", accent="teal")
sc1, sc2 = st.columns(2)
with sc1:
    fig_vol = make_impact_vs_volume_scatter(
        elig, set(top10["Player ID"].tolist()),
        x_col="hp_bf", y_col="hp_raa", name_col="name", id_col="striker_id",
        threshold_x=120,
        title="Runs Added Above Expectation (RAA) vs High-Pressure Balls Faced",
        x_label="High-Pressure Balls Faced", y_label="Runs Above Expectation (RAA)",
        accent_color=PALETTE["pink"],
    )
    st.plotly_chart(fig_vol, width='stretch')

with sc2:
    fig_sr = go.Figure()
    fig_sr.add_trace(
        go.Scatter(
            x=top10["ord_sr"], y=top10["Pressure strike rate"],
            mode="markers+text",
            text=[n.split()[-1] for n in top10["Player name"]],
            textposition="top center",
            marker=dict(size=13, color=PALETTE["pink"], line=dict(width=2, color=PALETTE["gold"])),
            customdata=top10[["Player name", "Player ID", "Pressure uplift/deterioration"]].values,
            hovertemplate="<b>%{customdata[0]}</b> (ID: %{customdata[1]})<br>Ordinary SR: %{x:.1f}<br>Pressure SR: %{y:.1f}<br>Uplift: %{customdata[2]:+.1f}<extra></extra>",
            name="Top 10 Batters",
        )
    )
    fig_sr.add_trace(
        go.Scatter(x=[105, 215], y=[105, 215], mode="lines", name="Equal Rate Line",
                   line=dict(dash="dash", color="rgba(255,255,255,0.35)", width=1.5))
    )
    style_plotly_fig(fig_sr, title="Top 10 Batters: High-Pressure SR vs Ordinary SR", height=420)
    fig_sr.update_xaxes(title_text="Ordinary Situation Strike Rate")
    fig_sr.update_yaxes(title_text="High-Pressure Strike Rate")
    st.plotly_chart(fig_sr, width='stretch')

# Detailed 10-Part Batter Profile Selector (keyed by stable striker_id)
render_section_header("Interactive Batter Scouting Profile", accent="pink")
elig_sorted = elig.sort_values("Global_Rank").reset_index(drop=True)
id_to_label = {
    int(r["striker_id"]): f"#{int(r['Global_Rank'])} {r['name']} ({r['team']}) — ID: {int(r['striker_id'])} | Rating: {r['auction_rating']:.1f}"
    for _, r in elig_sorted.iterrows()
}
selected_pid = st.selectbox(
    "Select a Qualifying Batter to Inspect Full 10-Point Profile",
    options=list(id_to_label.keys()),
    format_func=lambda pid: id_to_label[pid],
    key="selected_batter_pid",
)
sel_row = elig_sorted[elig_sorted["striker_id"] == selected_pid].iloc[0]
render_batter_profile(sel_row)

render_metric_glossary(["Auction Rating", "Pressure Impact Score", "Ordinary Performance Score", "Runs Above Expectation (RAA)", "Wickets Above Expectation (Batting WAA)", "Pressure Strike Rate", "Match Consistency", "Ranking Stability"])
render_footer(mode)
