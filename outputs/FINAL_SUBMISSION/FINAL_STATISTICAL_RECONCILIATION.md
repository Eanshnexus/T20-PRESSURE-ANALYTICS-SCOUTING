# Final Statistical Reconciliation & Pre-Submission Audit
**Project:** SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Analytics  
**Date:** November 2026  
**Scope:** End-to-End Calculation Verification, Competition Classification Correction, Format-Weighting Decomposition & Deliverable Reconciliation  

---

## 1. Calculation-Level Canonical Player Identity Verification

To confirm whether six previously corrected player IDs affected any underlying statistics, model predictions, or rankings, every delivery was independently re-aggregated directly from raw `ball_by_ball.csv` and `outputs/processed/deliveries_with_expected.parquet` using each player's canonical integer ID (`striker_id` / `bowler_id`) and compared against the final ranking CSVs:

### Batters: Raw Source Recalculation vs Final Ranking CSV
| Player Name | Canonical ID | Raw Total BF (excl. Wides) | Raw Total Runs | HP Balls Faced (Recalc / CSV) | HP Runs | Exp Runs | HP RAA (Recalc / CSV) | HP SR (Recalc / CSV) | HP Dism / Exp | HP WAA (Recalc / CSV) | Match? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dhruv Jurel** | `7260` | 798 | 1,207 | **283 / 283** | 523 | 442.87 | **+80.13 / +80.1** | **184.81 / 184.8** | 16 / 21.51 | **+5.51 / +5.51** | **EXACT** |
| **Naman Dhir** | `37052` | 589 | 992 | **209 / 209** | 395 | 316.09 | **+78.91 / +78.9** | **189.00 / 189.0** | 13 / 15.27 | **+2.27 / +2.27** | **EXACT** |
| **Rishabh Pant** | `4703` | 1,240 | 1,774 | **266 / 266** | 525 | 427.87 | **+97.13 / +97.1** | **197.37 / 197.4** | 17 / 18.34 | **+1.34 / +1.34** | **EXACT** |
| **Ashutosh Sharma** | `8101` | 347 | 577 | **283 / 283** | 498 | 394.30 | **+103.70 / +103.7** | **175.97 / 176.0** | 19 / 21.26 | **+2.26 / +2.26** | **EXACT** |

### Bowlers: Raw Source Recalculation vs Final Ranking CSV
| Player Name | Canonical ID | Raw Total Legal Balls | HP Legal Balls (Recalc / CSV) | HP Runs | Exp Runs | HP RPA (Recalc / CSV) | HP Econ (Recalc / CSV) | HP Wkts / Exp | HP WAA (Recalc / CSV) | Match? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mohammad Nawaz** | `2490` | 1,004 | **175 / 175** | 156 | 200.21 | **+44.21 / +44.2** | **5.35 / 5.35** | 17 / 11.03 | **+5.97 / +5.97** | **EXACT** |
| **Umran Malik** | `25048` | 560 | **170 / 170** | 205 | 231.42 | **+26.42 / +26.4** | **7.24 / 7.24** | 17 / 10.40 | **+6.60 / +6.60** | **EXACT** |

### Audit Determination
- The six draft IDs (`8014`, `37804`, `1700`, `36996`, `3081`, `8006`) and three secondary-cohort draft IDs (`2901`, `2420`, `2423`) were **strictly clerical presentation errors in early markdown drafts**.
- In the source database, five of the six primary draft IDs and all three secondary draft IDs have **0 rows**; `8014` maps to Avi Dixit (Singapore, 19 HP BF, excluded by the 120-ball threshold).
- **Zero underlying aggregations, ML expectations, or rankings were affected.**

---

## 2. Investigation of Sufiyan Muqeem's 65 Alleged "IPL" Deliveries

