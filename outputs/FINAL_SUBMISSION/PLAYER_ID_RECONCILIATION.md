# Canonical Player Identity Reconciliation & Verification Audit

**Project:** SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Analytics  
**Date:** November 2026  
**Auditor:** Quantitative Cricket Analytics Unit  

---

## 1. Executive Summary & Audit Verdict

During the preliminary documentation audit, six player IDs were flagged for verification against the canonical source files (`ball_by_ball.csv`, `competition_team_player_mapping.csv`, and `playing_eleven.csv`):

| Player Name | Preliminary Draft ID | Canonical Source ID | Primary Affiliation | Source Verification Status | Underlying Calculation Affected? |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Dhruv Jurel** | `8014` | **`7260`** | Rajasthan Royals / India | **Verified Canonical** (`8014` is Avi Dixit) | **NO — Presentation error only** |
| **Naman Dhir** | `37804` | **`37052`** | Mumbai Indians / India | **Verified Canonical** (`37804` non-existent) | **NO — Presentation error only** |
| **Rishabh Pant** | `1700` | **`4703`** | Delhi Capitals / India | **Verified Canonical** (`1700` non-existent) | **NO — Presentation error only** |
| **Ashutosh Sharma** | `36996` | **`8101`** | Delhi Capitals / India | **Verified Canonical** (`36996` non-existent) | **NO — Presentation error only** |
| **Mohammad Nawaz** | `3081` | **`2490`** | Pakistan | **Verified Canonical** (`3081` non-existent) | **NO — Presentation error only** |
| **Umran Malik** | `8006` | **`25048`** | Sunrisers Hyderabad / India | **Verified Canonical** (`8006` non-existent) | **NO — Presentation error only** |

**Audit Conclusion:**
The analytical pipeline (`rank_batters.py`, `rank_bowlers.py`, and `build_match_context.py`) strictly executed SQL-style group-bys directly on the raw integer fields `striker_id` and `bowler_id` from `ball_by_ball.csv`. At no point were statistics computed using the non-existent draft IDs or merged across players. The discrepancy was confined entirely to clerical transcription in early markdown text drafts, which has now been 100% reconciled across all CSV deliverables, technical documentation, and the PDF publication report.

---

## 2. Granular Player-by-Player Verification Evidence

### 2.1 Dhruv Jurel (Canonical ID: `7260`)
- **Mapping Verification:** In `competition_team_player_mapping.csv`, ID `7260` maps uniquely to `Dhruv Jurel` across teams `['Rajasthan Royals', 'India']`. Draft ID `8014` maps to `Avi Dixit` (`['Singapore']`).
- **Match Exposure:** In `playing_eleven.csv`, ID `7260` appears in 76 contested matches, whereas ID `8014` appears in 3 matches.
- **Ball-by-Ball Exposure:** ID `7260` faced 824 total balls (283 High-Pressure balls). ID `8014` faced 33 total balls (19 High-Pressure balls, which is below the 120-ball qualifying threshold).
- **Statistical Integrity:** All reported figures (283 HP BF, 523 runs, 184.8 SR, +80.1 RAA, 70.4% match consistency) originate exclusively from delivery records tagged with `striker_id == 7260`. Zero balls from Avi Dixit were included.

### 2.2 Naman Dhir (Canonical ID: `37052`)
- **Mapping Verification:** In `competition_team_player_mapping.csv`, ID `37052` maps uniquely to `Naman Dhir` across `['Mumbai Indians', 'India A', 'India']`. Draft ID `37804` does not exist in any source file (0 rows).
- **Match Exposure:** Appears in 58 matches in `playing_eleven.csv`.
- **Ball-by-Ball Exposure:** 603 total balls faced (209 High-Pressure balls) and 169 balls bowled.
- **Statistical Integrity:** Performance metrics (209 HP BF, 395 runs, 189.0 SR, +78.9 RAA, 75.0% consistency) are calculated entirely from `striker_id == 37052`.

