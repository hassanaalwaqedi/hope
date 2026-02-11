# ========================
# HOPE Backend - Azure Deployment Script
# Run this script to deploy the infrastructure
# ========================

# INSTRUCTIONS:
# 1. Make sure Azure CLI is installed: winget install Microsoft.AzureCLI
# 2. Login: az login
# 3. Run this script: .\deploy-azure.ps1

param(
    [string]$ResourceGroup = "hope-prod-rg",
    [string]$Location = "eastus",
    [string]$AppName = "hope-api"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HOPE Backend - Azure Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Azure CLI login
Write-Host "`nChecking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in. Running 'az login'..." -ForegroundColor Yellow
    az login
}
Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green

# Create Resource Group
Write-Host "`nStep 1: Creating Resource Group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location

# Generate secure PostgreSQL password
Write-Host "`nStep 2: Generating secure password..." -ForegroundColor Yellow
$postgresPassword = -join ((65..90) + (97..122) + (48..57) + (33,35,36,37,38,42) | Get-Random -Count 24 | ForEach-Object {[char]$_})
Write-Host "Generated PostgreSQL password (save this securely!): $postgresPassword" -ForegroundColor Magenta

# Deploy infrastructure
Write-Host "`nStep 3: Deploying Azure infrastructure (this takes 5-10 minutes)..." -ForegroundColor Yellow
az deployment group create `
    --resource-group $ResourceGroup `
    --template-file azure/main.bicep `
    --parameters appName=$AppName postgresAdminPassword=$postgresPassword

# Get outputs
Write-Host "`nStep 4: Getting deployment outputs..." -ForegroundColor Yellow
$deployment = az deployment group show --resource-group $ResourceGroup --name main --query properties.outputs | ConvertFrom-Json

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "ACR Login Server: $($deployment.acrLoginServer.value)"
Write-Host "Web App URL: $($deployment.webAppUrl.value)"
Write-Host "PostgreSQL Host: $($deployment.postgresHost.value)"

Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "1. Build and push Docker image:"
Write-Host "   az acr build --registry $($AppName)acr --image $AppName`:latest ."
Write-Host ""
Write-Host "2. Configure app secrets (in Azure Portal or CLI):"
Write-Host "   - HOPE_DB_PASSWORD=$postgresPassword"
Write-Host "   - HOPE_JWT_SECRET_KEY=<generate-secure-key>"
Write-Host "   - HOPE_ENCRYPTION_KEY=<generate-secure-key>"
Write-Host "   - HOPE_GEMINI_API_KEY=<your-api-key>"
Write-Host ""
Write-Host "3. Run database migrations:"
Write-Host "   az webapp ssh --name $AppName --resource-group $ResourceGroup"
Write-Host "   alembic upgrade head"
Write-Host ""
Write-Host "4. Test the API:"
Write-Host "   Invoke-WebRequest $($deployment.webAppUrl.value)/health"
