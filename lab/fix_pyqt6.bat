@echo off
echo ========================================
echo Fix PyQt6 DLL Issue
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Uninstalling PyQt6...
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip

echo.
echo Step 2: Reinstalling PyQt6...
pip install PyQt6

echo.
echo Step 3: Installing other dependencies...
pip install requests websocket-client

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Try running: python main.py
echo.
pause
