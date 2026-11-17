"""
charts.py — Consistent dark-themed interactive Plotly charts matching the luxury
cricket palette (#101426 navy, #211B36 purple, #EA3D91 pink, #F4C542 gold, #35C6B5 teal).
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.formatting import PALETTE


def style_plotly_fig(fig: go.Figure, title: str = "", height: int = 410, legend_top: bool = True) -> go.Figure:
    top_margin = (86 if legend_top else 56) if title else 34
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Outfit, Inter, sans-serif", size=14.5, color=PALETTE["text_primary"]),
            x=0.01,
            y=0.965,
            yanchor="top",
        ),
        height=height,
        paper_bgcolor="rgba(27, 24, 48, 0.85)",
        plot_bgcolor="rgba(16, 20, 38, 0.65)",
        font=dict(family="Inter, sans-serif", color=PALETTE["text_primary"], size=12),
        margin=dict(l=54, r=32, t=top_margin, b=52),
        hoverlabel=dict(bgcolor="#161830", bordercolor=PALETTE["pink"], font=dict(color=PALETTE["text_primary"], size=12)),
        xaxis=dict(gridcolor=PALETTE["grid"], zerolinecolor="rgba(255,255,255,0.14)"),
        yaxis=dict(gridcolor=PALETTE["grid"], zerolinecolor="rgba(255,255,255,0.14)"),
    )
    if legend_top:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.015,
                xanchor="left",
                x=0.0,
                font=dict(size=11),
                bgcolor="rgba(0,0,0,0)",
            )
        )
    return fig


def make_top10_bar(df: pd.DataFrame, name_col: str, val_col: str, rank_col: str, color: str, title: str, x_range=None, extra_hover_cols=None) -> go.Figure:
    plot_df = df.sort_values(rank_col, ascending=False).copy()
    labels = [f"#{int(r)} {n}" for r, n in zip(plot_df[rank_col], plot_df[name_col])]
    hover_texts = []
    for _, row in plot_df.iterrows():
        parts = [f"<b>#{int(row[rank_col])} {row[name_col]}</b> (ID: {row['Player ID']})", f"Auction Rating: <b>{row[val_col]:.1f}</b>"]
        if extra_hover_cols:
            for lbl, col in extra_hover_cols:
                if col in row:
                    parts.append(f"{lbl}: {row[col]}")
        hover_texts.append("<br>".join(parts))

    fig = go.Figure(
        go.Bar(
            x=plot_df[val_col],
            y=labels,
            orientation="h",
            marker=dict(
                color=[PALETTE["gold"] if int(r) == 1 else color for r in plot_df[rank_col]],
                line=dict(color="rgba(255,255,255,0.15)", width=1),
            ),
            text=[f"{v:.1f}" for v in plot_df[val_col]],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color="#101426", size=11, family="Outfit, sans-serif"),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )
    style_plotly_fig(fig, title=title, height=390, legend_top=False)
    if x_range:
        fig.update_xaxes(range=x_range)
    fig.update_xaxes(title_text="Auction Rating (0–100 Scale)")
    return fig


def make_season_format_chart(by_season_format: list) -> go.Figure:
    sdf = pd.DataFrame(by_season_format)
    cat_order = ["IPL", "International T20I", "Other T20"]
    color_map = {"IPL": PALETTE["pink"], "International T20I": PALETTE["teal"], "Other T20": PALETTE["gold"]}
    fig = go.Figure()
    for cat in cat_order:
        sub = sdf[sdf["comp_category"] == cat]
        if len(sub) > 0:
            fig.add_trace(
                go.Bar(
                    x=sub["season"].astype(str),
                    y=sub["deliveries"],
                    name=cat,
                    marker_color=color_map[cat],
                    hovertemplate="<b>%{x}</b><br>" + cat + ": %{y:,} deliveries<extra></extra>",
                )
            )
    fig.update_layout(barmode="stack")
    style_plotly_fig(fig, title="Deliveries Analyzed by Season & 3-Way Competition Category", height=370)
    fig.update_xaxes(title_text="Season")
    fig.update_yaxes(title_text="Contested Deliveries")
    return fig


def make_cpi_histogram(cpi_hist: list) -> go.Figure:
    hdf = pd.DataFrame(cpi_hist)
    colors = [
        PALETTE["pink"] if m >= 0.60 else (PALETTE["gold"] if m >= 0.35 else PALETTE["teal"])
        for m in hdf["bin_mid"]
    ]
    fig = go.Figure(
        go.Bar(
            x=hdf["bin_mid"],
            y=hdf["count"],
            marker_color=colors,
            width=0.036,
            hovertemplate="CPI Range: %{customdata[0]:.2f}–%{customdata[1]:.2f}<br>Deliveries: %{y:,}<extra></extra>",
            customdata=hdf[["bin_start", "bin_end"]].values,
        )
    )
    fig.add_vline(x=0.60, line_dash="dash", line_color=PALETTE["pink"], line_width=2,
                  annotation_text="High Pressure (>=0.60)", annotation_position="top right",
                  annotation_font=dict(color=PALETTE["pink"], size=11))
    fig.add_vline(x=0.35, line_dash="dot", line_color=PALETTE["gold"], line_width=1.5,
                  annotation_text="Medium (>=0.35)", annotation_position="top left",
                  annotation_font=dict(color=PALETTE["gold"], size=11))
    style_plotly_fig(fig, title="Pre-Delivery Composite Pressure Index (CPI) Distribution", height=370, legend_top=False)
    fig.update_xaxes(title_text="Composite Pressure Index (CPI)", range=[0, 1.02])
    fig.update_yaxes(title_text="Number of Deliveries")
    return fig


def make_over_pressure_chart(by_over_innings: list) -> go.Figure:
    odf = pd.DataFrame(by_over_innings)
    fig = go.Figure()
    for inn, color, label in [(1, PALETTE["teal"], "1st Innings (Target Setting)"), (2, PALETTE["pink"], "2nd Innings (Chase)")]:
        sub = odf[odf["innings"] == inn].sort_values("overid")
        fig.add_trace(
            go.Scatter(
                x=sub["overid"],
                y=sub["hp_pct"],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3),
                marker=dict(size=7),
                hovertemplate="Over %{x}<br>" + label + "<br>High-Pressure Share: %{y:.1f}%<br>Mean CPI: %{customdata:.3f}<extra></extra>",
                customdata=sub["mean_cpi"],
            )
        )
    fig.add_vrect(x0=0.5, x1=6.5, fillcolor="rgba(53,198,181,0.06)", line_width=0, annotation_text="Powerplay", annotation_position="top left")
    fig.add_vrect(x0=15.5, x1=20.5, fillcolor="rgba(234,61,145,0.09)", line_width=0, annotation_text="Death Overs", annotation_position="top right")
    style_plotly_fig(fig, title="High-Pressure Delivery Share (%) Across Overs 1–20 by Innings", height=380)
    fig.update_xaxes(title_text="Over Number", dtick=1, range=[0.5, 20.5])
    fig.update_yaxes(title_text="High-Pressure Share (%)", range=[0, 102])
    return fig


def make_chase_heatmap(chase_heatmap: list) -> go.Figure:
    hdf = pd.DataFrame(chase_heatmap)
    rrr_order = ["<6", "6-8", "8-10", "10-12", "12-15", "15+"]
    wkt_order = ["9-10 Wkts", "7-8 Wkts", "5-6 Wkts", "3-4 Wkts", "1-2 Wkts"]
    piv = hdf.pivot(index="rrr_bucket", columns="wkt_grp", values="mean_cpi").reindex(index=rrr_order, columns=wkt_order)
    fig = go.Figure(
        go.Heatmap(
            z=piv.values,
            x=piv.columns,
            y=piv.index,
            colorscale=[[0.0, "#161830"], [0.45, "#35C6B5"], [0.70, "#F4C542"], [1.0, "#EA3D91"]],
            zmin=0.15,
            zmax=0.95,
            text=np.round(piv.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=11, color="#F5F6FA"),
            hovertemplate="RRR: %{y}<br>Wickets in Hand: %{x}<br>Mean CPI: %{z:.3f}<extra></extra>",
            colorbar=dict(title="Mean CPI"),
        )
    )
    style_plotly_fig(fig, title="2nd Innings Pressure Matrix: Mean CPI by Required Run Rate vs Wickets in Hand", height=390, legend_top=False)
    fig.update_xaxes(title_text="Wickets Remaining")
    fig.update_yaxes(title_text="Required Run Rate (RRR)")
    return fig


def make_impact_vs_volume_scatter(elig_df: pd.DataFrame, top10_ids: set, x_col: str, y_col: str, name_col: str, id_col: str, threshold_x: int, title: str, x_label: str, y_label: str, accent_color: str) -> go.Figure:
    df = elig_df.copy()
    df["Group"] = np.where(df[id_col].isin(top10_ids), "Global Top 10", "Other Qualifying Players")
    fig = go.Figure()
    others = df[df["Group"] != "Global Top 10"]
    top = df[df["Group"] == "Global Top 10"]

    fig.add_trace(
        go.Scatter(
            x=others[x_col],
            y=others[y_col],
            mode="markers",
            name="Other Qualifying Pool",
            marker=dict(size=8, color="rgba(167, 174, 192, 0.45)", line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
            text=others[name_col],
            customdata=others[[id_col, "auction_rating"]].values,
            hovertemplate="<b>%{text}</b> (ID: %{customdata[0]})<br>" + x_label + ": %{x}<br>" + y_label + ": %{y:+.1f}<br>Auction Rating: %{customdata[1]:.1f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=top[x_col],
            y=top[y_col],
            mode="markers+text",
            name="Global Top 10",
            marker=dict(size=13, color=accent_color, line=dict(width=2, color=PALETTE["gold"])),
            text=[n.split()[-1] for n in top[name_col]],
            textposition="top center",
            textfont=dict(size=10, color=PALETTE["text_primary"]),
            customdata=top[[name_col, id_col, "auction_rating"]].values,
            hovertemplate="<b>%{customdata[0]}</b> (ID: %{customdata[1]})<br>" + x_label + ": %{x}<br>" + y_label + ": %{y:+.1f}<br>Auction Rating: %{customdata[2]:.1f}<extra></extra>",
        )
    )
    fig.add_vline(x=threshold_x, line_dash="dash", line_color=PALETTE["gold"], line_width=1.5,
                  annotation_text=f"Cutoff ({threshold_x})", annotation_position="top right",
                  annotation_font=dict(color=PALETTE["gold"], size=10))
    style_plotly_fig(fig, title=title, height=420)
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)
    return fig


def make_radar_chart(players_data: list, categories: list, title: str) -> go.Figure:
    colors = [PALETTE["pink"], PALETTE["teal"], PALETTE["gold"]]
    fills = ["rgba(234,61,145,0.22)", "rgba(53,198,181,0.20)", "rgba(244,197,66,0.20)"]
    fig = go.Figure()
    for i, pdata in enumerate(players_data):
        vals = list(pdata["values"]) + [pdata["values"][0]]
        cats = list(categories) + [categories[0]]
        raw_vals = list(pdata["raw_labels"]) + [pdata["raw_labels"][0]]
        fig.add_trace(
            go.Scatterpolar(
                r=vals,
                theta=cats,
                fill="toself",
                fillcolor=fills[i % 3],
                line=dict(color=colors[i % 3], width=2.5),
                name=pdata["name"],
                customdata=raw_vals,
                hovertemplate="<b>" + pdata["name"] + "</b><br>%{theta}: %{customdata}<br>Normalized Score: %{r:.1f}/100<extra></extra>",
            )
        )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(16,20,38,0.65)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=PALETTE["grid"], tickfont=dict(size=10, color=PALETTE["text_secondary"])),
            angularaxis=dict(gridcolor=PALETTE["grid"], tickfont=dict(size=11, color=PALETTE["text_primary"])),
        )
    )
    style_plotly_fig(fig, title=title, height=450, legend_top=True)
    fig.update_layout(margin=dict(l=88, r=88, t=96, b=48))
    return fig
