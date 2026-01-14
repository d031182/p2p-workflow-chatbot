# Cloud Foundry SSO Login Helper Script
# This script helps with the SSO login process

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SAP BTP Cloud Foundry Login" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get fresh passcode
Write-Host "STEP 1: Get Your Passcode" -ForegroundColor Yellow
Write-Host "Opening browser to get passcode..." -ForegroundColor Gray
Start-Process "https://login.cf.eu10.hana.ondemand.com/passcode"

Write-Host ""
Write-Host "A browser window has opened. Please:" -ForegroundColor White
Write-Host "  1. Login with your SAP credentials" -ForegroundColor Gray
Write-Host "  2. Copy the passcode shown" -ForegroundColor Gray
Write-Host "  3. Come back here" -ForegroundColor Gray
Write-Host ""

# Step 2: Get passcode from user
Write-Host "STEP 2: Enter Passcode" -ForegroundColor Yellow
$passcode = Read-Host "Paste your passcode here"

if ([string]::IsNullOrWhiteSpace($passcode)) {
    Write-Host "No passcode entered. Exiting." -ForegroundColor Red
    exit 1
}

# Step 3: Login with passcode
Write-Host ""
Write-Host "STEP 3: Authenticating..." -ForegroundColor Yellow

# Use cf auth with passcode
$env:CF_PASSWORD = $passcode
$result = echo $passcode | cf login -a https://api.cf.eu10.hana.ondemand.com --sso 2>&1

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Login process completed!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: cf target" -ForegroundColor Gray
Write-Host "  2. Run: cf push" -ForegroundColor Gray
Write-Host ""
