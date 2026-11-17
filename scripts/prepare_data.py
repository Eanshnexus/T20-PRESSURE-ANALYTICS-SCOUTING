"""
prepare_data.py - SupeRR Selector Season 2
Stage 1 of Pipeline: Ingestion, Validation, Cricket Accounting & Standardization.
"""

import os
import pandas as pd
import numpy as np

def run_prepare_data():
    print("="*60)
    print("STAGE 1: PREPARING DATA & ENFORCING CRICKET ACCOUNTING")
    print("="*60)

    # 1. Load Data
    print("Loading CSV datasets...")
    bbb = pd.read_csv('ball_by_ball.csv', low_memory=False)
    matches = pd.read_csv('matches.csv', low_memory=False)
    comps = pd.read_csv('competitions.csv', low_memory=False)
    teams = pd.read_csv('teams.csv', low_memory=False)
    pe = pd.read_csv('playing_eleven.csv', low_memory=False)
    mapping = pd.read_csv('competition_team_player_mapping.csv', low_memory=False)

    print(f"Loaded ball_by_ball: {len(bbb):,} rows")
    print(f"Loaded matches: {len(matches):,} rows")
    print(f"Loaded competitions: {len(comps):,} rows")

    # 2. Reconcile Matches & Abandoned Matches
    # Exclude matches with 0 deliveries (abandoned before toss/play)
    matches_contested = matches[matches['match_id'].isin(bbb['match_id'].unique())].copy()
    print(f"Contested matches: {len(matches_contested):,} (out of {len(matches):,} scheduled)")

    # 3. Cricket Accounting & Delivery Legality
    # A delivery is illegal if extras_type is wide, Overstep, or other (beamers/height no balls)
    bbb['is_illegal'] = bbb['extras_type'].isin(['wide', 'Overstep', 'other'])
    bbb['is_legal'] = ~bbb['is_illegal']

    # Batter ball faced: legal deliveries + no-balls (Overstep, other). Wides do NOT count as balls faced.
    bbb['is_ball_faced'] = bbb['extras_type'] != 'wide'

    # Batter runs: runs off the bat
    bbb['bat_runs'] = bbb['runs'].astype(int)

    # Total runs on the delivery: bat runs + extras1 + extras_2
    bbb['total_runs'] = bbb['bat_runs'] + bbb['extras1_runs'].fillna(0).astype(int) + bbb['extras_2_runs'].fillna(0).astype(int)

    # Bowler runs conceded: bat runs + wide extras + no-ball extras (Overstep, other)
    # Bowlers are NOT charged with byes, legbyes, or penalty runs
    bowler_extras_mask = bbb['extras_type'].isin(['wide', 'Overstep', 'other'])
    bbb['bowler_runs'] = bbb['bat_runs'] + np.where(bowler_extras_mask, bbb['extras1_runs'].fillna(0).astype(int), 0)

    # Dismissal Standardization
    bbb['dismissal_type'] = bbb['dismissal_type'].replace({'Obstracting the field': 'Obstructing the field'})

    # Handle Tilak Varma retired out anomaly (match 40709, delivery 127899)
    mask_tilak_retire = (bbb['match_id'] == 40709) & (bbb['dismissal_type'] == 'Retire Out') & (bbb['dismissed_player_id'].isnull())
    if mask_tilak_retire.any():
        bbb.loc[mask_tilak_retire, 'dismissed_player_id'] = 7897.0
        bbb.loc[mask_tilak_retire, 'is_wicket'] = True

    # Bowler wicket: dismissal_type in ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
    bowler_wicket_types = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
    bbb['is_bowler_wicket'] = bbb['is_wicket'] & bbb['dismissal_type'].isin(bowler_wicket_types)

    # Team wicket lost
    bbb['is_team_wicket'] = bbb['is_wicket'] | bbb['dismissed_player_id'].notnull()

    # Boundary indicators
    bbb['is_four'] = bbb['is_four'].astype(bool)
    bbb['is_six'] = bbb['is_six'].astype(bool)
    bbb['is_boundary'] = bbb['is_four'] | bbb['is_six']
    bbb['is_dot_ball'] = (bbb['total_runs'] == 0) & bbb['is_legal']

    # 4. Merge Match Metadata
    match_meta = matches_contested[['match_id', 'comp_id', 'match_date', 'stage', 'venue_id', 
                                    'venue_country', 'knock_out', 'result', 'revised_target', 
                                    'first_inn_revised_overs', 'second_inn_revised_overs']].copy()
    match_meta = match_meta.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

    bbb = bbb.merge(match_meta, on='match_id', how='left')

    # 5. Automated Data Integrity Assertions
    assert len(bbb) == 200999, f"Expected 200,999 rows, got {len(bbb)}"
    assert bbb['bat_runs'].between(0, 6).all(), "Batter runs out of bounds!"
    assert bbb['is_legal'].sum() == 192445, f"Legal deliveries count mismatch: {bbb['is_legal'].sum()}"
    assert bbb['is_bowler_wicket'].sum() == 10272, f"Bowler wickets mismatch: {bbb['is_bowler_wicket'].sum()}"
    print("Automated data assertions PASSED successfully!")

    # 6. Save Clean Deliveries Dataset
    os.makedirs('outputs/processed', exist_ok=True)
    out_path = 'outputs/processed/clean_deliveries.parquet'
    bbb.to_parquet(out_path, index=False)
    print(f"Clean deliveries saved to {out_path} ({os.path.getsize(out_path):,} bytes)")
    return bbb

if __name__ == '__main__':
    run_prepare_data()
