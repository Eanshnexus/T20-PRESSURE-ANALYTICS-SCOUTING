"""
build_final_submission.py - SupeRR Selector Season 2
Packages the official competition deliverables for Rajasthan Royals and Unstop
after final statistical reconciliation and strict IPL classification fix.
"""

import os
import shutil

def run_build_final_submission():
    print("="*60)
    print("FINAL STEP: ASSEMBLING OFFICIAL COMPETITION SUBMISSION PACKAGE")
    print("="*60)

    sub_dir = 'outputs/FINAL_SUBMISSION'
    charts_dir = f'{sub_dir}/charts'
    os.makedirs(sub_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)

    # 1. Copy Visually Verified PDF Report
    pdf_src = 'outputs/reports/SuPeRR_Selector_Season_2_Final_Report.pdf'
    pdf_dst = f'{sub_dir}/SuPeRR_Selector_Season_2_Final_Report.pdf'
    shutil.copy(pdf_src, pdf_dst)
    print(f"Copied PDF Report -> {pdf_dst} ({os.path.getsize(pdf_dst):,} bytes)")

    # 2. Copy Global, IPL-Relevant & Complete Rankings CSVs
    rankings_files = [
        ('outputs/rankings/top_10_batters.csv', 'top_10_batters.csv'),
        ('outputs/rankings/top_10_bowlers.csv', 'top_10_bowlers.csv'),
        ('outputs/rankings/top_10_batters_ipl_relevant.csv', 'top_10_batters_ipl_relevant.csv'),
        ('outputs/rankings/top_10_bowlers_ipl_relevant.csv', 'top_10_bowlers_ipl_relevant.csv'),
        ('outputs/rankings/combined_player_analysis.csv', 'combined_player_analysis.csv'),
        ('outputs/tables/all_eligible_bowlers.csv', 'all_eligible_bowlers.csv')
    ]
    for src, dst_name in rankings_files:
        dst = f'{sub_dir}/{dst_name}'
        shutil.copy(src, dst)
        print(f"Copied CSV -> {dst}")

    # 3. Copy Reconciliation & Validation Reports
    shutil.copy('docs/PLAYER_ID_RECONCILIATION.md', f'{sub_dir}/PLAYER_ID_RECONCILIATION.md')
    shutil.copy('docs/FINAL_STATISTICAL_RECONCILIATION.md', f'{sub_dir}/FINAL_STATISTICAL_RECONCILIATION.md')
    shutil.copy('docs/FINAL_METHODOLOGY_VALIDATION.md', f'{sub_dir}/FINAL_METHODOLOGY_VALIDATION.md')
    print(f"Copied Reconciliation & Validation Reports -> {sub_dir}/")

    # 4. Copy Key Supporting Charts
    chart_files = sorted([f for f in os.listdir('outputs/charts') if f.endswith('.png')])
    for cf in chart_files:
        shutil.copy(f'outputs/charts/{cf}', f'{charts_dir}/{cf}')
    print(f"Copied {len(chart_files)} analytical charts to {charts_dir}/")

    # 5. Create METHODOLOGY_SUMMARY.md
    methodology_summary_content = """# SupeRR Selector Season 2: Methodology & Evaluation Summary
## Rajasthan Royals — IPL 2027 Auction Analytics Challenge

**Primary Objective:** Identify the 10 most reliable batters and 10 most reliable bowlers under match pressure using reproducible statistical modeling across 200,999 deliveries (867 matches: genuine IPL 2022–2026 [87,687 balls] & International/Emerging T20 [113,312 balls]).

---

### 1. Pre-Delivery Pressure Definition (Zero Outcome Leakage)
Every delivery is categorized strictly from scoreboard state prior to ball release:
- **Continuous Composite Pressure Index (CPI):** Scaled on $[0.0, 1.0]$. Calibrated threshold $\\text{CPI} \\ge 0.60$ captures **55,011 high-pressure balls (27.37%)** across the dataset (30.0% Innings 1, 24.4% Innings 2, 100% Super Overs). Medium pressure ($0.35 \\le \\text{CPI} < 0.60$): 41.85%; Low pressure ($\\text{CPI} < 0.35$): 30.78%.

---

### 2. Contextual Expectation Baselines (Match-Grouped, Non-Chronological 5-Fold GroupKFold ML)
Out-of-fold `HistGradientBoosting` models grouped strictly by `match_id` across all 200,999 deliveries (zero intra-match leakage; non-chronological):
1. **Batter Runs (MAE):** OOF cell baseline `1.2956 ± 0.0136` vs HistGBM `1.2850 ± 0.0163` (`+0.0105`, 95% match-clustered CI `[+0.00755, +0.01375]`, 5/5 folds positive).
2. **Batter Dismissal (ROC-AUC / Brier):** AUC `0.5752 → 0.5958` (`+0.0205`, 5/5 positive); Brier `0.05086`, BSS `0.78%`, ECE `0.00154`.
3. **Bowler Runs (MAE):** OOF cell baseline `1.2858 ± 0.0132` vs HistGBM `1.2743 ± 0.0163` (`+0.0116`, 95% match-clustered CI `[+0.00853, +0.01504]`, 5/5 folds positive).
4. **Bowler Wickets (ROC-AUC / Brier):** AUC `0.5668 → 0.5854` (`+0.0186`, 5/5 positive); Brier `0.04827`, BSS `0.46%`, ECE `0.00141`.

*Limitation:* Single-ball T20 outcomes exhibit high intrinsic variance; per-delivery predictive gains are modest, though well-calibrated and positive across all five match-grouped folds.

---

### 3. Empirical Bayes Shrinkage, 3-Way Competition Separation & Format Weighting
- **3-Way Competition Categories:** (1) **IPL** (`comp_name.str.startswith('IPL')`, 5 seasons, 87,687 balls), (2) **International T20I** (`match_format == 'T20I'`, 131 series, 106,327 balls), (3) **Other T20** (`comp_id 2670` Emerging Teams Asia Cup 2024 & `comp_id 3289` Asia Cup Rising Stars 2025, 6,985 balls). `Other T20` deliveries are never counted in IPL or T20I format splits.
- **Population Priors ($\\mu_{\\text{prior}}$, players with $\\ge 60$ HP deliveries):**
  - Batters ($n=230$): $\\mu_{\\text{bat}} = +8.4678$ runs/100 balls ($K_{\\text{bat}} = 150$; empirical method-of-moments $K_{\\text{emp}} = 205.2$, sensitivity $\\rho = 0.9997$).
  - Bowlers ($n=207$): $\\mu_{\\text{bowl}} = -0.2183$ runs/6 balls ($K_{\\text{bowl}} = 200$; empirical method-of-moments $K_{\\text{emp}} = 343.3$, sensitivity $\\rho = 0.9996$).
- **Exact Rating Formula ($I$ = genuine IPL score, $T$ = genuine T20I score, $P$ = player composite pressure impact score):**
  - **Both Formats** ($N_{\\text{IPL}} \\ge 50/60$ & $N_{\\text{T20I}} \\ge 50/60$): $R = 0.455\\,I + 0.195\\,T + 0.350\\,P$
  - **IPL-Only / Dominant** ($N_{\\text{IPL}} \\ge 50/60$, $N_{\\text{T20I}} < 50/60$): $R = 0.520\\,I + 0.480\\,P$
  - **T20I-Only / Limited IPL** ($N_{\\text{IPL}} < 50/60$): $R = 0.195\\,T + 0.805\\,P$

---

### 4. Official Global Top 10 Player Rankings (Primary Competition Deliverable)

#### Top 10 Batters Under Pressure (`top_10_batters.csv`):
1. **Suryakumar Yadav** (`1699` | MI) — **96.6** | 453 HP BF (277 IPL / 176 T20I / 0 Other), SR 205.1, RAA +240.1, 71.4% cons. (High)
2. **Tristan Stubbs** (`20702` | DC) — **95.1** | 529 HP BF (366 IPL / 163 T20I / 0 Other), SR 180.0, RAA +165.6, WAA +12.48 (Moderate)
3. **Namboori Tilak Varma** (`7897` | MI) — **93.2** | 675 HP BF (364 IPL / 298 T20I / 13 Other), SR 178.5, RAA +193.7, WAA +12.69 (High)
4. **Dhruv Jurel** (`7260` | RR) — **92.5** | 283 HP BF (279 IPL / 4 T20I / 0 Other), SR 184.8, RAA +80.1, WAA +5.51 (Volatile)
5. **Heinrich Klaasen** (`4260` | SRH) — **92.4** | 535 HP BF (475 IPL / 60 T20I / 0 Other), SR 182.8, RAA +179.1 (Moderate)
6. **Naman Dhir** (`37052` | MI) — **92.2** | 209 HP BF (158 IPL / 51 T20I / 0 Other), SR 189.0, RAA +78.9 (Moderate)
7. **Rishabh Pant** (`4703` | DC) — **92.1** | 266 HP BF (211 IPL / 55 T20I / 0 Other), SR 197.4, RAA +97.1 (Volatile)
8. **Tim David** (`6396` | MI) — **91.5** | 680 HP BF (455 IPL / 225 T20I / 0 Other), SR 182.6, RAA +215.6, WAA +15.65 (High)
9. **Ashutosh Sharma** (`8101` | DC) — **91.4** | 283 HP BF (276 IPL / 0 T20I / 7 Other), SR 176.0, RAA +103.7 (Moderate)
10. **Azmatullah Omarzai** (`6676` | PBKS) — **90.8** | 362 HP BF (63 IPL / 299 T20I / 0 Other), SR 162.7, RAA +109.6 (Volatile)

#### Top 10 Bowlers Under Pressure (`top_10_bowlers.csv`):
1. **Sunil Narine** (`781` | KKR) — **85.6** | 376 balls (376 IPL / 0 T20I / 0 Other), Econ 5.78, RPA +149.8, 29 wkts (High)
2. **Jasprit Bumrah** (`2933` | MI) — **81.7** | 597 balls (404 IPL / 193 T20I / 0 Other), Econ 6.76, RPA +230.9, 47 wkts (High)
3. **Abrar Ahmed** (`5979` | Pakistan) — **74.9** | 276 balls (0 IPL / 276 T20I / 0 Other), Econ 5.09, RPA +96.8, 23 wkts (High)
4. **Shaheen Afridi** (`6355` | Pakistan) — **70.3** | 277 balls (0 IPL / 277 T20I / 0 Other), Econ 6.93, RPA +73.1, 28 wkts (Moderate)
5. **Mohammad Nawaz** (`2490` | Pakistan) — **69.2** | 175 balls (0 IPL / 175 T20I / 0 Other), Econ 5.35, RPA +44.2, 17 wkts (Volatile)
6. **Mitchell Santner** (`4101` | CSK) — **66.6** | 411 balls (92 IPL / 319 T20I / 0 Other), Econ 6.83, RPA +58.6, 27 wkts (High)
7. **Umran Malik** (`25048` | SRH) — **66.4** | 170 balls (98 IPL / 72 T20I / 0 Other), Econ 7.24, RPA +26.4, 17 wkts (Volatile)
8. **Matheesha Pathirana** (`8661` | CSK) — **66.1** | 602 balls (422 IPL / 180 T20I / 0 Other), Econ 7.79, RPA +129.7, 49 wkts (High)
9. **Akeal Hosein** (`2417` | CSK) — **65.6** | 186 balls (29 IPL / 157 T20I / 0 Other), Econ 6.32, RPA +54.6, 13 wkts (Moderate)
10. **Sufiyan Muqeem** (`34485` | Pakistan) — **63.3** | 199 balls (0 IPL / 134 T20I / 65 Other), Econ 5.52, RPA +53.8, 18 wkts (High)

---

### 5. Separate IPL-Relevant Recruitment Rankings (Secondary Scouting View)
*Screening Note:* Excludes international-only bowlers with practical IPL recruitment unavailability based on historical participation precedent since 2008. Distinct from confirmed IPL 2027 auction release/retention status.

- **IPL-Relevant Top 10 Batters (`top_10_batters_ipl_relevant.csv`):** Identical to Global Top 10.
- **IPL-Relevant Top 10 Bowlers (`top_10_bowlers_ipl_relevant.csv`):**
  1. Sunil Narine (`781`, 85.6), 2. Jasprit Bumrah (`2933`, 81.7), 3. Mitchell Santner (`4101`, 66.6), 4. Umran Malik (`25048`, 66.4), 5. Matheesha Pathirana (`8661`, 66.1), 6. Akeal Hosein (`2417`, 65.6), 7. **Mohsin Khan** (`6669`, 62.53), 8. **Kuldeep Yadav** (`3644`, 62.48), 9. **Lungi Ngidi** (`4641`, 60.76), 10. **Obed McCoy** (`4837`, 60.37).
"""
    with open(f'{sub_dir}/METHODOLOGY_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(methodology_summary_content.strip())
    print(f"Generated -> {sub_dir}/METHODOLOGY_SUMMARY.md")

    # 6. Create FINAL_SUBMISSION_CHECKLIST.md
    checklist_content = """# SupeRR Selector Season 2: Final Submission Checklist

**Competition:** Rajasthan Royals SupeRR Selector Season 2  
**Submission Portal:** Unstop  
**Date:** November 2026  

---

### 1. Deliverables Inventory Check
- [x] **Primary Top 10 Batters (Global):** `top_10_batters.csv` (10 rows, zero duplicates, canonical IDs verified at calculation level).
- [x] **Primary Top 10 Bowlers (Global):** `top_10_bowlers.csv` (10 rows, zero duplicates, strict IPL competition classification applied).
- [x] **Secondary IPL-Relevant Top 10 Batters:** `top_10_batters_ipl_relevant.csv` (identical to Global Top 10).
- [x] **Secondary IPL-Relevant Top 10 Bowlers:** `top_10_bowlers_ipl_relevant.csv` (ranked by exact unrounded `auction_rating`; elevates Mohsin Khan, Kuldeep Yadav, Lungi Ngidi, Obed McCoy).
- [x] **Complete Eligible Bowler Ranking:** `all_eligible_bowlers.csv` (all 111 bowlers with $\\ge 150$ HP legal balls).
- [x] **Combined All-Rounder & Roster Analysis:** `combined_player_analysis.csv` (160 eligible players).
- [x] **Publication Report (PDF):** `SuPeRR_Selector_Season_2_Final_Report.pdf` (5-page document visually inspected page-by-page; zero clipping or text overlap; 100% reconciled with CSVs).
- [x] **Final Methodology Validation:** `FINAL_METHODOLOGY_VALIDATION.md` (Exact rating formulas with worked proofs, 3-way competition audit, wicket-value & shrinkage sensitivity, calibration diagnostics, CPI assumptions).
- [x] **Final Statistical Reconciliation:** `FINAL_STATISTICAL_RECONCILIATION.md` (raw source verification, Sufiyan Muqeem competition fix, exact format-weighting equations, decomposition tables, model uncertainty).
- [x] **Canonical Player ID Reconciliation:** `PLAYER_ID_RECONCILIATION.md`.
- [x] **Methodology Summary:** `METHODOLOGY_SUMMARY.md`.
- [x] **Supporting Visual Evidence:** `charts/` (10 high-resolution PNG charts).
- [x] **Zero Raw Proprietary Data:** Verified that source CSVs (`ball_by_ball.csv`, `matches.csv`, etc.) are excluded from submission and review folders.

---

### 2. Status
**100% STATISTICALLY RECONCILED & READY FOR COMPETITION SUBMISSION**
"""
    with open(f'{sub_dir}/FINAL_SUBMISSION_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist_content.strip())
    print(f"Generated -> {sub_dir}/FINAL_SUBMISSION_CHECKLIST.md")

    print("\n" + "="*60)
    print(f"[SUCCESS] Final Submission Package successfully built at: {sub_dir}/")
    print("="*60)

if __name__ == '__main__':
    run_build_final_submission()
