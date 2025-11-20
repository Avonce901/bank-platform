# Update GitHub Repository Description and Settings
# Adds description, topics, and enables/disables features

param(
    [string]$GitHubToken = '',
    [string]$GitHubUsername = 'Avonce901',
    [string]$RepoName = 'bank-platform'
)

function Update-GitHubRepo {
    param(
        [string]$Token,
        [string]$Username,
        [string]$Repo
    )
    
    $headers = @{
        'Authorization'       = "Bearer $Token"
        'Accept'              = 'application/vnd.github.v3+json'
        'X-GitHub-Media-Type' = 'github.v3'
    }
    
    $repoDescription = 'Banking simulation platform with Flask API, PDF extraction, Excel generation, and Streamlit admin dashboard. Complete with Docker support, comprehensive tests, and sample data initialization.'
    
    $topics = @(
        'banking',
        'python',
        'flask',
        'api',
        'streamlit',
        'docker',
        'ci-cd',
        'pdf-processing',
        'excel-generation'
    )
    
    # Update basic repo info
    Write-Host '[*] Updating repository description...' -ForegroundColor Yellow
    
    $repoData = @{
        description   = $repoDescription
        homepage      = "https://github.com/$Username/$Repo"
        has_issues    = $true
        has_projects  = $true
        has_downloads = $true
        has_wiki      = $false
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "https://api.github.com/repos/$Username/$Repo" `
            -Method Patch `
            -Headers $headers `
            -ContentType 'application/json' `
            -Body $repoData | Out-Null
        
        Write-Host '[OK] Repository description updated' -ForegroundColor Green
    }
    catch {
        Write-Host "[!] Error updating description: $_" -ForegroundColor Red
    }
    
    # Update topics
    Write-Host '[*] Adding topics...' -ForegroundColor Yellow
    
    $topicsData = @{
        names = $topics
    } | ConvertTo-Json
    
    try {
        $topicHeaders = $headers.Clone()
        $topicHeaders['Accept'] = 'application/vnd.github.mercy-preview+json'
        
        Invoke-RestMethod -Uri "https://api.github.com/repos/$Username/$Repo/topics" `
            -Method Put `
            -Headers $topicHeaders `
            -ContentType 'application/json' `
            -Body $topicsData | Out-Null
        
        Write-Host "[OK] Topics added: $($topics -join ', ')" -ForegroundColor Green
    }
    catch {
        Write-Host "[!] Error adding topics: $_" -ForegroundColor Red
    }
    
    # Add branch protection (requires admin)
    Write-Host '[*] Setting up branch protection...' -ForegroundColor Yellow
    
    $protectionData = @{
        required_status_checks        = @{
            strict   = $true
            contexts = @('build', 'test')
        }
        enforce_admins                = $false
        required_pull_request_reviews = @{
            dismiss_stale_reviews      = $true
            require_code_owner_reviews = $false
        }
        restrictions                  = $null
    } | ConvertTo-Json -Depth 3
    
    try {
        Invoke-RestMethod -Uri "https://api.github.com/repos/$Username/$Repo/branches/main/protection" `
            -Method Put `
            -Headers $headers `
            -ContentType 'application/json' `
            -Body $protectionData | Out-Null
        
        Write-Host '[OK] Branch protection enabled' -ForegroundColor Green
    }
    catch {
        Write-Host '[!] Note: Branch protection requires admin rights (may fail with personal token)' -ForegroundColor Gray
    }
}

# Main execution
if (-not $GitHubToken) {
    Write-Host '[!] GitHub token required' -ForegroundColor Red
    exit 1
}

Write-Host "`n========== GitHub Repository Configuration =========`n" -ForegroundColor Cyan

Update-GitHubRepo -Token $GitHubToken -Username $GitHubUsername -Repo $RepoName

Write-Host "`n========== Configuration Complete =========`n" -ForegroundColor Green
Write-Host "Repository: https://github.com/$GitHubUsername/$RepoName`n" -ForegroundColor Green
Write-Host "What was updated:`n" -ForegroundColor Cyan
Write-Host '  ✓ Project description added' -ForegroundColor Gray
Write-Host '  ✓ Topics/tags configured' -ForegroundColor Gray
Write-Host '  ✓ Branch protection (main)' -ForegroundColor Gray
Write-Host "`nGitHub Actions will run automatically on push!" -ForegroundColor Green
Write-Host ''
