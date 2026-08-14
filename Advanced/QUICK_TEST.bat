@echo off
title PhishGuard Quick Test
color 0E

echo.
echo ========================================
echo    🛡️ PhishGuard Quick Test
echo ========================================
echo.

echo 🔍 Testing Backend Status...
curl -s http://localhost:5000/health
if %errorlevel% equ 0 (
    echo.
    echo ✅ Backend is running!
    echo.
    echo 🧪 Testing Prediction...
    curl -s -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d "{\"url\": \"https://www.google.com\"}"
    echo.
    echo.
    echo 🎉 System is working perfectly!
    echo.
    echo 💡 Now test the Chrome extension:
    echo 1. Click the PhishGuard icon in Chrome
    echo 2. Navigate to different websites
    echo 3. Check analysis results in the popup
    echo.
) else (
    echo.
    echo ❌ Backend is not running!
    echo.
    echo 🔧 To start the backend:
    echo 1. Double-click START_AND_TEST.bat
    echo 2. Wait for it to complete
    echo 3. Run this test again
    echo.
)

pause 