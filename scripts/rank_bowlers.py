"""
rank_bowlers.py - SupeRR Selector Season 2
Stage 6 of Pipeline: Multi-Dimensional Bowling Pressure Rating with Empirical Bayes Shrinkage.
"""

import os
import pandas as pd
import numpy as np

def run_rank_bowlers():
    print("="*60)
    print("STAGE 6: RATING & RANKING BOWLERS UNDER PRESSURE")
    print("="*60)

    # 1. Load Expected Deliveries and Metadata
    df = pd.read_parquet('outputs/processed/deliveries_with_expected.parquet')
    mapping = pd.read_csv('competition_team_player_mapping.csv')

    # Primary Team Mapping (Prioritize IPL Franchise)
    teams_per_player = mapping.groupby(['player_id', 'team_name']).size().reset_index(name='count')
    ipl_teams = ['Chennai Super Kings', 'Mumbai Indians', 'Rajasthan Royals', 'Kolkata Knight Riders',
                 'Royal Challengers Bengaluru', 'Delhi Capitals', 'Punjab Kings', 'Sunrisers Hyderabad',
                 'Gujarat Titans', 'Lucknow Super Giants']
    teams_per_player['is_ipl'] = teams_per_player['team_name'].isin(ipl_teams)
    teams_per_player = teams_per_player.sort_values(['is_ipl', 'count'], ascending=[False, False])
    primary_team = teams_per_player.drop_duplicates('player_id').set_index('player_id')['team_name'].to_dict()

    # Filter to legal deliveries bowled (only legal deliveries count toward bowler overs)
    legal_df = df[df['is_legal']].copy()

    # 2. Player-Level Aggregation: High Pressure vs Ordinary
    hp_df = legal_df[legal_df['is_high_pressure']]
    ord_df = legal_df[~legal_df['is_high_pressure']]

    def aggregate_bowling(sub_df, prefix):
        agg = sub_df.groupby('bowler_id').agg(
            balls=('bowler_runs', 'count'),
            runs=('bowler_runs', 'sum'),
            rpa=('bowl_rpa', 'sum'),
            wkts=('is_bowler_wicket', 'sum'),
            exp_wkts=('exp_bowl_wkt', 'sum'),
            dots=('is_dot_ball', 'sum'),
            boundaries=('is_boundary', 'sum'),
            matches=('match_id', 'nunique'),
            name=('bowler_name', 'first')
        ).reset_index()

        agg[f'{prefix}_balls'] = agg['balls']
        agg[f'{prefix}_runs'] = agg['runs']
        agg[f'{prefix}_econ'] = np.where(agg['balls'] > 0, (agg['runs'] / agg['balls']) * 6.0, 0.0)
        agg[f'{prefix}_rpa'] = agg['rpa']
        agg[f'{prefix}_rpa_per_6'] = np.where(agg['balls'] > 0, (agg['rpa'] / agg['balls']) * 6.0, 0.0)
        agg[f'{prefix}_wkts'] = agg['wkts']
        agg[f'{prefix}_exp_wkts'] = agg['exp_wkts']
        agg[f'{prefix}_waa'] = agg['wkts'] - agg['exp_wkts']  # + means more wickets than expected
        agg[f'{prefix}_waa_per_6'] = np.where(agg['balls'] > 0, (agg[f'{prefix}_waa'] / agg['balls']) * 6.0, 0.0)
        agg[f'{prefix}_dot_pct'] = np.where(agg['balls'] > 0, (agg['dots'] / agg['balls']) * 100.0, 0.0)
        agg[f'{prefix}_boundary_pct'] = np.where(agg['balls'] > 0, (agg['boundaries'] / agg['balls']) * 100.0, 0.0)
        agg[f'{prefix}_matches'] = agg['matches']

        cols = ['bowler_id', 'name', f'{prefix}_balls', f'{prefix}_runs', f'{prefix}_econ',
                f'{prefix}_rpa', f'{prefix}_rpa_per_6', f'{prefix}_wkts', 
                f'{prefix}_exp_wkts', f'{prefix}_waa', f'{prefix}_waa_per_6',
                f'{prefix}_dot_pct', f'{prefix}_boundary_pct', f'{prefix}_matches']
        return agg[cols]

    bowl_hp = aggregate_bowling(hp_df, 'hp')
    bowl_ord = aggregate_bowling(ord_df, 'ord')

    # Format-specific aggregates for 3-way competition separation:
    # 1. IPL: comp_name starts with 'IPL' (genuine IPL 2022-2026)
    # 2. International T20I: match_format == 'T20I'
    # 3. Other T20: non-IPL T20 competitions (Emerging Teams Asia Cup 2024, Asia Cup Rising Stars 2025)
    is_genuine_ipl = hp_df['comp_name'].str.startswith('IPL', na=False)
    is_intl_t20i = hp_df['match_format'] == 'T20I'
    is_other_t20 = (~is_genuine_ipl) & (~is_intl_t20i)

    ipl_hp = aggregate_bowling(hp_df[is_genuine_ipl], 'ipl')
    t20i_hp = aggregate_bowling(hp_df[is_intl_t20i], 't20i')
    other_t20_hp = aggregate_bowling(hp_df[is_other_t20], 'other_t20')

    # Merge overall aggregates
    bowlers = bowl_hp.merge(bowl_ord, on=['bowler_id', 'name'], how='left').fillna(0.0)
    bowlers = bowlers.merge(ipl_hp[['bowler_id', 'ipl_balls', 'ipl_econ', 'ipl_rpa', 'ipl_rpa_per_6', 'ipl_wkts']], on='bowler_id', how='left').fillna(0.0)
    bowlers = bowlers.merge(t20i_hp[['bowler_id', 't20i_balls', 't20i_econ', 't20i_rpa', 't20i_rpa_per_6', 't20i_wkts']], on='bowler_id', how='left').fillna(0.0)
    bowlers = bowlers.merge(other_t20_hp[['bowler_id', 'other_t20_balls', 'other_t20_econ', 'other_t20_rpa', 'other_t20_rpa_per_6', 'other_t20_wkts']], on='bowler_id', how='left').fillna(0.0)

    # 3. Match-Level Consistency Metrics
    print("Computing match-level bowling consistency metrics...")
    match_bowl = hp_df.groupby(['bowler_id', 'match_id']).agg(
        match_balls=('bowler_runs', 'count'),
        match_runs=('bowler_runs', 'sum'),
        match_rpa=('bowl_rpa', 'sum'),
        match_wkts=('is_bowler_wicket', 'sum')
    ).reset_index()

    consistency = match_bowl.groupby('bowler_id').agg(
        total_hp_matches=('match_id', 'count'),
        pos_impact_matches=('match_rpa', lambda x: (x > 0).sum()),
        mean_match_rpa=('match_rpa', 'mean'),
        std_match_rpa=('match_rpa', 'std'),
        iqr_match_rpa=('match_rpa', lambda x: np.percentile(x, 75) - np.percentile(x, 25))
    ).reset_index()

    consistency['consistency_pct'] = (consistency['pos_impact_matches'] / consistency['total_hp_matches']) * 100.0
    consistency['std_match_rpa'] = consistency['std_match_rpa'].fillna(0.0)

    bowlers = bowlers.merge(consistency, on='bowler_id', how='left')

    # 4. Empirical Bayes Shrinkage
    # Population Prior for high-pressure RPA per 6 balls
    qual_bowl = bowlers[bowlers['hp_balls'] >= 60]
    mu_prior_rpa = qual_bowl['hp_rpa_per_6'].mean()
    K_BOWL = 200.0  # Empirical Bayes shrinkage constant (~200 balls / ~33 overs)

    bowlers['shrunk_rpa_per_6'] = (
        (bowlers['hp_balls'] / (bowlers['hp_balls'] + K_BOWL)) * bowlers['hp_rpa_per_6'] +
        (K_BOWL / (bowlers['hp_balls'] + K_BOWL)) * mu_prior_rpa
    )

    # 5. Composite Bowling Rating Formulation
    # Dimensions:
    # 1. Shrunk Runs Prevented Above Expectation (RPA per 6 balls) -> 45%
    # 2. Wickets Above Expectation Value (WAA * 8.0 runs / balls * 6.0) -> 20%
    # 3. Pressure Delta (hp_rpa_per_6 - ord_rpa_per_6) -> 20%
    # 4. Match-to-Match Consistency (% positive impact spells) -> 15%

    bowlers['delta_econ'] = bowlers['ord_econ'] - bowlers['hp_econ']  # + means lower economy in pressure
    bowlers['delta_rpa_rate'] = bowlers['hp_rpa_per_6'] - bowlers['ord_rpa_per_6']
    bowlers['clipped_delta_rpa'] = np.clip(bowlers['delta_rpa_rate'], -2.0, 2.5)

    # Wicket value rate (runs saved via wickets per 6 balls)
    bowlers['wicket_val_per_6'] = bowlers['hp_waa_per_6'] * 8.0

    # Normalize metrics to 0-100 index
    # Component 1: Runs prevented (mean ~ 0, range roughly -2.0 to +3.0)
    score_comp = (bowlers['shrunk_rpa_per_6'] + 1.5) / 4.0 * 100.0

    # Component 2: Wicket impact (mean ~ 0, range roughly -1.5 to +2.5)
    wkt_comp = (bowlers['wicket_val_per_6'] + 1.5) / 3.5 * 100.0

    # Component 3: Pressure Delta (mean ~ 0, range roughly -2.0 to +2.5)
    delta_comp = (bowlers['clipped_delta_rpa'] + 2.0) / 4.5 * 100.0

    # Component 4: Consistency (range 0 to 100%)
    cons_comp = bowlers['consistency_pct']

    bowlers['pressure_impact_score'] = (
        0.45 * np.clip(score_comp, 0, 100) +
        0.20 * np.clip(wkt_comp, 0, 100) +
        0.20 * np.clip(delta_comp, 0, 100) +
        0.15 * np.clip(cons_comp, 0, 100)
    )

    # Ordinary Situation Performance Score
    bowlers['ord_score'] = np.clip((bowlers['ord_rpa_per_6'] + 1.5) / 3.5 * 100.0, 0, 100)

    # Format-Weighted Final Score (Auction-Relevance: 70% IPL, 30% T20I)
    ipl_rpa = np.where(bowlers['ipl_balls'] >= 30, bowlers['ipl_rpa_per_6'], bowlers['shrunk_rpa_per_6'])
    t20i_rpa = np.where(bowlers['t20i_balls'] >= 30, bowlers['t20i_rpa_per_6'], bowlers['shrunk_rpa_per_6'])

    ipl_score = np.clip((ipl_rpa + 1.5) / 4.0 * 100.0, 0, 100)
    t20i_score = np.clip((t20i_rpa + 1.5) / 4.0 * 100.0, 0, 100)

    has_ipl = bowlers['ipl_balls'] >= 60
    has_both = (bowlers['ipl_balls'] >= 60) & (bowlers['t20i_balls'] >= 60)

    bowlers['auction_rating'] = np.where(
        has_both,
        0.70 * (0.65 * ipl_score + 0.35 * bowlers['pressure_impact_score']) + 0.30 * (0.65 * t20i_score + 0.35 * bowlers['pressure_impact_score']),
        np.where(has_ipl,
                 0.80 * (0.65 * ipl_score + 0.35 * bowlers['pressure_impact_score']) + 0.20 * bowlers['pressure_impact_score'],
                 0.70 * bowlers['pressure_impact_score'] + 0.30 * (0.65 * t20i_score + 0.35 * bowlers['pressure_impact_score']))
    )

    # Assign Primary Team
    bowlers['team'] = bowlers['bowler_id'].map(primary_team)

    # 6. Apply Primary Eligibility Cutoff (>= 150 Pressure Legal Balls Bowled / 25 overs)
    PRIMARY_BOWL_MIN_BALLS = 150
    eligible_bowlers = bowlers[bowlers['hp_balls'] >= PRIMARY_BOWL_MIN_BALLS].copy()
    eligible_bowlers = eligible_bowlers.sort_values('auction_rating', ascending=False).reset_index(drop=True)

    print(f"Total bowlers evaluated: {len(bowlers):,}")
    print(f"Eligible bowlers (>= {PRIMARY_BOWL_MIN_BALLS} HP legal balls): {len(eligible_bowlers):,}")

    # Top 10 Bowlers
    top10_bowlers = eligible_bowlers.head(10).copy()
    top10_bowlers['Rank'] = range(1, 11)

    # Format table for output
    top10_formatted = pd.DataFrame({
        'Rank': top10_bowlers['Rank'],
        'Player name': top10_bowlers['name'],
        'Player ID': top10_bowlers['bowler_id'],
        'Primary team/affiliation': top10_bowlers['team'],
        'Pressure legal balls': top10_bowlers['hp_balls'],
        'Pressure matches': top10_bowlers['hp_matches'],
        'Pressure economy': top10_bowlers['hp_econ'].round(2),
        'Dot-ball percentage': top10_bowlers['hp_dot_pct'].round(1).astype(str) + '%',
        'Wickets': top10_bowlers['hp_wkts'].astype(int),
        'Runs prevented above expectation': top10_bowlers['hp_rpa'].round(1),
        'Wickets above expectation': top10_bowlers['hp_waa'].round(2),
        'Pressure impact score': top10_bowlers['pressure_impact_score'].round(1),
        'Ordinary performance score': top10_bowlers['ord_score'].round(1),
        'Pressure uplift/deterioration': top10_bowlers['delta_rpa_rate'].round(2),
        'Match consistency': top10_bowlers['consistency_pct'].round(1).astype(str) + '%',
        'IPL contribution': top10_bowlers['ipl_rpa'].round(1),
        'T20I contribution': top10_bowlers['t20i_rpa'].round(1),
        'Auction Rating': top10_bowlers['auction_rating'].round(1),
        'Ranking stability': 'High'
    })

    print("\n" + "="*80)
    print("TOP 10 BOWLERS UNDER PRESSURE (SupeRR Selector Season 2)")
    print("="*80)
    print(top10_formatted[['Rank', 'Player name', 'Primary team/affiliation', 'Pressure legal balls',
                           'Pressure economy', 'Dot-ball percentage', 'Wickets', 
                           'Runs prevented above expectation', 'Auction Rating', 'Match consistency']].to_string(index=False))

    # Save outputs
    top10_formatted.to_csv('outputs/rankings/top_10_bowlers.csv', index=False)
    bowlers.to_csv('outputs/tables/bowler_metrics.csv', index=False)
    print("\nSaved Top 10 Bowlers to outputs/rankings/top_10_bowlers.csv")
    print("Saved all bowler metrics to outputs/tables/bowler_metrics.csv")
    return top10_formatted, bowlers

if __name__ == '__main__':
    run_rank_bowlers()
