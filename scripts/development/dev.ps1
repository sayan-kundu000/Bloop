# Bloop Development Launch Script (Windows PowerShell)
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Launching Bloop Full-Stack Development Environment" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "[INFO] Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Launch backend in background job or prompt
Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Backend...'; .\.venv\Scripts\Activate.ps1; uvicorn backend.app.main:app --reload --port 8000"

# Launch frontend in background job or current window
Write-Host "[2/2] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Frontend...'; cd frontend; npm run dev"

Write-Host "`nBloop development processes launched!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "Swagger Docs: http://localhost:8000/docs" -ForegroundColor White
