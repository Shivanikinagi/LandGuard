# Stop Pied Piper services

Write-Host "Stopping Pied Piper 2.0..." -ForegroundColor Yellow

if (Test-Path ".pcc.pid") {
    $pccJobId = Get-Content ".pcc.pid"
    Stop-Job -Id $pccJobId -ErrorAction SilentlyContinue
    Remove-Job -Id $pccJobId -ErrorAction SilentlyContinue
    Write-Host "PCC stopped (Job ID: $pccJobId)" -ForegroundColor Green
    Remove-Item ".pcc.pid"
}

if (Test-Path ".landguard.pid") {
    $landguardJobId = Get-Content ".landguard.pid"
    Stop-Job -Id $landguardJobId -ErrorAction SilentlyContinue
    Remove-Job -Id $landguardJobId -ErrorAction SilentlyContinue
    Write-Host "LandGuard stopped (Job ID: $landguardJobId)" -ForegroundColor Green
    Remove-Item ".landguard.pid"
}

Write-Host "All services stopped" -ForegroundColor Green
