# Bloop Cloud Health Verification Script (Windows PowerShell)
param (
    [string]$TargetUrl = "http://localhost:8000"
)

$HealthEndpoint = "$TargetUrl/api/v1/health"
Write-Host "Pinging health endpoint: $HealthEndpoint..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri $HealthEndpoint -Method Get -TimeoutSec 10
    if ($response.success -eq $true) {
        Write-Host "Service is HEALTHY!" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 4) -ForegroundColor White
        exit 0
    } else {
        Write-Host "Service returned unhealthy status!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Failed to reach health endpoint: $_" -ForegroundColor Red
    exit 1
}
