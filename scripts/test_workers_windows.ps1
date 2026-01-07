# Test worker connectivity from Windows
# Tests connection to all workers from config.yaml

Write-Host ""
Write-Host "Testing Worker Connectivity" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

# Check if config.yaml exists
if (-not (Test-Path "config.yaml")) {
    Write-Host "Error: config.yaml not found!" -ForegroundColor Red
    Write-Host "Copy config.yaml.example and edit with your IPs" -ForegroundColor Yellow
    exit 1
}

# Read workers from config.yaml using Python
$workers = python -c @"
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
    for w in config['cluster']['workers']:
        print(f\"{w['host']}:{w['port']}\")
"@ -split "`n" | Where-Object { $_ }

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
