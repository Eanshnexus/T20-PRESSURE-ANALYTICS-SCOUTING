# Final Methodology Validation & Formula Proof Report
**Project:** SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Analytics  
**Date:** November 2026  
**Source Code Audited:** `scripts/prepare_data.py`, `scripts/calculate_pressure.py`, `scripts/build_expected_performance.py`, `scripts/rank_batters.py`, `scripts/rank_bowlers.py`, `scripts/export_ipl_relevant_rankings.py`  

---

## 1. Exact Mathematical Formulation of the Auction Rating System

All equations below are transcribed directly from `scripts/rank_batters.py` and `scripts/rank_bowlers.py` with zero approximations.

### 1.1 Eligibility, Filtering & Missing-Value Handling
- **Batters (`rank_batters.py`):** Filtered to deliveries where `is_ball_faced == True` (`extras_type != 'wide'`). Qualifying eligibility for official ranking: $N_{\text{HP}} = \text{hp\_bf} \ge 120$ high-pressure balls faced (122 qualified batters out of 763).
- **Bowlers (`rank_bowlers.py`):** Filtered to deliveries where `is_legal == True` (`extras_type not in {'wide', 'Overstep', 'other'}`). Qualifying eligibility for official ranking: $N_{\text{HP}} = \text{hp\_balls} \ge 150$ high-pressure legal balls bowled (111 qualified bowlers out of 552).
- **Missing-Value Treatment:** Players with zero ordinary-pressure deliveries or zero deliveries in a specific format (`ipl_hp`, `t20i_hp`, `other_t20_hp`) receive `0.0` via `.fillna(0.0)` on left merges; `std_match_raa` / `std_match_rpa` fills single-match `NaN` with `0.0`. For format-rate scoring (`ipl_score`, `t20i_score`), any format with $< 30$ high-pressure balls falls back to the player's shrunk overall rate (`shrunk_raa_per_100` / `shrunk_rpa_per_6`), preventing small-sample format noise.

### 1.2 Empirical Bayes Population Prior ($\mu_{\text{prior}}$) & Shrinkage Adjustment
- **Role-Specific, Format-Independent Population Prior ($\mu_{\text{prior}}$):** Mean observed high-pressure rate across all players with $\ge 60$ high-pressure deliveries:
  - **Batters ($n=230$):** $\mu_{\text{bat}} = \mathbf{+8.467843}$ runs above expectation per 100 balls ($K_{\text{bat}} = 150.0$).
  - **Bowlers ($n=207$):** $\mu_{\text{bowl}} = \mathbf{-0.218343}$ runs prevented above expectation per 6 legal balls ($K_{\text{bowl}} = 200.0$).
- **Shrinkage Equation:**
  $$\text{Shrunk Rate}_i = w_i \cdot \text{Observed Rate}_i + (1 - w_i) \cdot \mu_{\text{prior}}, \quad w_i = \frac{N_{\text{HP}, i}}{N_{\text{HP}, i} + K}$$

### 1.3 Component Definitions, Caps & Linear Normalizations (0–100 Scale)

#### Batting Components (`rank_batters.py`):
1. **Scoring Component (`score_comp`, weight 45%):**
   $$\text{score\_comp} = \text{clip}\!\left(\frac{\text{shrunk\_raa\_per\_100} + 15.0}{45.0} \times 100,\; 0,\; 100\right)$$
   *(Maps $[-15, +30]$ RAA/100 linearly onto $[0, 100]$; values above $+30$ cap at $100.0$.)*
2. **Wicket Preservation Component (`wkt_comp`, weight 20%):**
   $$\text{wicket\_val\_per\_100} = \text{hp\_waa\_per\_100} \times 8.0, \quad \text{wkt\_comp} = \text{clip}\!\left(\frac{\text{wicket\_val\_per\_100} + 15.0}{35.0} \times 100,\; 0,\; 100\right)$$
   *(Where $\text{hp\_waa} = \sum \text{exp\_dismissal} - \sum \text{is\_team\_wicket}$; maps $[-15, +20]$ onto $[0, 100]$.)*
3. **Pressure Uplift / Delta Component (`delta_comp`, weight 20%):**
   $$\Delta_{\text{raa}} = \text{clip}\!\left(\text{hp\_raa\_per\_100} - \text{ord\_raa\_per\_100},\; -20.0,\; +25.0\right), \quad \text{delta\_comp} = \text{clip}\!\left(\frac{\Delta_{\text{raa}} + 20.0}{45.0} \times 100,\; 0,\; 100\right)$$
   *(Note: The displayed CSV column `Pressure uplift/deterioration` reports raw strike-rate delta $\Delta_{\text{SR}} = \text{hp\_sr} - \text{ord\_sr}$ for cricket readability, while the composite score uses context-adjusted $\Delta_{\text{raa}}$.)*
