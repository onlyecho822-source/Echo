<#
.SYNOPSIS
    Echo GitHub Diagnostics Hub - PowerShell Integration Layer

.DESCRIPTION
    Links local PowerShell environment to GitHub Diagnostics and Adaptive Learning Layer.
    Part of the Echo Civilization framework.

.AUTHOR
    Nathan Poinsette

.VERSION
    1.0.0
#>

param(
    [Parameter()]
    [ValidateSet('Diagnostic', 'Adaptive', 'Secure', 'Integration')]
    [string]$Mode = 'Diagnostic',

    [Parameter()]
    [string]$RepoPath = '.',

    [Parameter()]
    [switch]$Verbose
)

# Echo Diagnostics Configuration
$EchoConfig = @{
    Version = "1.0.0"
    Quadrants = @('Diagnostic', 'Adaptive', 'Secure', 'Integration')
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# Diagnostic Functions
function Get-EchoGitStatus {
    <#
    .SYNOPSIS
        Get comprehensive Git status for Echo repository
    #>
    param([string]$Path = '.')

    Push-Location $Path
    try {
        $status = @{
            Branch = git rev-parse --abbrev-ref HEAD 2>$null
            RemoteUrl = git config --get remote.origin.url 2>$null
            Status = git status --porcelain 2>$null
            LastCommit = git log -1 --format="%H|%s|%ai" 2>$null
            Ahead = 0
            Behind = 0
        }

        # Get ahead/behind counts
        $tracking = git rev-parse --abbrev-ref '@{upstream}' 2>$null
        if ($tracking) {
            $counts = git rev-list --left-right --count "HEAD...$tracking" 2>$null
            if ($counts -match "(\d+)\s+(\d+)") {
                $status.Ahead = [int]$matches[1]
                $status.Behind = [int]$matches[2]
            }
        }

        return $status
    }
    finally {
        Pop-Location
    }
}

function Get-EchoHealthCheck {
    <#
    .SYNOPSIS
        Perform health check on Echo system components
    #>
    param([string]$Path = '.')

    $health = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Components = @()
        OverallStatus = "Healthy"
    }

    # Check core directories
    $requiredDirs = @('docs', 'engines', 'scripts', 'config', 'data', 'tests')
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $Path $dir
        $exists = Test-Path $dirPath
        $health.Components += @{
            Name = $dir
            Type = "Directory"
            Status = if ($exists) { "OK" } else { "Missing" }
            Path = $dirPath
        }
        if (-not $exists) {
            $health.OverallStatus = "Degraded"
        }
    }

    # Check core files
    $coreFiles = @(
        'docs/ECHO_MASTER_INDEX_vOmega.md',
        'config/master_repo_blueprint.yaml',
        'engines/echo_baby/config.yaml'
    )
    foreach ($file in $coreFiles) {
        $filePath = Join-Path $Path $file
        $exists = Test-Path $filePath
        $health.Components += @{
            Name = Split-Path $file -Leaf
            Type = "File"
            Status = if ($exists) { "OK" } else { "Missing" }
            Path = $filePath
        }
    }

    return $health
}

