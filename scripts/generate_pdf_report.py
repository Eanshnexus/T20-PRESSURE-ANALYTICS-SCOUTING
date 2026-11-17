"""
generate_pdf_report.py - SupeRR Selector Season 2
Generates a polished 5-page publication PDF report using matplotlib.backends.backend_pdf.
Fixes visual alignment, adds canonical Player IDs, prevents text clipping/overlap,
and ensures statistically accurate claim framing.
"""

import os
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Corporate Design Palette
RR_PINK = '#EA1A7F'
RR_BLUE = '#0B1A30'
RR_GOLD = '#D4AF37'
RR_NAVY = '#1A365D'
RR_GREY = '#708090'
LIGHT_BG = '#F8FAFC'

TEAM_ABBR = {
    'Mumbai Indians': 'MI',
    'Delhi Capitals': 'DC',
    'Rajasthan Royals': 'RR',
    'Sunrisers Hyderabad': 'SRH',
    'Punjab Kings': 'PBKS',
    'Kolkata Knight Riders': 'KKR',
    'Chennai Super Kings': 'CSK',
    'Lucknow Super Giants': 'LSG',
    'Royal Challengers Bengaluru': 'RCB',
    'Gujarat Titans': 'GT',
    'Pakistan': 'Pakistan'
}

def short_team(name):
    return TEAM_ABBR.get(name, name)

