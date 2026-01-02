# Pied Piper 2.0 - Automated Setup Script for Windows PowerShell
# This script sets up the entire project for local development

$ErrorActionPreference = "Stop"

Write-Host "Pied Piper 2.0 - Automated Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python 3 is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "README.md")) {
    Write-Host "[ERROR] Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Create base directory structure
Write-Host ""
Write-Host "Setting up directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path data, logs, backups | Out-Null

# Setup PCC (Compression Core)
Write-Host ""
Write-Host "Setting up PCC (Compression Core)..." -ForegroundColor Yellow
Set-Location pcc

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists"
}

Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "[OK] PCC setup complete" -ForegroundColor Green
deactivate

Set-Location ..

# Setup LandGuard (Backend API)
Write-Host ""
Write-Host "Setting up LandGuard (Backend API)..." -ForegroundColor Yellow
Set-Location landguard

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists"
}

Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    @"
# Database Configuration
DATABASE_URL=postgresql://piedpiper:changeme@localhost:5432/landguard
DATABASE_POOL_SIZE=20

# Security
SECRET_KEY=change_this_to_a_random_secret_key_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Blockchain (Optional - configure if using blockchain features)
BLOCKCHAIN_RPC_URL=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=
PRIVATE_KEY=

# IPFS/Pinata
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=http://localhost:3000
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "⚠️  Please edit landguard\.env with your actual credentials" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists"
}

Write-Host "✅ LandGuard setup complete" -ForegroundColor Green
deactivate

Set-Location ..

# Setup Blockchain (Optional)
Write-Host ""
$response = Read-Host "Do you want to set up Blockchain features? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Setting up Blockchain..." -ForegroundColor Yellow
    Set-Location landguard\Blockchain
    
    try {
        $nodeVersion = node --version 2>&1
        Write-Host "[OK] Node.js $nodeVersion found" -ForegroundColor Green
        
        Write-Host "Installing Node.js dependencies..."
        npm install
        
        # Create .env if it doesn't exist
        if (-not (Test-Path ".env")) {
            Write-Host "Creating blockchain .env file..."
            $envContent = @"
PRIVATE_KEY=your_wallet_private_key_without_0x_prefix
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGONSCAN_API_KEY=your_polygonscan_api_key
"@
            $envContent | Out-File -FilePath ".env" -Encoding UTF8
            Write-Host "Warning: Please edit landguard\Blockchain\.env with your wallet details" -ForegroundColor Yellow
        } else {
            Write-Host "Blockchain .env file already exists"
        }
        
        Write-Host "[OK] Blockchain setup complete" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Node.js is not installed. Skipping Blockchain setup." -ForegroundColor Yellow
        Write-Host "Please install Node.js 16+ to use blockchain features."
    }
    
    Set-Location ..\..
}

# Create helper scripts for starting services
Write-Host ""
Write-Host "Creating helper scripts..." -ForegroundColor Yellow

# Create start.ps1
@"
# Start Pied Piper services

Write-Host "🚀 Starting Pied Piper 2.0..." -ForegroundColor Cyan

# Start PCC in background
Write-Host "Starting PCC service..."
`$pccJob = Start-Job -ScriptBlock {
    Set-Location pcc
    .\venv\Scripts\Activate.ps1
    python -m uvicorn app:app --host 0.0.0.0 --port 8000
}
Write-Host "PCC running on http://localhost:8000 (Job ID: `$(`$pccJob.Id))" -ForegroundColor Green

# Start LandGuard in background
Write-Host "Starting LandGuard service..."
`$landguardJob = Start-Job -ScriptBlock {
    Set-Location landguard
    .\venv\Scripts\Activate.ps1
    python -m uvicorn app:app --host 0.0.0.0 --port 8001
}
Write-Host "LandGuard running on http://localhost:8001 (Job ID: `$(`$landguardJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host "PCC: http://localhost:8000"
Write-Host "LandGuard: http://localhost:8001"
Write-Host ""
Write-Host "To stop services, run: .\stop.ps1"
Write-Host "To view logs, use: Get-Job | Receive-Job"

# Save job IDs for cleanup
`$pccJob.Id | Out-File -FilePath ".pcc.pid"
`$landguardJob.Id | Out-File -FilePath ".landguard.pid"
"@ | Out-File -FilePath "start.ps1" -Encoding UTF8

# Create stop.ps1
@"
# Stop Pied Piper services

Write-Host "🛑 Stopping Pied Piper 2.0..." -ForegroundColor Yellow

if (Test-Path ".pcc.pid") {
    `$pccJobId = Get-Content ".pcc.pid"
    Stop-Job -Id `$pccJobId -ErrorAction SilentlyContinue
    Remove-Job -Id `$pccJobId -ErrorAction SilentlyContinue
    Write-Host "✅ PCC stopped (Job ID: `$pccJobId)" -ForegroundColor Green
    Remove-Item ".pcc.pid"
}

if (Test-Path ".landguard.pid") {
    `$landguardJobId = Get-Content ".landguard.pid"
    Stop-Job -Id `$landguardJobId -ErrorAction SilentlyContinue
    Remove-Job -Id `$landguardJobId -ErrorAction SilentlyContinue
    Write-Host "✅ LandGuard stopped (Job ID: `$landguardJobId)" -ForegroundColor Green
    Remove-Item ".landguard.pid"
}

Write-Host "All services stopped" -ForegroundColor Green
"@ | Out-File -FilePath "stop.ps1" -Encoding UTF8

# Final summary
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure your environment:"
Write-Host "   - Edit landguard\.env with your credentials"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "   - Edit landguard\Blockchain\.env with your wallet details"
}
Write-Host ""
Write-Host "2. Get required API keys:"
Write-Host "   - Pinata IPFS: https://pinata.cloud/"
Write-Host "   - Polygon Amoy: https://faucet.polygon.technology/"
Write-Host ""
Write-Host "3. Start the services:"
Write-Host "   .\start.ps1"
Write-Host ""
Write-Host "4. Test the installation:"
Write-Host "   cd pcc"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host "   python -c `"from compressors import Compressor; print('Working!')`""
Write-Host ""
Write-Host "5. Read the deployment guide:"
Write-Host "   Get-Content DEPLOYMENT.md"
Write-Host ""
Write-Host "Happy coding!" -ForegroundColor Cyan
