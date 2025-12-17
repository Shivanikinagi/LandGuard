@echo off
echo Starting LandGuard & PCC Complete System...

echo.
echo 1. Starting API Server...
echo ------------------------
start "API Server" cmd /k "cd /d f:\shivani\VSCode\projects\compression\compression-\api && ..\api_env\Scripts\activate && python server.py"

timeout /t 5 /nobreak >nul

echo.
echo 2. Starting Frontend Development Server...
echo ----------------------------------------
start "Frontend" cmd /k "cd /d f:\shivani\VSCode\projects\compression\compression-\frontend && npm run dev"

echo.
echo System startup initiated!
echo.
echo API Server will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:5175 (or next available port)
echo.
echo Press any key to exit...
pause >nul