"""
5_Methodology.py — PAGE 6: METHODOLOGY
Complete, transparent documentation of all 11 methodological stages with exact implemented LaTeX
equations, expandable technical proofs (Suryakumar Yadav, Tristan Stubbs, Sunil Narine), and clarity.
"""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Methodology | T20 Pressure Analytics", page_icon="🏏", layout="wide")

from components.sidebar import render_sidebar_and_mode
from components.metric_cards import (
    render_page_banner,
    render_section_header,
    render_insight_card,
    render_footer,
)
from utils.data_loader import get_active_data
from utils.formatting import PALETTE

mode = render_sidebar_and_mode()
data = get_active_data()

render_page_banner(
    title="Statistical Methodology & Exact Equations",
    subtitle="Transparent, Reproducible 11-Stage Architecture Verified Directly Against Pipeline Source Code",
    image_name="cricket_pitch_ball.jpg",
    accent=PALETTE["gold"],
)

# 1–3: Data Prep, Identity & Pre-Delivery State
render_section_header("1–3. Data Engineering, Canonical Identity & Zero-Leakage State", accent="pink")
c1, c2, c3 = st.columns(3)
with c1:
    render_insight_card(
        "1. Cricket Accounting & Legality",
        "Legal deliveries exclude <code>wide</code>, <code>Overstep</code>, and <code>other</code> (192,445 legal of 200,999 total). "
        "Batters are not charged balls faced on wides. Bowlers are charged bat runs + wides/no-balls only (excluding byes/legbyes/penalties), "
        "and bowler wickets exclude run-outs and retire-outs (10,272 genuine wickets).",
        "pink",
    )
with c2:
    render_insight_card(
        "2. Canonical Player ID Reconciliation",
        "All aggregations group strictly by canonical integer IDs (<code>striker_id</code>, <code>bowler_id</code>) verified against "
        "<code>ball_by_ball.csv</code> and <code>competition_team_player_mapping.csv</code>. Six earlier markdown draft ID typos were confirmed "
        "presentation-only with zero impact on underlying statistics.",
        "gold",
    )
with c3:
    render_insight_card(
        "3. Pre-Delivery State Reconstruction",
        "Cumulative runs (S<sub>t-1</sub>), team wickets lost (W<sub>t-1</sub>), wickets in hand (10 − W<sub>t-1</sub>), legal balls remaining "
        "(adjusted for DLS revised overs), CRR, and RRR are computed strictly prior to delivery t with zero future-outcome leakage.",
        "teal",
    )

# 4–5: Pressure Model & Expected-Performance ML (Full-Width Unclipped Equations)
render_section_header("4. Continuous Composite Pressure Index (Model B — Used for Official Rankings)", accent="teal")
st.markdown("**Second Innings (Chasing) Latent Leverage:**")
st.latex(r"z_{\text{chase}} = 0.40\left(\frac{\text{RRR}-9}{3}\right) + 0.30\left(\frac{5-W_{\text{hand}}}{2}\right) + 0.15\left(\frac{60-B_{\text{rem}}}{30}\right) + 0.15\left(\frac{\text{RRR}-\text{CRR}}{3}\right)")
st.markdown("**First Innings (Target Setting) Latent Leverage:**")
st.latex(r"z_{\text{first}} = 0.25\left(\frac{B_{\text{bowled}}-60}{30}\right) + 0.35\left(\frac{7-W_{\text{hand}}}{2}\right) + 0.25\,\mathbb{I}(\text{over}\ge 16) + 0.15\,\mathbb{I}(\text{collapse})")
st.markdown("**Logistic Sigmoid & Knockout Stakes Multiplier:**")
st.latex(r"\text{CPI} = \min\!\left(1.0,\;\sigma(z)\times S_{\text{stakes}}\right), \qquad S_{\text{stakes}} = \begin{cases}1.15 & \text{knockout match}\\ 1.00 & \text{league/group match}\end{cases}")
st.caption("Super Overs anchor at CPI = 1.00. High Pressure is defined as CPI >= 0.60 (55,011 deliveries = 27.37%).")

