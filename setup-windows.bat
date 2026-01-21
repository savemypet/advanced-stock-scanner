@echo off
echo ========================================
echo   Advanced Stock Scanner
echo   Windows Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python found: 
python --version
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js 18+ from:
    echo https://nodejs.org/
    pause
    exit /b 1
)

echo [2/4] Node.js found:
node --version
npm --version
echo.

echo [3/4] Installing backend dependencies...
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo Backend dependencies installed!
echo.

echo [4/4] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo Frontend dependencies installed!
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the app, run: start-scanner.bat
echo Or manually:
echo   Terminal 1: cd backend ^&^& python app.py
echo   Terminal 2: cd frontend ^&^& npm run dev
echo.
pause
