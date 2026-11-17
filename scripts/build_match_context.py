"""
build_match_context.py - SupeRR Selector Season 2
Stage 2 of Pipeline: Reconstruct Pre-Delivery Game State with Zero Leakage.
"""

import os
import pandas as pd
import numpy as np

def run_build_match_context():
    print("="*60)
    print("STAGE 2: RECONSTRUCTING PRE-DELIVERY MATCH CONTEXT")
    print("="*60)

    # 1. Load Clean Deliveries
    df = pd.read_parquet('outputs/processed/clean_deliveries.parquet')
    print(f"Loaded deliveries: {len(df):,} rows")

    # 2. Sort chronologically
    df = df.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)

    # 3. Compute Innings Totals for Chase Targets
    print("Computing Innings totals and targets...")
    inn_totals = df.groupby(['match_id', 'innings'])['total_runs'].sum().unstack()

    # Target calculation for Innings 2:
    # If revised_target is non-null, use revised_target; else Innings 1 total + 1
    target_series = np.where(df['revised_target'].notnull(), 
                             df['revised_target'], 
                             df['match_id'].map(inn_totals[1]) + 1)
    df['innings_target'] = np.where(df['innings'] == 2, target_series, np.nan)

    # For Super Over Innings 4: target is Innings 3 total + 1
    if 3 in inn_totals.columns and 4 in inn_totals.columns:
        so_target_series = df['match_id'].map(inn_totals[3]) + 1
        df.loc[df['innings'] == 4, 'innings_target'] = so_target_series

    # 4. Groupwise Cumulative Operations (STRICTLY EXCLUDING CURRENT DELIVERY)
    print("Calculating pre-delivery state variables...")
    grp = df.groupby(['match_id', 'innings'])

    # Cumulative runs before ball
    df['cum_runs_before'] = grp['total_runs'].cumsum() - df['total_runs']

    # Cumulative wickets lost before ball
    df['cum_wickets_before'] = grp['is_team_wicket'].cumsum() - df['is_team_wicket']
    df['wickets_in_hand'] = 10 - df['cum_wickets_before']

    # Cumulative legal balls bowled before ball
    df['cum_legal_balls'] = grp['is_legal'].cumsum() - df['is_legal']

    # Innings Max Legal Balls (Handling DLS revised overs)
    df['max_legal_balls'] = 120
    inn1_mask = (df['innings'] == 1) & (df['first_inn_revised_overs'].notnull())
    df.loc[inn1_mask, 'max_legal_balls'] = (df.loc[inn1_mask, 'first_inn_revised_overs'] * 6).astype(int)

    inn2_mask = (df['innings'] == 2) & (df['second_inn_revised_overs'].notnull())
    df.loc[inn2_mask, 'max_legal_balls'] = (df.loc[inn2_mask, 'second_inn_revised_overs'] * 6).astype(int)

    so_mask = df['innings'] >= 3
    df.loc[so_mask, 'max_legal_balls'] = 6

    # Legal Balls Remaining
    df['balls_remaining'] = np.maximum(0, df['max_legal_balls'] - df['cum_legal_balls'])

    # Current Run Rate (CRR) before delivery
    df['crr'] = np.where(df['cum_legal_balls'] > 0, (df['cum_runs_before'] * 6.0) / df['cum_legal_balls'], 0.0)

    # Runs Needed in Chase
    df['runs_needed'] = np.where(df['innings'].isin([2, 4]), 
                                 np.maximum(0, df['innings_target'] - df['cum_runs_before']), 
                                 0)

    # Required Run Rate (RRR) before delivery
    df['rrr'] = np.where((df['innings'].isin([2, 4])) & (df['balls_remaining'] > 0),
                         (df['runs_needed'] * 6.0) / df['balls_remaining'],
                         np.where(df['innings'].isin([2, 4]), df['runs_needed'] * 6.0, 0.0))

    # Innings Phase
    conditions = [
        df['overid'] <= 6,
        (df['overid'] >= 7) & (df['overid'] <= 15),
        df['overid'] >= 16
    ]
    choices = ['Powerplay', 'Middle', 'Death']
    df['innings_phase'] = np.select(conditions, choices, default='Middle')

    # Knockout stage standardization
    df['is_knockout'] = (df['knock_out'] == 1) | df['stage'].isin(['Final', 'Qualifier', 'Eliminator', 'Semi Final'])

    # 5. Integrity Verification
    print("Verifying pre-delivery calculations...")
    assert (df['cum_runs_before'] >= 0).all(), "Negative cumulative runs detected!"
    assert (df['cum_wickets_before'] >= 0).all(), "Negative cumulative wickets detected!"
    assert (df['wickets_in_hand'].between(0, 10)).all(), "Wickets in hand out of bounds [0, 10]!"
    assert (df['balls_remaining'] >= 0).all(), "Negative balls remaining detected!"
    assert df[df['innings'] == 2]['innings_target'].notnull().all(), "Missing targets in Innings 2!"
    print("Context integrity assertions PASSED successfully!")

    # 6. Save Processed Dataset
    out_path = 'outputs/processed/deliveries_with_context.parquet'
    df.to_parquet(out_path, index=False)
    print(f"Context deliveries saved to {out_path} ({os.path.getsize(out_path):,} bytes)")
    return df

if __name__ == '__main__':
    run_build_match_context()