### Root Cause Discovered in `competitions.csv` & Ranking Scripts
Inspection of `competitions.csv` revealed 7 competitions labeled `match_format == 'T20'`:
- Five genuine IPL seasons (`comp_id`: `1358` IPL 2022, `1715` IPL 2023, `2193` IPL 2024, `2725` IPL 2025, `3298` IPL 2026 — **87,687 deliveries**).
- Two non-IPL Asian Cricket Council emerging international tournaments (**6,985 deliveries**):
  - `comp_id 2670`: **Mens T20 Emerging Teams Asia Cup 2024**
  - `comp_id 3289`: **Asia Cup Rising Stars 2025**

Earlier versions of `scripts/rank_batters.py` and `scripts/rank_bowlers.py` filtered IPL deliveries using `hp_df['match_format'] == 'T20'`, inadvertently misclassifying those two emerging international tournaments as IPL.

### Complete Match-Level Breakdown of Sufiyan Muqeem (`ID: 34485`, 199 HP Legal Balls)
| Comp ID | Competition Name | Source `match_format` | Match ID | Match Date | HP Legal Balls | Runs | Wkts | Overs Bowled | True Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **`2670`** | **Mens T20 Emerging Teams Asia Cup 2024** | `T20` | `37091` | 2024-10-21 | **14** | 8 | 0 | 10, 12, 14 | **Non-IPL (Corrected)** |
| **`2670`** | **Mens T20 Emerging Teams Asia Cup 2024** | `T20` | `37095` | 2024-10-23 | **18** | 17 | 2 | 8, 10, 12 | **Non-IPL (Corrected)** |
| **`3289`** | **Asia Cup Rising Stars 2025** | `T20` | `48023` | 2025-11-18 | **12** | 4 | 2 | 12, 14 | **Non-IPL (Corrected)** |
| **`3289`** | **Asia Cup Rising Stars 2025** | `T20` | `48028` | 2025-11-21 | **12** | 8 | 0 | 13, 15 | **Non-IPL (Corrected)** |
| **`3289`** | **Asia Cup Rising Stars 2025** | `T20` | `48029` | 2025-11-23 | **9** | 8 | 1 | 11, 13 | **Non-IPL (Corrected)** |
| `2387` | Pakistan in Australia T20I Series 2024 | `T20I` | `37355` | 2024-11-16 | 9 | 7 | 0 | 12, 14 | International T20I |
| `2442` | Pakistan in South Africa T20I Series 2024 | `T20I` | `38795` | 2024-12-10 | 18 | 38 | 1 | 13, 17, 20 | International T20I |
| `2722` | Pakistan in Zimbabwe T20I Series 2024 | `T20I` | `37926` | 2024-12-01 | 6 | 5 | 2 | 14 | International T20I |
| `2722` | Pakistan in Zimbabwe T20I Series 2024 | `T20I` | `37927` | 2024-12-03 | 12 | 2 | 4 | 9, 11, 13 | International T20I |
| `2875` | Pakistan in West Indies T20I Series 2025 | `T20I` | `41510` | 2025-07-31 | 6 | 3 | 1 | 17 | International T20I |
| `2875` | Pakistan in West Indies T20I Series 2025 | `T20I` | `41511` | 2025-08-02 | 12 | 8 | 1 | 15, 17 | International T20I |
| `2875` | Pakistan in West Indies T20I Series 2025 | `T20I` | `41512` | 2025-08-03 | 6 | 3 | 1 | 18 | International T20I |
| `3133` | Asia Cup 2025 | `T20I` | `45498` | 2025-09-12 | 7 | 3 | 0 | 9, 16 | International T20I |
| `3159` | UAE T20I Tri-Series 2025 | `T20I` | `45851` | 2025-08-29 | 17 | 17 | 1 | 13, 15, 17 | International T20I |
| `3159` | UAE T20I Tri-Series 2025 | `T20I` | `45852` | 2025-08-30 | 24 | 43 | 0 | 12, 14, 16, 18 | International T20I |
| `3159` | UAE T20I Tri-Series 2025 | `T20I` | `45857` | 2025-09-07 | 17 | 9 | 2 | 12, 14, 16 | International T20I |