function Invoke-EchoDiagnostic {
    <#
    .SYNOPSIS
        Run full diagnostic suite
    #>
    param([string]$Path = '.')

    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "ECHO DIAGNOSTICS HUB" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""

    # Git Status
    Write-Host "[Git Status]" -ForegroundColor Yellow
    $gitStatus = Get-EchoGitStatus -Path $Path
    Write-Host "  Branch: $($gitStatus.Branch)"
    Write-Host "  Remote: $($gitStatus.RemoteUrl)"
    if ($gitStatus.LastCommit) {
        $parts = $gitStatus.LastCommit -split '\|'
        Write-Host "  Last Commit: $($parts[0].Substring(0, 8))... - $($parts[1])"
    }
    Write-Host ""

    # Health Check
    Write-Host "[Health Check]" -ForegroundColor Yellow
    $health = Get-EchoHealthCheck -Path $Path
    Write-Host "  Overall Status: $($health.OverallStatus)"
    Write-Host "  Components:"
    foreach ($comp in $health.Components) {
        $color = if ($comp.Status -eq "OK") { "Green" } else { "Red" }
        Write-Host "    - $($comp.Name): $($comp.Status)" -ForegroundColor $color
    }
    Write-Host ""

    # System Info
    Write-Host "[System Info]" -ForegroundColor Yellow
    Write-Host "  PowerShell Version: $($PSVersionTable.PSVersion)"
    Write-Host "  OS: $($PSVersionTable.OS)"
    Write-Host "  Platform: $($PSVersionTable.Platform)"
    Write-Host ""

    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "Diagnostic Complete" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan

    return @{
        Git = $gitStatus
        Health = $health
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
}

function Invoke-EchoAdaptive {
    <#
    .SYNOPSIS
        Adaptive learning layer - monitors and learns from patterns
    #>
    param([string]$Path = '.')

    Write-Host "[Adaptive Learning Layer]" -ForegroundColor Magenta

    # Collect metrics
    $metrics = @{
        FileCount = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue).Count
        DirCount = (Get-ChildItem -Path $Path -Recurse -Directory -ErrorAction SilentlyContinue).Count
        TotalSize = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Extensions = @{}
    }

    # Analyze file types
    Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        $ext = if ($_.Extension) { $_.Extension } else { "(none)" }
        if (-not $metrics.Extensions.ContainsKey($ext)) {
            $metrics.Extensions[$ext] = 0
        }
        $metrics.Extensions[$ext]++
    }

    Write-Host "  Files: $($metrics.FileCount)"
    Write-Host "  Directories: $($metrics.DirCount)"
    Write-Host "  Total Size: $([math]::Round($metrics.TotalSize / 1KB, 2)) KB"
    Write-Host "  File Types:"
    $metrics.Extensions.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "    $($_.Key): $($_.Value)"
    }

    return $metrics
}

function Invoke-EchoSecure {
    <#
    .SYNOPSIS
        Secure automation checks
    #>
    param([string]$Path = '.')

    Write-Host "[Secure Automation Layer]" -ForegroundColor Red

    $security = @{
        Sensitive = @()
        Warnings = @()
    }

    # Check for sensitive files
    $sensitivePatterns = @('.env', 'credentials', 'secret', 'key', 'token')
    Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        foreach ($pattern in $sensitivePatterns) {
            if ($_.Name -like "*$pattern*") {
                $security.Sensitive += $_.FullName
                $security.Warnings += "Potentially sensitive file: $($_.Name)"
            }
        }
    }

    if ($security.Warnings.Count -eq 0) {
        Write-Host "  No security warnings detected" -ForegroundColor Green
    }
    else {
        Write-Host "  Warnings: $($security.Warnings.Count)" -ForegroundColor Yellow
        foreach ($warn in $security.Warnings) {
            Write-Host "    - $warn" -ForegroundColor Yellow
        }
    }

    return $security
}

# Main execution
switch ($Mode) {
    'Diagnostic' {
        $result = Invoke-EchoDiagnostic -Path $RepoPath
    }
    'Adaptive' {
        Invoke-EchoDiagnostic -Path $RepoPath | Out-Null
        $result = Invoke-EchoAdaptive -Path $RepoPath
    }
    'Secure' {
        Invoke-EchoDiagnostic -Path $RepoPath | Out-Null
        $result = Invoke-EchoSecure -Path $RepoPath
    }
    'Integration' {
        $result = @{
            Diagnostic = Invoke-EchoDiagnostic -Path $RepoPath
            Adaptive = Invoke-EchoAdaptive -Path $RepoPath
            Secure = Invoke-EchoSecure -Path $RepoPath
        }
    }
}

# Output result
if ($Verbose) {
    $result | ConvertTo-Json -Depth 10
}