def run_generate_pdf():
    print("="*60)
    print("STAGE 9: GENERATING MULTI-PAGE PUBLICATION PDF REPORT")
    print("="*60)

    pdf_out = 'outputs/reports/SuPeRR_Selector_Season_2_Final_Report.pdf'
    top10_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
    top10_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')

    with PdfPages(pdf_out) as pdf:
        # =========================================================================
        # PAGE 1: COVER & EXECUTIVE SUMMARY
        # =========================================================================
        print("Rendering PDF Page 1: Cover & Executive Summary...")
        fig = plt.figure(figsize=(8.27, 11.69), dpi=300)  # A4
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        # Header Banner
        rect = plt.Rectangle((0, 0.86), 1, 0.14, facecolor=RR_BLUE, transform=ax.transAxes, zorder=1)
        ax.add_patch(rect)
        rect_strip = plt.Rectangle((0, 0.852), 1, 0.008, facecolor=RR_PINK, transform=ax.transAxes, zorder=2)
        ax.add_patch(rect_strip)

        ax.text(0.06, 0.95, "SUPERR SELECTOR SEASON 2", color='white', fontsize=22, fontweight='bold', transform=ax.transAxes)
        ax.text(0.06, 0.915, "Identifying the Most Reliable Batters and Bowlers Under Pressure", color=RR_GOLD, fontsize=12, fontweight='bold', transform=ax.transAxes)
        ax.text(0.06, 0.88, "Rajasthan Royals IPL 2027 Auction Analytics Challenge  |  Official Methodology & Findings Report", color='#CBD5E1', fontsize=9, transform=ax.transAxes)

        # Executive Summary Prose
        ax.text(0.06, 0.815, "1. EXECUTIVE SUMMARY & OBJECTIVE", color=RR_BLUE, fontsize=11.5, fontweight='bold', va='top', transform=ax.transAxes)
        summary_text = (
            "In high-stakes T20 cricket, conventional aggregate metrics (such as raw strike rate, overall batting average, and\n"
            "gross bowling economy) fail to capture player reliability under pressure. A boundary hit during comfortable middle\n"
            "overs is fundamentally different from a boundary struck when requiring 18 runs from the final over. To provide\n"
            "Rajasthan Royals with a decisive analytical advantage for the IPL 2027 Auction, this study engineered a transparent,\n"
            "reproducible framework analyzing 200,999 deliveries across 867 matches (IPL 2022–2026 and T20Is)."
        )
        ax.text(0.06, 0.79, summary_text, color='#334155', fontsize=8.4, linespacing=1.4, va='top', transform=ax.transAxes)

        # Metric KPI Cards
        kpi_x = [0.06, 0.29, 0.52, 0.75]
        kpi_vals = ["200,999", "55,011", "867", "100%"]
        kpi_labels = ["Total Deliveries", "High-Pressure (27.4%)", "Contested Matches", "Reproducible Code"]
        for x_pos, val, lbl in zip(kpi_x, kpi_vals, kpi_labels):
            card = plt.Rectangle((x_pos, 0.64), 0.19, 0.06, facecolor='#F1F5F9', edgecolor='#CBD5E1', transform=ax.transAxes, zorder=2)
            ax.add_patch(card)
            ax.text(x_pos + 0.095, 0.675, val, color=RR_PINK, fontsize=13, fontweight='bold', ha='center', va='center', transform=ax.transAxes, zorder=3)
            ax.text(x_pos + 0.095, 0.654, lbl, color='#475569', fontsize=7, fontweight='bold', ha='center', va='center', transform=ax.transAxes, zorder=3)

        # Core Findings Preview
        ax.text(0.06, 0.615, "2. CORE METHODOLOGICAL PILLARS", color=RR_BLUE, fontsize=11, fontweight='bold', va='top', transform=ax.transAxes)
        pillars_text = (
            "• Ex-Ante Pressure Index (CPI): Continuous latent leverage score [0.0, 1.0] conditioned strictly on pre-delivery\n"
            "  scoreboard state (RRR, wickets remaining, balls left, collapse state, knockout stakes) with zero outcome leakage.\n"
            "• 5-Fold GroupKFold ML Baselines: HistGradientBoosting models grouped strictly by match_id predicting expected runs\n"
            "  and dismissal probabilities; modest single-ball gains verified positive across all 5 out-of-fold splits.\n"
            "• Empirical Bayes Shrinkage: Observed rate metrics are shrunk toward population priors (K_bat=150, K_bowl=200)\n"
            "  to prevent small-sample anomalies from displacing proven, high-exposure match-winners.\n"
            "• Strategic Format Weighting: Domain-informed 70% IPL / 30% T20I blend (strictly genuine IPL 2022–2026 only),\n"
            "  paired with separate IPL-relevant cohorts reflecting practical recruitment availability."
        )
        ax.text(0.06, 0.59, pillars_text, color='#334155', fontsize=8.0, linespacing=1.4, va='top', transform=ax.transAxes)

        # Chart 1 Embed
        img1 = mpimg.imread('outputs/charts/01_dataset_coverage.png')
        ax_img1 = fig.add_axes([0.06, 0.06, 0.88, 0.39])
        ax_img1.imshow(img1)
        ax_img1.axis('off')

        # Footer
        ax.text(0.5, 0.025, "SupeRR Selector Season 2 — Rajasthan Royals  |  Page 1 of 5", color=RR_GREY, fontsize=8, ha='center', transform=ax.transAxes)
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # PAGE 2: PRESSURE MODEL & BASELINE VALIDATION
        # =========================================================================
        print("Rendering PDF Page 2: Pressure Model & Baselines...")
        fig = plt.figure(figsize=(8.27, 11.69), dpi=300)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        rect = plt.Rectangle((0, 0.93), 1, 0.07, facecolor=RR_BLUE, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.06, 0.96, "PRESSURE MODELING & CONTEXTUAL EXPECTATION BASELINES", color='white', fontsize=13.5, fontweight='bold', transform=ax.transAxes)
        ax.text(0.06, 0.94, "Dual Classification Architecture & 5-Fold GroupKFold Out-of-Fold Diagnostics", color=RR_GOLD, fontsize=8.5, transform=ax.transAxes)

        # Chart 2 Embed (Pressure Distribution)
        img2 = mpimg.imread('outputs/charts/02_pressure_distribution.png')
        ax_img2 = fig.add_axes([0.05, 0.62, 0.90, 0.29])
        ax_img2.imshow(img2)
        ax_img2.axis('off')

        # Table of Model Validation
        ax.text(0.06, 0.595, "MODEL VALIDATION DIAGNOSTICS: 5-FOLD GROUPKFOLD ON MATCH_ID", color=RR_BLUE, fontsize=10, fontweight='bold', va='top', transform=ax.transAxes)

        table_y = 0.56
        col_x = [0.06, 0.29, 0.49, 0.64, 0.77]
        headers = ["Target Dimension", "Algorithm", "Metric", "Simple Baseline", "ML Model (OOF)"]
        for x_pos, h in zip(col_x, headers):
            ax.text(x_pos, table_y, h, color=RR_BLUE, fontsize=7.5, fontweight='bold', transform=ax.transAxes)

        ax.plot([0.06, 0.94], [table_y - 0.01, table_y - 0.01], color=RR_PINK, linewidth=1.5, transform=ax.transAxes)

        t_rows = [
            ("Batter Runs", "HistGBM Regressor", "MAE (Runs)", "1.2953", "1.2850 (+0.80%)"),
            ("Batter Dismissal", "HistGBM Classifier", "ROC-AUC", "0.5810", "0.5950 (+2.41%)"),
            ("Bowler Runs", "HistGBM Regressor", "MAE (Runs)", "1.2855", "1.2743 (+0.87%)"),
            ("Bowler Wickets", "HistGBM Classifier", "ROC-AUC", "0.5723", "0.5848 (+2.18%)")
        ]
        curr_y = table_y - 0.028
        for row in t_rows:
            for x_pos, val in zip(col_x, row):
                ax.text(x_pos, curr_y, val, color='#1E293B', fontsize=7.3, transform=ax.transAxes)
            curr_y -= 0.022

        note_text = (
            "Model Validation & Limitations (Match-Grouped, Non-Chronological 5-Fold GroupKFold): Single-ball T20 outcomes carry high variance, so\n"
            "per-delivery gains over simple baselines are modest (all 5 folds positive; 95% match-clustered CI vs OOF cell baseline across 200,999 balls:\n"
            "Batter MAE +0.0105 [+0.0076, +0.0138]; Bowler MAE +0.0116 [+0.0085, +0.0150]; Dismissal ECE=0.0015, Wicket ECE=0.0014). CPI>=0.60: 27.37%."
        )
        ax.text(0.06, curr_y - 0.005, note_text, color='#475569', fontsize=6.9, linespacing=1.35, va='top', transform=ax.transAxes)

        # Chart 3 Embed (Pressure vs Ordinary)
        img3 = mpimg.imread('outputs/charts/03_pressure_vs_ordinary.png')
        ax_img3 = fig.add_axes([0.05, 0.06, 0.90, 0.35])
        ax_img3.imshow(img3)
        ax_img3.axis('off')

        ax.text(0.5, 0.025, "SupeRR Selector Season 2 — Rajasthan Royals  |  Page 2 of 5", color=RR_GREY, fontsize=8, ha='center', transform=ax.transAxes)
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # PAGE 3: TOP 10 BATTERS UNDER PRESSURE
        # =========================================================================
        print("Rendering PDF Page 3: Top 10 Batters...")
        fig = plt.figure(figsize=(8.27, 11.69), dpi=300)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        rect = plt.Rectangle((0, 0.93), 1, 0.07, facecolor=RR_BLUE, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.06, 0.96, "TOP 10 BATTERS UNDER PRESSURE", color='white', fontsize=14, fontweight='bold', transform=ax.transAxes)
        ax.text(0.06, 0.94, "Official Global Ranked Selections (All 10 Eligible for IPL Recruitment)", color=RR_GOLD, fontsize=8.5, transform=ax.transAxes)

        # Batters Table with Canonical Player IDs and Clean Team Abbreviations
        ax.text(0.06, 0.905, "OFFICIAL TOP 10 BATTERS SCORECARD (QUALIFYING HP BF >= 120)", color=RR_BLUE, fontsize=9.5, fontweight='bold', transform=ax.transAxes)

        b_cols = [0.055, 0.105, 0.315, 0.385, 0.450, 0.520, 0.595, 0.680, 0.765, 0.855]
        b_hdrs = ["Rank", "Player Name", "ID", "Team", "HP BF", "HP SR", "RAA", "WAA", "Rating", "Stability"]
        ty = 0.882
        for x_pos, h in zip(b_cols, b_hdrs):
            ax.text(x_pos, ty, h, color=RR_BLUE, fontsize=7.2, fontweight='bold', transform=ax.transAxes)
        ax.plot([0.055, 0.945], [ty - 0.008, ty - 0.008], color=RR_PINK, linewidth=1.5, transform=ax.transAxes)

        curr_y = ty - 0.023
        for _, r in top10_bat.iterrows():
            ax.text(b_cols[0], curr_y, f"#{r['Rank']}", color=RR_PINK, fontsize=7.2, fontweight='bold', transform=ax.transAxes)
            ax.text(b_cols[1], curr_y, r['Player name'], color='#0F172A', fontsize=7.2, fontweight='bold', transform=ax.transAxes)
            ax.text(b_cols[2], curr_y, str(r['Player ID']), color='#475569', fontsize=7.0, transform=ax.transAxes)
            ax.text(b_cols[3], curr_y, short_team(r['Primary team/affiliation']), color='#334155', fontsize=7.0, transform=ax.transAxes)
            ax.text(b_cols[4], curr_y, str(r['Pressure balls faced']), color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            ax.text(b_cols[5], curr_y, f"{r['Pressure strike rate']:.1f}", color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            ax.text(b_cols[6], curr_y, f"+{r['Runs above expectation']:.1f}", color='#15803D', fontsize=7.0, fontweight='bold', transform=ax.transAxes)
            ax.text(b_cols[7], curr_y, f"+{r['Dismissal performance']:.2f}", color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            ax.text(b_cols[8], curr_y, f"{r['Auction Rating']:.1f}", color=RR_PINK, fontsize=7.4, fontweight='bold', transform=ax.transAxes)
            ax.text(b_cols[9], curr_y, r['Ranking stability'], color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            curr_y -= 0.020

        # Chart 6 Embed (Top 10 Batters Scorecard)
        img6 = mpimg.imread('outputs/charts/06_top10_batters.png')
        ax_img6 = fig.add_axes([0.05, 0.36, 0.90, 0.28])
        ax_img6.imshow(img6)
        ax_img6.axis('off')

        # Chart 4 Embed (Batter Impact vs Sample)
        img4 = mpimg.imread('outputs/charts/04_batter_impact_vs_sample.png')
        ax_img4 = fig.add_axes([0.05, 0.06, 0.90, 0.28])
        ax_img4.imshow(img4)
        ax_img4.axis('off')

        ax.text(0.5, 0.02, "SupeRR Selector Season 2 — Rajasthan Royals  |  Page 3 of 5", color=RR_GREY, fontsize=8, ha='center', transform=ax.transAxes)
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # PAGE 4: TOP 10 BOWLERS UNDER PRESSURE
        # =========================================================================
        print("Rendering PDF Page 4: Top 10 Bowlers...")
        fig = plt.figure(figsize=(8.27, 11.69), dpi=300)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        rect = plt.Rectangle((0, 0.93), 1, 0.07, facecolor=RR_BLUE, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.06, 0.96, "TOP 10 BOWLERS UNDER PRESSURE", color='white', fontsize=14, fontweight='bold', transform=ax.transAxes)
        ax.text(0.06, 0.94, "Official Global Ranked Selections & IPL-Relevant Recruitment Screening", color=RR_GOLD, fontsize=8.5, transform=ax.transAxes)

        # Bowlers Table with Canonical Player IDs and Clean Team Abbreviations
        ax.text(0.06, 0.905, "OFFICIAL GLOBAL TOP 10 BOWLERS SCORECARD (QUALIFYING HP BALLS >= 150)", color=RR_BLUE, fontsize=9.5, fontweight='bold', transform=ax.transAxes)

        bw_cols = [0.055, 0.105, 0.315, 0.385, 0.465, 0.535, 0.610, 0.695, 0.765, 0.855]
        bw_hdrs = ["Rank", "Player Name", "ID", "Team", "HP Bls", "Econ", "RPA", "Wkts", "Rating", "Stability"]
        ty = 0.882
        for x_pos, h in zip(bw_cols, bw_hdrs):
            ax.text(x_pos, ty, h, color=RR_BLUE, fontsize=7.2, fontweight='bold', transform=ax.transAxes)
        ax.plot([0.055, 0.945], [ty - 0.008, ty - 0.008], color=RR_PINK, linewidth=1.5, transform=ax.transAxes)

        curr_y = ty - 0.023
        for _, r in top10_bowl.iterrows():
            ax.text(bw_cols[0], curr_y, f"#{r['Rank']}", color=RR_BLUE, fontsize=7.2, fontweight='bold', transform=ax.transAxes)
            ax.text(bw_cols[1], curr_y, r['Player name'], color='#0F172A', fontsize=7.2, fontweight='bold', transform=ax.transAxes)
            ax.text(bw_cols[2], curr_y, str(r['Player ID']), color='#475569', fontsize=7.0, transform=ax.transAxes)
            ax.text(bw_cols[3], curr_y, short_team(r['Primary team/affiliation']), color='#334155', fontsize=7.0, transform=ax.transAxes)
            ax.text(bw_cols[4], curr_y, str(r['Pressure legal balls']), color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            ax.text(bw_cols[5], curr_y, f"{r['Pressure economy']:.2f}", color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            ax.text(bw_cols[6], curr_y, f"+{r['Runs prevented above expectation']:.1f}", color='#15803D', fontsize=7.0, fontweight='bold', transform=ax.transAxes)
            ax.text(bw_cols[7], curr_y, str(r['Wickets']), color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            ax.text(bw_cols[8], curr_y, f"{r['Auction Rating']:.1f}", color=RR_PINK, fontsize=7.4, fontweight='bold', transform=ax.transAxes)
            ax.text(bw_cols[9], curr_y, r['Ranking stability'], color='#0F172A', fontsize=7.0, transform=ax.transAxes)
            curr_y -= 0.020

        # Eligibility screening note directly under table
        elig_note = (
            "IPL-Relevant Recruitment Note: Ranks #3–#5 & #10 (Abrar, Afridi, Nawaz, Muqeem) reflect international/Other T20 performance with zero genuine IPL\n"
            "exposure and practical IPL recruitment unavailability based on historical participation precedent. Separate IPL-Relevant Top 10 Bowlers (CSV included)\n"
            "elevates Mohsin Khan (ID 6669, 62.5), Kuldeep Yadav (ID 3644, 62.5), Lungi Ngidi (ID 4641, 60.8), & Obed McCoy (ID 4837, 60.4) into #7–#10."
        )
        ax.text(0.055, curr_y - 0.002, elig_note, color='#475569', fontsize=6.6, linespacing=1.3, va='top', transform=ax.transAxes)

        # Chart 7 Embed (Top 10 Bowlers Scorecard)
        img7 = mpimg.imread('outputs/charts/07_top10_bowlers.png')
        ax_img7 = fig.add_axes([0.05, 0.34, 0.90, 0.26])
        ax_img7.imshow(img7)
        ax_img7.axis('off')

        # Chart 5 Embed (Bowler Impact vs Sample)
        img5 = mpimg.imread('outputs/charts/05_bowler_impact_vs_sample.png')
        ax_img5 = fig.add_axes([0.05, 0.055, 0.90, 0.27])
        ax_img5.imshow(img5)
        ax_img5.axis('off')

        ax.text(0.5, 0.02, "SupeRR Selector Season 2 — Rajasthan Royals  |  Page 4 of 5", color=RR_GREY, fontsize=8, ha='center', transform=ax.transAxes)
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # PAGE 5: RELIABILITY, SENSITIVITY & AUCTION STRATEGY
        # =========================================================================
        print("Rendering PDF Page 5: Consistency, Robustness & Auction Strategy...")
        fig = plt.figure(figsize=(8.27, 11.69), dpi=300)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        rect = plt.Rectangle((0, 0.93), 1, 0.07, facecolor=RR_BLUE, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.06, 0.96, "CONSISTENCY, STABILITY & RAJASTHAN ROYALS STRATEGY", color='white', fontsize=13.5, fontweight='bold', transform=ax.transAxes)
        ax.text(0.06, 0.94, "Match Repeatability Diagnostics & IPL 2027 Auction Roster Recommendations", color=RR_GOLD, fontsize=8.5, transform=ax.transAxes)

        # Chart 8 Embed (Consistency)
        img8 = mpimg.imread('outputs/charts/08_player_consistency.png')
        ax_img8 = fig.add_axes([0.05, 0.65, 0.90, 0.26])
        ax_img8.imshow(img8)
        ax_img8.axis('off')

        # Chart 10 Embed (Sensitivity)
        img10 = mpimg.imread('outputs/charts/10_ranking_sensitivity.png')
        ax_img10 = fig.add_axes([0.05, 0.37, 0.90, 0.26])
        ax_img10.imshow(img10)
        ax_img10.axis('off')

        # Auction Strategy Box (Properly anchored with va='top' inside box)
        ax.text(0.06, 0.345, "EVIDENCE-BASED RECRUITMENT CONSIDERATIONS (CONDITIONAL ON AVAILABILITY)", color=RR_BLUE, fontsize=9.8, fontweight='bold', va='top', transform=ax.transAxes)
        rect_strat = plt.Rectangle((0.06, 0.06), 0.88, 0.26, facecolor='#F8FAFC', edgecolor=RR_PINK, linewidth=1.5, transform=ax.transAxes, zorder=1)
        ax.add_patch(rect_strat)

        strat_text = (
            "1. Dhruv Jurel (#4 Batter, ID: 7260): Strong historical high-pressure finishing profile (184.8 SR, 70.4% consistency, +80.1 RAA\n"
            "   across 283 HP balls). Caution: moderate sample creates higher CPI-cutoff rank volatility; subject to IPL 2027 retention rules.\n\n"
            "2. Tristan Stubbs (#2 Batter, ID: 20702): High boundary output (180.0 SR) paired with wicket preservation (+12.48 WAA across\n"
            "   529 HP balls) makes him a strong recruitment consideration if released into the IPL 2027 auction pool (unconfirmed).\n\n"
            "3. Defensive Spin Profiles (Mitchell Santner ID: 4101 / Akeal Hosein ID: 2417): Both record < 6.85 pressure economy with > 70%\n"
            "   consistency. Caution: Hosein's rating rests predominantly on T20I volume (157 T20I vs 29 IPL HP balls).\n\n"
            "4. Death Pace & Domestic Depth: Matheesha Pathirana (#8 Global / #5 IPL-Relevant, ID: 8661, 49 HP wkts, +129.7 RPA) leads\n"
            "   death-overs profiles; Mohsin Khan (ID: 6669, 62.53) & Kuldeep Yadav (ID: 3644, 62.48) lead the next IPL-active bowler tier."
        )
        ax.text(0.075, 0.305, strat_text, color='#1E293B', fontsize=7.4, linespacing=1.35, va='top', transform=ax.transAxes, zorder=2)

        ax.text(0.5, 0.02, "SupeRR Selector Season 2 — Rajasthan Royals  |  Page 5 of 5  |  End of Report", color=RR_GREY, fontsize=8, ha='center', transform=ax.transAxes)
        pdf.savefig(fig)
        plt.close(fig)

    print(f"\n[SUCCESS] Multi-Page Publication PDF Report generated: {pdf_out} ({os.path.getsize(pdf_out):,} bytes)")

if __name__ == '__main__':
    run_generate_pdf()
