"""
generate_visualizations.py - SupeRR Selector Season 2
Stage 8 of Pipeline: Generate 10 High-Resolution Analytical Charts for Report.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set Design Theme
RR_PINK = '#EA1A7F'
RR_BLUE = '#0B1A30'
RR_GOLD = '#D4AF37'
RR_CYAN = '#00A3E0'
RR_GREY = '#708090'
LIGHT_BG = '#F8F9FA'

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#FAFAFA'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

def run_generate_visualizations():
    print("="*60)
    print("STAGE 8: GENERATING ANALYTICAL VISUALIZATIONS")
    print("="*60)
    os.makedirs('outputs/charts', exist_ok=True)

    # Load Data
    dist_df = pd.read_csv('outputs/tables/pressure_distribution.csv')
    df = pd.read_parquet('outputs/processed/deliveries_with_expected.parquet')
    top_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
    top_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')
    bat_all = pd.read_csv('outputs/tables/batter_metrics.csv')
    bowl_all = pd.read_csv('outputs/tables/bowler_metrics.csv')
    fmt_df = pd.read_csv('outputs/tables/format_comparison.csv')
    sens_df = pd.read_csv('outputs/tables/ranking_sensitivity.csv')

    # -------------------------------------------------------------
    # Chart 1: Dataset Coverage & Deliveries by Season and Format
    # -------------------------------------------------------------
    print("Generating Chart 01: Dataset Coverage...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    df['comp_group'] = np.where(df['comp_name'].str.startswith('IPL', na=False), 'Genuine IPL (2022–2026)', 'International & Emerging T20')
    season_fmt = df.groupby(['season', 'comp_group']).size().unstack().fillna(0)[['Genuine IPL (2022–2026)', 'International & Emerging T20']]
    season_fmt.plot(kind='bar', stacked=True, ax=ax, color=[RR_PINK, RR_BLUE], width=0.6)
    ax.set_title('Deliveries Analyzed Across Seasons and Competitions (2022–2026)', fontsize=14, fontweight='bold', pad=15, color=RR_BLUE)
    ax.set_xlabel('Season', fontsize=11, fontweight='bold')
    ax.set_ylabel('Total Contested Deliveries', fontsize=11, fontweight='bold')
    ax.legend(['Genuine IPL (2022–2026)', 'International & Emerging T20'], frameon=True, facecolor='white', framealpha=0.9)
    plt.xticks(rotation=0)
    for p in ax.patches:
        height = p.get_height()
        if height > 2000:
            ax.annotate(f"{int(height):,}", (p.get_x() + p.get_width() / 2., p.get_y() + height / 2.),
                        ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    plt.tight_layout()
    plt.savefig('outputs/charts/01_dataset_coverage.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 2: Pressure Distribution & CPI Density
    # -------------------------------------------------------------
    print("Generating Chart 02: Pressure Distribution...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    # CPI Density
    sns.kdeplot(df['cpi'], ax=ax1, fill=True, color=RR_BLUE, alpha=0.3, linewidth=2)
    ax1.axvline(0.60, color=RR_PINK, linestyle='--', linewidth=2, label='High Pressure Cutoff (CPI >= 0.60)')
    ax1.axvline(0.35, color=RR_GOLD, linestyle=':', linewidth=2, label='Medium Pressure Cutoff (0.35)')
    ax1.set_title('Composite Pressure Index (CPI) Density Distribution', fontsize=12, fontweight='bold', color=RR_BLUE)
    ax1.set_xlabel('Pre-Delivery CPI Score', fontsize=11)
    ax1.set_ylabel('Density', fontsize=11)
    ax1.legend(loc='upper right')

    # Breakdown by Phase
    phase_data = dist_df[dist_df['Segment'].str.startswith('Phase:')].copy()
    phase_data['Phase'] = phase_data['Segment'].str.replace('Phase: ', '')
    x = np.arange(len(phase_data))
    width = 0.25
    ax2.bar(x - width, phase_data['High_Pct'], width, label='High Pressure', color=RR_PINK)
    ax2.bar(x, phase_data['Med_Pct'], width, label='Medium Pressure', color=RR_GOLD)
    ax2.bar(x + width, phase_data['Low_Pct'], width, label='Low/Ordinary', color=RR_BLUE)
    ax2.set_title('Pressure Classification Breakdown by Innings Phase', fontsize=12, fontweight='bold', color=RR_BLUE)
    ax2.set_xticks(x)
    ax2.set_xticklabels(phase_data['Phase'])
    ax2.set_ylabel('Percentage of Phase Deliveries (%)', fontsize=11)
    ax2.legend()
    plt.tight_layout()
    plt.savefig('outputs/charts/02_pressure_distribution.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 3: Pressure vs Ordinary Strike Rate & Economy Deltas
    # -------------------------------------------------------------
    print("Generating Chart 03: Pressure vs Ordinary...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # Batters (HP SR vs Ord SR)
    top_bat_merge = top_bat.merge(bat_all[['striker_id', 'ord_sr', 'hp_sr']], left_on='Player ID', right_on='striker_id')
    ax1.scatter(top_bat_merge['ord_sr'], top_bat_merge['hp_sr'], color=RR_PINK, s=120, edgecolors=RR_BLUE, zorder=5)
    lims = [120, 220]
    ax1.plot(lims, lims, '--', color=RR_GREY, alpha=0.7, label='Equal Rate Line')
    for _, r in top_bat_merge.iterrows():
        ax1.annotate(r['Player name'].split()[-1], (r['ord_sr'] + 1.2, r['hp_sr']), fontsize=9)
    ax1.set_title('Top 10 Batters: Pressure SR vs Ordinary SR', fontsize=12, fontweight='bold', color=RR_BLUE)
    ax1.set_xlabel('Ordinary Situation Strike Rate', fontsize=11)
    ax1.set_ylabel('High-Pressure Strike Rate', fontsize=11)
    ax1.legend(loc='lower right')

    # Bowlers (HP Econ vs Ord Econ)
    top_bowl_merge = top_bowl.merge(bowl_all[['bowler_id', 'ord_econ', 'hp_econ']], left_on='Player ID', right_on='bowler_id')
    ax2.scatter(top_bowl_merge['ord_econ'], top_bowl_merge['hp_econ'], color=RR_BLUE, s=120, edgecolors=RR_PINK, zorder=5)
    lims_b = [4.5, 9.5]
    ax2.plot(lims_b, lims_b, '--', color=RR_GREY, alpha=0.7, label='Equal Rate Line')
    for _, r in top_bowl_merge.iterrows():
        ax2.annotate(r['Player name'].split()[-1], (r['ord_econ'] + 0.1, r['hp_econ']), fontsize=9)
    ax2.set_title('Top 10 Bowlers: Pressure Economy vs Ordinary Economy', fontsize=12, fontweight='bold', color=RR_BLUE)
    ax2.set_xlabel('Ordinary Situation Economy', fontsize=11)
    ax2.set_ylabel('High-Pressure Economy', fontsize=11)
    ax2.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig('outputs/charts/03_pressure_vs_ordinary.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 4: Batter Impact vs Sample Size
    # -------------------------------------------------------------
    print("Generating Chart 04: Batter Impact vs Sample...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    qual_bat = bat_all[bat_all['hp_bf'] >= 60].copy()
    ax.scatter(qual_bat['hp_bf'], qual_bat['hp_raa'], color=RR_BLUE, alpha=0.4, s=50, label='Eligible Pool (>=60 BF)')
    top_bat_pts = qual_bat[qual_bat['striker_id'].isin(top_bat['Player ID'])]
    ax.scatter(top_bat_pts['hp_bf'], top_bat_pts['hp_raa'], color=RR_PINK, s=150, edgecolors='black', label='Top 10 Batters', zorder=6)
    for _, r in top_bat_pts.iterrows():
        ax.annotate(r['name'], (r['hp_bf'] + 8, r['hp_raa'] - 2), fontsize=8.5, fontweight='bold', color=RR_BLUE)
    ax.axhline(0, color=RR_GREY, linestyle=':')
    ax.axvline(120, color=RR_GOLD, linestyle='--', label='Primary Eligibility Threshold (120 BF)')
    ax.set_title('Batter Pressure Performance (RAA) vs Volume of Pressure Deliveries Faced', fontsize=13, fontweight='bold', color=RR_BLUE)
    ax.set_xlabel('High-Pressure Balls Faced', fontsize=11, fontweight='bold')
    ax.set_ylabel('Runs Added Above Expectation (RAA)', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig('outputs/charts/04_batter_impact_vs_sample.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 5: Bowler Impact vs Sample Size
    # -------------------------------------------------------------
    print("Generating Chart 05: Bowler Impact vs Sample...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    qual_bowl = bowl_all[bowl_all['hp_balls'] >= 60].copy()
    ax.scatter(qual_bowl['hp_balls'], qual_bowl['hp_rpa'], color=RR_PINK, alpha=0.4, s=50, label='Eligible Pool (>=60 Balls)')
    top_bowl_pts = qual_bowl[qual_bowl['bowler_id'].isin(top_bowl['Player ID'])]
    ax.scatter(top_bowl_pts['hp_balls'], top_bowl_pts['hp_rpa'], color=RR_BLUE, s=150, edgecolors='black', label='Top 10 Bowlers', zorder=6)
    for _, r in top_bowl_pts.iterrows():
        ax.annotate(r['name'], (r['hp_balls'] + 8, r['hp_rpa'] - 2), fontsize=8.5, fontweight='bold', color=RR_PINK)
    ax.axhline(0, color=RR_GREY, linestyle=':')
    ax.axvline(150, color=RR_GOLD, linestyle='--', label='Primary Eligibility Threshold (150 Balls)')
    ax.set_title('Bowler Pressure Performance (RPA) vs Volume of Pressure Legal Balls Bowled', fontsize=13, fontweight='bold', color=RR_BLUE)
    ax.set_xlabel('High-Pressure Legal Balls Bowled', fontsize=11, fontweight='bold')
    ax.set_ylabel('Runs Prevented Above Expectation (RPA)', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig('outputs/charts/05_bowler_impact_vs_sample.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 6: Top 10 Batters Scorecard
    # -------------------------------------------------------------
    print("Generating Chart 06: Top 10 Batters Scorecard...")
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    plot_bat = top_bat.sort_values('Rank', ascending=False)
    y_pos = np.arange(len(plot_bat))
    bars = ax.barh(y_pos, plot_bat['Auction Rating'], color=RR_PINK, height=0.6, edgecolor=RR_BLUE)
    ax.set_yticks(y_pos)
    labels = [f"#{r['Rank']} {r['Player name']} ({r['Primary team/affiliation'].split()[-1]})" for _, r in plot_bat.iterrows()]
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_xlabel('Auction Pressure Rating (0–100 Scale)', fontsize=11, fontweight='bold')
    ax.set_title('Rajasthan Royals SupeRR Selector: Top 10 Batters Under Pressure', fontsize=14, fontweight='bold', color=RR_BLUE, pad=15)
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.1f}", (w - 4.5, bar.get_y() + bar.get_height() / 2.),
                    ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    ax.set_xlim(80, 100)
    plt.tight_layout()
    plt.savefig('outputs/charts/06_top10_batters.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 7: Top 10 Bowlers Scorecard
    # -------------------------------------------------------------
    print("Generating Chart 07: Top 10 Bowlers Scorecard...")
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    plot_bowl = top_bowl.sort_values('Rank', ascending=False)
    y_pos = np.arange(len(plot_bowl))
    bars = ax.barh(y_pos, plot_bowl['Auction Rating'], color=RR_BLUE, height=0.6, edgecolor=RR_PINK)
    ax.set_yticks(y_pos)
    labels = [f"#{r['Rank']} {r['Player name']} ({r['Primary team/affiliation'].split()[-1]})" for _, r in plot_bowl.iterrows()]
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_xlabel('Auction Pressure Rating (0–100 Scale)', fontsize=11, fontweight='bold')
    ax.set_title('Rajasthan Royals SupeRR Selector: Top 10 Bowlers Under Pressure', fontsize=14, fontweight='bold', color=RR_BLUE, pad=15)
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.1f}", (w - 3.5, bar.get_y() + bar.get_height() / 2.),
                    ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    ax.set_xlim(55, 90)
    plt.tight_layout()
    plt.savefig('outputs/charts/07_top10_bowlers.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 8: Match-to-Match Consistency (% Positive Impact Matches)
    # -------------------------------------------------------------
    print("Generating Chart 08: Player Consistency...")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    comb_top = pd.concat([
        top_bat[['Player name', 'Match consistency', 'Primary team/affiliation']].assign(Discipline='Batter'),
        top_bowl[['Player name', 'Match consistency', 'Primary team/affiliation']].assign(Discipline='Bowler')
    ])
    comb_top['Consistency_Num'] = comb_top['Match consistency'].str.replace('%', '').astype(float)
    comb_top = comb_top.sort_values('Consistency_Num', ascending=True)

    y_pos = np.arange(len(comb_top))
    colors = [RR_PINK if d == 'Batter' else RR_BLUE for d in comb_top['Discipline']]
    ax.barh(y_pos, comb_top['Consistency_Num'], color=colors, height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{r['Player name']} ({r['Discipline']})" for _, r in comb_top.iterrows()], fontsize=9)
    ax.set_xlabel('Percentage of High-Pressure Matches with Net Positive Impact (%)', fontsize=11, fontweight='bold')
    ax.set_title('Match-to-Match Performance Reliability (% Positive Impact Outings)', fontsize=13, fontweight='bold', color=RR_BLUE)
    ax.axvline(50, color=RR_GREY, linestyle='--', label='50% Neutral Baseline')
    ax.set_xlim(35, 90)
    ax.legend()
    plt.tight_layout()
    plt.savefig('outputs/charts/08_player_consistency.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 9: IPL vs T20I Performance Comparison
    # -------------------------------------------------------------
    print("Generating Chart 09: IPL vs T20I Comparison...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    bat_fmt = fmt_df[fmt_df['Discipline'] == 'Batting'].copy()
    bowl_fmt = fmt_df[fmt_df['Discipline'] == 'Bowling'].copy()

    # Batters IPL vs T20I Strike Rate
    x = np.arange(len(bat_fmt))
    w = 0.35
    ax1.bar(x - w/2, bat_fmt['IPL_SR'], w, label='IPL Strike Rate', color=RR_BLUE)
    ax1.bar(x + w/2, bat_fmt['T20I_SR'], w, label='T20I Strike Rate', color=RR_PINK)
    ax1.set_xticks(x)
    ax1.set_xticklabels([n.split()[-1] for n in bat_fmt['Player Name']], rotation=45, ha='right', fontsize=9)
    ax1.set_title('Top 10 Batters: Strike Rate in IPL vs T20I', fontsize=12, fontweight='bold', color=RR_BLUE)
    ax1.set_ylabel('Strike Rate under Pressure', fontsize=11)
    ax1.legend()

    # Bowlers IPL vs T20I Economy
    x_b = np.arange(len(bowl_fmt))
    ax2.bar(x_b - w/2, bowl_fmt['IPL_SR'], w, label='IPL Economy', color=RR_BLUE)
    ax2.bar(x_b + w/2, bowl_fmt['T20I_SR'], w, label='T20I Economy', color=RR_PINK)
    ax2.set_xticks(x_b)
    ax2.set_xticklabels([n.split()[-1] for n in bowl_fmt['Player Name']], rotation=45, ha='right', fontsize=9)
    ax2.set_title('Top 10 Bowlers: Economy in IPL vs T20I', fontsize=12, fontweight='bold', color=RR_BLUE)
    ax2.set_ylabel('Economy Rate under Pressure (Lower is Better)', fontsize=11)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('outputs/charts/09_ipl_vs_t20i.png')
    plt.close()

    # -------------------------------------------------------------
    # Chart 10: Ranking Sensitivity & Stability Matrix
    # -------------------------------------------------------------
    print("Generating Chart 10: Ranking Sensitivity...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    stability_counts = sens_df.groupby(['Discipline', 'Stability_Class']).size().unstack().fillna(0)
    stability_counts[['High', 'Moderate', 'Volatile']].plot(
        kind='bar', stacked=True, ax=ax, 
        color=['#2ECC71', RR_GOLD, '#E74C3C'], width=0.5
    )
    ax.set_title('Top 10 Player Ranking Stability Across 4 Sensitivity Specifications', fontsize=13, fontweight='bold', color=RR_BLUE)
    ax.set_xlabel('Discipline', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Players in Top 10', fontsize=11, fontweight='bold')
    ax.legend(['High Stability (Rank Std <= 3.5)', 'Moderate Stability', 'Volatile'], frameon=True)
    plt.xticks(rotation=0, fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig('outputs/charts/10_ranking_sensitivity.png')
    plt.close()

    print("All 10 charts generated successfully in outputs/charts/")

if __name__ == '__main__':
    run_generate_visualizations()
