# LandGuard & PCC Complete System Startup Script

Write-Host "Starting LandGuard & PCC Complete System..." -ForegroundColor Cyan

Write-Host "`n1. Starting API Server..." -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow

# Start API server in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'f:\shivani\VSCode\projects\compression\compression-\api'; ..\api_env\Scripts\Activate.ps1; python server.py" -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host "`n2. Starting Frontend Development Server..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

# Start frontend server in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'f:\shivani\VSCode\projects\compression\compression-\frontend'; npm run dev" -WindowStyle Normal

Write-Host "`nSystem startup initiated!" -ForegroundColor Green
Write-Host "`nAPI Server will be available at: http://localhost:5000" -ForegroundColor White
Write-Host "Frontend will be available at: http://localhost:5175 (or next available port)" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")