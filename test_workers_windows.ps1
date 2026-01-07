# Test worker connectivity from Windows
# Tests connection to Mac workers

Write-Host ""
Write-Host "🔍 Testing Worker Connectivity from Windows" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$workers = @(
    "192.168.1.10:5001",  # Mac worker 1
    "192.168.1.10:5002",  # Mac worker 2
    "192.168.1.20:5001",  # This PC worker 3
    "192.168.1.20:5002"   # This PC worker 4
)

foreach ($worker in $workers) {
    Write-Host "Testing $worker ... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri "http://$worker/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.Content -like "*healthy*") {
            Write-Host "✅ OK" -ForegroundColor Green
        } else {
            Write-Host "❌ FAILED (unexpected response)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ FAILED ($($_.Exception.Message))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 If all workers are OK, run on Mac:" -ForegroundColor Cyan
Write-Host "   python3 main.py coordinator --task 1" -ForegroundColor Yellow
Write-Host ""