render_section_header("5–6. Out-of-Fold Contextual ML Baselines & Performance Above Expectation", accent="pink")
st.markdown(
    """
    Four `HistGradientBoosting` models are trained via **5-Fold GroupKFold grouped strictly by `match_id`** (match-grouped, non-chronological CV):
    1. **Expected Batter Runs:** $\\mathbb{E}[\\text{bat\\_runs} \\mid X_{t-1}]$ &nbsp;|&nbsp;
    2. **Expected Dismissal Probability:** $\\mathbb{P}(\\text{team\\_wicket} \\mid X_{t-1})$ &nbsp;|&nbsp;
    3. **Expected Bowler Runs Conceded:** $\\mathbb{E}[\\text{bowler\\_runs} \\mid X_{t-1}]$ &nbsp;|&nbsp;
    4. **Expected Genuine Bowler Wicket:** $\\mathbb{P}(\\text{bowler\\_wicket} \\mid X_{t-1})$
    """
)
st.latex(r"\text{RAA} = \sum (\text{bat\_runs} - \hat{r}_{\text{bat}}), \qquad \text{RPA} = \sum (\hat{r}_{\text{bowl}} - \text{bowler\_runs})")
st.latex(r"\text{WAA}_{\text{bat}} = \sum (\hat{p}_{\text{out}} - y_{\text{out}}), \qquad \text{WAA}_{\text{bowl}} = \sum (y_{\text{wkt}} - \hat{p}_{\text{wkt}})")

# 7–9: Wicket Valuation, Empirical Bayes Shrinkage & Match Consistency
render_section_header("7–9. Wicket Valuation, Empirical Bayes Shrinkage & Consistency", accent="gold")
st.latex(r"\text{Shrunk Rate}_i = w_i \cdot \text{Observed Rate}_i + (1 - w_i) \cdot \mu_{\text{prior}}, \qquad w_i = \frac{N_{\text{HP}, i}}{N_{\text{HP}, i} + K}")
s1, s2, s3 = st.columns(3)
with s1:
    render_insight_card(
        "7. Wicket Valuation (8.0 Runs / Wicket)",
        "Both batting wicket preservation (WAA) and bowling strike impact (WAA) value wickets at <strong>8.0 runs/wicket</strong> under high pressure. "
        "Sensitivity across [6, 8, 10, 12] runs/wicket yields Spearman &rho; &ge; 0.9979 across both disciplines.",
        "gold",
    )
with s2:
    render_insight_card(
        "8. Empirical Bayes Priors & Constants",
        "Role-specific priors across N &ge; 60 HP balls: <strong>&mu;<sub>bat</sub> = +8.4678</strong> runs/100 balls (K<sub>bat</sub> = 150; method-of-moments 205.2); "
        "<strong>&mu;<sub>bowl</sub> = −0.2183</strong> runs/6 balls (K<sub>bowl</sub> = 200; method-of-moments 343.3). Sensitivity &rho; &gt; 0.9995.",
        "pink",
    )
with s3:
    render_insight_card(
        "9. Match-to-Match Consistency",
        "Measured as the percentage of high-pressure matches where a player records net positive impact (&Sigma; RAA &gt; 0 for batters; &Sigma; RPA &gt; 0 for bowlers), "
        "preventing single outlier innings from masking match-level volatility.",
        "teal",
    )

# 10–11: Exact Final Auction Rating Formula (Batter & Bowler Specific)
render_section_header("10–11. Exact Final Auction Rating Equations (Implemented in Source Code)", accent="pink")
st.markdown("**Step A — Format-Independent Pressure Impact Score ($P$, 0–100 scale):**")
st.latex(r"P = 0.45 \cdot S_{\text{shrunk}} + 0.20 \cdot S_{\text{WAA}} + 0.20 \cdot S_{\Delta} + 0.15 \cdot S_{\text{consistency}}")

tab_bat_eq, tab_bowl_eq = st.tabs(["Batting Normalization & Rating Formula", "Bowling Normalization & Rating Formula"])
with tab_bat_eq:
    st.latex(r"S_{\text{shrunk}} = \text{clip}\!\left(\frac{\text{shrunk\_raa\_per\_100} + 15}{45}\times 100,\;0,\;100\right), \quad S_{\text{WAA}} = \text{clip}\!\left(\frac{8\cdot\text{hp\_waa\_per\_100} + 15}{35}\times 100,\;0,\;100\right)")
    st.latex(r"S_{\Delta} = \text{clip}\!\left(\frac{\text{clip}(\Delta_{\text{raa}}, -20, 25) + 20}{45}\times 100,\;0,\;100\right), \quad \text{Eligibility: } N_{\text{HP}} \ge 120\text{ HP BF}")
