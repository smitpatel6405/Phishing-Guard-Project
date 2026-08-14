@echo off
title PhishGuard - Auto Start & Test
color 0A

echo.
echo ========================================
echo    🛡️ PhishGuard Auto Start & Test
echo ========================================
echo.

echo 🔍 Checking if Python 3.8 is available...
py -3.8 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3.8 not found! Please install Python 3.8
    echo.
    pause
    exit /b 1
)

echo ✅ Python 3.8 found!
echo.

echo 🚀 Starting PhishGuard Backend Server...
echo.
echo This will:
echo 1. Start the Flask server on localhost:5000
echo 2. Wait for server to be ready
echo 3. Automatically test the backend
echo 4. Show you the results
echo.
echo Press any key to continue...
pause >nul

echo.
echo 🔧 Starting server in background...
start /min cmd /c "py -3.8 app.py"

echo ⏳ Waiting for server to start (10 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo 🧪 Testing the backend server...
echo.

echo 🔍 Health Check:
curl -s http://localhost:5000/health
if %errorlevel% equ 0 (
    echo ✅ Backend is responding!
) else (
    echo ❌ Backend not responding yet, waiting a bit more...
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:5000/health
)

echo.
echo 🔍 Testing API endpoints:
echo.

echo 📊 Home endpoint:
curl -s http://localhost:5000/

echo.
echo 🔮 Prediction test:
curl -s -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d "{\"url\": \"https://www.google.com\"}"

echo.
echo ========================================
echo 🎉 PhishGuard Backend is Ready!
echo ========================================
echo.
echo ✅ Server: http://localhost:5000
echo ✅ Status: Running and Tested
echo.
echo 💡 Next Steps:
echo 1. Load the Chrome extension in Chrome
echo 2. Go to chrome://extensions/
echo 3. Enable Developer mode
echo 4. Click "Load unpacked" and select this folder
echo.
echo 🔧 To stop the server later:
echo 1. Press Ctrl+Alt+Delete
echo 2. End the "python.exe" process
echo.
echo 🎯 The server will keep running in the background!
echo.
pause 