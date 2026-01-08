# Start both workers on Windows
# Run this script to start workers 3 and 4

Write-Host "Starting Worker 3 and 4 on Windows..." -ForegroundColor Cyan

# Get project root directory (parent of scripts folder)
$projectRoot = Split-Path -Parent $PSScriptRoot

# Start worker 3 in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; python main.py worker worker-3 --host 0.0.0.0 --port 5001"

# Wait a bit
Start-Sleep -Seconds 1

# Start worker 4 in new PowerShell window  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; python main.py worker worker-4 --host 0.0.0.0 --port 5002"

Write-Host ""
Write-Host "✅ Workers started in separate windows!" -ForegroundColor Green
Write-Host "   Close those windows to stop workers" -ForegroundColor Yellow
