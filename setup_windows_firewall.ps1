# Add Windows Firewall rules for MapReduce workers
# Run as Administrator!

Write-Host ""
Write-Host "🔥 Adding Windows Firewall Rules" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-Not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "Adding firewall rule for port 5001..." -ForegroundColor Yellow
netsh advfirewall firewall add rule name="MapReduce Worker 5001" dir=in action=allow protocol=TCP localport=5001

Write-Host "Adding firewall rule for port 5002..." -ForegroundColor Yellow
netsh advfirewall firewall add rule name="MapReduce Worker 5002" dir=in action=allow protocol=TCP localport=5002

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "✅ Firewall rules added successfully!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ports 5001 and 5002 are now open for incoming connections" -ForegroundColor White
Write-Host ""
Write-Host "To verify:" -ForegroundColor Cyan
Write-Host "  netsh advfirewall firewall show rule name=all | findstr MapReduce" -ForegroundColor Yellow
Write-Host ""
Write-Host "To remove (if needed):" -ForegroundColor Cyan
Write-Host "  netsh advfirewall firewall delete rule name='MapReduce Worker 5001'" -ForegroundColor Yellow
Write-Host "  netsh advfirewall firewall delete rule name='MapReduce Worker 5002'" -ForegroundColor Yellow
Write-Host ""
