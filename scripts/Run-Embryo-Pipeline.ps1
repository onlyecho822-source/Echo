<#
.SYNOPSIS
    OMEGA Cosmic Pipeline - Hardened Edition

.DESCRIPTION
    This PowerShell script acts as the perimeter guardian for the Echo OMEGA Embryo.
    It performs comprehensive pre-flight security checks, launches the Node.js embryo
    in a controlled manner, and monitors its health.

    Security Checks:
    - Local dependency validation (node, npm, git, gh)
    - Canary integrity verification (cryptographic hash check)
    - Process integrity monitoring (detect rogue processes)
    - System stealth checks (suspicious processes and network connections)
    - GitHub token authentication
    - Repository accessibility verification

.PARAMETER Repo
    The GitHub repository in "owner/name" format (e.g., "onlyecho822-source/Echo").
    This parameter is mandatory.

.PARAMETER EmbryoStatusFile
    Path to the embryo's status JSON file.
    Default: ".\cosmic_status\embryo_status.json"

.PARAMETER SkipSystemChecks
    Skip system-wide stealth checks (suspicious processes, network connections).
    Use this if you don't have administrator privileges.

.EXAMPLE
    .\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo"

.EXAMPLE
    $env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
    $env:OMEGA_SECRET_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    .\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo" -SkipSystemChecks

.NOTES
    Author: Nathan Poinsette
    Version: 2.0.0
    Requires: PowerShell 5.1+ (Windows) or PowerShell Core 7+ (Cross-platform)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [Parameter(Mandatory = $false)]
    [string]$EmbryoStatusFile = ".\cosmic_status\embryo_status.json",

    [Parameter(Mandatory = $false)]
    [switch]$SkipSystemChecks
)

# Enforce all-or-nothing execution
$ErrorActionPreference = "Stop"

# ==========================================
# CONFIGURATION
# ==========================================

$nodeAppPath = Join-Path (Get-Location) "index.js"
$canaryPath = Join-Path (Get-Location) "vault_canary.txt"
$envGitHubToken = $env:GITHUB_TOKEN
$envOmegaSecretKey = $env:OMEGA_SECRET_KEY

# Store the PID of the launched embryo for verification
$launchedEmbryoPID = $null

# ==========================================
# HELPER FUNCTIONS
# ==========================================

function Write-SectionHeader {
    param($Title)
    Write-Host "`n━━━ $Title ━━━" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "✔ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "✖ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "→ $Message" -ForegroundColor White
}

# ==========================================
# DEPENDENCY CHECKS
# ==========================================

function Test-Dependency {
    param([string]$Command)

    $cmd = Get-Command $Command -ErrorAction SilentlyContinue

    if ($cmd) {
        try {
            $ver = & $Command --version 2>$null | Select-Object -First 1
            Write-Success "$Command found (version: $($ver.Trim()))"
            return $true
        }
        catch {
            Write-Success "$Command found"
            return $true
        }
    }
    else {
        Write-Error "$Command NOT installed"
        return $false
    }
}

# ==========================================
# CANARY INTEGRITY CHECK
# ==========================================

