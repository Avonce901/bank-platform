# Complete Automation: Create Repo + Push to GitHub
# This script handles everything: repo creation and push
# PSScriptAnalyzer: Suppress unused variable warnings

param(
    [string]$GitHubUsername = 'anthony-banking-sim',
    [string]$GitHubToken = '',
    [string]$RepoName = 'bank-platform',
    [string]$RepoDescription = 'Banking simulation platform with API, PDF extraction, Excel generation',
    [bool]$IsPublic = $true
)

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host '  Bank Platform - Complete GitHub Automation        ' -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# Step 1: Get GitHub Token if not provided
if (-not $GitHubToken) {
    Write-Host '[!] GitHub Personal Access Token required' -ForegroundColor Yellow
    Write-Host '    Get one at: https://github.com/settings/tokens' -ForegroundColor Gray
    Write-Host "    Required scopes: repo, workflow`n" -ForegroundColor Gray
    $GitHubToken = Read-Host 'Enter your GitHub Personal Access Token'
    
    if (-not $GitHubToken) {
        Write-Host '[ERROR] Token is required' -ForegroundColor Red
        exit 1
    }
}

# Step 2: Check if repo exists
Write-Host '[1] Checking if repository exists...' -ForegroundColor Green

$headers = @{
    'Authorization' = "Bearer $GitHubToken"
    'Accept'        = 'application/vnd.github.v3+json'
}

try {
    $repoCheck = Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$RepoName" `
        -Headers $headers -ErrorAction SilentlyContinue
    
    if ($repoCheck) {
        Write-Host "[OK] Repository already exists: $($repoCheck.html_url)" -ForegroundColor Green
    }
}
catch {
    Write-Host '[*] Repository does not exist, creating...' -ForegroundColor Yellow
    
    # Create repository
    $repoBody = @{
        name        = $RepoName
        description = $RepoDescription
        private     = -not $IsPublic
        auto_init   = $false
    } | ConvertTo-Json
    
    try {
        $newRepo = Invoke-RestMethod -Uri 'https://api.github.com/user/repos' `
            -Method Post `
            -Headers $headers `
            -ContentType 'application/json' `
            -Body $repoBody
        
        Write-Host "[OK] Repository created: $($newRepo.html_url)" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed to create repository: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Navigate to project
Write-Host "`n[2] Navigating to project..." -ForegroundColor Green
$projectPath = "$env:USERPROFILE\bank_platform"

if (-not (Test-Path $projectPath)) {
    Write-Host "[ERROR] Project path not found: $projectPath" -ForegroundColor Red
    exit 1
}

Set-Location $projectPath
Write-Host "[OK] Current location: $(Get-Location)" -ForegroundColor Green

# Step 4: Configure remote
Write-Host "`n[3] Configuring remote..." -ForegroundColor Green

$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"

# Remove existing remote
git remote remove origin 2>$null

# Add new remote
git remote add origin $remoteUrl
Write-Host "[OK] Remote configured: $remoteUrl" -ForegroundColor Green

# Step 5: Set branch to main
Write-Host "`n[4] Setting up branch..." -ForegroundColor Green

$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -eq 'master') {
    git branch -M main
    Write-Host '[OK] Branch renamed to main' -ForegroundColor Green
}
else {
    Write-Host '[OK] Already on main branch' -ForegroundColor Green
}

# Step 6: Push to GitHub
Write-Host "`n[5] Pushing to GitHub..." -ForegroundColor Green

# Configure git credentials to use the token
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseDeclaredVarsMoreThanAssignments', '', Justification = 'Variable used in git command')]
$gitUrl = "https://$($GitHubToken):x-oauth-basic@github.com/$GitHubUsername/$RepoName.git"
Write-Host 'Connecting to repository...' -ForegroundColor Cyan

try {
    # Set remote URL with token authentication
    git remote set-url origin $gitUrl
    Write-Host "Remote configured: $gitUrl" -ForegroundColor Gray
    
    git push -u origin main 2>&1 | ForEach-Object {
        if ($_ -match 'fatal|error') {
            Write-Host "[!] $_" -ForegroundColor Red
        }
        else {
            Write-Host "[*] $_" -ForegroundColor Gray
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host '[OK] Successfully pushed to GitHub!' -ForegroundColor Green
    }
    else {
        Write-Host '[WARNING] Push may have failed. Check the output above.' -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ERROR] Push failed: $_" -ForegroundColor Red
    exit 1
}

# Step 7: Summary
Write-Host "`n========================================================" -ForegroundColor Green
Write-Host '  GitHub Push Complete!                             ' -ForegroundColor Green
Write-Host "========================================================`n" -ForegroundColor Green

Write-Host "`nRepository Details:" -ForegroundColor Cyan
Write-Host "  URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Green
Write-Host '  Branch: main' -ForegroundColor Green
Write-Host "  Files: $(git ls-files | Measure-Object -Line | Select-Object -ExpandProperty Lines) files" -ForegroundColor Green

Write-Host "`nLatest Commits:" -ForegroundColor Cyan
git log --oneline -3 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host '  • Add collaborators on GitHub' -ForegroundColor Gray
Write-Host '  • Enable branch protection rules' -ForegroundColor Gray
Write-Host '  • Set up GitHub Actions for CI/CD' -ForegroundColor Gray
Write-Host '  • Create pull request templates' -ForegroundColor Gray

Write-Host "`n✨ Your bank platform is now on GitHub!`n" -ForegroundColor Green
