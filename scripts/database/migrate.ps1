# Bloop Database Migration Script (Windows PowerShell)
Write-Host "Running Alembic database migrations..." -ForegroundColor Cyan
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database migrations applied successfully!" -ForegroundColor Green
} else {
    Write-Host "Migration failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
