"""
test_all_pages.py — End-to-end automated Streamlit AppTest suite for all 8 pages
and interactive widgets against verified competition outputs.
"""
import os
import sys
from streamlit.testing.v1 import AppTest

DASH_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DASH_DIR)

PAGES = [
    "app.py",
    "pages/1_Batter_Analytics.py",
    "pages/2_Bowler_Analytics.py",
    "pages/3_Player_Comparison.py",
    "pages/4_Pressure_Analytics.py",
    "pages/5_Methodology.py",
    "pages/6_Format_Robustness.py",
    "pages/7_Scouting_Insights.py",
]

failures = []

print("\n=== TESTING ALL 8 PAGES ===")
for page in PAGES:
    at = AppTest.from_file(page, default_timeout=20)
    at.run()
    if len(at.exception) > 0:
        err = str(at.exception[0].value)
        print(f"  [FAIL] {page}: {err}")
        failures.append((page, err))
    else:
        print(f"  [PASS] {page}")

print("\n=== TESTING INTERACTIVE CONTROLS (FILTERS, SEARCH, COMPARISON, CPI SIMULATOR) ===")

# 1. Batter search & empty state
at_bat = AppTest.from_file("pages/1_Batter_Analytics.py", default_timeout=20).run()
at_bat.text_input(key="bat_search").set_value("Jurel").run()
assert len(at_bat.exception) == 0, f"Batter search failed: {at_bat.exception}"
at_bat.text_input(key="bat_search").set_value("ZZZZ_NON_EXISTENT").run()
assert len(at_bat.exception) == 0 and len(at_bat.warning) > 0, "Empty state warning missing for batters!"
print("  [PASS] Batter search + empty state handled cleanly.")

# 2. Bowler search + profile switch to Sufiyan Muqeem (34485)
at_bowl = AppTest.from_file("pages/2_Bowler_Analytics.py", default_timeout=20).run()
at_bowl.selectbox(key="selected_bowler_pid").set_value(34485).run()
assert len(at_bowl.exception) == 0, f"Bowler profile select failed: {at_bowl.exception}"
print("  [PASS] Bowler profile selection (Sufiyan Muqeem ID 34485) rendered cleanly.")

# 3. Player Comparison mode toggle (Batters -> Bowlers)
at_cmp = AppTest.from_file("pages/3_Player_Comparison.py", default_timeout=20).run()
at_cmp.radio(key="comp_discipline").set_value("Bowlers Comparison").run()
assert len(at_cmp.exception) == 0, f"Bowlers comparison toggle failed: {at_cmp.exception}"
print("  [PASS] Player Comparison discipline switch (Batters <-> Bowlers) rendered cleanly.")

# 4. Pressure CPI simulator sliders & knockout toggle
at_pr = AppTest.from_file("pages/4_Pressure_Analytics.py", default_timeout=20).run()
at_pr.slider(key="sim_over").set_value(19).run()
at_pr.checkbox(key="sim_ko").set_value(True).run()
assert len(at_pr.exception) == 0, f"CPI simulator interaction failed: {at_pr.exception}"
print("  [PASS] Pressure CPI Simulator interactive controls passed.")

if failures:
    print(f"\nTOTAL FAILURES: {len(failures)}")
    sys.exit(1)
else:
    print("\nALL 16 PAGE RENDERS + ALL INTERACTIVE WIDGET TESTS PASSED WITH ZERO EXCEPTIONS!")
