"""
build_expected_performance.py - SupeRR Selector Season 2
Stage 4 of Pipeline: GroupKFold ML Models for Expected Runs and Expected Wickets.
"""

import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, roc_auc_score, brier_score_loss

def run_build_expected_performance():
    print("="*60)
    print("STAGE 4: BUILDING EXPECTED-PERFORMANCE BASELINES")
    print("="*60)

    # 1. Load Pressure Deliveries
    df = pd.read_parquet('outputs/processed/deliveries_with_pressure.parquet')
    print(f"Loaded deliveries: {len(df):,} rows")

    # 2. Engineer Feature Set (Pre-Delivery Context Only)
    feature_cols = [
        'cum_legal_balls', 'balls_remaining', 'wickets_in_hand', 
        'cum_runs_before', 'crr', 'rrr', 'overid', 'innings'
    ]
    X = df[feature_cols].copy()
    X['is_t20i'] = (df['match_format'] == 'T20I').astype(float)
    X['is_knockout'] = df['is_knockout'].astype(float)
    X['is_death'] = (df['overid'] >= 16).astype(float)
    X['is_powerplay'] = (df['overid'] <= 6).astype(float)

    # Fill any NaNs safely
    X = X.fillna(0.0)

    # 3. Simple Baseline Model Evaluation for Benchmarking
    print("Computing Simple Baseline (Hierarchical Cell Averages)...")
    df['wkt_bucket'] = pd.cut(df['wickets_in_hand'], bins=[-1, 2, 4, 6, 8, 10], labels=['1-2', '3-4', '5-6', '7-8', '9-10'])
    cell_keys = ['match_format', 'innings', 'innings_phase', 'wkt_bucket']
    
    simple_bat_runs = df.groupby(cell_keys, observed=False)['bat_runs'].transform('mean')
    simple_dismissal = df.groupby(cell_keys, observed=False)['is_team_wicket'].transform('mean')
    simple_bowl_runs = df.groupby(cell_keys, observed=False)['bowler_runs'].transform('mean')
    simple_bowl_wkt = df.groupby(cell_keys, observed=False)['is_bowler_wicket'].transform('mean')

    simple_mae_bat = mean_absolute_error(df['bat_runs'], simple_bat_runs)
    simple_brier_out = brier_score_loss(df['is_team_wicket'], simple_dismissal)
    simple_auc_out = roc_auc_score(df['is_team_wicket'], simple_dismissal)

    simple_mae_bowl = mean_absolute_error(df['bowler_runs'], simple_bowl_runs)
    simple_brier_wkt = brier_score_loss(df['is_bowler_wicket'], simple_bowl_wkt)
    simple_auc_wkt = roc_auc_score(df['is_bowler_wicket'], simple_bowl_wkt)

    # 4. 5-Fold GroupKFold Cross-Validation by match_id
    print("Training 5-Fold GroupKFold Out-of-Fold ML Models by match_id...")
    gkf = GroupKFold(n_splits=5)
    groups = df['match_id']

    oof_bat_runs = np.zeros(len(df))
    oof_dismissal = np.zeros(len(df))
    oof_bowl_runs = np.zeros(len(df))
    oof_bowl_wkt = np.zeros(len(df))

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, groups=groups)):
        print(f"--- Fitting Fold {fold + 1}/5 ---")
        X_train, y_bat_train = X.iloc[train_idx], df['bat_runs'].iloc[train_idx]
        y_out_train = df['is_team_wicket'].iloc[train_idx]
        y_bowl_train = df['bowler_runs'].iloc[train_idx]
        y_wkt_train = df['is_bowler_wicket'].iloc[train_idx]

        X_val = X.iloc[val_idx]

        # Model 1: Expected Batter Runs
        reg_bat = HistGradientBoostingRegressor(max_iter=50, random_state=42 + fold)
        reg_bat.fit(X_train, y_bat_train)
        oof_bat_runs[val_idx] = reg_bat.predict(X_val)

        # Model 2: Expected Batter Dismissal Probability
        clf_out = HistGradientBoostingClassifier(max_iter=50, random_state=42 + fold)
        clf_out.fit(X_train, y_out_train)
        oof_dismissal[val_idx] = clf_out.predict_proba(X_val)[:, 1]

        # Model 3: Expected Bowler Runs Conceded
        reg_bowl = HistGradientBoostingRegressor(max_iter=50, random_state=42 + fold)
        reg_bowl.fit(X_train, y_bowl_train)
        oof_bowl_runs[val_idx] = reg_bowl.predict(X_val)

        # Model 4: Expected Bowler Wicket Probability
        clf_wkt = HistGradientBoostingClassifier(max_iter=50, random_state=42 + fold)
        clf_wkt.fit(X_train, y_wkt_train)
        oof_bowl_wkt[val_idx] = clf_wkt.predict_proba(X_val)[:, 1]

    # 5. Model Evaluation Metrics
    ml_mae_bat = mean_absolute_error(df['bat_runs'], oof_bat_runs)
    ml_brier_out = brier_score_loss(df['is_team_wicket'], oof_dismissal)
    ml_auc_out = roc_auc_score(df['is_team_wicket'], oof_dismissal)

    ml_mae_bowl = mean_absolute_error(df['bowler_runs'], oof_bowl_runs)
    ml_brier_wkt = brier_score_loss(df['is_bowler_wicket'], oof_bowl_wkt)
    ml_auc_wkt = roc_auc_score(df['is_bowler_wicket'], oof_bowl_wkt)

    print("\n--- MODEL PERFORMANCE COMPARISON ---")
    val_records = [
        {'Target': 'Batter Runs', 'Model': 'Simple Baseline', 'MAE': round(simple_mae_bat, 4), 'Brier_Score': np.nan, 'ROC_AUC': np.nan},
        {'Target': 'Batter Runs', 'Model': 'ML (HistGBM 5-Fold OOF)', 'MAE': round(ml_mae_bat, 4), 'Brier_Score': np.nan, 'ROC_AUC': np.nan},
        {'Target': 'Dismissal Prob', 'Model': 'Simple Baseline', 'MAE': np.nan, 'Brier_Score': round(simple_brier_out, 4), 'ROC_AUC': round(simple_auc_out, 4)},
        {'Target': 'Dismissal Prob', 'Model': 'ML (HistGBM 5-Fold OOF)', 'MAE': np.nan, 'Brier_Score': round(ml_brier_out, 4), 'ROC_AUC': round(ml_auc_out, 4)},
        {'Target': 'Bowler Runs', 'Model': 'Simple Baseline', 'MAE': round(simple_mae_bowl, 4), 'Brier_Score': np.nan, 'ROC_AUC': np.nan},
        {'Target': 'Bowler Runs', 'Model': 'ML (HistGBM 5-Fold OOF)', 'MAE': round(ml_mae_bowl, 4), 'Brier_Score': np.nan, 'ROC_AUC': np.nan},
        {'Target': 'Bowler Wicket Prob', 'Model': 'Simple Baseline', 'MAE': np.nan, 'Brier_Score': round(simple_brier_wkt, 4), 'ROC_AUC': round(simple_auc_wkt, 4)},
        {'Target': 'Bowler Wicket Prob', 'Model': 'ML (HistGBM 5-Fold OOF)', 'MAE': np.nan, 'Brier_Score': round(ml_brier_wkt, 4), 'ROC_AUC': round(ml_auc_wkt, 4)}
    ]
    val_df = pd.DataFrame(val_records)
    val_df.to_csv('outputs/tables/model_validation_summary.csv', index=False)
    print(val_df.to_string())

    # 6. Assign Predictions to Deliveries
    df['exp_bat_runs'] = oof_bat_runs
    df['exp_dismissal'] = oof_dismissal
    df['exp_bowl_runs'] = oof_bowl_runs
    df['exp_bowl_wkt'] = oof_bowl_wkt

    # Performance Above Expectation (PAE)
    df['bat_raa'] = df['bat_runs'] - df['exp_bat_runs']
    df['bat_waa'] = df['exp_dismissal'] - df['is_team_wicket'].astype(float)  # Positive = avoided dismissal

    df['bowl_rpa'] = df['exp_bowl_runs'] - df['bowler_runs']  # Positive = conceded fewer runs than expected
    df['bowl_waa'] = df['is_bowler_wicket'].astype(float) - df['exp_bowl_wkt']  # Positive = took wicket above expectation

    # Save Output
    out_path = 'outputs/processed/deliveries_with_expected.parquet'
    df.to_parquet(out_path, index=False)
    print(f"\nDeliveries with expected metrics saved to {out_path} ({os.path.getsize(out_path):,} bytes)")
    return df

if __name__ == '__main__':
    run_build_expected_performance()
