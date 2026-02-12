@echo off
echo ==========================================
echo Starting Visual Similarity Search Engine...
echo ==========================================

:: Start Backend Server in a new window
echo Starting Backend...
start "Backend Server (Port 8001)" cmd /k "cd backend && python main.py"

:: Start Frontend Server in a new window
echo Starting Frontend...
start "Frontend App (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo Both services are launching in separate windows.
echo You can access the app at: http://localhost:5173
echo.
pause