- **Finding:** Sufiyan Muqeem has **0 genuine IPL deliveries** and **199 international / emerging-international high-pressure balls**.
- **Other Affected Players:** Across the full dataset, 122 batters and 87 bowlers had balls in `comp_id 2670/3289`. Within the Top 10 Batters, only Tilak Varma (13 HP BF) and Ashutosh Sharma (7 HP BF) had deliveries in those two competitions.
- **Correction Applied:** Updated `rank_batters.py`, `rank_bowlers.py`, and `generate_visualizations.py` to classify IPL strictly via `comp_name.str.startswith('IPL', na=False)`. All downstream CSVs, charts, sensitivity tables, and the 5-page PDF were regenerated.

---

## 3. Exact Format-Weighting Equations & Global Prior Definition

### 3.1 Clarifying the "Global Prior" vs Player Composite Score $P$
Earlier narrative summaries imprecisely referred to $P$ (`pressure_impact_score`) as a "Global Prior." The actual mathematical implementation distinguishes two distinct quantities:

1. **Empirical Bayes Population Prior ($\mu_{\text{prior}}$):**
   - Role-specific and format-independent across all players with $\ge 60$ high-pressure deliveries:
     - **Batters ($n=230$):** $\mu_{\text{bat}} = \mathbf{+8.4678}$ runs added per 100 balls ($K_{\text{bat}} = 150$).
     - **Bowlers ($n=207$):** $\mu_{\text{bowl}} = \mathbf{-0.2183}$ runs prevented per 6 balls ($K_{\text{bowl}} = 200$).
   - Applied via standard Empirical Bayes shrinkage:
     $$\text{Shrunk Rate} = w \cdot \text{Observed Rate} + (1 - w) \cdot \mu_{\text{prior}}, \quad w = \frac{N_{\text{HP}}}{N_{\text{HP}} + K}$$
   - Larger sample size $N_{\text{HP}}$ increases observation weight $w$ and reduces pull toward $\mu_{\text{prior}}$.

2. **Player Format-Independent Composite Pressure Score ($P$):**
   - Computed over **all** of a player's high-pressure deliveries across both formats:
     $$P = 0.45 \cdot S_{\text{shrunk}} + 0.20 \cdot S_{\text{WAA}} + 0.20 \cdot S_{\Delta} + 0.15 \cdot S_{\text{consistency}}$$
   - Because $P$ is computed on a player's own matches, when a player has **zero IPL exposure** (e.g., Abrar Ahmed, Shaheen Afridi, Mohammad Nawaz, Sufiyan Muqeem), $P$ is derived **100% from their international deliveries** (shrunk toward $\mu_{\text{prior}}$ in its 45% scoring component).

### 3.2 Exact Algebraic Branches in `rank_batters.py` & `rank_bowlers.py`
Let $I$ = normalized IPL high-pressure rate (`ipl_score`, computed from `ipl_raa_per_100` / `ipl_rpa_per_6` if format sample $\ge 30$, else from `shrunk_rate`) and $T$ = normalized international/non-IPL high-pressure rate (`t20i_score`, same rule). Thresholds: $N_{\text{min}} = 50$ HP BF (batters) or $60$ HP legal balls (bowlers):

1. **Branch 1 — Both Formats ($N_{\text{IPL}} \ge N_{\text{min}}$ AND $N_{\text{Intl}} \ge N_{\text{min}}$):**
   $$R = 0.70(0.65 I + 0.35 P) + 0.30(0.65 T + 0.35 P) = \mathbf{0.455\, I + 0.195\, T + 0.350\, P}$$
2. **Branch 2 — IPL-Dominant / IPL-Only ($N_{\text{IPL}} \ge N_{\text{min}}$ AND $N_{\text{Intl}} < N_{\text{min}}$):**
   $$R = 0.80(0.65 I + 0.35 P) + 0.20 P = \mathbf{0.520\, I + 0.480\, P}$$
