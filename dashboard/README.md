# T20 Pressure Analytics & Scouting Dashboard
**SupeRR Selector Season 2 — Interactive Streamlit Platform**

An interactive cricket analytics and player scouting web application built with **Streamlit**, **Plotly**, **Pandas**, and **NumPy** to explore, filter, compare, and audit T20 batter and bowler performance under match pressure.

---

## 1. Key Features (8 Pages)
1. **Home / Analytics Overview (`app.py`):** Cricket stadium hero banner, verified KPI summary cards, Global Top 10 previews, season × 3-way format coverage, and CPI distribution.
2. **Batter Analytics (`pages/1_Batter_Analytics.py`):** Official Global Top 10 leaderboard, searchable/sortable/filterable full qualifying pool (`>=120` HP BF) with preserved Global Rank, and a 10-point scouting profile for any selected batter.
3. **Bowler Analytics (`pages/2_Bowler_Analytics.py`):** Official Global Top 10 bowling leaderboard, separate IPL-Relevant Top 10 scouting view, searchable 111-bowler qualifying pool (`>=150` HP balls), and 10-point defensive profiles.
4. **Head-to-Head Player Comparison (`pages/3_Player_Comparison.py`):** Select 2 or 3 batters or bowlers for side-by-side KPI cards, transparently normalized radar charts, 3-way format bar comparisons, and exact metric tables.
5. **Pressure Analytics (`pages/4_Pressure_Analytics.py`):** Live interactive pre-delivery CPI scenario simulator, CPI histogram, over-by-over 1st vs 2nd innings curve, 2nd-innings RRR × Wickets pressure heatmap, and knockout stakes diagnostics.
6. **Methodology (`pages/5_Methodology.py`):** Complete 11-stage documentation with exact LaTeX equations matching pipeline source code plus expandable worked numerical proofs (Suryakumar Yadav, Tristan Stubbs, Sunil Narine).
7. **Format & Robustness (`pages/6_Format_Robustness.py`):** Strict 3-way competition separation (`IPL`, `International T20I`, `Other T20`), 4-specification ranking sensitivity table, wicket-value & shrinkage sensitivity summary, match-grouped 5-fold validation, probability calibration curve, and statistical limitations.
8. **Scouting & Recruitment Insights (`pages/7_Scouting_Insights.py`):** Evidence-based batting and bowling role classification derived strictly from batting order, phase ball-shares, and pace/spin style, plus multi-skill all-rounder profiles.

---

## 2. Data Protection Architecture (Dual Mode)

### LOCAL COMPETITION MODE (Default Locally)
- Reads verified competition outputs locally from `../outputs/FINAL_SUBMISSION/`, `../outputs/tables/`, and `./data_cache/`.
- Joins players strictly on stable integer `Player ID` (`striker_id` / `bowler_id`) and reads verified `Auction Rating` values directly without frontend recalculation.
- **Strictly offline:** No proprietary data is transmitted to external services.

### PUBLIC DEMO MODE (Deployment-Ready Sanitized Structure)
- Uses 100% synthetic, fictional players stored in `dashboard/demo_data/` (`demo_batters.csv`, `demo_bowlers.csv`, `demo_pressure_aggregates.json`).
- Clearly displays a gold **`DEMONSTRATION DATA ACTIVE (PUBLIC DEMO MODE)`** banner across every page.
- To prepare a safe public deployment later:
  1. Copy only the `dashboard/` directory (excluding `dashboard/data_cache/`, which is listed in `.gitignore`).
  2. Set environment variable `DASHBOARD_PUBLIC_DEMO=1` in your hosting platform (e.g., Streamlit Community Cloud).
  3. Never commit `outputs/`, `data_cache/`, or any competition CSV/parquet files.

---

## 3. Running Locally (Windows)

### Option A: One-Click Launcher
Double-click `dashboard\run_dashboard.bat` inside Windows Explorer.

### Option B: Command Line (PowerShell / Terminal)
```powershell
cd "c:\Users\gupta\Desktop\Rajasthan Royals\dashboard"
pip install -r requirements.txt
python validate_dashboard_data.py
streamlit run app.py
```
Then open `http://localhost:8501` in your browser.
