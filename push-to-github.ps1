#!/usr/bin/env powershell
<#
.DESCRIPTION
    Bank Platform - Automated GitHub Push Script
    Automates the entire process of pushing to GitHub
#>

param(
    [string]$Username = "",
    [string]$RepoName = "bank-platform"
)

function Write-Header {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Step, [int]$Number = 0)
    if ($Number -gt 0) {
        Write-Host "[$Number] $Step" -ForegroundColor Green
    } else {
        Write-Host "[*] $Step" -ForegroundColor Yellow
    }
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Failed {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Main execution
Write-Header "Bank Platform - Automated GitHub Push"

# Check if Git is installed
Write-Step "Checking Git installation" 1
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Git found: $gitVersion"
} else {
    Write-Failed "Git not found. Please install Git first."
    exit 1
}

# Get project path
$projectPath = Join-Path $env:USERPROFILE "bank_platform"

if (Test-Path $projectPath) {
    Write-Success "Project found at: $projectPath"
} else {
    Write-Failed "Project not found at: $projectPath"
    exit 1
}

# Get GitHub username if not provided
if ([string]::IsNullOrWhiteSpace($Username)) {
    $Username = Read-Host "Enter your GitHub username"
}

if ([string]::IsNullOrWhiteSpace($Username)) {
    Write-Failed "GitHub username required"
    exit 1
}

$RepoUrl = "https://github.com/$Username/$RepoName.git"

Write-Host "`nConfiguration:" -ForegroundColor Cyan
Write-Host "  Project: bank_platform"
Write-Host "  Username: $Username"
Write-Host "  Repository: $RepoName"
Write-Host "  URL: $RepoUrl"

$proceed = Read-Host "`nProceed with push? (y/n)"
if ($proceed -ne 'y') {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

# Initialize repository
Write-Step "Setting up repository" 2
Push-Location $projectPath

if (Test-Path ".git") {
    Write-Success "Git repository already initialized"
} else {
    Write-Host "Initializing repository..."
    git init
}

# Check for existing remote
Write-Step "Adding remote" 3
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote -and $existingRemote -ne "origin") {
    Write-Host "Existing remote found: $existingRemote"
    $update = Read-Host "Update it? (y/n)"
    if ($update -eq 'y') {
        git remote remove origin
        git remote add origin $RepoUrl
        Write-Success "Remote updated"
    }
} else {
    git remote add origin $RepoUrl 2>$null
    Write-Success "Remote added: $RepoUrl"
}

# Check branch
Write-Step "Checking branch" 4
$currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
if ($currentBranch -ne "main") {
    Write-Host "Renaming branch to 'main'..."
    git branch -M main
    Write-Success "Branch renamed"
} else {
    Write-Success "Already on 'main' branch"
}

# Push to GitHub
Write-Step "Pushing to GitHub" 5
Write-Host "When prompted, enter your GitHub credentials:" -ForegroundColor Yellow
Write-Host "  Username: $Username" -ForegroundColor Gray
Write-Host "  Password: Your Personal Access Token (PAT)" -ForegroundColor Gray
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Success "Successfully pushed to GitHub!"
    Write-Header "GitHub Push Complete"
    Write-Host "`nYour repository is available at:" -ForegroundColor Green
    Write-Host "  https://github.com/$Username/$RepoName`n" -ForegroundColor Cyan
} else {
    Write-Failed "Push to GitHub failed"
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check your GitHub username"
    Write-Host "  2. Use Personal Access Token (not password)"
    Write-Host "  3. Verify internet connection"
    Pop-Location
    exit 1
}

Pop-Location
Write-Host ""