### 2.3 Rishabh Pant (Canonical ID: `4703`)
- **Mapping Verification:** ID `4703` maps uniquely to `Rishabh Pant` across `['India', 'Delhi Capitals', 'Lucknow Super Giants']`. Draft ID `1700` does not exist in the dataset (0 rows).
- **Match Exposure:** Appears in 82 matches in `playing_eleven.csv`.
- **Ball-by-Ball Exposure:** 1,295 total balls faced (266 High-Pressure balls).
- **Statistical Integrity:** Performance metrics (266 HP BF, 525 runs, 197.4 SR, +97.1 RAA, 69.2% consistency) are calculated entirely from `striker_id == 4703`.

### 2.4 Ashutosh Sharma (Canonical ID: `8101`)
- **Mapping Verification:** ID `8101` maps uniquely to `Ashutosh Sharma` across `['Punjab Kings', 'Delhi Capitals', 'India A']`. Draft ID `36996` does not exist in the dataset (0 rows).
- **Match Exposure:** Appears in 47 matches in `playing_eleven.csv`.
- **Ball-by-Ball Exposure:** 369 total balls faced (283 High-Pressure balls).
- **Statistical Integrity:** Performance metrics (283 HP BF, 498 runs, 176.0 SR, +103.7 RAA, 53.8% consistency) are calculated entirely from `striker_id == 8101`.

### 2.5 Mohammad Nawaz (Canonical ID: `2490`)
- **Mapping Verification:** ID `2490` maps uniquely to `Mohammad Nawaz` for `['Pakistan']`. Draft ID `3081` does not exist in the dataset (0 rows).
- **Match Exposure:** Appears in 54 matches in `playing_eleven.csv`.
- **Ball-by-Ball Exposure:** 1,017 total balls bowled (175 High-Pressure legal balls) and 523 balls faced.
- **Statistical Integrity:** Defensive metrics (175 HP balls, 5.35 economy, 43.4% dot balls, 17 wickets, +44.2 RPA, 73.7% consistency) are calculated entirely from `bowler_id == 2490`.

### 2.6 Umran Malik (Canonical ID: `25048`)
- **Mapping Verification:** ID `25048` maps uniquely to `Umran Malik` across `['Sunrisers Hyderabad', 'India', 'Kolkata Knight Riders']`. Draft ID `8006` does not exist in the dataset (0 rows).
- **Match Exposure:** Appears in 61 matches in `playing_eleven.csv`.
- **Ball-by-Ball Exposure:** 600 total balls bowled (170 High-Pressure legal balls).
- **Statistical Integrity:** Defensive metrics (170 HP balls, 7.24 economy, 45.9% dot balls, 17 wickets, +26.4 RPA, 58.8% consistency) are calculated entirely from `bowler_id == 25048`.

---

## 3. Additional Secondary Cohort (IPL-Relevant Bowlers) Reconciliation

During final validation of the separate IPL-relevant bowler cohort, three additional text-draft IDs were reconciled against the canonical source mapping:
- **Mohsin Khan:** Draft `2901` → Canonical **`6669`** (Lucknow Super Giants)
- **Lungi Ngidi:** Draft `2420` → Canonical **`4641`** (Delhi Capitals / South Africa / RCB)
- **Obed McCoy:** Draft `2423` → Canonical **`4837`** (Rajasthan Royals / West Indies)

All draft IDs (`2901`, `2420`, `2423`) were non-existent in the source database (0 rows) and had zero impact on underlying metrics.

---

## 4. Reconciliation Across Deliverables

The canonical IDs have been audited across every project asset:

1. **Ranking CSVs (`top_10_batters.csv`, `top_10_bowlers.csv`):** 100% verified matching canonical IDs.
2. **Comprehensive CSV (`combined_player_analysis.csv`):** 100% verified matching canonical IDs.
3. **Internal Intermediate Tables (`batter_metrics.csv`, `bowler_metrics.csv`):** 100% verified matching canonical IDs.
4. **Documentation Reports (`FINAL_REPORT.md`, `METHODOLOGY.md`):** 100% verified matching canonical IDs.
5. **PDF Publication Report (`SuPeRR_Selector_Season_2_Final_Report.pdf`):** 100% verified matching canonical IDs.
