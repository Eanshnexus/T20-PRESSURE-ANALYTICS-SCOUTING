"""
player_profiles.py — Rich 10-part Batter & Bowler analytical scouting profiles.
"""
import streamlit as st
import plotly.graph_objects as go
from components.metric_cards import render_kpi_card, render_insight_card
from components.charts import style_plotly_fig
from utils.formatting import PALETTE, fmt_num, fmt_int, parse_pct, sample_reliability_tier
from utils.calculations import classify_weighting_branch


def render_batter_profile(row, is_global_top10: bool = True):
    """Render comprehensive 10-point batting pressure profile for a selected batter."""
    pid = int(row["striker_id"]) if "striker_id" in row else int(row["Player ID"])
    name = row["name"] if "name" in row else row["Player name"]
    team = row["team"] if "team" in row else row["Primary team/affiliation"]
    rank = int(row["Global_Rank"]) if "Global_Rank" in row else int(row["Rank"])
    rating = float(row["auction_rating"]) if "auction_rating" in row else float(row["Auction Rating"])
    p_score = float(row["pressure_impact_score"]) if "pressure_impact_score" in row else float(row["Pressure impact score"])
    ord_score = float(row["ord_score"]) if "ord_score" in row else float(row["Ordinary performance score"])
    hp_bf = int(row["hp_bf"]) if "hp_bf" in row else int(row["Pressure balls faced"])
    hp_matches = int(row["hp_matches"]) if "hp_matches" in row else int(row["Pressure matches"])
    hp_sr = float(row["hp_sr"]) if "hp_sr" in row else float(row["Pressure strike rate"])
    ord_sr = float(row["ord_sr"]) if "ord_sr" in row and row["ord_sr"] == row["ord_sr"] else None
    hp_raa = float(row["hp_raa"]) if "hp_raa" in row else float(row["Runs above expectation"])
    hp_waa = float(row["hp_waa"]) if "hp_waa" in row else float(row["Dismissal performance"])
    delta_sr = float(row["delta_sr"]) if "delta_sr" in row else float(row["Pressure uplift/deterioration"])
    cons = float(row["consistency_pct"]) if "consistency_pct" in row else parse_pct(row["Match consistency"])
    ipl_bf = int(row.get("ipl_bf", 0))
    t20i_bf = int(row.get("t20i_bf", 0))
    other_bf = int(row.get("other_t20_bf", 0))
    ipl_raa = float(row.get("ipl_raa", row.get("IPL contribution", 0.0)))
    t20i_raa = float(row.get("t20i_raa", row.get("T20I contribution", 0.0)))
    other_raa = float(row.get("other_t20_raa", 0.0))
    stability = row.get("Stability_Class", row.get("Ranking stability", None))
    stability_str = str(stability) if stability is not None and stability == stability else "Not in Top-10 Sensitivity"
    role = row.get("inferred_batting_role", "Qualifying Batter")
    reliability = sample_reliability_tier(hp_bf, "batting")
    branch = classify_weighting_branch(ipl_bf, t20i_bf, "batting")

    # 1. Player Overview Header
    st.markdown(
        f"""
        <div class="profile-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div>
                    <span class="rank-pill-gold">Global Rank #{rank}</span>
                    <span class="pill-pink">{role}</span>
                    <span class="pill-teal">ID: {pid}</span>
                    <h2 style="margin:8px 0 4px 0;font-size:1.7rem;">{name}</h2>
                    <div style="color:#A7AEC0;font-size:0.9rem;">
                        Primary Team: <strong style="color:#F5F6FA;">{team}</strong> &nbsp;|&nbsp;
                        Stability: <strong style="color:#F4C542;">{stability_str}</strong> &nbsp;|&nbsp;
                        Reliability: <strong style="color:#35C6B5;">{reliability}</strong>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;color:#A7AEC0;">Verified Auction Rating</div>
                    <div style="font-family:'Outfit',sans-serif;font-size:2.45rem;font-weight:800;color:#EA3D91;line-height:1.05;">{rating:.1f}</div>
                    <div style="font-size:0.75rem;color:#A7AEC0;">0–100 Scale</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2–7. Core KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi_card("Pressure Impact (P)", f"{p_score:.1f}", f"Ordinary Score: {ord_score:.1f}", "pink")
    with c2:
        render_kpi_card("Runs Above Exp (RAA)", fmt_num(hp_raa, 1, signed=True), f"Wicket Equity: {fmt_num(hp_waa, 2, signed=True)} WAA", "gold")
    with c3:
        ord_str = f"vs {ord_sr:.1f} Ordinary" if ord_sr is not None else f"Delta: {fmt_num(delta_sr, 1, signed=True)}"
        render_kpi_card("Pressure Strike Rate", f"{hp_sr:.1f}", ord_str, "pink")
    with c4:
        render_kpi_card("Match Consistency", f"{cons:.1f}%", f"Across {hp_matches} HP matches", "teal")
    with c5:
        render_kpi_card("Pressure Volume", f"{hp_bf:,} BF", f"SR Uplift: {fmt_num(delta_sr, 1, signed=True)}", "gold")

    # 8–9. Visual Breakdown Charts (Pressure vs Ordinary & 3-Way Format Exposure)
    ch1, ch2 = st.columns(2)
    with ch1:
        fig_po = go.Figure()
        fig_po.add_trace(
            go.Bar(
                x=["Pressure Impact (P)", "Ordinary Baseline Score", "Match Consistency (%)"],
                y=[p_score, ord_score, cons],
                marker_color=[PALETTE["pink"], PALETTE["teal"], PALETTE["gold"]],
                text=[f"{p_score:.1f}", f"{ord_score:.1f}", f"{cons:.1f}%"],
                textposition="outside",
            )
        )
        style_plotly_fig(fig_po, title="Pressure vs Ordinary Performance & Consistency", height=310, legend_top=False)
        fig_po.update_yaxes(range=[0, 112], title_text="Score / Percentage (0–100)")
        st.plotly_chart(fig_po, width='stretch')

    with ch2:
        fig_fmt = go.Figure()
        cats = ["IPL", "International T20I", "Other T20"]
        bf_vals = [ipl_bf, t20i_bf, other_bf]
        raa_vals = [ipl_raa, t20i_raa, other_raa]
        fig_fmt.add_trace(
            go.Bar(
                x=cats, y=bf_vals, name="HP Balls Faced",
                marker_color=[PALETTE["pink"], PALETTE["teal"], PALETTE["gold"]],
                text=[f"{b} BF<br>({r:+.1f} RAA)" for b, r in zip(bf_vals, raa_vals)],
                textposition="outside",
            )
        )
        style_plotly_fig(fig_fmt, title="3-Way Competition Exposure (IPL / T20I / Other T20)", height=310, legend_top=False)
        fig_fmt.update_yaxes(title_text="High-Pressure Balls Faced", range=[0, max(bf_vals + [50]) * 1.28])
        st.plotly_chart(fig_fmt, width='stretch')

    # 10. Strengths & Statistical Observations
    obs = []
    if delta_sr >= 25:
        obs.append(f"Elevates strike rate sharply under pressure ({fmt_num(delta_sr, 1, signed=True)} SR uplift vs ordinary overs).")
    elif delta_sr >= 0:
        obs.append(f"Maintains scoring tempo under pressure ({fmt_num(delta_sr, 1, signed=True)} SR delta).")
    else:
        obs.append(f"Experienced modest strike-rate compression ({fmt_num(delta_sr, 1, signed=True)}) under high CPI.")

    if hp_waa >= 5.0:
        obs.append(f"Strong wicket preservation (+{hp_waa:.2f} WAA), avoiding dismissals well above contextual expectation.")
    if ipl_bf < 100:
        obs.append(f"Limited genuine IPL sample ({ipl_bf} HP BF); rating draws substantially on International T20I volume ({t20i_bf} HP BF).")
    elif t20i_bf < 50:
        obs.append(f"Rating is anchored primarily in demonstrated IPL exposure ({ipl_bf} HP BF vs {t20i_bf} T20I HP BF).")
    if other_bf > 0:
        obs.append(f"Includes {other_bf} Other T20 HP balls ({other_raa:+.1f} RAA), kept strictly separate from IPL and T20I splits.")
    if stability_str == "Volatile":
        obs.append("Moderate pressure volume produces higher rank sensitivity under stricter CPI >= 0.70 cutoffs.")

    render_insight_card(
        f"Statistical Observations & Format Weighting — {name}",
        f"<strong>Applied Weighting Branch:</strong> {branch}<br>" + " • ".join(obs),
        accent="pink",
    )


def render_bowler_profile(row):
    """Render comprehensive 10-point bowling pressure profile for a selected bowler."""
    pid = int(row["bowler_id"]) if "bowler_id" in row else int(row["Player ID"])
    name = row["name"] if "name" in row else row["Player name"]
    team = row["team"] if "team" in row else row["Primary team/affiliation"]
    rank = int(row["Global_Rank"]) if "Global_Rank" in row else int(row["Rank"])
    rating = float(row["auction_rating"]) if "auction_rating" in row else float(row["Auction Rating"])
    p_score = float(row["pressure_impact_score"]) if "pressure_impact_score" in row else float(row["Pressure impact score"])
    ord_score = float(row["ord_score"]) if "ord_score" in row else float(row["Ordinary performance score"])
    hp_balls = int(row["hp_balls"]) if "hp_balls" in row else int(row["Pressure legal balls"])
    hp_matches = int(row["hp_matches"]) if "hp_matches" in row else int(row["Pressure matches"])
    hp_econ = float(row["hp_econ"]) if "hp_econ" in row else float(row["Pressure economy"])
    ord_econ = float(row["ord_econ"]) if "ord_econ" in row and row["ord_econ"] == row["ord_econ"] else None
    hp_rpa = float(row["hp_rpa"]) if "hp_rpa" in row else float(row["Runs prevented above expectation"])
    hp_wkts = int(row["hp_wkts"]) if "hp_wkts" in row else int(row["Wickets"])
    hp_waa = float(row["hp_waa"]) if "hp_waa" in row else float(row["Wickets above expectation"])
    hp_runs = float(row["hp_runs"]) if "hp_runs" in row and row["hp_runs"] == row["hp_runs"] else (hp_econ * hp_balls / 6.0)
    exp_runs = hp_runs + hp_rpa
    dot_pct = float(row["hp_dot_pct"]) if "hp_dot_pct" in row else parse_pct(row["Dot-ball percentage"])
    cons = float(row["consistency_pct"]) if "consistency_pct" in row else parse_pct(row["Match consistency"])
    ipl_b = int(row.get("ipl_balls", 0))
    t20i_b = int(row.get("t20i_balls", 0))
    other_b = int(row.get("other_t20_balls", 0))
    ipl_rpa = float(row.get("ipl_rpa", row.get("IPL contribution", 0.0)))
    t20i_rpa = float(row.get("t20i_rpa", row.get("T20I contribution", 0.0)))
    other_rpa = float(row.get("other_t20_rpa", 0.0))
    stability = row.get("Stability_Class", row.get("Ranking stability", None))
    stability_str = str(stability) if stability is not None and stability == stability else "Not in Top-10 Sensitivity"
    role = row.get("inferred_bowling_role", "Qualifying Bowler")
    reliability = sample_reliability_tier(hp_balls, "bowling")
    branch = classify_weighting_branch(ipl_b, t20i_b, "bowling")

    # 1. Profile Header
    st.markdown(
        f"""
        <div class="profile-card" style="border-color: rgba(53, 198, 181, 0.40);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div>
                    <span class="rank-pill-gold">Global Rank #{rank}</span>
                    <span class="pill-teal">{role}</span>
                    <span class="pill-pink">ID: {pid}</span>
                    <h2 style="margin:8px 0 4px 0;font-size:1.7rem;">{name}</h2>
                    <div style="color:#A7AEC0;font-size:0.9rem;">
                        Primary Team: <strong style="color:#F5F6FA;">{team}</strong> &nbsp;|&nbsp;
                        Stability: <strong style="color:#F4C542;">{stability_str}</strong> &nbsp;|&nbsp;
                        Reliability: <strong style="color:#35C6B5;">{reliability}</strong>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;color:#A7AEC0;">Verified Auction Rating</div>
                    <div style="font-family:'Outfit',sans-serif;font-size:2.45rem;font-weight:800;color:#35C6B5;line-height:1.05;">{rating:.1f}</div>
                    <div style="font-size:0.75rem;color:#A7AEC0;">0–100 Scale</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2–7. Core KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi_card("Pressure Impact (P)", f"{p_score:.1f}", f"Ordinary Score: {ord_score:.1f}", "teal")
    with c2:
        render_kpi_card("Runs Prevented (RPA)", fmt_num(hp_rpa, 1, signed=True), f"Actual {hp_runs:.0f} vs Exp {exp_runs:.1f}", "gold")
    with c3:
        ord_str = f"vs {ord_econ:.2f} Ordinary" if ord_econ is not None else "Lower is better"
        render_kpi_card("Pressure Economy", f"{hp_econ:.2f}", ord_str, "teal")
    with c4:
        render_kpi_card("Pressure Wickets", f"{hp_wkts}", f"WAA: {fmt_num(hp_waa, 2, signed=True)} • Dot: {dot_pct:.1f}%", "pink")
    with c5:
        render_kpi_card("Match Consistency", f"{cons:.1f}%", f"{hp_balls:,} HP legal balls ({hp_matches}m)", "gold")

    # 8–9. Charts: Expected vs Actual Runs + 3-Way Format Exposure
    ch1, ch2 = st.columns(2)
    with ch1:
        fig_ra = go.Figure()
        fig_ra.add_trace(
            go.Bar(
                x=["ML Expected Runs", "Actual Runs Conceded"],
                y=[exp_runs, hp_runs],
                marker_color=[PALETTE["gold"], PALETTE["teal"]],
                text=[f"{exp_runs:.1f}", f"{hp_runs:.0f}"],
                textposition="outside",
            )
        )
        style_plotly_fig(fig_ra, title=f"Expected vs Actual Runs Conceded Under Pressure (RPA: {hp_rpa:+.1f})", height=310, legend_top=False)
        fig_ra.update_yaxes(title_text="Cumulative Runs", range=[0, max(exp_runs, hp_runs) * 1.22])
        st.plotly_chart(fig_ra, width='stretch')

    with ch2:
        fig_fmt = go.Figure()
        cats = ["IPL", "International T20I", "Other T20"]
        b_vals = [ipl_b, t20i_b, other_b]
        rpa_vals = [ipl_rpa, t20i_rpa, other_rpa]
        fig_fmt.add_trace(
            go.Bar(
                x=cats, y=b_vals, name="HP Legal Balls",
                marker_color=[PALETTE["pink"], PALETTE["teal"], PALETTE["gold"]],
                text=[f"{b} Bls<br>({r:+.1f} RPA)" for b, r in zip(b_vals, rpa_vals)],
                textposition="outside",
            )
        )
        style_plotly_fig(fig_fmt, title="3-Way Competition Exposure (IPL / T20I / Other T20)", height=310, legend_top=False)
        fig_fmt.update_yaxes(title_text="High-Pressure Legal Balls", range=[0, max(b_vals + [50]) * 1.28])
        st.plotly_chart(fig_fmt, width='stretch')

    # 10. Strengths & Limitations
    obs = []
    if hp_econ <= 6.5:
        obs.append(f"Elite run suppression under pressure ({hp_econ:.2f} RPO, {dot_pct:.1f}% dots).")
    if hp_wkts >= 25:
        obs.append(f"Proven strike capability with {hp_wkts} pressure wickets ({fmt_num(hp_waa, 2, signed=True)} WAA).")
    if ipl_b == 0:
        obs.append(f"Zero genuine IPL deliveries in dataset — rating reflects international/non-IPL performance ({t20i_b} T20I, {other_b} Other T20) and must not be mistaken for proven IPL performance.")
    elif ipl_b < 60:
        obs.append(f"Limited genuine IPL sample ({ipl_b} HP balls vs {t20i_b} T20I HP balls); interpret IPL transferability cautiously.")
    if other_b > 0:
        obs.append(f"Separates {other_b} Other T20 HP balls ({other_rpa:+.1f} RPA) outside IPL and T20I splits.")
    if stability_str == "Volatile":
        obs.append("Smaller qualifying ball volume increases rank variance under strict CPI >= 0.70 cutoffs.")

    render_insight_card(
        f"Strengths, Limitations & Format Weighting — {name}",
        f"<strong>Applied Weighting Branch:</strong> {branch}<br>" + " • ".join(obs),
        accent="teal",
    )