function Test-CanaryIntegrity {
    param([string]$Path)

    Write-Info "Checking canary file integrity at: $Path"

    if (-not (Test-Path $Path)) {
        Write-Error "Canary file MISSING. Cannot verify vault integrity."
        return $false
    }

    try {
        $json = Get-Content $Path -Raw | ConvertFrom-Json

        # Extract fields
        $encryptedPayload = $json.encryptedPayload
        $storedHash = $json.hashOfEncryptedPayload
        $timestamp = Get-Date $json.timestamp

        if (-not $encryptedPayload -or -not $storedHash -or -not $timestamp) {
            Write-Error "Canary file MALFORMED. Missing required fields."
            return $false
        }

        # Calculate SHA-256 hash of the encrypted payload
        $stream = [System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($encryptedPayload))
        $currentHash = (Get-FileHash -InputStream $stream -Algorithm SHA256).Hash.ToLower()

        if ($currentHash -ne $storedHash) {
            Write-Error "Canary HASH MISMATCH! Vault tampering detected."
            Write-Error "  Expected: $($storedHash.Substring(0, 16))..."
            Write-Error "  Got:      $($currentHash.Substring(0, 16))..."
            return $false
        }

        # Check freshness
        $ageMinutes = (New-TimeSpan -Start $timestamp -End (Get-Date)).TotalMinutes

        if ($ageMinutes -gt 30) {
            Write-Warning "Canary is STALE ($([math]::Round($ageMinutes, 1)) min old, max 30 min)"
            Write-Warning "Vault may be frozen or writes are delayed."
        }
        else {
            Write-Success "Canary integrity OK (age: $([math]::Round($ageMinutes, 1)) min)"
        }

        return $true
    }
    catch {
        Write-Error "Error reading or parsing canary file: $_"
        return $false
    }
}

# ==========================================
# PROCESS INTEGRITY CHECKS
# ==========================================

function Test-RogueNodeProcesses {
    param([string]$ExpectedScriptPath)

    Write-Info "Checking for rogue Node.js processes..."

    $allNodeProcs = Get-Process -Name node -ErrorAction SilentlyContinue

    if (-not $allNodeProcs) {
        Write-Success "No Node.js processes running."
        return $true
    }

    $rogueProcs = @()

    foreach ($proc in $allNodeProcs) {
        try {
            $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$($proc.Id)" -ErrorAction SilentlyContinue).CommandLine

            if ($cmdline -and $cmdline -notlike "*$ExpectedScriptPath*") {
                $rogueProcs += [PSCustomObject]@{
                    PID         = $proc.Id
                    CommandLine = $cmdline
                    StartTime   = $proc.StartTime
                }
            }
        }
        catch {
            Write-Warning "Could not read command line for PID $($proc.Id)"
        }
    }

    if ($rogueProcs.Count -gt 0) {
        Write-Error "Suspicious Node.js processes DETECTED (not launched by this pipeline):"
        $rogueProcs | Format-Table -AutoSize
        return $false
    }
    else {
        Write-Success "No rogue Node.js processes found."
        return $true
    }
}

function Test-SuspiciousSystemProcesses {
    Write-Info "Scanning for general suspicious system processes..."

    $suspiciousPatterns = @(
        "mimikatz", "procdump", "psexec", "certutil", "bitsadmin",
        "nc.exe", "netcat", "socat", "powershell_ise"
    )

    $suspiciousProcesses = Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $proc = $_
        $cmdLine = ""

        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId=$($proc.Id)" -ErrorAction SilentlyContinue).CommandLine
        }
        catch { }

        # Check if process name or command line contains suspicious patterns
        ($suspiciousPatterns | Where-Object { $proc.ProcessName -like "*$_*" -or $cmdLine -like "*$_*" }).Count -gt 0
    }

    if ($suspiciousProcesses.Count -gt 0) {
        Write-Warning "Potentially suspicious system processes detected:"
        $suspiciousProcesses | Select-Object ProcessName, Id, Path, StartTime | Format-Table -AutoSize
        return $false
    }
    else {
        Write-Success "No highly suspicious system processes found."
        return $true
    }
}

function Test-UnusualNetworkConnections {
    Write-Info "Performing basic check for unusual network connections..."

    try {
        # This requires admin rights. If not available, it will gracefully skip.
        $suspiciousConnections = Get-NetTCPConnection -ErrorAction SilentlyContinue | Where-Object {
            ($_.State -eq 'Established') -and (
                # Common exploit/remote access ports
                ($_.RemotePort -eq 4444) -or
                ($_.RemotePort -eq 5985) -or
                ($_.RemotePort -eq 5986)
            )
        }

        if ($suspiciousConnections.Count -gt 0) {
            Write-Warning "Established network connections to suspicious ports detected:"
            $suspiciousConnections | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | Format-Table -AutoSize
            return $false
        }
        else {
            Write-Success "No immediately suspicious network connections detected."
            return $true
        }
    }
    catch {
        Write-Warning "Could not perform network check (requires admin rights): $($_.Exception.Message)"
        return $true  # Do not fail pipeline if this check can't run
    }
}

