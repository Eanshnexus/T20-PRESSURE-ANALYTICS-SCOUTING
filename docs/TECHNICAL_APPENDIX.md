# Technical Appendix: Mathematical Formulations, Model Specs & Validation Data

**Challenge:** SupeRR Selector Season 2 — Rajasthan Royals  
**Dataset Grain:** 200,999 Deliveries Across 867 Contested Matches  

---

## 1. Formal Mathematical Specifications

### 1.1 Pre-Delivery State Recurrence Relations
For match $m$, innings $i$, and delivery sequence $t \in \{1, \dots, T_{m, i}\}$:

$$\text{cum\_runs}_{m,i,t} = \sum_{k=1}^{t-1} \text{total\_runs}_{m,i,k}$$
$$\text{cum\_wickets}_{m,i,t} = \sum_{k=1}^{t-1} \text{is\_team\_wicket}_{m,i,k}$$
$$\text{cum\_legal\_balls}_{m,i,t} = \sum_{k=1}^{t-1} \mathbb{I}(\text{extras\_type}_{m,i,k} \notin \{\text{'wide'}, \text{'Overstep'}, \text{'other'}\})$$
$$\text{balls\_remaining}_{m,i,t} = \max\left(0, B_{\text{max}, m, i} - \text{cum\_legal\_balls}_{m,i,t}\right)$$

Where $B_{\text{max}, m, i}$ is 120 for standard 20-over innings, $6 \times \text{revised\_overs}$ for rain interruptions, and 6 for Super Overs.

Innings 2 Chase Target $T_m$:
$$T_m = \begin{cases} \text{revised\_target}_m, & \text{if } \text{revised\_target}_m \neq \text{NaN} \\ \sum_{k=1}^{T_{m, 1}} \text{total\_runs}_{m, 1, k} + 1, & \text{otherwise} \end{cases}$$

Required Run Rate (RRR):
$$\text{RRR}_{m,2,t} = \begin{cases} \frac{\max(0, T_m - \text{cum\_runs}_{m,2,t}) \times 6}{\text{balls\_remaining}_{m,2,t}}, & \text{balls\_remaining}_{m,2,t} > 0 \\ \max(0, T_m - \text{cum\_runs}_{m,2,t}) \times 6, & \text{balls\_remaining}_{m,2,t} = 0 \end{cases}$$

---

## 2. Machine Learning Baseline Model Architecture

### 2.1 Model Specifications
- **Framework:** `sklearn.ensemble.HistGradientBoostingRegressor` and `HistGradientBoostingClassifier`
- **Validation:** 5-Fold `GroupKFold` on `match_id` (zero intra-match leakage).
- **Hyperparameters:**
  - `max_iter`: 50
  - `learning_rate`: 0.1
  - `max_leaf_nodes`: 31
  - `min_samples_leaf`: 20
  - `l2_regularization`: 1.0
  - `random_state`: 42 + fold_idx
- **Feature Vector:**
  $$\mathbf{x} = \begin{bmatrix} \text{cum\_legal\_balls} \\ \text{balls\_remaining} \\ \text{wickets\_in_hand} \\ \text{cum\_runs\_before} \\ \text{crr} \\ \text{rrr} \\ \text{overid} \\ \text{innings} \\ \mathbb{I}(\text{is\_t20i}) \\ \mathbb{I}(\text{is\_knockout}) \\ \mathbb{I}(\text{is\_death}) \\ \mathbb{I}(\text{is\_powerplay}) \end{bmatrix}$$

### 2.2 Validation Error Matrix

| Model Task | Algorithm | Loss Function | Training Size (Folds) | Test Size (Fold) | OOF MAE / Brier | Benchmark MAE / Brier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Batter Runs** | HistGBM Regressor | Squared Error | ~160,800 | ~40,200 | **1.2850** | 1.2953 (Cell Average) |
| **Batter Dismissal** | HistGBM Classifier | Log Loss | ~160,800 | ~40,200 | **0.0509 (AUC 0.595)** | 0.0509 (AUC 0.581) |
| **Bowler Runs** | HistGBM Regressor | Squared Error | ~160,800 | ~40,200 | **1.2743** | 1.2855 (Cell Average) |
| **Bowler Wickets** | HistGBM Classifier | Log Loss | ~160,800 | ~40,200 | **0.0483 (AUC 0.585)** | 0.0483 (AUC 0.572) |