4. **Match Consistency (`cons_comp`, weight 15%):**
   $$\text{consistency\_pct} = \frac{\text{Count of HP matches with } \sum \text{bat\_raa} > 0}{\text{Total HP matches played}} \times 100$$
5. **Pressure Impact Score ($P$):**
   $$P_{\text{bat}} = 0.45 \cdot \text{score\_comp} + 0.20 \cdot \text{wkt\_comp} + 0.20 \cdot \text{delta\_comp} + 0.15 \cdot \text{cons\_comp}$$
6. **Ordinary Performance Score (`ord_score`, diagnostic only):**
   $$\text{ord\_score}_{\text{bat}} = \text{clip}\!\left(\frac{\text{ord\_raa\_per\_100} + 15.0}{40.0} \times 100,\; 0,\; 100\right)$$

#### Bowling Components (`rank_bowlers.py`):
1. **Run Prevention Component (`score_comp`, weight 45%):**
   $$\text{score\_comp} = \text{clip}\!\left(\frac{\text{shrunk\_rpa\_per\_6} + 1.5}{4.0} \times 100,\; 0,\; 100\right)$$
   *(Maps $[-1.5, +2.5]$ RPA/6 linearly onto $[0, 100]$.)*
2. **Wicket Impact Component (`wkt_comp`, weight 20%):**
   $$\text{wicket\_val\_per\_6} = \text{hp\_waa\_per\_6} \times 8.0, \quad \text{wkt\_comp} = \text{clip}\!\left(\frac{\text{wicket\_val\_per\_6} + 1.5}{3.5} \times 100,\; 0,\; 100\right)$$
   *(Where $\text{hp\_waa} = \sum \text{is\_bowler\_wicket} - \sum \text{exp\_bowl\_wkt}$; maps $[-1.5, +2.0]$ onto $[0, 100]$.)*
3. **Pressure Uplift / Delta Component (`delta_comp`, weight 20%):**
   $$\Delta_{\text{rpa}} = \text{clip}\!\left(\text{hp\_rpa\_per\_6} - \text{ord\_rpa\_per\_6},\; -2.0,\; +2.5\right), \quad \text{delta\_comp} = \text{clip}\!\left(\frac{\Delta_{\text{rpa}} + 2.0}{4.5} \times 100,\; 0,\; 100\right)$$
   *(Displayed CSV column `Pressure uplift/deterioration` reports $\Delta_{\text{econ}} = \text{ord\_econ} - \text{hp\_econ}$ where positive = tighter economy under pressure.)*
4. **Match Consistency (`cons_comp`, weight 15%):**
   $$\text{consistency\_pct} = \frac{\text{Count of HP matches with } \sum \text{bowl\_rpa} > 0}{\text{Total HP matches played}} \times 100$$
5. **Pressure Impact Score ($P$):**
   $$P_{\text{bowl}} = 0.45 \cdot \text{score\_comp} + 0.20 \cdot \text{wkt\_comp} + 0.20 \cdot \text{delta\_comp} + 0.15 \cdot \text{cons\_comp}$$
6. **Ordinary Performance Score (`ord_score`, diagnostic only):**
   $$\text{ord\_score}_{\text{bowl}} = \text{clip}\!\left(\frac{\text{ord\_rpa\_per\_6} + 1.5}{3.5} \times 100,\; 0,\; 100\right)$$

### 1.4 Format-Specific Scores ($I$, $T$) & Final Auction Rating ($R$)
- **Raw CSV Contributions (`IPL contribution`, `T20I contribution`):** Cumulative runs above expectation (`ipl_raa`, `t20i_raa`) or runs prevented (`ipl_rpa`, `t20i_rpa`) in genuine IPL and genuine International T20I respectively.
- **Normalized Format Rate Scores ($I$, $T$):**
  - Batters: $I = \text{clip}\!\left(\frac{r_{\text{IPL}} + 15.0}{45.0}\times 100, 0, 100\right)$ where $r_{\text{IPL}} = \text{ipl\_raa\_per\_100}$ if $\text{ipl\_bf} \ge 30$ else $\text{shrunk\_raa\_per\_100}$ (analogously for $T$ using $\text{t20i\_bf} \ge 30$).
  - Bowlers: $I = \text{clip}\!\left(\frac{r_{\text{IPL}} + 1.5}{4.0}\times 100, 0, 100\right)$ where $r_{\text{IPL}} = \text{ipl\_rpa\_per\_6}$ if $\text{ipl\_balls} \ge 30$ else $\text{shrunk\_rpa\_per\_6}$ (analogously for $T$ using $\text{t20i\_balls} \ge 30$).
