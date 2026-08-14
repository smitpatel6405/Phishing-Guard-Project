@echo off
title PhishGuard - Start BOTH (Current:5000 + Advanced:5001) & Test
color 0A

echo ===============================================
echo   PhishGuard - One Click Start and Test (Both)
echo ===============================================
echo.

echo [1/5] Checking Python 3.8 ...
py -3.8 --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ERROR: Python 3.8 not found. Install Python 3.8 first.
  echo.
  pause
  exit /b 1
)

echo [2/5] Installing dependencies (Current) ...
py -3.8 -m pip install --disable-pip-version-check -q -r requirements.txt

echo [3/5] Installing dependencies (Advanced) ...
py -3.8 -m pip install --disable-pip-version-check -q -r Advanced\requirements.txt

echo [4/5] Starting servers ...
REM Start Current (5000)
start /min cmd /c "py -3.8 app.py"
REM Start Advanced (5001)
start /min cmd /c "py -3.8 Advanced\app.py"

echo Waiting 10 seconds for servers to boot ...
timeout /t 10 /nobreak >nul

echo [5/5] Running health checks ...
echo --- Current (5000) ---
powershell -Command "$r=Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing; Write-Output $r.StatusCode; Write-Output $r.Content" 2>nul
echo --- Advanced (5001) ---
powershell -Command "$r=Invoke-WebRequest -Uri http://localhost:5001/health -UseBasicParsing; Write-Output $r.StatusCode; Write-Output $r.Content" 2>nul

echo.
echo Testing predict endpoints ...
echo --- Current /predict (google.com) ---
powershell -Command "Invoke-WebRequest -Uri http://localhost:5000/predict -Method POST -ContentType 'application/json' -Body '{\"url\":\"https://www.google.com\"}' | % { $_.StatusCode; $_.Content }" 2>nul
echo --- Advanced /predict_fused (google.com, URL-only) ---
powershell -Command "Invoke-WebRequest -Uri http://localhost:5001/predict_fused -Method POST -ContentType 'application/json' -Body '{\"url\":\"https://www.google.com\"}' | % { $_.StatusCode; $_.Content }" 2>nul

echo.
echo ===============================================
echo  DONE. Both servers are running in the background.
echo  - Current:  http://localhost:5000
echo  - Advanced: http://localhost:5001
echo ===============================================
echo.
echo Tip:
echo  - Load the extension from this folder for Current.
echo  - Load from Advanced\ for the Advanced build, enable consent, and click Visual Scan.
echo.
pause












