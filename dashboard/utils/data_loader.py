"""
data_loader.py — Cached verified data loader for T20 Pressure Analytics Dashboard.
Uses configurable relative paths and joins strictly on stable integer Player IDs.
Never recalculates Auction Ratings in the frontend; reads verified source CSVs directly.
"""
import os
import json
import pandas as pd
import streamlit as st

DASHBOARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)


def get_project_paths() -> dict:
    """Resolve configurable relative paths cleanly across local and Streamlit Cloud deployments."""
    root = os.environ.get("SUPERR_PROJECT_ROOT", PROJECT_ROOT)
    return {
        "final_sub": os.path.join(root, "outputs", "FINAL_SUBMISSION"),
        "tables": os.path.join(root, "outputs", "tables"),
        "cache": os.path.join(DASHBOARD_DIR, "data_cache"),
        "assets": os.path.join(DASHBOARD_DIR, "assets"),
    }


def is_local_competition_available() -> bool:
    """Check whether verified competition outputs exist."""
    p = get_project_paths()
    required = [
        os.path.join(p["final_sub"], "top_10_batters.csv"),
        os.path.join(p["final_sub"], "top_10_bowlers.csv"),
        os.path.join(p["tables"], "batter_metrics.csv"),
        os.path.join(p["tables"], "bowler_metrics.csv"),
    ]
    return all(os.path.exists(f) for f in required)


