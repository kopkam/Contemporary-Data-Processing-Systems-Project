# Test worker connectivity from Windows
# Tests connection to Mac workers

Write-Host ""
Write-Host "Testing Worker Connectivity from Windows" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$workers = @(
    "192.168.1.10:5001",
    "192.168.1.10:5002",
    "192.168.1.20:5001",
    "192.168.1.20:5002"
)

foreach ($worker in $workers) {
    Write-Host "Testing $worker ... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri "http://$worker/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.Content -like "*healthy*") {
            Write-Host "OK" -ForegroundColor Green
        } else {
            Write-Host "FAILED (unexpected response)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "FAILED" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "If all workers are OK, you can run the coordinator" -ForegroundColor Cyan
Write-Host ""
