@echo off
echo ========================================
echo   Advanced Stock Scanner
echo   Windows Launcher
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
echo Starting backend server...
start "Backend Server - Advanced Stock Scanner" cmd /k "cd /d %~dp0backend && python app.py"
timeout /t 3 /nobreak > nul

echo Starting frontend development server...
start "Frontend Server - Advanced Stock Scanner" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000 (or check terminal for actual port)
echo.
echo Two windows will open - keep them open!
echo Close them to stop the servers.
echo ========================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak > nul
start http://localhost:3000
echo.
echo Press any key to exit this window (servers will keep running)...
pause > nul