3. **Branch 3 — International-Only / Limited IPL ($N_{\text{IPL}} < N_{\text{min}}$):**
   $$R = 0.70 P + 0.30(0.65 T + 0.35 P) = \mathbf{0.195\, T + 0.805\, P}$$

### 3.3 Assessment of Missing-Format Behavior & Sensitivity Check
- **Does a T20I-only bowler receive a rating equivalent to their T20I impact?** Yes—algebraically $R = 0.195\, T + 0.805\, P$, where both $T$ and $P$ are computed exclusively from international deliveries (with $P$ shrunk toward $\mu_{\text{bowl}} = -0.2183$). Notice that compared to Branch 2 (IPL-only, $0.520\, I + 0.480\, P$), Branch 3 places **80.5% weight on the shrunk composite $P$** and only **19.5% on unshrunk raw rate $T$**, making T20I-only ratings naturally more conservative than equivalent raw IPL rates.
- **Zero IPL exposure is never claimed to demonstrate IPL performance.**
- **Sensitivity Test (Strict Missing-IPL Penalty):** If format-specific rates were shrunk independently toward $\mu_{\text{bowl}}$ ($K_{\text{fmt}}=100$) so that zero IPL balls receive the league-average score $\mu_{\text{bowl}}$ ($32.0$ on the 0–100 scale), the top 10 bowlers would become: #1 Bumrah (76.7), #2 Narine (70.5), #3 Pathirana (60.6), #4 Kuldeep (59.3), #5 Umran (58.4), #6 Abrar (58.0), #7 Hosein (56.6), #8 Shaheen (55.3), #9 Nawaz (54.0), #10 Santner (53.2) — dropping Muqeem out of the Top 10.
- **Decision:** We retain the corrected 3-branch formula for the **Global Top 10** because the competition mandate explicitly requires using IPL and T20I fairly without artificially penalizing international players to league average; simultaneously, we supply the separate **IPL-Relevant Top 10** so missing IPL exposure cannot distort franchise recruitment decisions.

---

## 4. Exact Rating Decomposition for All Top 10 Players (Post-Correction)

### Top 10 Batters Decomposition
| Rank | Player Name | ID | Branch | IPL BF | Intl BF | EB Obs Wt ($w$) | $I$ Score | $T$ Score | $P$ Score | IPL Contrib | Intl Contrib | $P$ Contrib | Exact Total | CSV Rating |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Suryakumar Yadav | `1699` | Both | 277 | 176 | 0.751 | 100.0 | 100.0 | 90.2 | 45.50 | 19.50 | 31.58 | **96.58** | **96.6** |
| 2 | Tristan Stubbs | `20702` | Both | 366 | 163 | 0.779 | 100.0 | 93.3 | 89.7 | 45.50 | 18.20 | 31.39 | **95.09** | **95.1** |
| 3 | Namboori Tilak Varma | `7897` | Both | 364 | 311 | 0.818 | 100.0 | 91.2 | 86.7 | 45.50 | 17.78 | 30.36 | **93.63** | **93.6** |
| 4 | Dhruv Jurel | `7260` | IPL-Only | 279 | 4 | 0.654 | 100.0 | 81.0 | 84.5 | 52.00 | 0.00 | 40.55 | **92.55** | **92.5** |
| 5 | Heinrich Klaasen | `4260` | Both | 475 | 60 | 0.781 | 100.0 | 100.0 | 78.4 | 45.50 | 19.50 | 27.44 | **92.44** | **92.4** |
| 6 | Naman Dhir | `37052` | Both | 158 | 51 | 0.582 | 96.8 | 100.0 | 81.9 | 44.05 | 19.50 | 28.65 | **92.20** | **92.2** |
| 7 | Rishabh Pant | `4703` | Both | 211 | 55 | 0.639 | 100.0 | 90.8 | 82.7 | 45.50 | 17.71 | 28.93 | **92.14** | **92.1** |
| 8 | Tim David | `6396` | Both | 455 | 225 | 0.819 | 100.0 | 100.0 | 75.6 | 45.50 | 19.50 | 26.47 | **91.47** | **91.5** |
| 9 | Ashutosh Sharma | `8101` | IPL-Only | 276 | 7 | 0.654 | 100.0 | 93.1 | 82.2 | 52.00 | 0.00 | 39.44 | **91.44** | **91.4** |
| 10 | Azmatullah Omarzai | `6676` | Both | 63 | 299 | 0.707 | 99.5 | 100.0 | 74.3 | 45.28 | 19.50 | 26.00 | **90.78** | **90.8** |

