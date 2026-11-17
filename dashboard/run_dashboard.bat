@echo off
title T20 Pressure Analytics Dashboard (Local Competition Mode)
echo ========================================================================
echo   T20 PRESSURE ANALYTICS ^& SCOUTING DASHBOARD
echo   Starting Local Competition Mode on http://localhost:8501
echo ========================================================================
cd /d "%~dp0"
python validate_dashboard_data.py
if errorlevel 1 (
    echo [WARNING] Validation reported an issue. Check output above before proceeding.
    pause
)
python -m streamlit run app.py --server.port 8501 --client.showSidebarNavigation false
pause
