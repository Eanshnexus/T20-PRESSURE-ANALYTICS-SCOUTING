# T20 Pressure Analytics & Scouting Platform
### Rajasthan Royals — SupeRR Selector Season 2 (IPL 2027 Auction Analytics Challenge)
**Developed by Eko_Dev**

A reproducible T20 cricket analytics framework and interactive 8-page Streamlit scouting platform identifying the most reliable batters and bowlers under high-pressure match situations across **200,999 deliveries** and **867 contested matches** (IPL, International T20I, and Other T20).

---

## Live Dashboard (Streamlit Cloud)

- **Main Entrypoint:** `dashboard/app.py`
- **Dependencies:** `requirements.txt` (root) / `dashboard/requirements.txt`
- **Local Run:**
  ```bash
  pip install -r requirements.txt
  python -m streamlit run dashboard/app.py
  ```

### Dashboard Modules
1. **Dashboard (`dashboard/app.py`)** — Verified dataset coverage KPIs, Global Top 10 Batters & Bowlers snapshots, and platform directory.
2. **Batter Analytics** — Interactive filters, search, Pressure vs. Ordinary comparison, and individual batter scouting profiles.
3. **Bowler Analytics** — Global Top 10 vs. IPL-Relevant Top 10 recruitment pool toggle, economy/wicket impact scatter, and bowler profiles.
4. **Player Comparison** — Head-to-head radar overlays, format splits, and pressure uplift comparisons.
5. **Pressure Analytics** — Pre-delivery Composite Pressure Index (`CPI >= 0.60`) distributions and interactive live CPI Simulator.
6. **Methodology** — Mathematical specification of ex-ante CPI, 5-fold match-grouped HistGBM expected performance models, Empirical Bayes shrinkage, and Auction Rating formula.
7. **Format & Robustness** — Strict 3-way competition separation (`IPL` / `T20I` / `Other T20`) and cross-model rank stability matrix.
8. **Scouting Insights** — IPL 2027 auction archetypes, recruitment flags, and downloadable shortlist CSVs.

---

## Repository Structure

```text
├── dashboard/                     # 8-page interactive Streamlit application
│   ├── app.py                     # Main Streamlit entrypoint
│   ├── pages/                     # 7 analytical & scouting pages
│   ├── components/                # Sidebar, KPI cards, Plotly charts, player profiles
│   ├── utils/                     # Verified data loader, validation & formatting
│   ├── data_cache/                # Strictly aggregated JSON/CSV summaries (no raw rows)
│   └── assets/                    # Bespoke stadium/action imagery, crest SVG, CSS theme
├── outputs/
│   ├── FINAL_SUBMISSION/          # Verified Top 10 CSVs, 5-page PDF report, 10 charts, audits
│   └── tables/                    # Eligible player metrics, sensitivity & validation tables
├── scripts/                       # Reproducible end-to-end analytical pipeline
├── docs/                          # Full technical report, methodology & data audit
├── requirements.txt               # Streamlit Cloud dependencies
└── .gitignore                     # Excludes raw proprietary ball-by-ball CSVs & parquets
```

> **Data Protection Note:** Raw competition ball-by-ball CSVs and intermediate `.parquet` files are excluded via `.gitignore`. All committed files under `outputs/` and `dashboard/data_cache/` contain strictly aggregated player-level and match-segment summary statistics.