### Top 10 Bowlers Decomposition
| Rank | Player Name | ID | Branch | IPL Bls | Intl Bls | EB Obs Wt ($w$) | $I$ Score | $T$ Score | $P$ Score | IPL Contrib | Intl Contrib | $P$ Contrib | Exact Total | CSV Rating |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Sunil Narine | `781` | IPL-Only | 376 | 0 | 0.653 | 97.3 | 74.6 | 73.0 | 50.57 | 0.00 | 35.02 | **85.60** | **85.6** |
| 2 | Jasprit Bumrah | `2933` | Both | 404 | 193 | 0.749 | 100.0 | 58.9 | 70.7 | 45.50 | 11.48 | 24.74 | **81.71** | **81.7** |
| 3 | Abrar Ahmed | `5979` | Intl-Only | 0 | 276 | 0.580 | 65.7 | 90.1 | 71.2 | 0.00 | 17.57 | 57.28 | **74.85** | **74.9** |
| 4 | Shaheen Afridi | `6355` | Intl-Only | 0 | 277 | 0.581 | 58.2 | 77.1 | 68.6 | 0.00 | 15.03 | 55.24 | **70.27** | **70.3** |
| 5 | Mohammad Nawaz | `2490` | Intl-Only | 0 | 175 | 0.467 | 52.3 | 75.4 | 67.7 | 0.00 | 14.70 | 54.46 | **69.16** | **69.2** |
| 6 | Mitchell Santner | `4101` | Both | 92 | 319 | 0.673 | 83.7 | 51.7 | 52.6 | 38.06 | 10.09 | 18.40 | **66.55** | **66.6** |
| 7 | Umran Malik | `25048` | Both | 98 | 72 | 0.459 | 76.3 | 39.7 | 68.4 | 34.73 | 7.74 | 23.94 | **66.41** | **66.4** |
| 8 | Sufiyan Muqeem | `34485` | Intl-Only | 0 | 199 | 0.499 | 55.0 | 78.1 | 63.5 | 0.00 | 15.22 | 51.10 | **66.33** | **66.3** |
| 9 | Matheesha Pathirana | `8661` | Both | 422 | 180 | 0.751 | 80.2 | 45.4 | 59.2 | 36.51 | 8.84 | 20.74 | **66.09** | **66.1** |
| 10 | Akeal Hosein | `2417` | Intl-Only | 29 | 157 | 0.482 | 55.9 | 78.6 | 62.4 | 0.00 | 15.33 | 50.27 | **65.59** | **65.6** |

---

## 5. Reconciliation of IPL-Relevant Bowler Ranking Discrepancy