- **Final Auction Rating ($R$) across Three Branches** ($N_{\text{min}} = 50$ HP BF for batters; $60$ HP legal balls for bowlers):
  1. **Both IPL & T20I ($N_{\text{IPL}} \ge N_{\text{min}}$ AND $N_{\text{T20I}} \ge N_{\text{min}}$):**
     $$R = 0.70(0.65 I + 0.35 P) + 0.30(0.65 T + 0.35 P) = \mathbf{0.455\,I + 0.195\,T + 0.350\,P}$$
  2. **IPL-Only / Dominant ($N_{\text{IPL}} \ge N_{\text{min}}$ AND $N_{\text{T20I}} < N_{\text{min}}$):**
     $$R = 0.80(0.65 I + 0.35 P) + 0.20 P = \mathbf{0.520\,I + 0.480\,P}$$
  3. **T20I-Only / Limited IPL ($N_{\text{IPL}} < N_{\text{min}}$):**
     $$R = 0.70 P + 0.30(0.65 T + 0.35 P) = \mathbf{0.195\,T + 0.805\,P}$$

### 1.5 Worked Step-by-Step Reproduction Proofs

#### Proof A: Suryakumar Yadav (Batter, `ID: 1699`, Branch: Both)
- Raw inputs: `hp_bf = 453`, `hp_raa = +240.0520`, `hp_raa_per_100 = 52.9916`, `ord_raa_per_100 = 24.8287`, `hp_waa = 5.8927` (`hp_waa_per_100 = 1.3008`), `consistency_pct = 71.4286%`.
- Empirical Bayes shrinkage: $w = \frac{453}{453+150} = 0.751244 \implies \text{shrunk\_raa\_per\_100} = 0.751244(52.9916) + 0.248756(8.4678) = 41.9160$.
- Components:
  - `score_comp` $= \text{clip}((41.9160+15)/45 \times 100, 0, 100) = \mathbf{100.0000}$
  - `wkt_comp` $= \text{clip}((1.3008 \times 8 + 15)/35 \times 100, 0, 100) = \mathbf{72.5899}$
  - `delta_comp`: $\Delta_{\text{raa}} = \text{clip}(52.9916 - 24.8287, -20, 25) = 25.0000 \implies \mathbf{100.0000}$
  - `cons_comp` $= \mathbf{71.4286}$
- Pressure Impact Score: $P = 0.45(100) + 0.20(72.5899) + 0.20(100) + 0.15(71.4286) = \mathbf{90.2323}$ (CSV: `90.2`).
- Format scores: IPL (`277` BF, `37.6135` RAA/100) $\implies I = \mathbf{100.0000}$; T20I (`176` BF, `77.1946` RAA/100) $\implies T = \mathbf{100.0000}$.
- Final Auction Rating: $R = 0.455(100) + 0.195(100) + 0.350(90.2323) = \mathbf{96.5813} \to \mathbf{96.6}$ (**Exact CSV Match**).

#### Proof B: Tristan Stubbs (Batter, `ID: 20702`, Branch: Both)
- Raw inputs: `hp_bf = 529`, `hp_raa = +165.5861`, `hp_raa_per_100 = 31.3017`, `ord_raa_per_100 = -8.2252`, `hp_waa = 12.4776` (`hp_waa_per_100 = 2.3587`), `consistency_pct = 60.5263%`.
- Empirical Bayes shrinkage: $w = \frac{529}{529+150} = 0.779087 \implies \text{shrunk\_raa\_per\_100} = 26.2574$.
- Components: `score_comp` $= \mathbf{91.6832}$, `wkt_comp` $= \mathbf{96.7708}$ (`wkt_val = 18.8698`), `delta_comp` $= \mathbf{100.0000}$ ($\Delta = 39.53 \to 25.0$), `cons_comp` $= \mathbf{60.5263}$.
- Pressure Impact Score: $P = 0.45(91.6832) + 0.20(96.7708) + 0.20(100) + 0.15(60.5263) = \mathbf{89.6905}$ (CSV: `89.7`).
- Format scores: IPL (`366` BF, `33.2213` RAA/100) $\implies I = \mathbf{100.0000}$; T20I (`163` BF, `26.9915` RAA/100) $\implies T = \mathbf{93.3145}$.
- Final Auction Rating: $R = 0.455(100) + 0.195(93.3145) + 0.350(89.6905) = \mathbf{95.0880} \to \mathbf{95.1}$ (**Exact CSV Match**).

