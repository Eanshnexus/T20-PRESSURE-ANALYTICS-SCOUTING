"""
formatting.py — Metric glossary, units, direction indicators, and display formatters.
Every displayed metric has a clear label, definition, unit, and better-direction indicator.
"""

PALETTE = {
    "bg_primary": "#101426",
    "bg_secondary": "#211B36",
    "bg_card": "#1B1830",
    "pink": "#EA3D91",
    "gold": "#F4C542",
    "teal": "#35C6B5",
    "text_primary": "#F5F6FA",
    "text_secondary": "#A7AEC0",
    "grid": "rgba(255, 255, 255, 0.08)",
}

METRIC_GLOSSARY = {
    "Auction Rating": {
        "label": "Auction Rating",
        "definition": "Final format-weighted pressure reliability score blending IPL rate score, T20I rate score, and overall Pressure Impact Score across 3 exposure branches.",
        "unit": "0–100 index",
        "direction": "Higher is better",
    },
    "Pressure Impact Score": {
        "label": "Pressure Impact Score (P)",
        "definition": "Format-independent 4-component high-pressure rating: 45% shrunk RAA/RPA + 20% wicket equity (8 runs/wkt) + 20% pressure delta + 15% match consistency.",
        "unit": "0–100 index",
        "direction": "Higher is better",
    },
    "Ordinary Performance Score": {
        "label": "Ordinary Performance Score",
        "definition": "Normalized contextual run contribution during non-high-pressure (CPI < 0.60) deliveries.",
        "unit": "0–100 index",
        "direction": "Higher is better",
    },
    "Runs Above Expectation (RAA)": {
        "label": "Runs Above Expectation (RAA)",
        "definition": "Cumulative actual batter runs minus out-of-fold ML expected runs across high-pressure balls faced.",
        "unit": "Runs",
        "direction": "Higher is better",
    },
    "Runs Prevented Above Expectation (RPA)": {
        "label": "Runs Prevented Above Expectation (RPA)",
        "definition": "Cumulative out-of-fold ML expected runs minus actual bowler runs conceded across high-pressure legal balls.",
        "unit": "Runs saved",
        "direction": "Higher is better",
    },
    "Wickets Above Expectation (Batting WAA)": {
        "label": "Dismissal Equity (Batting WAA)",
        "definition": "Cumulative expected dismissals minus actual dismissals under pressure; positive means preserving wicket better than expected.",
        "unit": "Wickets saved",
        "direction": "Higher is better",
    },
    "Wickets Above Expectation (Bowling WAA)": {
        "label": "Wickets Above Expectation (Bowling WAA)",
        "definition": "Actual genuine bowler wickets (excl. run-outs/retire-outs) minus out-of-fold ML expected wickets under pressure.",
        "unit": "Wickets",
        "direction": "Higher is better",
    },
    "Pressure Strike Rate": {
        "label": "Pressure Strike Rate",
        "definition": "Batter runs scored per 100 high-pressure balls faced (excluding wides).",
        "unit": "Runs / 100 balls",
        "direction": "Higher is better",
    },
    "Pressure Economy": {
        "label": "Pressure Economy",
        "definition": "Bowler runs conceded (bat + wides + no-balls; excl. byes/legbyes) per 6 high-pressure legal balls.",
        "unit": "Runs / over",
        "direction": "Lower is better",
    },
    "Dot-Ball Percentage": {
        "label": "Dot-Ball Percentage",
        "definition": "Percentage of high-pressure legal deliveries resulting in zero total runs.",
        "unit": "%",
        "direction": "Higher is better",
    },
    "Match Consistency": {
        "label": "Match Consistency",
        "definition": "Percentage of high-pressure match outings where the player recorded net positive RAA (> 0) or RPA (> 0).",
        "unit": "% of HP matches",
        "direction": "Higher is better",
    },
    "CPI": {
        "label": "Composite Pressure Index (CPI)",
        "definition": "Pre-delivery continuous match leverage score on [0.0, 1.0]; High Pressure is defined as CPI >= 0.60.",
        "unit": "0.00–1.00 scale",
        "direction": "Higher = greater match pressure",
    },
    "Ranking Stability": {
        "label": "Ranking Stability",
        "definition": "Rank standard deviation across 4 sensitivity definitions (Primary CPI >= 0.60, Strict >= 0.70, Broad >= 0.50, Rule Model A): High (SD <= 3.5), Moderate (3.5–8.0), Volatile (> 8.0).",
        "unit": "Category (High / Moderate / Volatile)",
        "direction": "High stability indicates stronger robustness",
    },
}


def fmt_num(val, decimals=1, signed=False, suffix=""):
    """Format numeric value safely without masking NaN/None as zero."""
    if val is None or (isinstance(val, float) and (val != val)):
        return "N/A"
    try:
        num = float(val)
        fmt_str = f"{{:{'+' if signed else ''},.{decimals}f}}"
        return f"{fmt_str.format(num)}{suffix}"
    except (ValueError, TypeError):
        return str(val)


def fmt_int(val):
    if val is None or (isinstance(val, float) and (val != val)):
        return "N/A"
    try:
        return f"{int(round(float(val))):,}"
    except (ValueError, TypeError):
        return str(val)


def parse_pct(val):
    """Parse percentage string like '71.4%' into float 71.4, preserving NaN."""
    if val is None or (isinstance(val, float) and (val != val)):
        return float("nan")
    if isinstance(val, str):
        cleaned = val.replace("%", "").strip()
        return float(cleaned) if cleaned else float("nan")
    return float(val)


def sample_reliability_tier(n_balls, discipline="batting"):
    """Transparent sample-size reliability label."""
    if n_balls is None or n_balls != n_balls:
        return "Unavailable"
    if discipline == "batting":
        if n_balls >= 400:
            return "High Volume (>=400 HP BF)"
        elif n_balls >= 250:
            return "Moderate-High (250–399 HP BF)"
        elif n_balls >= 120:
            return "Qualifying Moderate (120–249 HP BF)"
        return "Below Primary Cutoff (<120 HP BF)"
    else:
        if n_balls >= 400:
            return "High Volume (>=400 HP Balls)"
        elif n_balls >= 250:
            return "Moderate-High (250–399 HP Balls)"
        elif n_balls >= 150:
            return "Qualifying Moderate (150–249 HP Balls)"
        return "Below Primary Cutoff (<150 HP Balls)"
