# Premier League Prediction Web App Setup Script
# This script sets up both the FastAPI backend and React frontend

Write-Host "Setting up Premier League Prediction Web App..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "GW1Pred.py")) {
    Write-Host "Error: Please run this script from the gw1pred directory" -ForegroundColor Red
    exit 1
}

# Backend Setup
Write-Host "`nSetting up FastAPI Backend..." -ForegroundColor Yellow
Set-Location backend

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Backend setup complete!" -ForegroundColor Green

# Frontend Setup
Write-Host "`nSetting up React Frontend..." -ForegroundColor Yellow
Set-Location ..\frontend

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "Found npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

Write-Host "Frontend setup complete!" -ForegroundColor Green

# Return to root directory
Set-Location ..

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run './start.ps1' to start both servers" -ForegroundColor White
Write-Host "2. Or start them manually:" -ForegroundColor White
Write-Host "   Backend:  cd backend && python main.py" -ForegroundColor Gray
Write-Host "   Frontend: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host "`nThe app will be available at:" -ForegroundColor Yellow
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "- API Docs: http://localhost:8000/docs" -ForegroundColor White
