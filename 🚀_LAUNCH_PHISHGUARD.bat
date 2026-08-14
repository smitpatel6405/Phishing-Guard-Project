@echo off
title 🛡️ PhishGuard Launcher
color 0B

:menu
cls
echo.
echo ========================================
echo    🛡️ PhishGuard Launcher Menu
echo ========================================
echo.
echo Choose an option:
echo.
echo 1. 🚀 Start Backend + Auto Test (Recommended)
echo 2. 🧪 Start Backend + Run Demo
echo 3. 🔧 Start Backend Only
echo 4. 🧪 Test Backend Only
echo 5. 🎬 Run Demo Only
echo 6. ❌ Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto auto_start_test
if "%choice%"=="2" goto start_demo
if "%choice%"=="3" goto start_only
if "%choice%"=="4" goto test_only
if "%choice%"=="5" goto demo_only
if "%choice%"=="6" goto exit
goto menu

:auto_start_test
cls
echo.
echo 🚀 Starting Auto Start & Test...
echo.
call START_AND_TEST.bat
goto menu

:start_demo
cls
echo.
echo 🧪 Starting Backend + Demo...
echo.
py -3.8 auto_start_test.py
goto menu

:start_only
cls
echo.
echo 🔧 Starting Backend Only...
echo.
echo Starting Flask server on localhost:5000...
echo Press Ctrl+C to stop when done.
echo.
py -3.8 app.py
goto menu

:test_only
cls
echo.
echo 🧪 Testing Backend Only...
echo.
py -3.8 test_backend.py
echo.
pause
goto menu

:demo_only
cls
echo.
echo 🎬 Running Demo Only...
echo.
py -3.8 demo.py
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye! Stay safe online! 🛡️
timeout /t 2 >nul
exit 