#### Proof C: Sunil Narine (Bowler, `ID: 781`, Branch: IPL-Only)
- Raw inputs: `hp_balls = 376`, `hp_rpa = +149.7961`, `hp_rpa_per_6 = 2.3904`, `ord_rpa_per_6 = 1.4410`, `hp_waa = 8.3363` (`hp_waa_per_6 = 0.1330`), `consistency_pct = 77.5000%`.
- Empirical Bayes shrinkage: $w = \frac{376}{376+200} = 0.652778 \implies \text{shrunk\_rpa\_per\_6} = 0.652778(2.3904) + 0.347222(-0.2183) = 1.4846$.
- Components:
  - `score_comp` $= (1.4846 + 1.5)/4.0 \times 100 = \mathbf{74.6141}$
  - `wkt_comp` $= (0.1330 \times 8 + 1.5)/3.5 \times 100 = \mathbf{73.2631}$
  - `delta_comp`: $\Delta_{\text{rpa}} = 2.3904 - 1.4410 = 0.9494 \implies (0.9494+2.0)/4.5 \times 100 = \mathbf{65.5417}$
  - `cons_comp` $= \mathbf{77.5000}$
- Pressure Impact Score: $P = 0.45(74.6141) + 0.20(73.2631) + 0.20(65.5417) + 0.15(77.5000) = \mathbf{72.9623}$ (CSV: `73.0`).
- Format score: IPL (`376` balls, `2.3904` RPA/6) $\implies I = (2.3904+1.5)/4.0 \times 100 = \mathbf{97.2591}$; T20I (`0` balls).
- Final Auction Rating (IPL-Only Branch): $R = 0.520(97.2591) + 0.480(72.9623) = \mathbf{85.5966} \to \mathbf{85.6}$ (**Exact CSV Match**).

---

## 2. Three-Way Competition Classification Audit

Inspecting all 138 contested competitions in `competitions.csv` yields **three distinct competition categories** (zero other domestic or franchise T20 leagues exist in the supplied data pack):

| Competition Category | Identification Rule | Competitions | Contested Matches | Total Deliveries | High-Pressure Deliveries |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. IPL (Genuine)** | `comp_name.str.startswith('IPL')` (`1358, 1715, 2193, 2725, 3298`) | 5 | 367 | **87,687** | 23,652 |
| **2. International T20I** | `match_format == 'T20I'` | 131 | 470 | **106,327** | 29,351 |
| **3. Other T20** | `match_format == 'T20'` & NOT IPL (`2670, 3289`) | 2 | 30 | **6,985** | 2,008 |
| **Total** | — | **138** | **867** | **200,999** | **55,011** |

- **`Other T20` Detail:**
  - `comp_id 2670`: *Mens T20 Emerging Teams Asia Cup 2024* (`match_format = T20`, 15 matches, 3,519 balls, 943 HP balls).
  - `comp_id 3289`: *Asia Cup Rising Stars 2025* (`match_format = T20`, 15 matches, 3,466 balls, 1,065 HP balls).
- **Code Update Applied:** `rank_batters.py` and `rank_bowlers.py` now cleanly separate `IPL`, `International T20I`, and `Other T20` into distinct aggregations so `Other T20` deliveries are **never** classified as IPL or T20I, while remaining transparently accounted for in overall `hp_bf`/`hp_balls` and `pressure_impact_score` ($P$).

---

## 3. Investigation of Sufiyan Muqeem's 65 Alleged IPL Deliveries

Sufiyan Muqeem (`ID: 34485`) bowled **0 genuine IPL deliveries**. The 65 deliveries previously reported as IPL (`+31.6` RPA) came exclusively from `Other T20` ACC emerging tournaments:

| Comp ID | Competition Name | Match ID | Match Date | HP Legal Balls | Runs | Wkts | Overs | Pressure Class |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| `2670` | Mens T20 Emerging Teams Asia Cup 2024 | `37091` | 2024-10-21 | 14 | 8 | 0 | 10, 12, 14 | High ($\text{CPI} \ge 0.60$) |
| `2670` | Mens T20 Emerging Teams Asia Cup 2024 | `37095` | 2024-10-23 | 18 | 17 | 2 | 8, 10, 12 | High ($\text{CPI} \ge 0.60$) |
| `3289` | Asia Cup Rising Stars 2025 | `48023` | 2025-11-18 | 12 | 4 | 2 | 12, 14 | High ($\text{CPI} \ge 0.60$) |
| `3289` | Asia Cup Rising Stars 2025 | `48028` | 2025-11-21 | 12 | 8 | 0 | 13, 15 | High ($\text{CPI} \ge 0.60$) |
| `3289` | Asia Cup Rising Stars 2025 | `48029` | 2025-11-23 | 9 | 8 | 1 | 11, 13 | High ($\text{CPI} \ge 0.60$) |
| **Subtotal** | **Other T20 (Misclassified previously as IPL)** | **5 matches** | — | **65** | **45** | **5** | — | **RPA: +31.6** |
| — | **Genuine International T20I (11 matches)** | — | — | **134** | **138** | **13** | — | **RPA: +22.2** |
| — | **Genuine IPL** | **0 matches** | — | **0** | **0** | **0** | — | **RPA: +0.0** |

