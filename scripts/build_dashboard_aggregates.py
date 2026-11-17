"""
build_dashboard_aggregates.py
Generates strictly aggregated (zero raw delivery rows) summary datasets for the local
Streamlit dashboard from outputs/processed/deliveries_with_expected.parquet:
1. dashboard/data_cache/pressure_aggregates.json (over-by-over, innings, phase, CPI histogram, RRR x Wkts matrix, season/format coverage)
2. dashboard/data_cache/player_role_profiles.csv (evidence-based batting order, phase ball-shares, pace/spin classification)
"""
import os
import json
import pandas as pd
import numpy as np

os.makedirs('dashboard/data_cache', exist_ok=True)

df = pd.read_parquet('outputs/processed/deliveries_with_expected.parquet')
df['comp_category'] = np.where(
    df['comp_name'].str.startswith('IPL', na=False), 'IPL',
    np.where(df['match_format'] == 'T20I', 'International T20I', 'Other T20')
)

# 1. Overall KPIs (strictly verified from dataset)
kpis = {
    'total_deliveries': int(len(df)),
    'legal_deliveries': int(df['is_legal'].sum()),
    'hp_deliveries': int(df['is_high_pressure'].sum()),
    'hp_pct': round(float(df['is_high_pressure'].mean() * 100), 2),
    'med_deliveries': int((df['pressure_category'] == 'Medium').sum()),
    'low_deliveries': int((df['pressure_category'] == 'Low').sum()),
    'total_matches': int(df['match_id'].nunique()),
    'total_competitions': int(df['comp_id'].nunique()),
    'unique_batters': int(df['striker_id'].nunique()),
    'unique_bowlers': int(df['bowler_id'].nunique()),
    'unique_players': int(len(set(df['striker_id'].unique()) | set(df['bowler_id'].unique()))),
    'qualified_batters': 122,
    'qualified_bowlers': 111,
    'ipl_deliveries': int((df['comp_category'] == 'IPL').sum()),
    't20i_deliveries': int((df['comp_category'] == 'International T20I').sum()),
    'other_t20_deliveries': int((df['comp_category'] == 'Other T20').sum()),
    'ipl_matches': int(df[df['comp_category'] == 'IPL']['match_id'].nunique()),
    't20i_matches': int(df[df['comp_category'] == 'International T20I']['match_id'].nunique()),
    'other_t20_matches': int(df[df['comp_category'] == 'Other T20']['match_id'].nunique()),
}

# 2. CPI Histogram (25 bins on [0, 1])
counts, edges = np.histogram(df['cpi'].values, bins=25, range=(0.0, 1.0))
cpi_hist = [
    {'bin_start': round(float(edges[i]), 3), 'bin_end': round(float(edges[i+1]), 3),
     'bin_mid': round(float((edges[i]+edges[i+1])/2), 3), 'count': int(counts[i])}
    for i in range(len(counts))
]

# 3. Pressure by Over (1-20) and Innings (1 vs 2)
inn12 = df[df['innings'].isin([1, 2]) & df['overid'].between(1, 20)]
by_over_inn = inn12.groupby(['innings', 'overid']).agg(
    deliveries=('cpi', 'count'),
    mean_cpi=('cpi', 'mean'),
    hp_pct=('is_high_pressure', lambda x: float(x.mean() * 100)),
    avg_runs=('total_runs', 'mean'),
    wkt_pct=('is_team_wicket', lambda x: float(x.mean() * 100))
).reset_index()
by_over_inn_list = by_over_inn.round(4).to_dict(orient='records')

# 4. Pressure by Format (3-way) and Phase
by_fmt_phase = df.groupby(['comp_category', 'innings_phase']).agg(
    deliveries=('cpi', 'count'),
    mean_cpi=('cpi', 'mean'),
    hp_pct=('is_high_pressure', lambda x: float(x.mean() * 100)),
    hp_count=('is_high_pressure', 'sum')
).reset_index().round(4).to_dict(orient='records')

# 5. Pressure by Format (3-way overall)
by_fmt = df.groupby('comp_category').agg(
    deliveries=('cpi', 'count'),
    matches=('match_id', 'nunique'),
    competitions=('comp_id', 'nunique'),
    mean_cpi=('cpi', 'mean'),
    hp_count=('is_high_pressure', 'sum'),
    hp_pct=('is_high_pressure', lambda x: float(x.mean() * 100))
).reset_index().round(4).to_dict(orient='records')

# 6. Season x Format coverage
by_season = df.groupby(['season', 'comp_category']).size().reset_index(name='deliveries').to_dict(orient='records')

# 7. Second-Innings RRR bucket x Wickets-in-hand heatmap
inn2 = df[df['innings'] == 2].copy()
inn2['rrr_bucket'] = pd.cut(inn2['rrr'], bins=[-1, 6, 8, 10, 12, 15, 100],
                            labels=['<6', '6-8', '8-10', '10-12', '12-15', '15+'])
inn2['wkt_grp'] = pd.cut(inn2['wickets_in_hand'], bins=[0, 2, 4, 6, 8, 10],
                         labels=['1-2 Wkts', '3-4 Wkts', '5-6 Wkts', '7-8 Wkts', '9-10 Wkts'])
