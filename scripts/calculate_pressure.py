"""
calculate_pressure.py - SupeRR Selector Season 2
Stage 3 of Pipeline: Construct Dual Pressure Models (Rule-Based & Continuous CPI).
"""

import os
import pandas as pd
import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15, 15)))

def run_calculate_pressure():
    print("="*60)
    print("STAGE 3: CALCULATING COMPOSITE PRESSURE INDEX (CPI)")
    print("="*60)

    # 1. Load Context Deliveries
    df = pd.read_parquet('outputs/processed/deliveries_with_context.parquet')
    print(f"Loaded deliveries: {len(df):,} rows")

    # 2. MODEL A: Transparent Domain Rule-Based Pressure Model
    print("Building Model A: Rule-Based Pressure Classification...")
    
    # Innings 2 (Chases) High Pressure Conditions
    chase_high_rrr = (df['innings'] == 2) & (
        ((df['rrr'] >= 11.5) & (df['balls_remaining'] <= 60)) |
        ((df['rrr'] >= 10.0) & (df['balls_remaining'] <= 36)) |
        ((df['rrr'] >= 13.0))
    )
    chase_close_death = (df['innings'] == 2) & (df['overid'] >= 16) & (df['runs_needed'] > 0) & (df['runs_needed'] <= 55)
    chase_wicket_crisis = (df['innings'] == 2) & (df['wickets_in_hand'] <= 4) & (df['runs_needed'] > 15)
    chase_high = chase_high_rrr | chase_close_death | chase_wicket_crisis

    # Innings 1 (Target Setting) High Pressure Conditions
    inn1_early_collapse = (df['innings'] == 1) & (
        ((df['overid'] <= 6) & (df['wickets_in_hand'] <= 7)) |
        ((df['overid'] <= 12) & (df['wickets_in_hand'] <= 5))
    )
    inn1_death_leverage = (df['innings'] == 1) & (df['overid'] >= 16) & (
        (df['wickets_in_hand'] <= 5) | (df['is_knockout'])
    )
    inn1_high = inn1_early_collapse | inn1_death_leverage

    # Super Overs (Innings 3 & 4)
    super_over_high = df['innings'] >= 3

    # Knockout Playoff Boost
    knockout_boost = (df['is_knockout']) & (df['overid'] >= 14) & (df['wickets_in_hand'] <= 6)

    rule_high = chase_high | inn1_high | super_over_high | knockout_boost

    # Medium Pressure Conditions
    chase_medium = (df['innings'] == 2) & (~rule_high) & (
        ((df['overid'] >= 11) & (df['rrr'] >= 8.5)) |
        ((df['wickets_in_hand'] <= 6) & (df['runs_needed'] > 25)) |
        ((df['overid'] >= 16) & (df['runs_needed'] > 0))
    )
    inn1_medium = (df['innings'] == 1) & (~rule_high) & (
        (df['overid'] >= 16) |
        ((df['overid'] >= 7) & (df['wickets_in_hand'] <= 6))
    )
    rule_medium = (~rule_high) & (chase_medium | inn1_medium)

    df['pressure_rule'] = np.select([rule_high, rule_medium], ['High', 'Medium'], default='Low')

    # 3. MODEL B: Statistically Derived Continuous Composite Pressure Index (CPI)
    print("Building Model B: Continuous Composite Pressure Index (CPI)...")

    # Second Innings Latent Factor
    # Standardized components: RRR difficulty, wicket scarcity, balls remaining compression, rate acceleration
    z_rrr = (df['rrr'] - 9.0) / 3.0
    z_wkts_inn2 = (5.0 - df['wickets_in_hand']) / 2.0
    z_balls_inn2 = (60.0 - df['balls_remaining']) / 30.0
    z_accel = (df['rrr'] - df['crr']) / 3.0

    z_chase = 0.40 * z_rrr + 0.30 * z_wkts_inn2 + 0.15 * z_balls_inn2 + 0.15 * z_accel
    cpi_chase = sigmoid(z_chase)

    # First Innings Latent Factor
    # Standardized components: death progression, resource depletion / collapse, death phase indicator
    z_prog_inn1 = (df['cum_legal_balls'] - 60.0) / 30.0
    z_wkts_inn1 = (7.0 - df['wickets_in_hand']) / 2.0
    is_death_num = (df['overid'] >= 16).astype(float)
    is_collapse_num = inn1_early_collapse.astype(float)

    z_inn1 = 0.25 * z_prog_inn1 + 0.35 * z_wkts_inn1 + 0.25 * is_death_num + 0.15 * is_collapse_num
    cpi_inn1 = sigmoid(z_inn1)

    # Super Overs: maximum base index
    cpi_base = np.where(df['innings'] >= 3, 1.0,
               np.where(df['innings'].isin([2, 4]), cpi_chase, cpi_inn1))

    # Stakes multiplier for knockout matches
    stakes_mult = np.where(df['is_knockout'], 1.15, 1.0)
    df['cpi'] = np.clip(cpi_base * stakes_mult, 0.0, 1.0)

    # CPI Category Thresholds (Primary: High >= 0.60, Medium [0.35, 0.60), Low < 0.35)
    cpi_conds = [
        df['cpi'] >= 0.60,
        (df['cpi'] >= 0.35) & (df['cpi'] < 0.60)
    ]
    df['pressure_category'] = np.select(cpi_conds, ['High', 'Medium'], default='Low')
    df['is_high_pressure'] = df['pressure_category'] == 'High'

    # Alternative Sensitivity Thresholds
    df['is_pressure_strict'] = df['cpi'] >= 0.70
    df['is_pressure_broad'] = df['cpi'] >= 0.50

    # 4. Generate Comprehensive Distribution Summary Table
    print("Computing pressure distributions across segments...")
    dist_records = []

    def compute_dist(sub_df, segment_name):
        n = len(sub_df)
        if n == 0:
            return
        n_high = (sub_df['pressure_category'] == 'High').sum()
        n_med = (sub_df['pressure_category'] == 'Medium').sum()
        n_low = (sub_df['pressure_category'] == 'Low').sum()
        mean_cpi = sub_df['cpi'].mean()
        dist_records.append({
            'Segment': segment_name,
            'Total_Deliveries': n,
            'High_Count': n_high,
            'High_Pct': round(n_high / n * 100, 2),
            'Med_Count': n_med,
            'Med_Pct': round(n_med / n * 100, 2),
            'Low_Count': n_low,
            'Low_Pct': round(n_low / n * 100, 2),
            'Mean_CPI': round(mean_cpi, 4)
        })

    compute_dist(df, 'All Deliveries')
    for inn in [1, 2, 3, 4]:
        compute_dist(df[df['innings'] == inn], f'Innings {inn}')
    for fmt in df['match_format'].dropna().unique():
        compute_dist(df[df['match_format'] == fmt], f'Format: {fmt}')
    for ph in ['Powerplay', 'Middle', 'Death']:
        compute_dist(df[df['innings_phase'] == ph], f'Phase: {ph}')
    for s in sorted(df['season'].dropna().unique()):
        compute_dist(df[df['season'] == s], f'Season: {s}')
    compute_dist(df[df['is_knockout']], 'Knockout Matches')
    compute_dist(df[~df['is_knockout']], 'League/Group Matches')

    dist_df = pd.DataFrame(dist_records)
    out_table = 'outputs/tables/pressure_distribution.csv'
    dist_df.to_csv(out_table, index=False)
    print(f"Pressure distribution table saved to {out_table}")
    print(dist_df.to_string())

    # 5. Save Processed Deliveries
    out_path = 'outputs/processed/deliveries_with_pressure.parquet'
    df.to_parquet(out_path, index=False)
    print(f"Deliveries with pressure saved to {out_path} ({os.path.getsize(out_path):,} bytes)")
    return df

if __name__ == '__main__':
    run_calculate_pressure()
