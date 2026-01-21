@echo off
echo ========================================
echo   Advanced Stock Scanner - Setup
echo ========================================
echo.

echo Step 1: Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing backend dependencies!
    pause
    exit /b 1
)
cd ..
echo Backend dependencies installed successfully!
echo.

echo Step 2: Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo Error installing frontend dependencies!
    pause
    exit /b 1
)
cd ..
echo Frontend dependencies installed successfully!
echo.

echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start the scanner, run: start-scanner.bat
echo.
pause
