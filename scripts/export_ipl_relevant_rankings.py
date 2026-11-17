"""
export_ipl_relevant_rankings.py - Generate and export formatted IPL-relevant Top 10 rankings
and complete eligible bowler rankings sorted by exact unrounded auction_rating.
"""
import pandas as pd
import numpy as np

# Load authoritative tables
bat_metrics = pd.read_csv('outputs/tables/batter_metrics.csv')
bowl_metrics = pd.read_csv('outputs/tables/bowler_metrics.csv')
comb = pd.read_csv('outputs/rankings/combined_player_analysis.csv')
sens = pd.read_csv('outputs/tables/ranking_sensitivity.csv')
top10_bat_global = pd.read_csv('outputs/rankings/top_10_batters.csv')
mapping = pd.read_csv('competition_team_player_mapping.csv')

# Identify players representing Pakistan without IPL franchise history (practical IPL recruitment unavailability)
pak_teams = ['Pakistan', 'Pakistan Shaheens', 'Pakistan A']
pak_player_ids = mapping[mapping['team_name'].isin(pak_teams)]['player_id'].unique().tolist()
ipl_franchises = ['Mumbai Indians', 'Chennai Super Kings', 'Kolkata Knight Riders', 'Rajasthan Royals', 
                  'Royal Challengers Bengaluru', 'Delhi Capitals', 'Punjab Kings', 'Sunrisers Hyderabad', 
                  'Gujarat Titans', 'Lucknow Super Giants']

pak_only_ids = []
for pid in pak_player_ids:
    p_teams = mapping[mapping['player_id'] == pid]['team_name'].unique().tolist()
    has_ipl_team = any(any(ipl in t for ipl in ipl_franchises) for t in p_teams)
    if not has_ipl_team:
        pak_only_ids.append(pid)

# 1. COMPLETE ELIGIBLE BOWLER RANKING (All bowlers >= 150 HP legal balls)
all_elig_bowl = bowl_metrics[bowl_metrics['hp_balls'] >= 150].copy()
all_elig_bowl = all_elig_bowl.merge(
    comb[['Player_ID', 'Primary_Team']], left_on='bowler_id', right_on='Player_ID', how='left'
)
sens_bowl = sens[sens['Discipline'] == 'Bowling'].copy()
all_elig_bowl = all_elig_bowl.merge(
    sens_bowl[['Player ID', 'Stability_Class']], left_on='bowler_id', right_on='Player ID', how='left'
)
all_elig_bowl['Stability_Class'] = all_elig_bowl['Stability_Class'].fillna('Not Top-10 Evaluated')
all_elig_bowl['IPL_Recruitment_Pool'] = ~all_elig_bowl['bowler_id'].isin(pak_only_ids)

# Sort strictly by exact unrounded auction_rating
all_elig_bowl = all_elig_bowl.sort_values('auction_rating', ascending=False).reset_index(drop=True)
all_elig_bowl['Global_Rank'] = range(1, len(all_elig_bowl) + 1)

all_elig_export = pd.DataFrame({
    'Global_Rank': all_elig_bowl['Global_Rank'],
    'Player name': all_elig_bowl['name'],
    'Player ID': all_elig_bowl['bowler_id'],
    'Primary team/affiliation': all_elig_bowl['Primary_Team'],
    'IPL_Recruitment_Pool': all_elig_bowl['IPL_Recruitment_Pool'],
    'Pressure legal balls': all_elig_bowl['hp_balls'],
    'IPL HP balls': all_elig_bowl['ipl_balls'].astype(int),
    'T20I HP balls': all_elig_bowl['t20i_balls'].astype(int),
    'Other T20 HP balls': all_elig_bowl['other_t20_balls'].astype(int),
    'Pressure matches': all_elig_bowl['hp_matches'],
    'Pressure economy': all_elig_bowl['hp_econ'].round(2),
    'Dot-ball percentage': all_elig_bowl['hp_dot_pct'].round(1).astype(str) + '%',
    'Wickets': all_elig_bowl['hp_wkts'],
    'Runs prevented above expectation': all_elig_bowl['hp_rpa'].round(1),
    'Wickets above expectation': all_elig_bowl['hp_waa'].round(2),
    'Pressure impact score': all_elig_bowl['pressure_impact_score'].round(2),
    'Auction Rating (Exact)': all_elig_bowl['auction_rating'].round(3),
    'Auction Rating': all_elig_bowl['auction_rating'].round(1),
    'Ranking stability': all_elig_bowl['Stability_Class']
})
all_elig_export.to_csv('outputs/tables/all_eligible_bowlers.csv', index=False)
print(f"Saved outputs/tables/all_eligible_bowlers.csv ({len(all_elig_export)} eligible bowlers)")