# ==========================================
# GITHUB CHECKS
# ==========================================

function Test-GitHubToken {
    param([string]$Token)

    Write-Info "Authenticating GitHub token..."

    if (-not $Token) {
        Write-Error "No GitHub token in environment. Export GITHUB_TOKEN."
        return $false
    }

    try {
        $headers = @{ Authorization = "token $Token" }
        $user = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/user" -ErrorAction Stop

        Write-Success "Authenticated to GitHub as $($user.login)"
        return $true
    }
    catch {
        Write-Error "GitHub authentication failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-GitHubRepoAccess {
    param([string]$Token, [string]$RepoName)

    Write-Info "Checking if GitHub repository '$RepoName' exists and is accessible..."

    try {
        $headers = @{ Authorization = "token $Token" }
        $repo = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$RepoName" -ErrorAction Stop

        Write-Success "GitHub repo found: $($repo.full_name) (Private: $($repo.private))"
        return $true
    }
    catch {
        Write-Error "GitHub repo '$RepoName' does not exist or access denied."
        return $false
    }
}

# ==========================================
# EMBRYO VERIFICATION
# ==========================================

function Test-LaunchedEmbryoProcess {
    param([int]$PID, [string]$ExpectedScriptPath)

    Write-Info "Verifying launched embryo process (PID: $PID)..."

    try {
        $proc = Get-Process -Id $PID -ErrorAction Stop
        $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$($proc.Id)").CommandLine

        if ($cmdline -like "*$ExpectedScriptPath*") {
            Write-Success "Launched embryo process (PID $PID) is running as expected."
            return $true
        }
        else {
            Write-Error "Launched embryo process (PID $PID) command line mismatch: $cmdline"
            return $false
        }
    }
    catch {
        Write-Error "Launched embryo process (PID $PID) not found or cannot be verified: $($_.Exception.Message)"
        return $false
    }
}

function Get-EmbryoStatus {
    param([string]$Path)

    Write-Info "Attempting to read embryo status file from: $Path"

    if (Test-Path $Path) {
        try {
            $json = Get-Content $Path -Raw | ConvertFrom-Json
            Write-Success "Embryo status file found and parsed successfully."
            return $json
        }
        catch {
            Write-Error "Error reading or parsing embryo status file: $_"
            return $null
        }
    }
    else {
        Write-Error "Embryo status file NOT FOUND."
        return $null
    }
}

# ==========================================
# MAIN PIPELINE EXECUTION
# ==========================================

Write-Host "`n" -NoNewline
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "   🌌 OMEGA COSMIC PIPELINE - HARDENED EDITION 🌌   " -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$allChecksPassed = $true

# ==========================================
# 1. LOCAL ENVIRONMENT CHECKS
# ==========================================

Write-SectionHeader "1. LOCAL ENVIRONMENT CHECKS"

$deps = @(
    (Test-Dependency "node"),
    (Test-Dependency "npm"),
    (Test-Dependency "git"),
    (Test-Dependency "gh")
)

if ($deps -contains $false) {
    $allChecksPassed = $false
}

# Check for OMEGA_SECRET_KEY
if (-not $envOmegaSecretKey) {
    Write-Error "OMEGA_SECRET_KEY environment variable not set."
    $allChecksPassed = $false
}
elseif ($envOmegaSecretKey.Length -ne 64) {
    Write-Error "OMEGA_SECRET_KEY must be 64 characters (32 bytes hex)."
    $allChecksPassed = $false
}
else {
    Write-Success "OMEGA_SECRET_KEY environment variable is set."
}

# ==========================================
# 2. CANARY INTEGRITY CHECK
# ==========================================

Write-SectionHeader "2. CANARY INTEGRITY CHECK"

if (-not (Test-CanaryIntegrity $canaryPath)) {
    $allChecksPassed = $false
}

# ==========================================
# 3. SYSTEM INTEGRITY CHECKS (STEALTH)
# ==========================================

if (-not $SkipSystemChecks) {
    Write-SectionHeader "3. SYSTEM INTEGRITY CHECKS (STEALTH)"

    if (-not (Test-RogueNodeProcesses $nodeAppPath)) {
        $allChecksPassed = $false
    }

    if (-not (Test-SuspiciousSystemProcesses)) {
        # Warning only - don't fail pipeline
        Write-Warning "Suspicious processes detected, but continuing..."
    }

    if (-not (Test-UnusualNetworkConnections)) {
        # Warning only - don't fail pipeline
        Write-Warning "Unusual network connections detected, but continuing..."
    }
}
else {
    Write-Warning "System-wide stealth checks SKIPPED (use -SkipSystemChecks:$false to enable)"
}

# ==========================================
# 4. GITHUB TOKEN AUTHENTICATION
# ==========================================

Write-SectionHeader "4. GITHUB TOKEN AUTHENTICATION"

if (-not (Test-GitHubToken $envGitHubToken)) {
    $allChecksPassed = $false
}

# ==========================================
# 5. GITHUB REPOSITORY ACCESS
# ==========================================

Write-SectionHeader "5. GITHUB REPOSITORY ACCESS"

if (-not (Test-GitHubRepoAccess $envGitHubToken $Repo)) {
    $allChecksPassed = $false
}

# ==========================================
# PRE-FLIGHT CHECK SUMMARY
# ==========================================

if (-not $allChecksPassed) {
    Write-Host "`n" -NoNewline
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    Write-Error "CRITICAL PRE-FLIGHT CHECKS FAILED. ABORTING OMEGA EMBRYO LAUNCH."
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "`n" -NoNewline
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Success "All critical pre-flight checks PASSED. Proceeding with embryo launch."
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
}

# ==========================================
# 6. LAUNCH EMBRYO
# ==========================================

Write-SectionHeader "6. LAUNCHING OMEGA EMBRYO"

# Set environment variable for the embryo
$env:GITHUB_REPO = $Repo

try {
    # Launch with visible window to show dashboard
    $proc = Start-Process node -ArgumentList $nodeAppPath -PassThru -WindowStyle Normal

    $launchedEmbryoPID = $proc.Id
    Write-Success "OMEGA Embryo launched successfully with PID: $launchedEmbryoPID"

    # Give embryo time to initialize
    Write-Info "Waiting 10 seconds for embryo to initialize..."
    Start-Sleep -Seconds 10
}
catch {
    Write-Error "FATAL: Failed to launch OMEGA Embryo: $_"
    exit 1
}

# ==========================================
# 7. POST-LAUNCH VERIFICATION
# ==========================================

Write-SectionHeader "7. POST-LAUNCH VERIFICATION & STATUS REPORT"

# Verify the specific launched process
if (-not (Test-LaunchedEmbryoProcess $launchedEmbryoPID $nodeAppPath)) {
    Write-Error "FATAL: Launched embryo process verification failed. Investigate immediately."
    exit 1
}

# Read embryo status
$status = Get-EmbryoStatus $EmbryoStatusFile

if ($status) {
    Write-Host "`n━━━ Embryo Status Report ━━━" -ForegroundColor Cyan
    $status | Format-List
}
else {
    Write-Warning "Embryo status report not available or malformed. Check Node.js logs."
}

# ==========================================
# COMPLETION
# ==========================================

Write-Host "`n" -NoNewline
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "   ✅ OMEGA COSMIC PIPELINE COMPLETE - SYSTEM ONLINE ✅   " -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "`nOMEGA Embryo is running in a separate window. Press Q or Ctrl+C in that window to exit.`n" -ForegroundColor Cyan