---

## 3. Empirical Bayes Shrinkage Derivation

Let $y_i$ denote the observed rate (e.g., RAA per 100 balls) for player $i$, facing $n_i$ balls.
We model:
$$y_i \mid \theta_i \sim \mathcal{N}\left(\theta_i, \frac{\sigma^2}{n_i}\right)$$
$$\theta_i \sim \mathcal{N}(\mu, \tau^2)$$

The Bayes estimator under quadratic loss is:
$$\hat{\theta}_i = \mathbb{E}[\theta_i \mid y_i] = \frac{n_i}{n_i + \frac{\sigma^2}{\tau^2}} y_i + \frac{\frac{\sigma^2}{\tau^2}}{n_i + \frac{\sigma^2}{\tau^2}} \mu$$

From delivery-level sample residuals:
- **Batting Residual Variance:** $\sigma^2_{\text{bat}} = 3.175 \times 10^4$
- **Batting Between-Player Variance:** $\tau^2_{\text{bat}} = 154.8$
- **Theoretical $K_{\text{bat}}$:** $\frac{\sigma^2}{\tau^2} \approx 205.2$. We chose a robust conservative threshold of $K_{\text{bat}} = 150.0$ balls.
- **Bowling Residual Variance:** $\sigma^2_{\text{bowl}} = 114.0$
- **Bowling Between-Player Variance:** $\tau^2_{\text{bowl}} = 0.33$
- **Theoretical $K_{\text{bowl}}$:** $\frac{\sigma^2}{\tau^2} \approx 343.3$. We adopted $K_{\text{bowl}} = 200.0$ legal balls.

---

## 4. Sensitivity Analysis & Specification Testing

The table below documents the stability of our primary Top 10 rankings across four alternative specifications:

| Player Name | Discipline | Primary Rank | Strict CPI $\ge 0.70$ | Broad CPI $\ge 0.50$ | Rule Model A | Rank Std Dev | Stability Class |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Suryakumar Yadav** | Batting | **1** | 3 | 1 | 5 | 2.60 | **High** |
| **Tristan Stubbs** | Batting | **2** | 6 | 3 | 13 | 5.15 | **Moderate** |
| **Namboori Tilak Varma**| Batting | **3** | 4 | 2 | 4 | 0.71 | **High** |
| **Dhruv Jurel** | Batting | **4** | 22 | 8 | 4 | 12.30 | **Volatile** |
| **Heinrich Klaasen** | Batting | **5** | 7 | 6 | 17 | 5.70 | **Moderate** |
| **Naman Dhir** | Batting | **6** | 12 | 10 | 6 | 4.55 | **Moderate** |
| **Rishabh Pant** | Batting | **7** | 35 | 11 | 9 | 17.02 | **Volatile** |
| **Tim David** | Batting | **8** | 8 | 9 | 7 | 0.71 | **High** |
| **Ashutosh Sharma** | Batting | **9** | 14 | 15 | 3 | 5.48 | **Moderate** |
| **Azmatullah Omarzai** | Batting | **10** | 10 | 17 | 37 | 15.22 | **Volatile** |
| **Sunil Narine** | Bowling | **1** | 2 | 1 | 4 | 1.22 | **High** |
| **Jasprit Bumrah** | Bowling | **2** | 1 | 2 | 2 | 0.43 | **High** |
| **Sufiyan Muqeem** | Bowling | **3** | 4 | 4 | 1 | 1.66 | **High** |
| **Abrar Ahmed** | Bowling | **4** | 3 | 3 | 6 | 1.48 | **High** |
| **Shaheen Afridi** | Bowling | **5** | 6 | 7 | 14 | 3.57 | **Moderate** |
| **Mohammad Nawaz** | Bowling | **6** | 18 | 6 | 7 | 9.39 | **Volatile** |
| **Mitchell Santner** | Bowling | **7** | 7 | 9 | 13 | 2.38 | **High** |
| **Umran Malik** | Bowling | **8** | 85 | 19 | 11 | 45.30 | **Volatile** |
| **Matheesha Pathirana** | Bowling | **9** | 5 | 8 | 5 | 0.83 | **High** |
| **Akeal Hosein** | Bowling | **10** | 12 | 10 | 18 | 4.33 | **Moderate** |
