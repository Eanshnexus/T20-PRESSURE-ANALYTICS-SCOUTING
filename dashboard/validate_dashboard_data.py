"""
validate_dashboard_data.py — Standalone CLI automated validation script.
Compares dashboard-loaded data directly against FINAL_SUBMISSION CSVs and verifies
canonical IDs, Sufiyan Muqeem's 3-way split, zero Other T20 -> IPL contamination,
and missing-value integrity.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_validation import run_validation_checks


def main():
    print("=" * 78)
    print("T20 PRESSURE ANALYTICS DASHBOARD — AUTOMATED DATA VALIDATION REPORT")
    print("=" * 78)
    checks = run_validation_checks()
    failed = 0
    for c in checks:
        status = c["Status"]
        if status != "PASS":
            failed += 1
        print(f"[{status}] {c['Check']}")
        print(f"       {c['Detail']}")
    print("=" * 78)
    print(f"SUMMARY: {len(checks) - failed}/{len(checks)} checks PASSED.")
    print("=" * 78)
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