- **Earlier Narrative Draft:** Listed Kuldeep Yadav (`64.8`), Arshdeep Singh (`64.2`), Varun Chakravarthy (`63.8`), and Mohsin Khan (`63.1`).
- **Root Cause:** Those four numbers never existed in `outputs/tables/bowler_metrics.csv`; they were unverified narrative placeholders carried over from a truncated session note before programmatic extraction.
- **Authoritative Computation (`outputs/tables/bowler_metrics.csv` & `outputs/tables/all_eligible_bowlers.csv`, all 111 eligible bowlers sorted by exact unrounded `auction_rating`):**
  - **#11 Global / #7 IPL-Relevant:** Mohsin Khan (`ID: 6669`, LSG) — **`62.528`** (`62.5`)
  - **#12 Global / #8 IPL-Relevant:** Kuldeep Yadav (`ID: 3644`, DC) — **`62.477`** (`62.5`)
  - **#13 Global / #9 IPL-Relevant:** Lungi Ngidi (`ID: 4641`, DC) — **`60.765`** (`60.8`)
  - **#14 Global / #10 IPL-Relevant:** Obed McCoy (`ID: 4837`, RR) — **`60.372`** (`60.4`)
  - *(For reference: Arshdeep Singh `ID: 6464` ranks #21 Global at `53.076`; Varun Chakravarthy `ID: 6256` ranks outside top 25 at `49.523`.)*

The complete 111-bowler ranking has been exported to `outputs/tables/all_eligible_bowlers.csv` and verified identically across CSVs, Markdown reports, and PDF.

---

## 6. Summary of Rating & Ranking Changes Resulting from Corrections

1. **Top 10 Batters:** All 10 players and ranks (#1–#10) remain **unchanged**. Tilak Varma's rating moved from `93.2` → **`93.6`** (still #3) after removing 13 Emerging Asia Cup balls from his IPL split; Ashutosh Sharma's IPL BF adjusted from 283 → `276` (rating unchanged at `91.4`, #9).
2. **Top 10 Bowlers (Global):** Same 10 bowlers qualify, with internal reordering caused by removing 65 Emerging/Rising Stars Asia Cup deliveries from Sufiyan Muqeem's IPL count:
   - **Sufiyan Muqeem (`34485`):** Rank #3 (`79.9`) → **Rank #8 (`66.3`)**
   - **Abrar Ahmed (`5979`):** Rank #4 → **Rank #3 (`74.9`)**
   - **Shaheen Afridi (`6355`):** Rank #5 → **Rank #4 (`70.3`)**
   - **Mohammad Nawaz (`2490`):** Rank #6 → **Rank #5 (`69.2`)**
   - **Mitchell Santner (`4101`):** Rank #7 → **Rank #6 (`66.6`)**
   - **Umran Malik (`25048`):** Rank #8 → **Rank #7 (`66.4`)**
   - **Matheesha Pathirana (`8661`):** Unchanged at **Rank #9 (`66.1`)**
   - **Akeal Hosein (`2417`):** Unchanged at **Rank #10 (`65.6`)**
3. **Top 10 Bowlers (IPL-Relevant):** Tie-break order between Mohsin Khan (`62.528`, #7) and Kuldeep Yadav (`62.477`, #8) is now strictly ordered by unrounded `auction_rating`.

---

## 7. Model Performance Uncertainty & Honest Framing

Out-of-fold 5-fold GroupKFold (grouped by `match_id`) evaluation against an out-of-fold contextual cell baseline (match-clustered bootstrap, $B=500$):
- **Batter Runs (MAE):** Baseline `1.3177` vs HistGBM `1.2810` → Diff `+0.0367` (95% Match-Cluster CI: `[+0.0335, +0.0400]`; positive in all 5/5 folds: `mean +0.0367 ± 0.0026`). *(Relative to in-sample global cell baseline `1.2953`: `+0.80%` gain.)*
- **Batter Dismissal (ROC-AUC):** Baseline `0.5759` vs HistGBM `0.5974` → Diff `+0.0215` (positive in 5/5 folds: `mean +0.0205 ± 0.0049`).
- **Bowler Runs (MAE):** Baseline `1.3167` vs HistGBM `1.3016` → Diff `+0.0150` (95% Match-Cluster CI: `[+0.0121, +0.0184]`; positive in 5/5 folds: `mean +0.0150 ± 0.0043`). *(Relative to in-sample global cell baseline `1.2855`: `+0.87%` gain.)*
- **Bowler Wickets (ROC-AUC):** Baseline `0.5678` vs HistGBM `0.5880` → Diff `+0.0201` (positive in 5/5 folds: `mean +0.0198 ± 0.0048`).

**Limitation:** Single-ball T20 outcomes carry high stochastic noise (0, 1, 4, 6, wicket). While the HistGBM models consistently beat simple baselines across all 5 match-grouped folds, per-delivery MAE reductions remain modest (~0.015–0.037 runs/ball).

---

## 8. Final Rankings Summary

- **Final Global Top 10 Batters:** `top_10_batters.csv` — 1. Suryakumar Yadav (`1699`, 96.6), 2. Tristan Stubbs (`20702`, 95.1), 3. Namboori Tilak Varma (`7897`, 93.6), 4. Dhruv Jurel (`7260`, 92.5), 5. Heinrich Klaasen (`4260`, 92.4), 6. Naman Dhir (`37052`, 92.2), 7. Rishabh Pant (`4703`, 92.1), 8. Tim David (`6396`, 91.5), 9. Ashutosh Sharma (`8101`, 91.4), 10. Azmatullah Omarzai (`6676`, 90.8).
- **Final Global Top 10 Bowlers:** `top_10_bowlers.csv` — 1. Sunil Narine (`781`, 85.6), 2. Jasprit Bumrah (`2933`, 81.7), 3. Abrar Ahmed (`5979`, 74.9), 4. Shaheen Afridi (`6355`, 70.3), 5. Mohammad Nawaz (`2490`, 69.2), 6. Mitchell Santner (`4101`, 66.6), 7. Umran Malik (`25048`, 66.4), 8. Sufiyan Muqeem (`34485`, 66.3), 9. Matheesha Pathirana (`8661`, 66.1), 10. Akeal Hosein (`2417`, 65.6).
- **Final IPL-Relevant Top 10 Batters:** `top_10_batters_ipl_relevant.csv` — Identical to Global Top 10.
- **Final IPL-Relevant Top 10 Bowlers:** `top_10_bowlers_ipl_relevant.csv` — 1. Sunil Narine (`781`, 85.6), 2. Jasprit Bumrah (`2933`, 81.7), 3. Mitchell Santner (`4101`, 66.6), 4. Umran Malik (`25048`, 66.4), 5. Matheesha Pathirana (`8661`, 66.1), 6. Akeal Hosein (`2417`, 65.6), 7. Mohsin Khan (`6669`, 62.5), 8. Kuldeep Yadav (`3644`, 62.5), 9. Lungi Ngidi (`4641`, 60.8), 10. Obed McCoy (`4837`, 60.4).

---

## 9. PDF-to-CSV Reconciliation Status & Remaining Limitations

- **PDF-to-CSV Status:** 100% reconciled across all 5 pages of `SuPeRR_Selector_Season_2_Final_Report.pdf` (canonical player IDs, updated ranks #1–#10, Tilak Varma 93.6, Sufiyan Muqeem #8 at 66.3, updated charts, zero overlap/clipping).
- **Remaining Limitations Requiring Human Judgment:**
  1. **Unconfirmed IPL 2027 Auction Availability:** This analysis evaluates historical performance and practical recruitment availability (based on historical IPL participation precedent since 2008), NOT confirmed IPL 2027 franchise retentions, releases, injuries, or auction registrations.
  2. **Moderate-Sample Rank Volatility:** Players near the lower end of qualifying volume (Dhruv Jurel 283 BF, Rishabh Pant 266 BF, Umran Malik 170 balls, Mohammad Nawaz 175 balls) exhibit higher rank sensitivity under strict $\text{CPI} \ge 0.70$ cutoffs.
  3. **International-Heavy Samples:** Akeal Hosein (29 IPL / 157 Intl balls) and Azmatullah Omarzai (63 IPL / 299 Intl balls) derive a majority of their evidence from international T20s rather than Indian IPL venues.
  4. **Domain-Chosen Weighting:** The 70/30 IPL-to-T20I blend reflects strategic auction relevance rather than an empirically fitted regression parameter.
