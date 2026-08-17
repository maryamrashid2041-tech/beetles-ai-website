@echo off
title Beetles AI Launcher
color 0A

echo.
echo ================================================
echo   BEETLES AI - Starting Application
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Setting execution policy...
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force"

echo [3/3] Launching Beetles AI...
echo.
echo Your browser will open in a few seconds.
echo Press Ctrl+C to stop the app.
echo.

streamlit run app.py

pause