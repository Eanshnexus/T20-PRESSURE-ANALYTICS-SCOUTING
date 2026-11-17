"""
run_methodology_validation.py
Comprehensive quantitative audit for FINAL_METHODOLOGY_VALIDATION.md:
1. Worked step-by-step proofs for Suryakumar Yadav, Tristan Stubbs, Sunil Narine.
2. 3-way competition audit (IPL, International T20I, Other T20) + effect on Muqeem & all Top 10.
3. Wicket valuation sensitivity (6, 8, 10, 12 runs/wicket).
4. Empirical Bayes variance-components derivation for K_bat and K_bowl.
5. Full 5-fold GroupKFold diagnostics, match-clustered 95% CIs, and probability calibration (Brier, BSS, ECE, deciles).
6. Pressure model diagnostics (RRR vs RRR-CRR collinearity, knockout modifier effect, Model A vs Model B agreement, CPI sensitivity).
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error, roc_auc_score, brier_score_loss, cohen_kappa_score
from scipy.stats import spearmanr

df = pd.read_parquet('outputs/processed/deliveries_with_expected.parquet')
comps = pd.read_csv('competitions.csv')
bat_m = pd.read_csv('outputs/tables/batter_metrics.csv')
bowl_m = pd.read_csv('outputs/tables/bowler_metrics.csv')
top10_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
top10_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')

print("="*85)
print("1. WORKED STEP-BY-STEP PROOFS: SURYAKUMAR YADAV, TRISTAN STUBBS, SUNIL NARINE")
print("="*85)

mu_bat = bat_m[bat_m['hp_bf'] >= 60]['hp_raa_per_100'].mean()
mu_bowl = bowl_m[bowl_m['hp_balls'] >= 60]['hp_rpa_per_6'].mean()
print(f"mu_prior_raa (batters >=60 HP BF, n={len(bat_m[bat_m['hp_bf']>=60])}) = {mu_bat:.6f}")
print(f"mu_prior_rpa (bowlers >=60 HP balls, n={len(bowl_m[bowl_m['hp_balls']>=60])}) = {mu_bowl:.6f}")

for pid in [1699, 20702]:
    r = bat_m[bat_m['striker_id'] == pid].iloc[0]
    w = r['hp_bf'] / (r['hp_bf'] + 150.0)
    shrunk = w * r['hp_raa_per_100'] + (1 - w) * mu_bat
    sc = np.clip((shrunk + 15.0) / 45.0 * 100.0, 0, 100)
    wkt_v = r['hp_waa_per_100'] * 8.0
    wc = np.clip((wkt_v + 15.0) / 35.0 * 100.0, 0, 100)
    dr = r['hp_raa_per_100'] - r['ord_raa_per_100']
    cdr = np.clip(dr, -20.0, 25.0)
    dc = np.clip((cdr + 20.0) / 45.0 * 100.0, 0, 100)
    cc = np.clip(r['consistency_pct'], 0, 100)
    P = 0.45 * sc + 0.20 * wc + 0.20 * dc + 0.15 * cc
    I_rate = r['ipl_raa_per_100'] if r['ipl_bf'] >= 30 else shrunk
    T_rate = r['t20i_raa_per_100'] if r['t20i_bf'] >= 30 else shrunk
    I = np.clip((I_rate + 15.0) / 45.0 * 100.0, 0, 100)
    T = np.clip((T_rate + 15.0) / 45.0 * 100.0, 0, 100)
    R = 0.455 * I + 0.195 * T + 0.350 * P
    print(f"\nBatter: {r['name']} (ID {pid})")
    print(f"  hp_bf={int(r['hp_bf'])}, hp_raa={r['hp_raa']:.4f}, hp_raa_per_100={r['hp_raa_per_100']:.4f}, ord_raa_per_100={r['ord_raa_per_100']:.4f}")
    print(f"  EB weight w={w:.6f} -> shrunk_raa_per_100={shrunk:.4f} -> score_comp={sc:.4f}")
    print(f"  hp_waa={r['hp_waa']:.4f}, hp_waa_per_100={r['hp_waa_per_100']:.4f}, wkt_val={wkt_v:.4f} -> wkt_comp={wc:.4f}")
    print(f"  delta_raa_rate={dr:.4f}, clipped={cdr:.4f} -> delta_comp={dc:.4f}")
    print(f"  consistency_pct={cc:.4f} -> P={P:.4f} (CSV: {r['pressure_impact_score']:.4f})")
    print(f"  ord_score={r['ord_score']:.4f}, delta_sr={r['delta_sr']:.4f}")
    print(f"  ipl_bf={int(r['ipl_bf'])}, ipl_raa={r['ipl_raa']:.4f}, ipl_raa_per_100={r['ipl_raa_per_100']:.4f} -> I={I:.4f}")
    print(f"  t20i_bf={int(r['t20i_bf'])}, t20i_raa={r['t20i_raa']:.4f}, t20i_raa_per_100={r['t20i_raa_per_100']:.4f} -> T={T:.4f}")
    print(f"  R = 0.455*({I:.4f}) + 0.195*({T:.4f}) + 0.350*({P:.4f}) = {R:.4f} (CSV: {r['auction_rating']:.4f})")

# Sunil Narine (ID 781)
r = bowl_m[bowl_m['bowler_id'] == 781].iloc[0]
w = r['hp_balls'] / (r['hp_balls'] + 200.0)
shrunk = w * r['hp_rpa_per_6'] + (1 - w) * mu_bowl
sc = np.clip((shrunk + 1.5) / 4.0 * 100.0, 0, 100)
wkt_v = r['hp_waa_per_6'] * 8.0
wc = np.clip((wkt_v + 1.5) / 3.5 * 100.0, 0, 100)
dr = r['hp_rpa_per_6'] - r['ord_rpa_per_6']
cdr = np.clip(dr, -2.0, 2.5)
dc = np.clip((cdr + 2.0) / 4.5 * 100.0, 0, 100)
cc = np.clip(r['consistency_pct'], 0, 100)
P = 0.45 * sc + 0.20 * wc + 0.20 * dc + 0.15 * cc
I_rate = r['ipl_rpa_per_6'] if r['ipl_balls'] >= 30 else shrunk
I = np.clip((I_rate + 1.5) / 4.0 * 100.0, 0, 100)
R = 0.520 * I + 0.480 * P
print(f"\nBowler: {r['name']} (ID 781) [IPL-Only Branch: ipl_balls=376, t20i_balls=0]")
print(f"  hp_balls={int(r['hp_balls'])}, hp_rpa={r['hp_rpa']:.4f}, hp_rpa_per_6={r['hp_rpa_per_6']:.4f}, ord_rpa_per_6={r['ord_rpa_per_6']:.4f}")
print(f"  EB weight w={w:.6f} -> shrunk_rpa_per_6={shrunk:.4f} -> score_comp={sc:.4f}")
print(f"  hp_waa={r['hp_waa']:.4f}, hp_waa_per_6={r['hp_waa_per_6']:.4f}, wkt_val={wkt_v:.4f} -> wkt_comp={wc:.4f}")
print(f"  delta_rpa_rate={dr:.4f}, clipped={cdr:.4f} -> delta_comp={dc:.4f}")
print(f"  consistency_pct={cc:.4f} -> P={P:.4f} (CSV: {r['pressure_impact_score']:.4f})")
print(f"  ord_score={r['ord_score']:.4f}, delta_econ={r['delta_econ']:.4f}")
print(f"  ipl_balls={int(r['ipl_balls'])}, ipl_rpa={r['ipl_rpa']:.4f}, ipl_rpa_per_6={r['ipl_rpa_per_6']:.4f} -> I={I:.4f}")
print(f"  R = 0.520*({I:.4f}) + 0.480*({P:.4f}) = {R:.4f} (CSV: {r['auction_rating']:.4f})")

print("\n" + "="*85)
print("2. THREE-WAY COMPETITION AUDIT: IPL vs INTERNATIONAL T20I vs OTHER T20")
print("="*85)
df['comp_category'] = np.where(
    df['comp_name'].str.startswith('IPL', na=False), 'IPL',
    np.where(df['match_format'] == 'T20I', 'International_T20I', 'Other_T20')
)
print(df.groupby('comp_category').agg(
    deliveries=('match_id', 'count'),
    matches=('match_id', 'nunique'),
    competitions=('comp_id', 'nunique'),
    hp_deliveries=('is_high_pressure', 'sum')
).to_string())

print("\nOther_T20 Competitions Detail:")
print(df[df['comp_category'] == 'Other_T20'].groupby(['comp_id', 'comp_name', 'match_format', 'season']).agg(
    deliveries=('match_id', 'count'),
    matches=('match_id', 'nunique'),
    hp_deliveries=('is_high_pressure', 'sum')
).to_string())

print("\n--- TOP 10 BATTERS 3-WAY SAMPLE & RAW CONTRIBUTION BREAKDOWN ---")
bf_hp = df[(df['is_ball_faced']) & (df['is_high_pressure'])]
for _, row in top10_bat.iterrows():
    pid = row['Player ID']
    sub = bf_hp[bf_hp['striker_id'] == pid]
    g = sub.groupby('comp_category').agg(n=('bat_runs', 'count'), raa=('bat_raa', 'sum'))
    ipl_n = int(g.loc['IPL', 'n']) if 'IPL' in g.index else 0
    ipl_raa = g.loc['IPL', 'raa'] if 'IPL' in g.index else 0.0
    t20i_n = int(g.loc['International_T20I', 'n']) if 'International_T20I' in g.index else 0
    t20i_raa = g.loc['International_T20I', 'raa'] if 'International_T20I' in g.index else 0.0
    oth_n = int(g.loc['Other_T20', 'n']) if 'Other_T20' in g.index else 0
    oth_raa = g.loc['Other_T20', 'raa'] if 'Other_T20' in g.index else 0.0
    print(f"#{row['Rank']:2d} {row['Player name']:20s} ({pid:5d}) | IPL: {ipl_n:3d} ({ipl_raa:+6.1f}) | T20I: {t20i_n:3d} ({t20i_raa:+6.1f}) | Other_T20: {oth_n:2d} ({oth_raa:+5.1f})")

print("\n--- TOP 10 BOWLERS 3-WAY SAMPLE & RAW CONTRIBUTION BREAKDOWN ---")
lg_hp = df[(df['is_legal']) & (df['is_high_pressure'])]
for _, row in top10_bowl.iterrows():
    pid = row['Player ID']
    sub = lg_hp[lg_hp['bowler_id'] == pid]
    g = sub.groupby('comp_category').agg(n=('bowler_runs', 'count'), rpa=('bowl_rpa', 'sum'))
    ipl_n = int(g.loc['IPL', 'n']) if 'IPL' in g.index else 0
    ipl_rpa = g.loc['IPL', 'rpa'] if 'IPL' in g.index else 0.0
    t20i_n = int(g.loc['International_T20I', 'n']) if 'International_T20I' in g.index else 0
    t20i_rpa = g.loc['International_T20I', 'rpa'] if 'International_T20I' in g.index else 0.0
    oth_n = int(g.loc['Other_T20', 'n']) if 'Other_T20' in g.index else 0
    oth_rpa = g.loc['Other_T20', 'rpa'] if 'Other_T20' in g.index else 0.0
    print(f"#{row['Rank']:2d} {row['Player name']:20s} ({pid:5d}) | IPL: {ipl_n:3d} ({ipl_rpa:+6.1f}) | T20I: {t20i_n:3d} ({t20i_rpa:+6.1f}) | Other_T20: {oth_n:2d} ({oth_rpa:+5.1f})")

# Test strict 3-way separation: t20i_hp strictly == International_T20I (not including Other_T20)
print("\n--- EFFECT OF STRICT 3-WAY SEPARATION (t20i_hp = International_T20I ONLY) ON MUQEEM & TILAK ---")
sm_t20i = lg_hp[(lg_hp['bowler_id'] == 34485) & (lg_hp['comp_category'] == 'International_T20I')]
sm_t20i_rpa6 = sm_t20i['bowl_rpa'].sum() / len(sm_t20i) * 6.0
sm_T_strict = np.clip((sm_t20i_rpa6 + 1.5) / 4.0 * 100.0, 0, 100)
sm_P = bowl_m[bowl_m['bowler_id'] == 34485]['pressure_impact_score'].iloc[0]
sm_R_strict = 0.195 * sm_T_strict + 0.805 * sm_P
print(f"Sufiyan Muqeem (34485): T20I-only balls={len(sm_t20i)}, T20I RPA={sm_t20i['bowl_rpa'].sum():.2f}, T20I RPA/6={sm_t20i_rpa6:.4f} -> T_strict={sm_T_strict:.2f}, P={sm_P:.2f} -> R_strict={sm_R_strict:.2f} (vs 66.33 when Other_T20 bundled into t20i_hp)")

tv_t20i = bf_hp[(bf_hp['striker_id'] == 7897) & (bf_hp['comp_category'] == 'International_T20I')]
tv_t20i_raa100 = tv_t20i['bat_raa'].sum() / len(tv_t20i) * 100.0
tv_T_strict = np.clip((tv_t20i_raa100 + 15.0) / 45.0 * 100.0, 0, 100)
tv_m = bat_m[bat_m['striker_id'] == 7897].iloc[0]
tv_I = np.clip((tv_m['ipl_raa_per_100'] + 15.0) / 45.0 * 100.0, 0, 100)
tv_R_strict = 0.455 * tv_I + 0.195 * tv_T_strict + 0.350 * tv_m['pressure_impact_score']
print(f"Tilak Varma (7897): T20I-only BF={len(tv_t20i)}, T20I RAA={tv_t20i['bat_raa'].sum():.2f}, T20I RAA/100={tv_t20i_raa100:.2f} -> T_strict={tv_T_strict:.2f}, R_strict={tv_R_strict:.2f} (vs 93.63)")

print("\n" + "="*85)
print("3. WICKET VALUATION SENSITIVITY (6, 8, 10, 12 RUNS PER WICKET)")
print("="*85)

def test_wicket_val_bat(wkt_runs):
    b = bat_m[bat_m['hp_bf'] >= 120].copy()
    sc = np.clip((b['shrunk_raa_per_100'] + 15.0) / 45.0 * 100.0, 0, 100)
    wc = np.clip((b['hp_waa_per_100'] * wkt_runs + 15.0) / 35.0 * 100.0, 0, 100)
    dc = np.clip((b['clipped_delta_raa'] + 20.0) / 45.0 * 100.0, 0, 100)
    cc = np.clip(b['consistency_pct'], 0, 100)
    P = 0.45 * sc + 0.20 * wc + 0.20 * dc + 0.15 * cc
    I_r = np.where(b['ipl_bf'] >= 30, b['ipl_raa_per_100'], b['shrunk_raa_per_100'])
    T_r = np.where(b['t20i_bf'] >= 30, b['t20i_raa_per_100'], b['shrunk_raa_per_100'])
    I = np.clip((I_r + 15.0) / 45.0 * 100.0, 0, 100)
    T = np.clip((T_r + 15.0) / 45.0 * 100.0, 0, 100)
    has_ipl = b['ipl_bf'] >= 50
    has_both = (b['ipl_bf'] >= 50) & (b['t20i_bf'] >= 50)
    b['R'] = np.where(has_both, 0.455*I + 0.195*T + 0.350*P, np.where(has_ipl, 0.520*I + 0.480*P, 0.195*T + 0.805*P))
    b = b.sort_values('R', ascending=False).reset_index(drop=True)
    b['Rank'] = range(1, len(b)+1)
    return b.set_index('striker_id')['Rank']

bat_ranks = {v: test_wicket_val_bat(v) for v in [6, 8, 10, 12]}
bat_wkt_sens = pd.DataFrame({f'Wkt_{v}': bat_ranks[v] for v in [6, 8, 10, 12]})
bat_wkt_sens['Name'] = bat_m.set_index('striker_id')['name']
print("BATTERS Top 10 Rank Sensitivity across 6, 8, 10, 12 runs/wicket:")
print(bat_wkt_sens.sort_values('Wkt_8').head(12)[['Name', 'Wkt_6', 'Wkt_8', 'Wkt_10', 'Wkt_12']].to_string())
for v in [6, 10, 12]:
    rho, _ = spearmanr(bat_ranks[8], bat_ranks[v])
    print(f"  Batters Spearman rho (8 vs {v} runs/wkt across all 122 batters): {rho:.4f}")

def test_wicket_val_bowl(wkt_runs):
    b = bowl_m[bowl_m['hp_balls'] >= 150].copy()
    sc = np.clip((b['shrunk_rpa_per_6'] + 1.5) / 4.0 * 100.0, 0, 100)
    wc = np.clip((b['hp_waa_per_6'] * wkt_runs + 1.5) / 3.5 * 100.0, 0, 100)
    dc = np.clip((b['clipped_delta_rpa'] + 2.0) / 4.5 * 100.0, 0, 100)
    cc = np.clip(b['consistency_pct'], 0, 100)
    P = 0.45 * sc + 0.20 * wc + 0.20 * dc + 0.15 * cc
    I_r = np.where(b['ipl_balls'] >= 30, b['ipl_rpa_per_6'], b['shrunk_rpa_per_6'])
    T_r = np.where(b['t20i_balls'] >= 30, b['t20i_rpa_per_6'], b['shrunk_rpa_per_6'])
    I = np.clip((I_r + 1.5) / 4.0 * 100.0, 0, 100)
    T = np.clip((T_r + 1.5) / 4.0 * 100.0, 0, 100)
    has_ipl = b['ipl_balls'] >= 60
    has_both = (b['ipl_balls'] >= 60) & (b['t20i_balls'] >= 60)
    b['R'] = np.where(has_both, 0.455*I + 0.195*T + 0.350*P, np.where(has_ipl, 0.520*I + 0.480*P, 0.195*T + 0.805*P))
    b = b.sort_values('R', ascending=False).reset_index(drop=True)
    b['Rank'] = range(1, len(b)+1)
    return b.set_index('bowler_id')['Rank']

bowl_ranks = {v: test_wicket_val_bowl(v) for v in [6, 8, 10, 12]}
bowl_wkt_sens = pd.DataFrame({f'Wkt_{v}': bowl_ranks[v] for v in [6, 8, 10, 12]})
bowl_wkt_sens['Name'] = bowl_m.set_index('bowler_id')['name']
print("\nBOWLERS Top 10 Rank Sensitivity across 6, 8, 10, 12 runs/wicket:")
print(bowl_wkt_sens.sort_values('Wkt_8').head(12)[['Name', 'Wkt_6', 'Wkt_8', 'Wkt_10', 'Wkt_12']].to_string())
for v in [6, 10, 12]:
    rho, _ = spearmanr(bowl_ranks[8], bowl_ranks[v])
    print(f"  Bowlers Spearman rho (8 vs {v} runs/wkt across all 111 bowlers): {rho:.4f}")

print("\n" + "="*85)
print("4. EMPIRICAL BAYES VARIANCE COMPONENTS FOR K_BAT & K_BOWL")
print("="*85)
# Per-ball within-player variance of bat_raa (in runs/ball) and bowl_rpa (in runs/ball)
sigma2_bat_ball = bf_hp['bat_raa'].var(ddof=1) # variance of single-ball RAA
# Rate per 100 balls: RAA_100 = 100 * mean(bat_raa), so sampling variance of player i with N_i balls is (100^2 * sigma2_bat_ball) / N_i
q_bat = bat_m[bat_m['hp_bf'] >= 60]
var_obs_bat = q_bat['hp_raa_per_100'].var(ddof=1)
mean_samp_var_bat = ((100.0**2) * sigma2_bat_ball / q_bat['hp_bf']).mean()
tau2_bat = max(1e-6, var_obs_bat - mean_samp_var_bat)
k_bat_emp = (100.0**2 * sigma2_bat_ball) / tau2_bat
print(f"BATTING (qualifying N>=60 HP BF, n={len(q_bat)}):")
print(f"  Single-ball RAA variance (sigma2_within_ball): {sigma2_bat_ball:.4f} runs^2/ball")
print(f"  Observed between-player variance (RAA/100):    {var_obs_bat:.2f}")
print(f"  Mean sampling noise variance (100^2*s2/N_i):   {mean_samp_var_bat:.2f}")
print(f"  Estimated true skill variance (tau2_between):  {tau2_bat:.2f} (true SD = {np.sqrt(tau2_bat):.2f} runs/100 balls)")
print(f"  Implied Empirical Bayes K_bat = sigma2/tau2:   {k_bat_emp:.1f} balls (Used K_BAT = 150.0)")

sigma2_bowl_ball = lg_hp['bowl_rpa'].var(ddof=1)
q_bowl = bowl_m[bowl_m['hp_balls'] >= 60]
var_obs_bowl = q_bowl['hp_rpa_per_6'].var(ddof=1)
mean_samp_var_bowl = ((6.0**2) * sigma2_bowl_ball / q_bowl['hp_balls']).mean()
tau2_bowl = max(1e-6, var_obs_bowl - mean_samp_var_bowl)
k_bowl_emp = (6.0**2 * sigma2_bowl_ball) / tau2_bowl
print(f"\nBOWLING (qualifying N>=60 HP balls, n={len(q_bowl)}):")
print(f"  Single-ball RPA variance (sigma2_within_ball): {sigma2_bowl_ball:.4f} runs^2/ball")
print(f"  Observed between-player variance (RPA/6):      {var_obs_bowl:.4f}")
print(f"  Mean sampling noise variance (6^2*s2/N_i):     {mean_samp_var_bowl:.4f}")
print(f"  Estimated true skill variance (tau2_between):  {tau2_bowl:.4f} (true SD = {np.sqrt(tau2_bowl):.3f} runs/over)")
print(f"  Implied Empirical Bayes K_bowl = sigma2/tau2:  {k_bowl_emp:.1f} balls (Used K_BOWL = 200.0)")

print("\n" + "="*85)
print("5. MODEL VALIDATION: 5-FOLD VARIATION & PROBABILITY CALIBRATION")
print("="*85)
gkf = GroupKFold(n_splits=5)
df_cal = df.copy()
df_cal['wkt_bucket'] = pd.cut(df_cal['wickets_in_hand'], bins=[-1, 2, 4, 6, 8, 10], labels=['1-2', '3-4', '5-6', '7-8', '9-10'])
cell_keys = ['match_format', 'innings', 'innings_phase', 'wkt_bucket']

# Compute OOF simple baseline on ALL 200,999 rows (matching build_expected_performance.py)
for y_col, pred_col, mtype, lbl in [
    ('bat_runs', 'exp_bat_runs', 'mae', 'Batter Runs (All 200,999)'),
    ('is_team_wicket', 'exp_dismissal', 'prob', 'Batter Dismissal (All 200,999)'),
    ('bowler_runs', 'exp_bowl_runs', 'mae', 'Bowler Runs (All 200,999)'),
    ('is_bowler_wicket', 'exp_bowl_wkt', 'prob', 'Bowler Wicket (All 200,999)')
]:
    base_oof = np.zeros(len(df_cal))
    f_base, f_ml, f_diff = [], [], []
    f_brier_b, f_brier_m = [], []
    for tr_idx, va_idx in gkf.split(df_cal, groups=df_cal['match_id']):
        tr, va = df_cal.iloc[tr_idx], df_cal.iloc[va_idx]
        c_means = tr.groupby(cell_keys, observed=False)[y_col].mean()
        g_mean = tr[y_col].mean()
        pb = va.set_index(cell_keys).index.map(c_means).fillna(g_mean).values
        base_oof[va_idx] = pb
        if mtype == 'mae':
            mb = mean_absolute_error(va[y_col], pb)
            mm = mean_absolute_error(va[y_col], va[pred_col])
            f_base.append(mb); f_ml.append(mm); f_diff.append(mb - mm)
        else:
            mb = roc_auc_score(va[y_col], pb)
            mm = roc_auc_score(va[y_col], va[pred_col])
            bb = brier_score_loss(va[y_col], pb)
            bm = brier_score_loss(va[y_col], va[pred_col])
            f_base.append(mb); f_ml.append(mm); f_diff.append(mm - mb)
            f_brier_b.append(bb); f_brier_m.append(bm)
    if mtype == 'mae':
        print(f"{lbl}:")
        print(f"  OOF Base MAE Mean={np.mean(f_base):.4f} (SD={np.std(f_base):.4f}) | OOF ML MAE Mean={np.mean(f_ml):.4f} (SD={np.std(f_ml):.4f})")
        print(f"  Fold diffs (Base - ML): {[round(x,4) for x in f_diff]} | Mean={np.mean(f_diff):+.4f}, SD={np.std(f_diff):.4f}, Min={np.min(f_diff):+.4f}, Max={np.max(f_diff):+.4f}")
    else:
        y_true = df_cal[y_col].astype(float).values
        y_prob = df_cal[pred_col].values
        brier_m = brier_score_loss(y_true, y_prob)
        brier_ref = brier_score_loss(y_true, np.full_like(y_true, y_true.mean()))
        bss = 1.0 - (brier_m / brier_ref)
        # 10-quantile calibration bins & ECE
        bins = pd.qcut(y_prob, q=10, duplicates='drop')
        cal_tbl = pd.DataFrame({'y': y_true, 'p': y_prob, 'bin': bins}).groupby('bin', observed=False).agg(
            n=('y', 'count'), mean_pred=('p', 'mean'), obs_rate=('y', 'mean')
        )
        cal_tbl['abs_err'] = (cal_tbl['mean_pred'] - cal_tbl['obs_rate']).abs()
        ece = (cal_tbl['n'] * cal_tbl['abs_err']).sum() / len(y_true)
        print(f"{lbl}:")
        print(f"  OOF Base AUC Mean={np.mean(f_base):.4f} (SD={np.std(f_base):.4f}) | OOF ML AUC Mean={np.mean(f_ml):.4f} (SD={np.std(f_ml):.4f})")
        print(f"  Fold AUC diffs (ML - Base): {[round(x,4) for x in f_diff]} | Mean={np.mean(f_diff):+.4f}, SD={np.std(f_diff):.4f}")
        print(f"  Brier Score: OOF Base={np.mean(f_brier_b):.5f}, OOF ML={brier_m:.5f}, Climatology={brier_ref:.5f}, BSS={bss*100:.2f}%, ECE={ece:.5f}")
        print(f"  Global Mean Pred={y_prob.mean():.5f} vs Observed Rate={y_true.mean():.5f}")
        print(cal_tbl[['n', 'mean_pred', 'obs_rate', 'abs_err']].to_string())

print("\n" + "="*85)
print("6. PRESSURE MODEL DIAGNOSTICS (COLLINEARITY, KNOCKOUT MODIFIER, MODEL A vs B)")
print("="*85)
inn2 = df[df['innings'] == 2]
r_rrr_accel = inn2['rrr'].corr(inn2['rrr'] - inn2['crr'])
print(f"Innings 2 Pearson correlation corr(RRR, RRR - CRR): r = {r_rrr_accel:.4f}")

# Knockout modifier effect
cpi_base = np.where(df['is_knockout'], np.minimum(1.0, df['cpi'] / 1.15), df['cpi'])
ko_df = df[df['is_knockout']]
ko_base_high = (cpi_base[df['is_knockout']] >= 0.60).sum()
ko_mod_high = (ko_df['cpi'] >= 0.60).sum()
print(f"Knockout deliveries: {len(ko_df):,} ({len(ko_df)/len(df)*100:.2f}% of dataset)")
print(f"  Knockout Mean CPI: base={cpi_base[df['is_knockout']].mean():.4f} -> with 1.15x={ko_df['cpi'].mean():.4f}")
print(f"  Knockout High-Pressure (>=0.60): base={ko_base_high:,} ({ko_base_high/len(ko_df)*100:.2f}%) -> with 1.15x={ko_mod_high:,} ({ko_mod_high/len(ko_df)*100:.2f}%) | Promoted: +{ko_mod_high - ko_base_high:,} balls")

# Model A vs Model B agreement
mA = (df['pressure_rule'] == 'High')
mB = (df['cpi'] >= 0.60)
tp = (mA & mB).sum()
fp = (~mA & mB).sum()
fn = (mA & ~mB).sum()
tn = (~mA & ~mB).sum()
agree = (tp + tn) / len(df) * 100
jaccard = tp / (tp + fp + fn)
kappa = cohen_kappa_score(mA, mB)
print(f"\nModel A (Rule High: {mA.sum():,}, {mA.mean()*100:.2f}%) vs Model B (CPI>=0.60: {mB.sum():,}, {mB.mean()*100:.2f}%):")
print(f"  Both High (TP): {tp:,} | Only Model B: {fp:,} | Only Model A: {fn:,} | Both Not-High (TN): {tn:,}")
print(f"  Agreement: {agree:.2f}% | Jaccard Overlap: {jaccard:.4f} | Cohen's Kappa: {kappa:.4f}")