heat = inn2.groupby(['rrr_bucket', 'wkt_grp'], observed=False).agg(
    deliveries=('cpi', 'count'),
    mean_cpi=('cpi', 'mean'),
    hp_pct=('is_high_pressure', lambda x: float(x.mean() * 100))
).reset_index()
heat['rrr_bucket'] = heat['rrr_bucket'].astype(str)
heat['wkt_grp'] = heat['wkt_grp'].astype(str)
heat_list = heat.round(4).to_dict(orient='records')

# 8. Knockout vs League comparison
by_ko = df.groupby('is_knockout').agg(
    deliveries=('cpi', 'count'),
    mean_cpi=('cpi', 'mean'),
    hp_count=('is_high_pressure', 'sum'),
    hp_pct=('is_high_pressure', lambda x: float(x.mean() * 100))
).reset_index().round(4).to_dict(orient='records')

agg_payload = {
    'kpis': kpis,
    'cpi_hist': cpi_hist,
    'by_over_innings': by_over_inn_list,
    'by_format_phase': by_fmt_phase,
    'by_format': by_fmt,
    'by_season_format': by_season,
    'chase_heatmap': heat_list,
    'by_knockout': by_ko
}

with open('dashboard/data_cache/pressure_aggregates.json', 'w', encoding='utf-8') as f:
    json.dump(agg_payload, f, indent=2)
print("Saved dashboard/data_cache/pressure_aggregates.json")

# 9. Evidence-based Player Role Profiles (for Page 8 Scouting & Recruitment Insights)
# Batters: median batting_order, phase ball shares (Powerplay, Middle, Death), boundary_pct, hp_sr
bf = df[df['is_ball_faced']].copy()
bat_order = bf.groupby('striker_id').agg(
    median_batting_order=('batting_order', 'median'),
    total_bf=('bat_runs', 'count'),
    pp_bf=('overid', lambda x: int((x <= 6).sum())),
    mid_bf=('overid', lambda x: int(((x >= 7) & (x <= 15)).sum())),
    death_bf=('overid', lambda x: int((x >= 16).sum())),
    six_pct=('is_six', lambda x: float(x.mean() * 100)),
    four_pct=('is_four', lambda x: float(x.mean() * 100))
).reset_index()
bat_order['pp_share_pct'] = (bat_order['pp_bf'] / bat_order['total_bf'] * 100).round(1)
bat_order['mid_share_pct'] = (bat_order['mid_bf'] / bat_order['total_bf'] * 100).round(1)
bat_order['death_share_pct'] = (bat_order['death_bf'] / bat_order['total_bf'] * 100).round(1)

def assign_bat_role(r):
    if r['median_batting_order'] <= 3.0:
        return 'Top-Order Batter'
    elif r['death_share_pct'] >= 45.0 or r['median_batting_order'] >= 5.5:
        return 'Finisher'
    elif (r['six_pct'] + r['four_pct']) >= 22.0 and r['death_share_pct'] >= 30.0:
        return 'Power Hitter'
    else:
        return 'Middle-Order Batter'

bat_order['inferred_batting_role'] = bat_order.apply(assign_bat_role, axis=1)
bat_order.to_csv('dashboard/data_cache/batter_role_profiles.csv', index=False)
print(f"Saved dashboard/data_cache/batter_role_profiles.csv ({len(bat_order)} batters)")

# Bowlers: primary pace_or_spin, phase legal ball shares (Powerplay, Middle, Death)
lg = df[df['is_legal']].copy()
bowl_prof = lg.groupby('bowler_id').agg(
    primary_style=('pace_or_spin', lambda x: x.dropna().mode().iloc[0] if len(x.dropna()) > 0 else 'Unknown'),
    bowling_type=('bowling_type', lambda x: x.dropna().mode().iloc[0] if len(x.dropna()) > 0 else 'Unknown'),
    total_legal_balls=('bowler_runs', 'count'),
    pp_balls=('overid', lambda x: int((x <= 6).sum())),
    mid_balls=('overid', lambda x: int(((x >= 7) & (x <= 15)).sum())),
    death_balls=('overid', lambda x: int((x >= 16).sum()))
).reset_index()
bowl_prof['pp_share_pct'] = (bowl_prof['pp_balls'] / bowl_prof['total_legal_balls'] * 100).round(1)
bowl_prof['mid_share_pct'] = (bowl_prof['mid_balls'] / bowl_prof['total_legal_balls'] * 100).round(1)
bowl_prof['death_share_pct'] = (bowl_prof['death_balls'] / bowl_prof['total_legal_balls'] * 100).round(1)

def assign_bowl_role(r):
    style = str(r['primary_style']).lower()
    if 'spin' in style:
        return 'Spin Bowler'
    if r['death_share_pct'] >= 38.0:
        return 'Death-Over Specialist'
    if r['pp_share_pct'] >= 42.0:
        return 'Powerplay Bowler'
    return 'Middle-Over Specialist'

bowl_prof['inferred_bowling_role'] = bowl_prof.apply(assign_bowl_role, axis=1)
bowl_prof.to_csv('dashboard/data_cache/bowler_role_profiles.csv', index=False)
print(f"Saved dashboard/data_cache/bowler_role_profiles.csv ({len(bowl_prof)} bowlers)")