**Impact of Strict 3-Way Separation on Muqeem:**
- Previously (65 balls misclassified as IPL): `Auction Rating = 79.9` (**#3 Global**).
- Intermediate fix (65 balls grouped with T20I): `Auction Rating = 66.3` (**#8 Global**).
- **Final Strict 3-Way Separation (`t20i_hp` = International T20I only):** Muqeem's genuine T20I rate is $+22.19 / 134 \times 6 = +0.9937$ RPA/6 $\implies T = 62.34$, $P = 63.48 \implies R = 0.195(62.34) + 0.805(63.48) = \mathbf{63.26} \to \mathbf{63.3}$ (**#10 Global**).

---

## 4. Complete 3-Way Format Exposure & Rating Decomposition (All Top 10 Players)

*Explicit Distinction:* Columns `IPL RAA/RPA`, `T20I RAA/RPA`, and `Other T20 RAA/RPA` are **raw cumulative totals**; columns `IPL Wt Comp`, `T20I Wt Comp`, and `P Wt Comp` are the **weighted rating components** summing to the exact `Auction Rating`.

### Top 10 Batters: 3-Way Samples, Raw Contributions & Weighted Rating Decomposition
| Rank | Batter Name | ID | IPL BF (Raw RAA) | T20I BF (Raw RAA) | Other T20 BF (Raw RAA) | Weighting Branch | IPL Wt Comp | T20I Wt Comp | $P$ Wt Comp | Auction Rating |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | Suryakumar Yadav | `1699` | 277 (+104.2) | 176 (+135.9) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 19.50 | 31.58 | **96.6** (`96.58`) |
| **2** | Tristan Stubbs | `20702` | 366 (+121.6) | 163 (+44.0) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 18.20 | 31.39 | **95.1** (`95.09`) |
| **3** | Namboori Tilak Varma | `7897` | 364 (+112.8) | 298 (+74.9) | 13 (+6.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 17.39 | 30.36 | **93.2** (`93.25`) |
| **4** | Dhruv Jurel | `7260` | 279 (+83.9) | 4 (-3.7) | 0 (+0.0) | IPL-Only ($0.520 I + 0.480 P$) | 52.00 | 0.00 | 40.55 | **92.5** (`92.55`) |
| **5** | Heinrich Klaasen | `4260` | 475 (+153.6) | 60 (+25.5) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 19.50 | 27.44 | **92.4** (`92.44`) |
| **6** | Naman Dhir | `37052` | 158 (+45.1) | 51 (+33.8) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 44.05 | 19.50 | 28.65 | **92.2** (`92.20`) |
| **7** | Rishabh Pant | `4703` | 211 (+82.9) | 55 (+14.2) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 17.71 | 28.93 | **92.1** (`92.14`) |
| **8** | Tim David | `6396` | 455 (+137.3) | 225 (+78.2) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 19.50 | 26.47 | **91.5** (`91.47`) |
| **9** | Ashutosh Sharma | `8101` | 276 (+103.0) | 0 (+0.0) | 7 (+0.7) | IPL-Only ($0.520 I + 0.480 P$) | 52.00 | 0.00 | 39.44 | **91.4** (`91.44`) |
| **10**| Azmatullah Omarzai | `6676` | 63 (+18.8) | 299 (+90.9) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.28 | 19.50 | 26.00 | **90.8** (`90.78`) |

### Top 10 Bowlers: 3-Way Samples, Raw Contributions & Weighted Rating Decomposition
| Rank | Bowler Name | ID | IPL Bls (Raw RPA) | T20I Bls (Raw RPA) | Other T20 Bls (Raw RPA) | Weighting Branch | IPL Wt Comp | T20I Wt Comp | $P$ Wt Comp | Auction Rating |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | Sunil Narine | `781` | 376 (+149.8) | 0 (+0.0) | 0 (+0.0) | IPL-Only ($0.520 I + 0.480 P$) | 50.57 | 0.00 | 35.02 | **85.6** (`85.60`) |
| **2** | Jasprit Bumrah | `2933` | 404 (+203.5) | 193 (+27.5) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 45.50 | 11.48 | 24.74 | **81.7** (`81.71`) |
| **3** | Abrar Ahmed | `5979` | 0 (+0.0) | 276 (+96.8) | 0 (+0.0) | T20I-Only ($0.195 T + 0.805 P$) | 0.00 | 17.57 | 57.28 | **74.9** (`74.85`) |
| **4** | Shaheen Afridi | `6355` | 0 (+0.0) | 277 (+73.1) | 0 (+0.0) | T20I-Only ($0.195 T + 0.805 P$) | 0.00 | 15.03 | 55.24 | **70.3** (`70.27`) |
| **5** | Mohammad Nawaz | `2490` | 0 (+0.0) | 175 (+44.2) | 0 (+0.0) | T20I-Only ($0.195 T + 0.805 P$) | 0.00 | 14.70 | 54.46 | **69.2** (`69.16`) |
| **6** | Mitchell Santner | `4101` | 92 (+28.3) | 319 (+30.3) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 38.06 | 10.09 | 18.40 | **66.6** (`66.55`) |
| **7** | Umran Malik | `25048` | 98 (+25.4) | 72 (+1.0) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 34.73 | 7.74 | 23.94 | **66.4** (`66.41`) |
| **8** | Matheesha Pathirana | `8661` | 422 (+120.2) | 180 (+9.4) | 0 (+0.0) | Both ($0.455 I + 0.195 T + 0.350 P$) | 36.51 | 8.84 | 20.74 | **66.1** (`66.09`) |
| **9** | Akeal Hosein | `2417` | 29 (+11.6) | 157 (+43.0) | 0 (+0.0) | T20I-Dom ($0.195 T + 0.805 P$) | 0.00 | 15.33 | 50.27 | **65.6** (`65.59`) |
| **10**| Sufiyan Muqeem | `34485` | 0 (+0.0) | 134 (+22.2) | 65 (+31.6) | T20I/Other ($0.195 T + 0.805 P$) | 0.00 | 12.16 | 51.10 | **63.3** (`63.26`) |

*Note on Other T20:* Players with `Other T20` deliveries (Tilak Varma, Ashutosh Sharma, Sufiyan Muqeem) have those deliveries included strictly in their overall `hp_bf`/`hp_balls` and $P$, never in `IPL` or `T20I` rate scores ($I$, $T$). For T20I-only players (Abrar, Afridi, Nawaz, Muqeem), `IPL Wt Comp = 0.00`—no IPL performance is implied or assumed.

---

## 5. Wicket Valuation Sensitivity & Empirical Bayes Shrinkage Audit

### 5.1 Wicket Valuation Sensitivity (`6`, `8`, `10`, `12` Runs per Wicket)
Both `rank_batters.py` (line 124) and `rank_bowlers.py` (line 124) value wickets at **8.0 runs/wicket** under pressure (reflecting lower marginal wicket cost late in T20 innings compared to early-innings ~15–20 run values). Testing sensitivity across `6, 8, 10, 12` runs/wicket across all qualifying players:

| Comparison vs Baseline (`8` runs/wkt) | Batters Spearman $\rho$ ($n=122$) | Batters Top-10 Overlap | Bowlers Spearman $\rho$ ($n=111$) | Bowlers Top-10 Overlap |
| :--- | :---: | :---: | :---: | :---: |
| **6 runs / wicket** | **0.9993** | 9 / 10 *(Tim David #8→#11, Ferreira #10)* | **0.9988** | **10 / 10** |
| **10 runs / wicket** | **0.9994** | **10 / 10** | **0.9992** | **10 / 10** |
| **12 runs / wicket** | **0.9986** | **10 / 10** | **0.9979** | **10 / 10** |

*Conclusion:* Top-3 batters (Suryakumar, Stubbs, Tilak) and Top-5 bowlers (Narine, Bumrah, Abrar, Afridi, Nawaz) do not change by a single rank across the entire `[6, 12]` range.

### 5.2 Empirical Variance-Components Audit of $K_{\text{bat}} = 150$ and $K_{\text{bowl}} = 200$
Method-of-moments variance decomposition on qualifying players ($N_{\text{HP}} \ge 60$):
- **Batting ($n=230$):**
  - Single-ball within-player RAA variance: $\sigma^2_{\text{ball}} = 3.1751\text{ runs}^2/\text{ball}$.
  - Observed between-player variance (`hp_raa_per_100`): $s^2_{\text{obs}} = 420.50$; mean sampling noise variance ($100^2\sigma^2_{\text{ball}}/N_i$): $265.74$.
  - Estimated true skill variance: $\tau^2_{\text{bat}} = 154.76$ (true SD $= 12.44$ runs/100 balls).
  - **Implied Empirical Bayes $K_{\text{bat,emp}} = \frac{100^2 \sigma^2_{\text{ball}}}{\tau^2_{\text{bat}}} = \mathbf{205.2}$ balls** (vs chosen $K_{\text{bat}} = 150.0$).
  - Sensitivity (`K=150` vs `K=205.2`): Spearman $\rho = \mathbf{0.9997}$, **10/10 Top-10 overlap**.
- **Bowling ($n=207$):**
  - Single-ball within-player RPA variance: $\sigma^2_{\text{ball}} = 3.1655\text{ runs}^2/\text{ball}$.
  - Observed between-player variance (`hp_rpa_per_6`): $s^2_{\text{obs}} = 1.1512$; mean sampling noise variance ($6^2\sigma^2_{\text{ball}}/N_i$): $0.8192$.
  - Estimated true skill variance: $\tau^2_{\text{bowl}} = 0.3320$ (true SD $= 0.576$ runs/over).
  - **Implied Empirical Bayes $K_{\text{bowl,emp}} = \frac{6^2 \sigma^2_{\text{ball}}}{\tau^2_{\text{bowl}}} = \mathbf{343.3}$ balls** (vs chosen $K_{\text{bowl}} = 200.0$).
  - Sensitivity (`K=200` vs `K=343.3`): Spearman $\rho = \mathbf{0.9996}$, **10/10 Top-10 overlap**.
- **Disclosure:** $K_{\text{bat}} = 150$ and $K_{\text{bowl}} = 200$ are domain-regularized shrinkage constants slightly less aggressive than pure method-of-moments estimates ($205.2$ and $343.3$), chosen to avoid over-compressing 150–250 ball specialists; rankings are virtually invariant ($\rho > 0.9995$).
- **Shrunk vs Unshrunk Inventory:**
  - *Shrunk:* `shrunk_raa_per_100` (inside batting `score_comp`) and `shrunk_rpa_per_6` (inside bowling `score_comp`).
  - *Retained Unshrunk:* Cumulative totals (`hp_raa`, `hp_rpa`, `hp_waa`, `ipl_raa`, `t20i_raa`, `ipl_rpa`, `t20i_rpa`), wicket rates (`hp_waa_per_100`, `hp_waa_per_6`), pressure deltas (`delta_raa_rate`, `delta_rpa_rate`), match consistency, and format-specific rates (`ipl_raa_per_100`, `t20i_raa_per_100`, `ipl_rpa_per_6`, `t20i_rpa_per_6` whenever format balls $\ge 30$).

---

## 6. Model Validation, Calibration Diagnostics & Limitations

Evaluated across **all 200,999 deliveries** using **5-Fold GroupKFold grouped by `match_id`** (note: this is **match-grouped, non-chronological** cross-validation—it eliminates intra-match leakage, but does not enforce chronological walk-forward testing across future seasons):

| Target (All 200,999 Balls) | OOF Cell Baseline (Mean ± Fold SD) | OOF HistGBM (Mean ± Fold SD) | 5-Fold Diff (Mean ± SD, Min–Max) | Match-Clustered 95% CI (Base − ML) | Calibration / Skill Diagnostics |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Batter Runs (MAE)** | `1.2956 ± 0.0136` | `1.2850 ± 0.0163` | `+0.0105 ± 0.0028` (`+0.0050` to `+0.0127`) | **`[+0.00755, +0.01375]`** | Modest single-ball gain; 5/5 folds positive |
| **Bowler Runs (MAE)** | `1.2858 ± 0.0132` | `1.2743 ± 0.0163` | `+0.0116 ± 0.0032` (`+0.0053` to `+0.0144`) | **`[+0.00853, +0.01504]`** | Modest single-ball gain; 5/5 folds positive |
| **Dismissal Prob (AUC / Brier)** | AUC `0.5752 ± 0.0038` / Brier `0.05100` | AUC `0.5958 ± 0.0028` / Brier `0.05086` | AUC `+0.0205 ± 0.0038` (5/5 positive) | Brier Diff `+0.00014` **`[+0.00010, +0.00018]`** | **BSS = `0.78%`**, **ECE = `0.00154`** (Mean pred `0.05460` vs obs `0.05419`) |
| **Bowler Wicket (AUC / Brier)** | AUC `0.5668 ± 0.0053` / Brier `0.04834` | AUC `0.5854 ± 0.0017` / Brier `0.04827` | AUC `+0.0186 ± 0.0046` (5/5 positive) | Brier Diff `+0.00007` **`[+0.00003, +0.00012]`** | **BSS = `0.46%`**, **ECE = `0.00141`** (Mean pred `0.05149` vs obs `0.05110`) |

- **Probability Calibration Deciles:** Across all 10 equal-frequency probability deciles, observed dismissal rates increase monotonically from `3.41%` (pred `3.61%`) in decile 1 to `10.38%` (pred `10.85%`) in decile 10 (max bin error `0.47%`); bowler wicket rates increase monotonically from `3.46%` (pred `3.47%`) to `8.94%` (pred `9.42%`, max bin error `0.48%`).
- **Honest Interpretation:** Per-delivery MAE improvements (`~0.011` runs/ball) and Brier skill scores (`< 1%`) are **modest**, reflecting the irreducible stochasticity of single-ball outcomes. We do not claim that modest single-ball gains automatically guarantee large player-level separation; rather, the ML baseline provides a well-calibrated, smoothly regularized contextual expectation benchmark superior to coarse cell averages across all five folds.

---

## 7. Pressure-Model Methodology & Assumption Sensitivity

- **Final Ranking Model Selection:** Official rankings use **strictly Model B (Continuous CPI $\ge 0.60$, 55,011 balls = 27.37%)**. Model A (`pressure_rule == 'High'`, 51,331 balls = 25.54%) is retained exclusively as an independent robustness benchmark in `ranking_sensitivity.csv`.
- **Model A vs Model B Agreement:** `39,501` both High, `15,510` Model B only, `11,830` Model A only, `134,158` both Not-High → **86.40% overall agreement**, **Jaccard overlap = 0.5910**, **Cohen's Kappa = 0.6506** (substantial agreement).
- **Inclusion & Collinearity of `RRR` and `RRR - CRR`:** `z_rrr = (RRR - 9)/3` (weight `0.40`) captures absolute scoring demand, while `z_accel = (RRR - CRR)/3` (weight `0.15`) was intended to capture required acceleration relative to pitch/match tempo. However, empirical audit reveals **high collinearity ($r = 0.9786$ in Innings 2)** because `RRR` variance dominates `CRR` late in chases. Removing `z_accel` (assigning `0.55` weight to `z_rrr`) produces **99.11% delivery agreement** and rank correlations $\rho = \mathbf{0.9942}$ (batters) and $\rho = \mathbf{0.9895}$ (bowlers).
- **Knockout Stakes Modifier (`1.15x`):** Applies to 7,335 knockout deliveries (3.65% of dataset), raising knockout mean CPI from `0.4680` to `0.5382` and promoting `+729` knockout deliveries into High Pressure (`26.08% → 36.02%`). Removing the modifier (`1.0x`) produces **99.64% delivery agreement** and rank correlations $\rho = \mathbf{0.9959}$ (batters) and $\rho = \mathbf{0.9942}$ (bowlers).

---

## 8. Summary of Final Ranking Updates from 3-Way Competition Separation

- **Top 10 Batters (`top_10_batters.csv`):** All 10 players and ranks (#1–#10) unchanged. Tilak Varma (`7897`) separates `364` IPL, `298` T20I, and `13` Other T20 balls (`Rating = 93.2`, #3); Ashutosh Sharma (`8101`) separates `276` IPL, `0` T20I, and `7` Other T20 balls (`Rating = 91.4`, #9).
- **Top 10 Bowlers (`top_10_bowlers.csv`):** Sufiyan Muqeem (`34485`) separates `0` IPL, `134` T20I, and `65` Other T20 balls, updating his rating to **`63.3` (#10 Global)** (behind Matheesha Pathirana #8 at `66.1` and Akeal Hosein #9 at `65.6`).
- **Separate IPL-Relevant Top 10 Bowlers (`top_10_bowlers_ipl_relevant.csv`):** 1. Sunil Narine (`781`, 85.6), 2. Jasprit Bumrah (`2933`, 81.7), 3. Mitchell Santner (`4101`, 66.6), 4. Umran Malik (`25048`, 66.4), 5. Matheesha Pathirana (`8661`, 66.1), 6. Akeal Hosein (`2417`, 65.6), 7. Mohsin Khan (`6669`, 62.5), 8. Kuldeep Yadav (`3644`, 62.5), 9. Lungi Ngidi (`4641`, 60.8), 10. Obed McCoy (`4837`, 60.4).

---

## 9. Final Submission Readiness Verdict

Every formula reproduces the published CSVs to four decimal places, the 3-way competition classification (`IPL`, `International T20I`, `Other T20`) is enforced across all scripts and outputs, shrinkage/wicket/CPI assumptions have been empirically stress-tested, probability calibration and fold-level model uncertainty are disclosed without overstatement, and recruitment wording is conditional and evidence-based. All deliverables in `outputs/FINAL_SUBMISSION/` are fully reconciled and ready for submission.
