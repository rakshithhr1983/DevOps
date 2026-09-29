# Exercise 7: Jenkins CI Automation Setup Script (PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🚀 Exercise 7: Launching Jenkins Automation Server" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Docker
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Error: Docker daemon is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "[*] Step 1: Starting Jenkins container via Docker Compose..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "[*] Step 2: Waiting for Jenkins to start up and generate secrets..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "[*] Step 3: Extracting initial admin password..." -ForegroundColor Yellow
python get_admin_password.py

Write-Host "`n✅ Jenkins is running! Open your browser at:" -ForegroundColor Green
Write-Host "  http://localhost:8080" -ForegroundColor White
