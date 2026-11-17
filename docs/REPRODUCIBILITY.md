# Reproducibility Guide: SupeRR Selector Season 2

**Repository / Workspace:** `Rajasthan Royals`  
**Execution Environment:** Python 3.10+ (Tested on Python 3.13 Windows)  
**Required Libraries:** `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `pyarrow`  

---

## 1. Directory Architecture

```
Rajasthan Royals/
├── ball_by_ball.csv
├── matches.csv
├── competitions.csv
├── teams.csv
├── playing_eleven.csv
├── competition_team_player_mapping.csv
├── scripts/
│   ├── prepare_data.py
│   ├── build_match_context.py
│   ├── calculate_pressure.py
│   ├── build_expected_performance.py
│   ├── rank_batters.py
│   ├── rank_bowlers.py
│   ├── robustness_analysis.py
│   ├── generate_visualizations.py
│   └── run_analysis.py
├── outputs/
│   ├── processed/
│   ├── tables/
│   ├── charts/
│   ├── rankings/
│   ├── reports/
│   └── CLAUDE_REVIEW_PACKAGE/
└── docs/
    ├── DATA_AUDIT.md
    ├── DATA_DICTIONARY.md
    ├── METHODOLOGY.md
    ├── FINAL_REPORT.md
    ├── TECHNICAL_APPENDIX.md
    └── REPRODUCIBILITY.md
```

---

## 2. One-Command Master Execution

To run the complete data processing, pre-delivery reconstruction, 5-fold cross-validation, player ranking, robustness sensitivity testing, and chart generation:

```bash
python scripts/run_analysis.py
```

**Expected Runtime:** $\approx 24.7$ seconds on a modern multi-core workstation.

---

## 3. Step-by-Step Modular Execution

Each stage can be executed independently:

```bash
# Stage 1: Data Ingestion & Cricket Rules Standardization
python scripts/prepare_data.py

# Stage 2: Reconstruct Pre-Delivery Cumulative Context (Zero-Leakage)
python scripts/build_match_context.py

# Stage 3: Pressure Models (Rule-Based & Continuous CPI)
python scripts/calculate_pressure.py

# Stage 4: 5-Fold GroupKFold ML Models for Expected Runs and Wickets
python scripts/build_expected_performance.py

# Stage 5: Batter Rating & Ranking
python scripts/rank_batters.py

# Stage 6: Bowler Rating & Ranking
python scripts/rank_bowlers.py

# Stage 7: Sensitivity & Robustness Analysis
python scripts/robustness_analysis.py

# Stage 8: Generate 10 High-Resolution Visualizations
python scripts/generate_visualizations.py
```

---

## 4. Key Verification Checkpoints

The pipeline executes automated programmatic assertions:
1. `prepare_data.py`: Checks delivery counts (200,999), legal deliveries (192,445), and bowler wickets (10,272).
2. `build_match_context.py`: Checks monotonicity of pre-delivery cumulative states, bounded wickets in hand $[0, 10]$, non-negative balls remaining, and 100% chase target coverage.
3. `calculate_pressure.py`: Verifies CPI distribution bounded $[0.0, 1.0]$ and categorizes ~27.4% deliveries as High Pressure.
4. `build_expected_performance.py`: Asserts 5-fold out-of-fold predictions cover 100% of deliveries with superior error metrics over baseline.
5. `run_analysis.py`: Verifies existence and non-zero size for all 23 pipeline outputs.