with tab_bowl_eq:
    st.latex(r"S_{\text{shrunk}} = \text{clip}\!\left(\frac{\text{shrunk\_rpa\_per\_6} + 1.5}{4.0}\times 100,\;0,\;100\right), \quad S_{\text{WAA}} = \text{clip}\!\left(\frac{8\cdot\text{hp\_waa\_per\_6} + 1.5}{3.5}\times 100,\;0,\;100\right)")
    st.latex(r"S_{\Delta} = \text{clip}\!\left(\frac{\text{clip}(\Delta_{\text{rpa}}, -2.0, 2.5) + 2.0}{4.5}\times 100,\;0,\;100\right), \quad \text{Eligibility: } N_{\text{HP}} \ge 150\text{ HP Legal Balls}")

st.markdown("**Step B — Final 3-Branch Format-Weighted Auction Rating ($R$):**")
st.markdown("Let $I$ = normalized genuine IPL rate score (`ipl_score`) and $T$ = normalized genuine International T20I rate score (`t20i_score`), with format branch threshold $N_{\\min} = 50$ HP BF (batters) or $60$ HP legal balls (bowlers). `Other T20` deliveries are excluded from both $I$ and $T$ and remain solely inside overall $P$:")
st.latex(r"R = \begin{cases} 0.455\,I + 0.195\,T + 0.350\,P & \text{if } N_{\text{IPL}} \ge N_{\min} \text{ and } N_{\text{T20I}} \ge N_{\min}\;\; (\text{Both Formats}) \\ 0.520\,I + 0.480\,P & \text{if } N_{\text{IPL}} \ge N_{\min} \text{ and } N_{\text{T20I}} < N_{\min}\;\; (\text{IPL-Only / Dominant}) \\ 0.195\,T + 0.805\,P & \text{if } N_{\text{IPL}} < N_{\min}\;\; (\text{T20I-Only / Limited IPL}) \end{cases}")

# Expandable Worked Numerical Proofs
with st.expander("Worked Numerical Reproduction Proofs (Suryakumar Yadav, Tristan Stubbs, Sunil Narine)", expanded=False):
    st.markdown(
        """
        - **Suryakumar Yadav (`ID: 1699`, Both Formats — 277 IPL BF, 176 T20I BF):**
          - $w = 453/(453+150) = 0.7512 \\implies \\text{shrunk RAA/100} = 41.916 \\implies S_{\\text{shrunk}} = 100.0$
          - $S_{\\text{WAA}} = 72.5899$, $S_{\\Delta} = 100.0$, $S_{\\text{cons}} = 71.4286 \\implies P = 90.2323$
          - $I = 100.0$, $T = 100.0 \\implies R = 0.455(100) + 0.195(100) + 0.350(90.2323) = \\mathbf{96.5813 \\to 96.6}$ *(Exact CSV match)*
        - **Tristan Stubbs (`ID: 20702`, Both Formats — 366 IPL BF, 163 T20I BF):**
          - $w = 529/(529+150) = 0.7791 \\implies \\text{shrunk RAA/100} = 26.257 \\implies S_{\\text{shrunk}} = 91.6832$
          - $S_{\\text{WAA}} = 96.7708$, $S_{\\Delta} = 100.0$, $S_{\\text{cons}} = 60.5263 \\implies P = 89.6905$
          - $I = 100.0$, $T = 93.3145 \\implies R = 0.455(100) + 0.195(93.3145) + 0.350(89.6905) = \\mathbf{95.0880 \\to 95.1}$ *(Exact CSV match)*
        - **Sunil Narine (`ID: 781`, IPL-Only — 376 IPL Balls, 0 T20I Balls):**
          - $w = 376/(376+200) = 0.6528 \\implies \\text{shrunk RPA/6} = 1.4846 \\implies S_{\\text{shrunk}} = 74.6141$
          - $S_{\\text{WAA}} = 73.2631$, $S_{\\Delta} = 65.5417$, $S_{\\text{cons}} = 77.5000 \\implies P = 72.9623$
          - $I = 97.2591 \\implies R = 0.520(97.2591) + 0.480(72.9623) = \\mathbf{85.5966 \\to 85.6}$ *(Exact CSV match)*
        """
    )

render_footer(mode)
