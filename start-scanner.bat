@echo off
echo ========================================
echo   Advanced Stock Scanner
echo ========================================
echo.
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak > nul

echo Starting frontend development server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit...
pause > nul
