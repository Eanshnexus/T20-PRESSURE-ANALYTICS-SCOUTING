"""
run_analysis.py - SupeRR Selector Season 2
Master Orchestrator: Executes the entire analytical pipeline end-to-end with automated verification.
"""

import os
import sys
import time

# Import pipeline stages
from prepare_data import run_prepare_data
from build_match_context import run_build_match_context
from calculate_pressure import run_calculate_pressure
from build_expected_performance import run_build_expected_performance
from rank_batters import run_rank_batters
from rank_bowlers import run_rank_bowlers
from robustness_analysis import run_robustness_analysis
from generate_visualizations import run_generate_visualizations

def run_master_pipeline():
    start_time = time.time()
    print("="*75)
    print("RAJASTHAN ROYALS: SUPERR SELECTOR SEASON 2 MASTER PIPELINE")
    print("="*75)

    # Stage 1: Data Preparation & Cricket Accounting
    run_prepare_data()

    # Stage 2: Reconstruct Pre-Delivery Context
    run_build_match_context()

    # Stage 3: Pressure Models (Rule-Based & CPI)
    run_calculate_pressure()

    # Stage 4: Expected Performance Baselines (GroupKFold ML)
    run_build_expected_performance()

    # Stage 5: Batter Rating & Ranking
    top_bat, bat_metrics = run_rank_batters()

    # Stage 6: Bowler Rating & Ranking
    top_bowl, bowl_metrics = run_rank_bowlers()

    # Stage 7: Robustness & Consistency Analysis
    run_robustness_analysis()

    # Stage 8: Generate Visualizations
    run_generate_visualizations()

    # Verification of All Artifacts
    required_artifacts = [
        'outputs/processed/clean_deliveries.parquet',
        'outputs/processed/deliveries_with_context.parquet',
        'outputs/processed/deliveries_with_pressure.parquet',
        'outputs/processed/deliveries_with_expected.parquet',
        'outputs/rankings/top_10_batters.csv',
        'outputs/rankings/top_10_bowlers.csv',
        'outputs/rankings/combined_player_analysis.csv',
        'outputs/tables/pressure_distribution.csv',
        'outputs/tables/model_validation_summary.csv',
        'outputs/tables/batter_metrics.csv',
        'outputs/tables/bowler_metrics.csv',
        'outputs/tables/format_comparison.csv',
        'outputs/tables/ranking_sensitivity.csv',
        'outputs/tables/match_consistency.csv',
        'outputs/charts/01_dataset_coverage.png',
        'outputs/charts/02_pressure_distribution.png',
        'outputs/charts/03_pressure_vs_ordinary.png',
        'outputs/charts/04_batter_impact_vs_sample.png',
        'outputs/charts/05_bowler_impact_vs_sample.png',
        'outputs/charts/06_top10_batters.png',
        'outputs/charts/07_top10_bowlers.png',
        'outputs/charts/08_player_consistency.png',
        'outputs/charts/09_ipl_vs_t20i.png',
        'outputs/charts/10_ranking_sensitivity.png'
    ]

    print("\n" + "="*75)
    print("AUTOMATED PIPELINE VERIFICATION")
    print("="*75)
    all_ok = True
    for path in required_artifacts:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"[PASSED] {path} ({os.path.getsize(path):,} bytes)")
        else:
            print(f"[FAILED] {path} MISSING OR EMPTY!")
            all_ok = False

    elapsed = time.time() - start_time
    print(f"\nPipeline execution finished in {elapsed:.1f} seconds. Status: {'SUCCESS' if all_ok else 'FAILED'}")
    return all_ok

if __name__ == '__main__':
    # Ensure current scripts directory is on sys.path
    sys.path.append(os.path.abspath('scripts'))
    run_master_pipeline()
