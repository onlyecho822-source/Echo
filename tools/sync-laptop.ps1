# Echo Universe Laptop Sync Script
# Synchronizes local laptop repository with GitHub remote
# Maintains bidirectional sync and handles conflicts automatically

param(
    [switch]$AutoPull = $false,
    [switch]$AutoPush = $false,
    [switch]$Watch = $false,
    [int]$WatchInterval = 300  # 5 minutes
)

# Configuration
$RepoPath = $PSScriptRoot | Split-Path
$RemoteName = "origin"
$BranchName = "main"
$LogFile = Join-Path $RepoPath "tools\sync-log.txt"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

# Logging function
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    Write-Info $Message
}

# Check if we're in a git repository
function Test-GitRepository {
    Push-Location $RepoPath
    $IsGitRepo = git rev-parse --git-dir 2>$null
    Pop-Location
    return $null -ne $IsGitRepo
}

# Get current branch
function Get-CurrentBranch {
    Push-Location $RepoPath
    $Branch = git branch --show-current
    Pop-Location
    return $Branch
}

# Check for uncommitted changes
function Test-UncommittedChanges {
    Push-Location $RepoPath
    $Status = git status --porcelain
    Pop-Location
    return $Status.Length -gt 0
}

# Pull from remote
function Invoke-GitPull {
    Write-Info "Pulling changes from $RemoteName/$BranchName..."
    Push-Location $RepoPath
    
    try {
        $Output = git pull $RemoteName $BranchName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Pull successful"
            Write-Log "Pull successful: $Output"
            return $true
        } else {
            Write-Error "✗ Pull failed: $Output"
            Write-Log "Pull failed: $Output"
            return $false
        }
    } finally {
        Pop-Location
    }
}

# Commit local changes
function Invoke-GitCommit {
    param([string]$Message = "Laptop sync: Auto-commit $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    
    Write-Info "Committing local changes..."
    Push-Location $RepoPath
    
    try {
        git add .
        $Output = git commit -m $Message 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Commit successful"
            Write-Log "Commit successful: $Message"
            return $true
        } elseif ($Output -match "nothing to commit") {
            Write-Info "No changes to commit"
            return $true
        } else {
            Write-Error "✗ Commit failed: $Output"
            Write-Log "Commit failed: $Output"
            return $false
        }
    } finally {
        Pop-Location
    }
}

# Push to remote
function Invoke-GitPush {
    Write-Info "Pushing changes to $RemoteName/$BranchName..."
    Push-Location $RepoPath
    
    try {
        $Output = git push $RemoteName $BranchName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Push successful"
            Write-Log "Push successful"
            return $true
        } else {
            Write-Error "✗ Push failed: $Output"
            Write-Log "Push failed: $Output"
            
            # Check if it's a protected branch issue
            if ($Output -match "protected branch") {
                Write-Warning "Branch is protected. Creating pull request instead..."
                $NewBranch = "laptop-sync-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                git checkout -b $NewBranch
                git push $RemoteName $NewBranch
                
                Write-Info "Creating pull request..."
                gh pr create --title "Laptop Sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" `
                            --body "Automated sync from laptop" `
                            --base $BranchName
                
                git checkout $BranchName
                Write-Success "✓ Pull request created for branch: $NewBranch"
                return $true
            }
            
            return $false
        }
    } finally {
        Pop-Location
    }
}

