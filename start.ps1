# Premier League Prediction Web App Development Server Launcher
# This script starts both the FastAPI backend and React frontend in development mode

Write-Host "Starting Premier League Prediction Web App..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "Error: Please run this script from the gw1pred directory" -ForegroundColor Red
    Write-Host "Make sure both 'backend' and 'frontend' directories exist" -ForegroundColor Red
    exit 1
}

# Function to start backend in a new window
function Start-Backend {
    Write-Host "Starting FastAPI Backend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd 'backend'; & '.\venv\Scripts\Activate.ps1'; Write-Host 'Backend server starting...' -ForegroundColor Green; python main.py"
    ) -WindowStyle Normal
}

# Function to start frontend in a new window
function Start-Frontend {
    Write-Host "Starting React Frontend..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2  # Give backend a moment to start
    Start-Process powershell -ArgumentList @(
        "-NoExit", 
        "-Command",
        "cd 'frontend'; Write-Host 'Frontend server starting...' -ForegroundColor Green; npm run dev"
    ) -WindowStyle Normal
}

# Start both servers
Start-Backend
Start-Frontend

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Development servers are starting!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "`nServers will be available at:" -ForegroundColor Yellow
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "- API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nTwo PowerShell windows will open:" -ForegroundColor Yellow
Write-Host "1. Backend server (FastAPI/Python)" -ForegroundColor White
Write-Host "2. Frontend server (React/Vite)" -ForegroundColor White
Write-Host "`nTo stop the servers:" -ForegroundColor Yellow
Write-Host "- Close the PowerShell windows, or" -ForegroundColor White
Write-Host "- Press Ctrl+C in each window" -ForegroundColor White
Write-Host "`nWaiting for servers to start..." -ForegroundColor Cyan

# Wait a bit for servers to start
Start-Sleep -Seconds 5

# Try to open the frontend in the default browser
try {
    Write-Host "Opening browser..." -ForegroundColor Green
    Start-Process "http://localhost:3000"
} catch {
    Write-Host "Could not open browser automatically. Please navigate to http://localhost:3000" -ForegroundColor Yellow
}

Write-Host "`nSetup complete! Check the browser and server windows." -ForegroundColor Green
