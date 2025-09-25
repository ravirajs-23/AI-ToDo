@echo off
echo Setting up AI To-Do List Manager Demo Recording...
echo.

REM Clear screen and set title
cls
title AI To-Do List Manager - E2E Demo Recording

REM Check if backend is running
echo Checking backend status...
curl -s http://localhost:5000/api/health > nul 2>&1
if %errorlevel% neq 0 (
    echo Backend not running! Please start it first:
    echo    cd backend ^&^& python app.py
    pause
    exit /b 1
)

echo Backend is running!
echo.
echo Ready to start recording!
echo    1. Start your screen recording software
echo    2. Press any key to begin demo
echo    3. Recording will auto-start the demo
pause > nul

REM Run the demo
python video_demo_e2e.py

echo.
echo Demo completed! Stop your recording now.
pause
