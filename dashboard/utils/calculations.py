"""
calculations.py — Interactive analytical helpers (CPI live simulator, radar normalization,
format-branch labeler). NEVER recalculates or overrides the verified Auction Rating.
"""
import numpy as np


def sigmoid(x: float) -> float:
    return float(1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0))))


def compute_live_cpi(
    innings: int,
    over: int,
    wickets_in_hand: int,
    rrr: float = 9.0,
    crr: float = 8.0,
    is_knockout: bool = False,
    is_super_over: bool = False,
) -> dict:
    """
    Exact replica of Model B (Continuous CPI) from calculate_pressure.py
    for interactive scenario exploration on Page 5 (Pressure Analytics).
    """
    cum_legal_balls = max(0, (over - 1) * 6 + 3)
    balls_remaining = max(1, 120 - cum_legal_balls)

    if is_super_over:
        cpi_base = 1.0
        z_val = float("inf")
    elif innings == 2:
        z_rrr = (rrr - 9.0) / 3.0
        z_wkts = (5.0 - wickets_in_hand) / 2.0
        z_balls = (60.0 - balls_remaining) / 30.0
        z_accel = (rrr - crr) / 3.0
        z_val = 0.40 * z_rrr + 0.30 * z_wkts + 0.15 * z_balls + 0.15 * z_accel
        cpi_base = sigmoid(z_val)
    else:
        z_prog = (cum_legal_balls - 60.0) / 30.0
        z_wkts = (7.0 - wickets_in_hand) / 2.0
        is_death = 1.0 if over >= 16 else 0.0
        is_collapse = 1.0 if ((over <= 6 and wickets_in_hand <= 7) or (over <= 12 and wickets_in_hand <= 5)) else 0.0
        z_val = 0.25 * z_prog + 0.35 * z_wkts + 0.25 * is_death + 0.15 * is_collapse
        cpi_base = sigmoid(z_val)

    mult = 1.15 if is_knockout else 1.0
    cpi = float(np.clip(cpi_base * mult, 0.0, 1.0))
    if cpi >= 0.60:
        category = "High Pressure"
    elif cpi >= 0.35:
        category = "Medium Pressure"
    else:
        category = "Low / Ordinary"

    return {
        "cpi": round(cpi, 4),
        "cpi_base": round(cpi_base, 4),
        "category": category,
        "stakes_multiplier": mult,
        "balls_remaining": balls_remaining,
    }


def classify_weighting_branch(ipl_balls: float, t20i_balls: float, discipline: str = "batting") -> str:
    """Identify the exact format-weighting branch applied in rank_batters.py / rank_bowlers.py."""
    cutoff = 50 if discipline == "batting" else 60
    has_ipl = ipl_balls >= cutoff
    has_t20i = t20i_balls >= cutoff
    if has_ipl and has_t20i:
        return "Both Formats (0.455 IPL + 0.195 T20I + 0.350 P)"
    elif has_ipl:
        return "IPL-Dominant / Only (0.520 IPL + 0.480 P)"
    else:
        return "T20I / Limited IPL (0.195 T20I + 0.805 P)"


def normalize_for_radar(series, lower_is_better: bool = False, bounds=None):
    """
    Min-max normalize values to [10, 100] strictly for visual radar comparison,
    with transparent bounds.
    """
    vals = np.asarray(series, dtype=float)
    if bounds is not None:
        vmin, vmax = bounds
    else:
        vmin = np.nanmin(vals)
        vmax = np.nanmax(vals)
    if vmax == vmin:
        return np.full_like(vals, 50.0)
    norm = (vals - vmin) / (vmax - vmin)
    if lower_is_better:
        norm = 1.0 - norm
    return np.clip(norm * 100.0, 0.0, 100.0)