# 2. IPL-RELEVANT TOP 10 BATTERS
top10_bat_ipl = top10_bat_global.copy()
top10_bat_ipl.to_csv('outputs/rankings/top_10_batters_ipl_relevant.csv', index=False)
print("Saved outputs/rankings/top_10_batters_ipl_relevant.csv")

# 3. IPL-RELEVANT TOP 10 BOWLERS
ipl_elig_bowl = all_elig_bowl[all_elig_bowl['IPL_Recruitment_Pool']].head(10).copy()
ipl_elig_bowl['Rank'] = range(1, 11)

formatted_bowl_ipl = pd.DataFrame({
    'Rank': ipl_elig_bowl['Rank'],
    'Player name': ipl_elig_bowl['name'],
    'Player ID': ipl_elig_bowl['bowler_id'],
    'Primary team/affiliation': ipl_elig_bowl['Primary_Team'],
    'Pressure legal balls': ipl_elig_bowl['hp_balls'],
    'Pressure matches': ipl_elig_bowl['hp_matches'],
    'Pressure economy': ipl_elig_bowl['hp_econ'].round(2),
    'Dot-ball percentage': ipl_elig_bowl['hp_dot_pct'].round(1).astype(str) + '%',
    'Wickets': ipl_elig_bowl['hp_wkts'],
    'Runs prevented above expectation': ipl_elig_bowl['hp_rpa'].round(1),
    'Wickets above expectation': ipl_elig_bowl['hp_waa'].round(2),
    'Pressure impact score': ipl_elig_bowl['pressure_impact_score'].round(1),
    'Ordinary performance score': ipl_elig_bowl['ord_score'].round(1),
    'Pressure uplift/deterioration': ipl_elig_bowl['delta_econ'].round(2),
    'Match consistency': ipl_elig_bowl['consistency_pct'].round(1).astype(str) + '%',
    'IPL contribution': ipl_elig_bowl['ipl_rpa'].round(1),
    'T20I contribution': ipl_elig_bowl['t20i_rpa'].round(1),
    'Auction Rating': ipl_elig_bowl['auction_rating'].round(1),
    'Ranking stability': ipl_elig_bowl['Stability_Class'].replace({'Not Top-10 Evaluated': 'Moderate'})
})

formatted_bowl_ipl.to_csv('outputs/rankings/top_10_bowlers_ipl_relevant.csv', index=False)
print("Saved outputs/rankings/top_10_bowlers_ipl_relevant.csv")

print("\n--- UPDATED GLOBAL TOP 15 BOWLERS ---")
print(all_elig_export[['Global_Rank', 'Player name', 'Player ID', 'Primary team/affiliation', 'IPL HP balls', 'T20I HP balls', 'Other T20 HP balls', 'Auction Rating (Exact)', 'IPL_Recruitment_Pool']].head(15).to_string(index=False))

print("\n--- UPDATED IPL-RELEVANT TOP 10 BOWLERS ---")
print(formatted_bowl_ipl[['Rank', 'Player name', 'Player ID', 'Primary team/affiliation', 'Pressure legal balls', 'Pressure economy', 'Runs prevented above expectation', 'Wickets', 'Auction Rating', 'Ranking stability']].to_string(index=False))
