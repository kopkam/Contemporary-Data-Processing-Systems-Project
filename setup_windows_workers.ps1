# Setup Workers on Windows Machine
# Run this script on Windows PC (Machine 2)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  NYC Taxi Map-Reduce - Windows Worker Setup" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Get IP address
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*Ethernet*"} | Select-Object -First 1).IPAddress

Write-Host "📍 This Windows PC IP: $IP" -ForegroundColor Green
Write-Host ""

# Check if project exists
if (-Not (Test-Path "Contemporary-Data-Processing-Systems-Project")) {
    Write-Host "❌ Project not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please clone the repository first:" -ForegroundColor Yellow
    Write-Host "  git clone <repo-url>" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Set-Location Contemporary-Data-Processing-Systems-Project

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create data directories
Write-Host ""
Write-Host "📁 Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\worker3" | Out-Null
New-Item -ItemType Directory -Force -Path "data\worker4" | Out-Null

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start workers on this Windows PC:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Open PowerShell Window 1:" -ForegroundColor White
Write-Host "     python main.py worker worker-3 --host 0.0.0.0 --port 5001" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Open PowerShell Window 2:" -ForegroundColor White
Write-Host "     python main.py worker worker-4 --host 0.0.0.0 --port 5002" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 Remember to:" -ForegroundColor Cyan
Write-Host "  - Copy config.yaml from Mac (or sync via git)" -ForegroundColor White
Write-Host "  - Update config.yaml with this IP: $IP" -ForegroundColor White
Write-Host "  - Open Windows Firewall ports 5001-5002" -ForegroundColor White
Write-Host ""
