@echo off
echo ========================================
echo   Advanced Stock Scanner
echo   Windows Launcher (with IB Gateway)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Checking dependencies...
echo.

REM Check if backend dependencies are installed
if not exist "backend\venv" (
    echo Installing backend dependencies...
    cd backend
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install backend dependencies
        pause
        exit /b 1
    )
    cd ..
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo ========================================
echo Starting IB Gateway first...
echo ========================================
echo.

REM Check if IB Gateway is already running
netstat -ano | findstr ":7497" >nul 2>&1
if not errorlevel 1 (
    echo IB Gateway is already running on port 7497
    goto :start_backend
)

REM Try to find and start IB Gateway
echo Looking for IB Gateway...
set IB_GATEWAY_PATH=

REM Common IB Gateway installation paths
if exist "C:\Program Files\IB Gateway\ibgateway.exe" (
    set IB_GATEWAY_PATH=C:\Program Files\IB Gateway\ibgateway.exe
    goto :start_ib_gateway
)
if exist "C:\Program Files (x86)\IB Gateway\ibgateway.exe" (
    set IB_GATEWAY_PATH=C:\Program Files (x86)\IB Gateway\ibgateway.exe
    goto :start_ib_gateway
)
if exist "%USERPROFILE%\IB Gateway\ibgateway.exe" (
    set IB_GATEWAY_PATH=%USERPROFILE%\IB Gateway\ibgateway.exe
    goto :start_ib_gateway
)

REM Try TWS as fallback
if exist "C:\Program Files\IBJts\tws.exe" (
    set IB_GATEWAY_PATH=C:\Program Files\IBJts\tws.exe
    goto :start_ib_gateway
)
if exist "C:\Program Files (x86)\IBJts\tws.exe" (
    set IB_GATEWAY_PATH=C:\Program Files (x86)\IBJts\tws.exe
    goto :start_ib_gateway
)

echo.
echo WARNING: IB Gateway not found in common locations!
echo.
echo Please start IB Gateway manually, then:
echo 1. Log in with your credentials
echo 2. Enable API in Configure ^> API ^> Settings
echo 3. Set port to 7497 (paper trading) or 7496 (live)
echo.
echo Press any key to continue starting the app anyway...
pause > nul
goto :start_backend

:start_ib_gateway
echo Found IB Gateway at: %IB_GATEWAY_PATH%
echo Starting IB Gateway...
start "" "%IB_GATEWAY_PATH%"
echo.
echo Waiting 10 seconds for IB Gateway to start...
timeout /t 10 /nobreak > nul
echo.
echo IMPORTANT: Please log in to IB Gateway when it opens!
echo Make sure API is enabled in Configure ^> API ^> Settings
echo.
pause

:start_backend
echo.
echo ========================================
echo Starting backend server...
echo ========================================
start "Backend Server - Advanced Stock Scanner" cmd /k "cd /d %~dp0backend && python app.py"
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo Starting frontend development server...
echo ========================================
start "Frontend Server - Advanced Stock Scanner" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo All servers are starting...
echo.
echo IB Gateway:  Check the IB Gateway window (should be running)
echo Backend:     http://localhost:5000
echo Frontend:    http://localhost:3000 (or check terminal for actual port)
echo.
echo Three windows will open - keep them open!
echo Close them to stop the servers.
echo ========================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak > nul
start http://localhost:3000
echo.
echo Press any key to exit this window (servers will keep running)...
pause > nul
