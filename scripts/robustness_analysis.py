"""
robustness_analysis.py - SupeRR Selector Season 2
Stage 7 of Pipeline: Rigorous Sensitivity, Stability, Bootstrap, and Format Comparability.
"""

import os
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

def run_robustness_analysis():
    print("="*60)
    print("STAGE 7: ROBUSTNESS, SENSITIVITY & FORMAT COMPARISON")
    print("="*60)

    # 1. Load Data
    df = pd.read_parquet('outputs/processed/deliveries_with_expected.parquet')
    mapping = pd.read_csv('competition_team_player_mapping.csv')
    top10_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
    top10_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')
    bat_all = pd.read_csv('outputs/tables/batter_metrics.csv')
    bowl_all = pd.read_csv('outputs/tables/bowler_metrics.csv')

    # 2. Format Comparison Table (IPL vs T20I)
    print("Analyzing format differences and format-specific rankings...")
    format_records = []
    for pid in top10_bat['Player ID']:
        row = bat_all[bat_all['striker_id'] == pid].iloc[0]
        format_records.append({
            'Player ID': pid,
            'Player Name': row['name'],
            'Discipline': 'Batting',
            'Overall_Rank': top10_bat[top10_bat['Player ID'] == pid]['Rank'].values[0],
            'IPL_Balls': row['ipl_bf'],
            'IPL_SR': round(row['ipl_sr'], 1),
            'IPL_RAA': round(row['ipl_raa'], 1),
            'T20I_Balls': row['t20i_bf'],
            'T20I_SR': round(row['t20i_sr'], 1),
            'T20I_RAA': round(row['t20i_raa'], 1),
            'Primary_Format_Driver': 'IPL' if row['ipl_bf'] > row['t20i_bf'] else 'T20I'
        })

    for pid in top10_bowl['Player ID']:
        row = bowl_all[bowl_all['bowler_id'] == pid].iloc[0]
        format_records.append({
            'Player ID': pid,
            'Player Name': row['name'],
            'Discipline': 'Bowling',
            'Overall_Rank': top10_bowl[top10_bowl['Player ID'] == pid]['Rank'].values[0],
            'IPL_Balls': row['ipl_balls'],
            'IPL_SR': round(row['ipl_econ'], 2),  # Economy
            'IPL_RAA': round(row['ipl_rpa'], 1),  # RPA
            'T20I_Balls': row['t20i_balls'],
            'T20I_SR': round(row['t20i_econ'], 2),
            'T20I_RAA': round(row['t20i_rpa'], 1),
            'Primary_Format_Driver': 'IPL' if row['ipl_balls'] > row['t20i_balls'] else 'T20I'
        })

    format_df = pd.DataFrame(format_records)
    format_df.to_csv('outputs/tables/format_comparison.csv', index=False)
    print(f"Saved format comparison to outputs/tables/format_comparison.csv")

    # 3. Sensitivity Under Alternative Pressure Definitions & Weighting
    print("Testing ranking sensitivity across alternative specifications...")
    specs = {
        'Primary (CPI >= 0.60)': df['is_high_pressure'].values,
        'Strict (CPI >= 0.70)': (df['cpi'] >= 0.70).values,
        'Broad (CPI >= 0.50)': (df['cpi'] >= 0.50).values,
        'Rule-Based Model A': (df['pressure_rule'] == 'High').values
    }

    # Evaluate Batters Sensitivity
    bat_sensitivity_records = []
    for pid in top10_bat['Player ID']:
        name = top10_bat[top10_bat['Player ID'] == pid]['Player name'].values[0]
        ranks_in_specs = {}
        for spec_name, mask in specs.items():
            sub = df[df['is_ball_faced'] & mask]
            agg = sub.groupby('striker_id').agg(bf=('bat_runs', 'count'), raa=('bat_raa', 'sum')).reset_index()
            agg = agg[agg['bf'] >= 60].sort_values('raa', ascending=False).reset_index(drop=True)
            if pid in agg['striker_id'].values:
                ranks_in_specs[spec_name] = int(agg[agg['striker_id'] == pid].index[0] + 1)
            else:
                ranks_in_specs[spec_name] = 999

        valid_ranks = [r for r in ranks_in_specs.values() if r < 999]
        rank_std = np.std(valid_ranks) if len(valid_ranks) > 1 else 0.0
        stability_flag = 'High' if rank_std <= 3.5 else ('Moderate' if rank_std <= 7.0 else 'Volatile')

        rec = {
            'Player ID': pid,
            'Player Name': name,
            'Discipline': 'Batting',
            'Primary_Rank': top10_bat[top10_bat['Player ID'] == pid]['Rank'].values[0],
            'Strict_CPI_0.70_Rank': ranks_in_specs.get('Strict (CPI >= 0.70)', 'N/A'),
            'Broad_CPI_0.50_Rank': ranks_in_specs.get('Broad (CPI >= 0.50)', 'N/A'),
            'Rule_Model_A_Rank': ranks_in_specs.get('Rule-Based Model A', 'N/A'),
            'Rank_Std_Dev': round(rank_std, 2),
            'Stability_Class': stability_flag
        }
        bat_sensitivity_records.append(rec)

    # Evaluate Bowlers Sensitivity
    bowl_sensitivity_records = []
    for pid in top10_bowl['Player ID']:
        name = top10_bowl[top10_bowl['Player ID'] == pid]['Player name'].values[0]
        ranks_in_specs = {}
        for spec_name, mask in specs.items():
            sub = df[df['is_legal'] & mask]
            agg = sub.groupby('bowler_id').agg(balls=('bowler_runs', 'count'), rpa=('bowl_rpa', 'sum')).reset_index()
            agg = agg[agg['balls'] >= 60].sort_values('rpa', ascending=False).reset_index(drop=True)
            if pid in agg['bowler_id'].values:
                ranks_in_specs[spec_name] = int(agg[agg['bowler_id'] == pid].index[0] + 1)
            else:
                ranks_in_specs[spec_name] = 999

        valid_ranks = [r for r in ranks_in_specs.values() if r < 999]
        rank_std = np.std(valid_ranks) if len(valid_ranks) > 1 else 0.0
        stability_flag = 'High' if rank_std <= 3.5 else ('Moderate' if rank_std <= 7.0 else 'Volatile')

        rec = {
            'Player ID': pid,
            'Player Name': name,
            'Discipline': 'Bowling',
            'Primary_Rank': top10_bowl[top10_bowl['Player ID'] == pid]['Rank'].values[0],
            'Strict_CPI_0.70_Rank': ranks_in_specs.get('Strict (CPI >= 0.70)', 'N/A'),
            'Broad_CPI_0.50_Rank': ranks_in_specs.get('Broad (CPI >= 0.50)', 'N/A'),
            'Rule_Model_A_Rank': ranks_in_specs.get('Rule-Based Model A', 'N/A'),
            'Rank_Std_Dev': round(rank_std, 2),
            'Stability_Class': stability_flag
        }
        bowl_sensitivity_records.append(rec)

    sensitivity_df = pd.DataFrame(bat_sensitivity_records + bowl_sensitivity_records)
    sensitivity_df.to_csv('outputs/tables/ranking_sensitivity.csv', index=False)
    print(f"Saved ranking sensitivity to outputs/tables/ranking_sensitivity.csv")

    # Update top 10 stability labels in rankings files
    stability_map = sensitivity_df.set_index('Player ID')['Stability_Class'].to_dict()
    top10_bat['Ranking stability'] = top10_bat['Player ID'].map(stability_map)
    top10_bat.to_csv('outputs/rankings/top_10_batters.csv', index=False)

    top10_bowl['Ranking stability'] = top10_bowl['Player ID'].map(stability_map)
    top10_bowl.to_csv('outputs/rankings/top_10_bowlers.csv', index=False)

    # 4. Save Match-Level Consistency Metrics Table
    print("Generating comprehensive match consistency summary...")
    match_bat_summary = bat_all[['striker_id', 'name', 'team', 'hp_bf', 'hp_matches', 
                                 'consistency_pct', 'mean_match_raa', 'std_match_raa', 'iqr_match_raa']].copy()
    match_bat_summary.columns = ['Player_ID', 'Player_Name', 'Team', 'HP_Volume', 'HP_Matches',
                                 'Consistency_Pct', 'Mean_Match_Impact', 'Std_Match_Impact', 'IQR_Match_Impact']
    match_bat_summary['Discipline'] = 'Batting'

    match_bowl_summary = bowl_all[['bowler_id', 'name', 'team', 'hp_balls', 'hp_matches',
                                   'consistency_pct', 'mean_match_rpa', 'std_match_rpa', 'iqr_match_rpa']].copy()
    match_bowl_summary.columns = ['Player_ID', 'Player_Name', 'Team', 'HP_Volume', 'HP_Matches',
                                  'Consistency_Pct', 'Mean_Match_Impact', 'Std_Match_Impact', 'IQR_Match_Impact']
    match_bowl_summary['Discipline'] = 'Bowling'

    match_consistency_all = pd.concat([match_bat_summary, match_bowl_summary], ignore_index=True)
    match_consistency_all.to_csv('outputs/tables/match_consistency.csv', index=False)
    print("Saved match consistency table to outputs/tables/match_consistency.csv")

    # 5. Combined Player Analysis Table (All-Rounders & Single-Discipline Profiles)
    print("Building Combined Player Analysis (identifying high-pressure all-rounders)...")
    combined = bat_all.merge(
        bowl_all, 
        left_on='striker_id', 
        right_on='bowler_id', 
        how='outer', 
        suffixes=('_bat', '_bowl')
    ).copy()
    
    player_id = combined['striker_id'].combine_first(combined['bowler_id']).astype(int)
    player_name = combined['name_bat'].combine_first(combined['name_bowl'])
    primary_team = combined['team_bat'].combine_first(combined['team_bowl'])

    hp_bf = combined['hp_bf'].fillna(0).astype(int)
    hp_bat_raa = combined['hp_raa'].fillna(0.0).round(1)
    hp_sr = combined['hp_sr'].fillna(0.0).round(1)
    bat_rating = combined['auction_rating_bat'].fillna(0.0).round(1)

    hp_balls = combined['hp_balls'].fillna(0).astype(int)
    hp_bowl_rpa = combined['hp_rpa'].fillna(0.0).round(1)
    hp_econ = combined['hp_econ'].fillna(0.0).round(2)
    bowl_rating = combined['auction_rating_bowl'].fillna(0.0).round(1)

    is_allrounder = (hp_bf >= 50) & (hp_balls >= 60)
    comb_val = np.where(is_allrounder, bat_rating + bowl_rating, np.maximum(bat_rating, bowl_rating)).round(1)

    combined_out = pd.DataFrame({
        'Player_ID': player_id,
        'Player_Name': player_name,
        'Primary_Team': primary_team,
        'Is_AllRounder': is_allrounder,
        'HP_Balls_Faced': hp_bf,
        'HP_Strike_Rate': hp_sr,
        'HP_Batting_RAA': hp_bat_raa,
        'Batting_Auction_Rating': bat_rating,
        'HP_Legal_Balls_Bowled': hp_balls,
        'HP_Economy': hp_econ,
        'HP_Bowling_RPA': hp_bowl_rpa,
        'Bowling_Auction_Rating': bowl_rating,
        'Combined_Pressure_Value': comb_val
    }).sort_values('Combined_Pressure_Value', ascending=False)

    combined_out.to_csv('outputs/rankings/combined_player_analysis.csv', index=False)
    print("Saved combined player analysis to outputs/rankings/combined_player_analysis.csv")
    return sensitivity_df, format_df, combined_out

if __name__ == '__main__':
    run_robustness_analysis()