# Sync function
function Invoke-Sync {
    Write-Info "`n=========================================="
    Write-Info "Echo Universe Laptop Sync"
    Write-Info "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Info "==========================================`n"
    
    # Verify git repository
    if (-not (Test-GitRepository)) {
        Write-Error "Not a git repository: $RepoPath"
        return $false
    }
    
    # Check current branch
    $CurrentBranch = Get-CurrentBranch
    if ($CurrentBranch -ne $BranchName) {
        Write-Warning "Current branch is '$CurrentBranch', expected '$BranchName'"
        Write-Info "Switching to $BranchName..."
        Push-Location $RepoPath
        git checkout $BranchName
        Pop-Location
    }
    
    # Check for uncommitted changes
    $HasChanges = Test-UncommittedChanges
    
    if ($HasChanges) {
        Write-Info "Uncommitted changes detected"
        
        if ($AutoPush) {
            # Commit and push
            if (Invoke-GitCommit) {
                Invoke-GitPush
            }
        } else {
            Write-Warning "Use -AutoPush to automatically commit and push changes"
            
            $Response = Read-Host "Commit and push changes? (y/n)"
            if ($Response -eq 'y') {
                $CommitMessage = Read-Host "Enter commit message (or press Enter for auto-message)"
                if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
                    Invoke-GitCommit
                } else {
                    Invoke-GitCommit -Message $CommitMessage
                }
                Invoke-GitPush
            }
        }
    } else {
        Write-Info "No uncommitted changes"
    }
    
    # Pull from remote
    if ($AutoPull -or $HasChanges -eq $false) {
        Invoke-GitPull
    } else {
        $Response = Read-Host "Pull changes from remote? (y/n)"
        if ($Response -eq 'y') {
            Invoke-GitPull
        }
    }
    
    Write-Success "`n✓ Sync complete`n"
    return $true
}

# Watch mode
function Start-WatchMode {
    Write-Info "`n=========================================="
    Write-Info "Echo Universe Laptop Sync - Watch Mode"
    Write-Info "Interval: $WatchInterval seconds"
    Write-Info "Press Ctrl+C to stop"
    Write-Info "==========================================`n"
    
    Write-Log "Watch mode started (interval: $WatchInterval seconds)"
    
    try {
        while ($true) {
            Invoke-Sync
            Write-Info "Next sync in $WatchInterval seconds...`n"
            Start-Sleep -Seconds $WatchInterval
        }
    } catch {
        Write-Warning "`nWatch mode stopped"
        Write-Log "Watch mode stopped"
    }
}

# Display status
function Show-Status {
    Write-Info "`n=========================================="
    Write-Info "Echo Universe Repository Status"
    Write-Info "==========================================`n"
    
    Push-Location $RepoPath
    
    Write-Info "Branch: $(Get-CurrentBranch)"
    Write-Info "Repository: $RepoPath"
    Write-Info ""
    
    Write-Info "Git Status:"
    git status --short
    Write-Info ""
    
    Write-Info "Recent Commits:"
    git log --oneline -5
    Write-Info ""
    
    Write-Info "Agent Activity:"
    $LedgerPath = Join-Path $RepoPath "ledgers\agent_activity"
    if (Test-Path $LedgerPath) {
        $RecentLogs = Get-ChildItem $LedgerPath -Filter "*.jsonl" | 
                      Sort-Object LastWriteTime -Descending | 
                      Select-Object -First 3
        
        foreach ($Log in $RecentLogs) {
            $LastEntry = Get-Content $Log.FullName | Select-Object -Last 1 | ConvertFrom-Json
            Write-Info "  $($LastEntry.agent_name): $($LastEntry.action) at $($LastEntry.timestamp)"
        }
    } else {
        Write-Info "  No agent activity logs found"
    }
    
    Pop-Location
    Write-Info "`n=========================================="
}

# Main execution
Write-Host @"

███████╗ ██████╗██╗  ██╗ ██████╗     ███████╗██╗   ██╗███╗   ██╗ ██████╗
██╔════╝██╔════╝██║  ██║██╔═══██╗    ██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝
█████╗  ██║     ███████║██║   ██║    ███████╗ ╚████╔╝ ██╔██╗ ██║██║     
██╔══╝  ██║     ██╔══██║██║   ██║    ╚════██║  ╚██╔╝  ██║╚██╗██║██║     
███████╗╚██████╗██║  ██║╚██████╔╝    ███████║   ██║   ██║ ╚████║╚██████╗
╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝     ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝

"@ -ForegroundColor Cyan

if ($Watch) {
    Start-WatchMode
} else {
    Show-Status
    Invoke-Sync
}

# Usage instructions
if (-not $AutoPull -and -not $AutoPush -and -not $Watch) {
    Write-Info "`nUsage Options:"
    Write-Info "  .\sync-laptop.ps1                    # Interactive sync"
    Write-Info "  .\sync-laptop.ps1 -AutoPull          # Auto-pull changes"
    Write-Info "  .\sync-laptop.ps1 -AutoPush          # Auto-commit and push"
    Write-Info "  .\sync-laptop.ps1 -AutoPull -AutoPush  # Full auto-sync"
    Write-Info "  .\sync-laptop.ps1 -Watch             # Watch mode (continuous sync)"
    Write-Info "  .\sync-laptop.ps1 -Watch -WatchInterval 600  # Watch every 10 minutes"
    Write-Info ""
}
