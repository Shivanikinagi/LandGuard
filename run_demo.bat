@echo off
REM LandGuard & PCC Demo Runner
REM ==========================

echo ============================================
echo      LandGuard ^& PCC Demo Runner
echo ============================================

echo This script will run the PowerShell demo script.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo Running PowerShell demo script...
powershell -ExecutionPolicy Bypass -File "%~dp0demo_script.ps1"

echo.
echo Demo script completed.
echo Press any key to exit...
pause >nul