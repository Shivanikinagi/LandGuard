# Pied Piper 2.0 Status Information

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Pied Piper 2.0 - Project Status" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This project consists of CLI tools, not web services." -ForegroundColor Yellow
Write-Host ""
Write-Host "Available Components:" -ForegroundColor Green
Write-Host ""
Write-Host "1. PCC (Compression Core) - CLI Tool"
Write-Host "   Location: pcc/"
Write-Host "   Usage:"
Write-Host "   - cd pcc"
Write-Host "   - .\venv\Scripts\Activate.ps1"
Write-Host "   - python main.py pack <file> --password <password>"
Write-Host "   - python main.py unpack <file.ppc> --password <password>"
Write-Host ""
Write-Host "2. LandGuard (AI Agents) - CLI Tool"
Write-Host "   Location: landguard/"
Write-Host "   Usage:"
Write-Host "   - cd landguard"
Write-Host "   - .\venv\Scripts\Activate.ps1"
Write-Host "   - python -m cli.landguard_cli --help"
Write-Host ""
Write-Host "3. Blockchain Smart Contracts"
Write-Host "   Location: landguard/Blockchain/"
Write-Host "   Usage:"
Write-Host "   - cd landguard\Blockchain"
Write-Host "   - npm run deploy:amoy"
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "For full documentation, see:" -ForegroundColor Yellow
Write-Host "- QUICK_START.md"
Write-Host "- DEPLOYMENT.md"
Write-Host "- README.md"
Write-Host "==================================" -ForegroundColor Cyan
