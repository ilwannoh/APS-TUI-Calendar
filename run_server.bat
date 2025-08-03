@echo off
echo Starting APS Web Application...
echo.

REM Start backend server
echo Starting backend server...
cd backend
start cmd /k "python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend server
echo Starting frontend server...
cd ..\frontend
start cmd /k "python -m http.server 3000"

echo.
echo Application started!
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo.
echo Press any key to stop servers...
pause > nul