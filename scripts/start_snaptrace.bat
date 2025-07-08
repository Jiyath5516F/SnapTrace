@echo off
REM SnapTrace Startup Script
REM This script starts SnapTrace in the background system tray

echo Starting SnapTrace...
echo The application will run in the system tray.
echo Press Ctrl+Shift+S to take a screenshot from anywhere!
echo.

cd /d "d:\SnapTrace 2.O"
python main.py

echo.
echo SnapTrace has exited.
pause
