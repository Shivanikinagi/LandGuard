# PowerShell script to start the backend server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LandGuard Backend Server Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run the database setup script first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\setup_postgres.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check if database is initialized
Write-Host ""
Write-Host "Checking database..." -ForegroundColor Yellow
python -c "from database.connection import check_db_connection; exit(0 if check_db_connection() else 1)"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Cannot connect to database!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "  1. PostgreSQL is running" -ForegroundColor Cyan
    Write-Host "  2. Database connection settings in .env are correct" -ForegroundColor Cyan
    Write-Host "  3. Run database setup: .\scripts\setup_postgres.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "✓ Database connection successful" -ForegroundColor Green

# Initialize database with sample data
Write-Host ""
$initDb = Read-Host "Initialize database with sample data? (yes/no)"
if ($initDb -eq "yes") {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    python scripts/init_database.py
}

# Start the server
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Starting FastAPI Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Green
Write-Host "  - Local:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - Health:   http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000