@st.cache_data(show_spinner=False)
def load_local_competition_data() -> dict:
    """Load verified local competition outputs using stable Player ID joins."""
    p = get_project_paths()

    top10_bat = pd.read_csv(os.path.join(p["final_sub"], "top_10_batters.csv"))
    top10_bowl = pd.read_csv(os.path.join(p["final_sub"], "top_10_bowlers.csv"))
    top10_bat_ipl = pd.read_csv(os.path.join(p["final_sub"], "top_10_batters_ipl_relevant.csv"))
    top10_bowl_ipl = pd.read_csv(os.path.join(p["final_sub"], "top_10_bowlers_ipl_relevant.csv"))
    all_elig_bowl = pd.read_csv(os.path.join(p["final_sub"], "all_eligible_bowlers.csv"))
    combined = pd.read_csv(os.path.join(p["final_sub"], "combined_player_analysis.csv"))

    bat_metrics = pd.read_csv(os.path.join(p["tables"], "batter_metrics.csv"))
    bowl_metrics = pd.read_csv(os.path.join(p["tables"], "bowler_metrics.csv"))
    sensitivity = pd.read_csv(os.path.join(p["tables"], "ranking_sensitivity.csv"))
    model_val = pd.read_csv(os.path.join(p["tables"], "model_validation_summary.csv"))
    pressure_dist = pd.read_csv(os.path.join(p["tables"], "pressure_distribution.csv"))

    # Load pre-aggregated pressure summaries & evidence-based role profiles
    with open(os.path.join(p["cache"], "pressure_aggregates.json"), "r", encoding="utf-8") as f:
        pressure_agg = json.load(f)
    bat_roles = pd.read_csv(os.path.join(p["cache"], "batter_role_profiles.csv"))
    bowl_roles = pd.read_csv(os.path.join(p["cache"], "bowler_role_profiles.csv"))

    # Build enriched eligible batters table (N >= 120 HP BF) joined strictly on striker_id
    elig_bat = bat_metrics[bat_metrics["hp_bf"] >= 120].copy()
    elig_bat = elig_bat.sort_values("auction_rating", ascending=False).reset_index(drop=True)
    elig_bat["Global_Rank"] = range(1, len(elig_bat) + 1)

    # Join stability from sensitivity on Player ID (preserving NaN where not evaluated in top-10 sensitivity)
    sens_bat = sensitivity[sensitivity["Discipline"] == "Batting"][["Player ID", "Stability_Class", "Rank_Std_Dev"]]
    elig_bat = elig_bat.merge(sens_bat, left_on="striker_id", right_on="Player ID", how="left").drop(columns=["Player ID"])
    elig_bat = elig_bat.merge(bat_roles, on="striker_id", how="left")

    # Enrich Top 10 Batters with full 3-way format breakdown & role profile via Player ID
    top10_bat_enriched = top10_bat.merge(
        elig_bat[[
            "striker_id", "ipl_bf", "ipl_raa", "ipl_sr", "t20i_bf", "t20i_raa", "t20i_sr",
            "other_t20_bf", "other_t20_raa", "ord_bf", "ord_sr", "ord_raa_per_100",
            "hp_runs", "hp_dismissals", "hp_exp_dismissals", "hp_boundary_pct",
            "shrunk_raa_per_100", "delta_raa_rate", "Rank_Std_Dev",
            "inferred_batting_role", "median_batting_order", "pp_share_pct", "mid_share_pct", "death_share_pct"
        ]],
        left_on="Player ID", right_on="striker_id", how="left"
    ).drop(columns=["striker_id"])

    # Build enriched eligible bowlers table (N >= 150 HP legal balls) joined strictly on bowler_id
    elig_bowl = bowl_metrics[bowl_metrics["hp_balls"] >= 150].copy()
    elig_bowl = elig_bowl.sort_values("auction_rating", ascending=False).reset_index(drop=True)
    elig_bowl["Global_Rank"] = range(1, len(elig_bowl) + 1)
    sens_bowl = sensitivity[sensitivity["Discipline"] == "Bowling"][["Player ID", "Stability_Class", "Rank_Std_Dev"]]
    elig_bowl = elig_bowl.merge(sens_bowl, left_on="bowler_id", right_on="Player ID", how="left").drop(columns=["Player ID"])
    elig_bowl = elig_bowl.merge(bowl_roles, on="bowler_id", how="left")
    elig_bowl = elig_bowl.merge(
        all_elig_bowl[["Player ID", "IPL_Recruitment_Pool"]],
        left_on="bowler_id", right_on="Player ID", how="left"
    ).drop(columns=["Player ID"])

    # Enrich Top 10 Bowlers with full 3-way format breakdown & role profile via Player ID
    top10_bowl_enriched = top10_bowl.merge(
        elig_bowl[[
            "bowler_id", "ipl_balls", "ipl_rpa", "ipl_econ", "t20i_balls", "t20i_rpa", "t20i_econ",
            "other_t20_balls", "other_t20_rpa", "ord_balls", "ord_econ", "ord_rpa_per_6",
            "hp_runs", "hp_exp_wkts", "hp_boundary_pct", "shrunk_rpa_per_6", "delta_rpa_rate",
            "Rank_Std_Dev", "IPL_Recruitment_Pool", "primary_style", "bowling_type",
            "inferred_bowling_role", "pp_share_pct", "mid_share_pct", "death_share_pct"
        ]],
        left_on="Player ID", right_on="bowler_id", how="left"
    ).drop(columns=["bowler_id"])

    return {
        "mode": "LOCAL_COMPETITION",
        "top10_bat_raw": top10_bat,
        "top10_bowl_raw": top10_bowl,
        "top10_bat": top10_bat_enriched,
        "top10_bowl": top10_bowl_enriched,
        "top10_bat_ipl": top10_bat_ipl,
        "top10_bowl_ipl": top10_bowl_ipl,
        "elig_bat": elig_bat,
        "elig_bowl": elig_bowl,
        "all_elig_bowl": all_elig_bowl,
        "combined": combined,
        "sensitivity": sensitivity,
        "model_val": model_val,
        "pressure_dist": pressure_dist,
        "pressure_agg": pressure_agg,
    }


def get_active_data() -> dict:
    """Return verified competition analytics dataset."""
    st.session_state["app_mode"] = "LOCAL_COMPETITION"
    return load_local_competition_data()
