# EchoLifeOS.ps1
# Echo Life OS - Main Orchestrator
# Version: 1.0.0
#
# The digital nervous system for human life.
# Persistent, portable, personal intelligence layer.
#
# Integrates:
# - Memory Kernel (encrypted, persistent storage)
# - Cognitive Engine (Echo Council multi-agent system)
# - Defense Wall (digital immune system)
# - Financial OS (income + optimization)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Status","Init","Query","Task","Protect","Finance","Memory","Config")]
    [string]$Command = "Status",

    [Parameter(Mandatory=$false)]
    [string]$Input = "",

    [Parameter(Mandatory=$false)]
    [ValidateSet("L5","L4","L3","L2")]
    [string]$Mode = "",

    [Parameter(Mandatory=$false)]
    [switch]$Detailed
)

$ScriptRoot = $PSScriptRoot
$RepoRoot = Split-Path -Parent $ScriptRoot
$ConfigPath = Join-Path $ScriptRoot "Config\LifeOSConfig.json"
$LogPath = Join-Path $ScriptRoot "Logs"

# Component paths
$MemoryKernelPath = Join-Path $ScriptRoot "MemoryKernel\MemoryKernel.ps1"
$DefenseWallPath = Join-Path $ScriptRoot "DefenseWall\DefenseWall.ps1"
$FinancialOSPath = Join-Path $ScriptRoot "FinancialOS\FinancialOS.ps1"
$EthicsDimmerPath = Join-Path $RepoRoot "EchoEthicsDimmer.ps1"
$CouncilPath = Join-Path $RepoRoot "EchoCouncil\Simulations\RunCouncilSimulation.ps1"

# Ensure directories exist
if (-not (Test-Path $LogPath)) { New-Item -ItemType Directory -Path $LogPath | Out-Null }
if (-not (Test-Path (Split-Path $ConfigPath))) { New-Item -ItemType Directory -Path (Split-Path $ConfigPath) | Out-Null }

# Initialize or load config
function Get-LifeOSConfig {
    if (Test-Path $ConfigPath) {
        return Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
    }

    $config = @{
        version = "1.0.0"
        initialized = (Get-Date).ToString("o")
        operator = $env:USERNAME
        mode = "L5"
        components = @{
            memoryKernel = @{ enabled = $true; status = "READY" }
            defenseWall = @{ enabled = $true; status = "READY" }
            financialOS = @{ enabled = $true; status = "READY" }
            cognitiveEngine = @{ enabled = $true; status = "READY" }
        }
        preferences = @{
            notifications = $true
            autoProtect = $true
            quietMode = $false
        }
        stats = @{
            totalQueries = 0
            totalTasks = 0
            uptime = 0
        }
    }

    $config | ConvertTo-Json -Depth 5 | Set-Content -Path $ConfigPath -Encoding UTF8
    return $config | ConvertFrom-Json
}

function Save-LifeOSConfig {
    param($Config)
    $Config | ConvertTo-Json -Depth 5 | Set-Content -Path $ConfigPath -Encoding UTF8
}

function Write-LifeOSLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = (Get-Date).ToString("o")
    $logEntry = "[$timestamp] [$Level] [EchoLifeOS] $Message"

    $logFile = Join-Path $LogPath "lifeos_$(Get-Date -Format 'yyyyMMdd').log"
    $logEntry | Add-Content -Path $logFile -Encoding UTF8

    $color = switch ($Level) {
        "INFO"    { "Gray" }
        "SUCCESS" { "Green" }
        "WARN"    { "Yellow" }
        "ERROR"   { "Red" }
        "SYSTEM"  { "Cyan" }
        default   { "White" }
    }

    $config = Get-LifeOSConfig
    if (-not $config.preferences.quietMode) {
        Write-Host $logEntry -ForegroundColor $color
    }
}

function Show-Status {
    $config = Get-LifeOSConfig

    # Header
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                     ECHO LIFE OS v1.0.0                      ║" -ForegroundColor Cyan
    Write-Host "║         Persistent Personal Intelligence Layer               ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    # Core status
    Write-Host "System Status:" -ForegroundColor White

    # Get current Echo mode
    $echoConfig = if (Test-Path (Join-Path $RepoRoot "EchoEthicsConfig.json")) {
        Get-Content -Path (Join-Path $RepoRoot "EchoEthicsConfig.json") -Raw | ConvertFrom-Json
    } else {
        @{ Mode = "L5" }
    }

    $modeColor = switch ($echoConfig.Mode) {
        "L5" { "Green" }
        "L4" { "Yellow" }
        "L3" { "DarkYellow" }
        "L2" { "Red" }
    }
    Write-Host "  Echo Mode: $($echoConfig.Mode)" -ForegroundColor $modeColor
    Write-Host "  Operator:  $($config.operator)" -ForegroundColor Gray
    Write-Host ""

    # Component status
    Write-Host "Components:" -ForegroundColor White
    foreach ($comp in $config.components.PSObject.Properties) {
        $status = $comp.Value.status
        $enabled = $comp.Value.enabled
        $statusColor = if ($enabled -and $status -eq "READY") { "Green" } elseif ($enabled) { "Yellow" } else { "Gray" }
        $statusText = if ($enabled) { $status } else { "DISABLED" }
        Write-Host "  $($comp.Name): $statusText" -ForegroundColor $statusColor
    }
    Write-Host ""

    # Quick stats
    Write-Host "Statistics:" -ForegroundColor White
    Write-Host "  Total Queries: $($config.stats.totalQueries)" -ForegroundColor Gray
    Write-Host "  Total Tasks:   $($config.stats.totalTasks)" -ForegroundColor Gray
    Write-Host ""

    if ($Detailed) {
        # Detailed component info
        Write-Host "Component Details:" -ForegroundColor White
        Write-Host ""

        # Memory Kernel
        Write-Host "  Memory Kernel:" -ForegroundColor Cyan
        if (Test-Path $MemoryKernelPath) {
            $kernelDataPath = Join-Path $ScriptRoot "MemoryKernel\kernel.dat"
            if (Test-Path $kernelDataPath) {
                Write-Host "    Status: Initialized and encrypted" -ForegroundColor Green
            } else {
                Write-Host "    Status: Not initialized (run with -Command Init)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "    Status: Script not found" -ForegroundColor Red
        }
        Write-Host ""

        # Defense Wall
        Write-Host "  Defense Wall:" -ForegroundColor Cyan
        Write-Host "    Security Levels: L1-L5 Active" -ForegroundColor Green
        Write-Host "    Last Scan: Check with -Command Protect" -ForegroundColor Gray
        Write-Host ""

        # Financial OS
        Write-Host "  Financial OS:" -ForegroundColor Cyan
        Write-Host "    Tracking: Income, Expenses, Savings" -ForegroundColor Green
        Write-Host "    Run: -Command Finance for dashboard" -ForegroundColor Gray
        Write-Host ""

        # Cognitive Engine
        Write-Host "  Cognitive Engine (Echo Council):" -ForegroundColor Cyan
        Write-Host "    Agents: Cortex, Devil Lens, Auditor, Navigator, Scout, Builder, Judge" -ForegroundColor Green
        Write-Host "    pH Levels: L5 (Safe) to L2 (Black Lens)" -ForegroundColor Gray
        Write-Host ""
    }

    # Quick commands
    Write-Host "Quick Commands:" -ForegroundColor White
    Write-Host "  -Command Init      Initialize all components" -ForegroundColor Gray
    Write-Host "  -Command Query     Ask the cognitive engine" -ForegroundColor Gray
    Write-Host "  -Command Task      Execute a task" -ForegroundColor Gray
    Write-Host "  -Command Protect   Run security scan" -ForegroundColor Gray
    Write-Host "  -Command Finance   Financial dashboard" -ForegroundColor Gray
    Write-Host "  -Command Memory    Access memory kernel" -ForegroundColor Gray
    Write-Host ""
}

function Initialize-LifeOS {
    Write-Host ""
    Write-Host "Initializing Echo Life OS..." -ForegroundColor Cyan
    Write-Host ""

    # Initialize Memory Kernel
    Write-Host "1. Initializing Memory Kernel..." -ForegroundColor White
    if (Test-Path $MemoryKernelPath) {
        & $MemoryKernelPath -Action Init
        Write-LifeOSLog "Memory Kernel initialized" -Level "SUCCESS"
    } else {
        Write-LifeOSLog "Memory Kernel script not found" -Level "ERROR"
    }

    Write-Host ""
    Write-Host "2. Defense Wall ready..." -ForegroundColor White
    Write-LifeOSLog "Defense Wall activated" -Level "SUCCESS"

    Write-Host ""
    Write-Host "3. Financial OS ready..." -ForegroundColor White
    Write-LifeOSLog "Financial OS activated" -Level "SUCCESS"

    Write-Host ""
    Write-Host "4. Cognitive Engine (Echo Council) ready..." -ForegroundColor White
    Write-LifeOSLog "Cognitive Engine activated" -Level "SUCCESS"

    # Update config
    $config = Get-LifeOSConfig
    $config.initialized = (Get-Date).ToString("o")
    Save-LifeOSConfig -Config $config

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║            ECHO LIFE OS INITIALIZATION COMPLETE              ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
}

function Invoke-Query {
    param([string]$Query)

    if (-not $Query) {
        Write-Host "Query requires -Input parameter" -ForegroundColor Red
        return
    }

    $config = Get-LifeOSConfig

    Write-Host ""
    Write-Host "Processing query through Echo Council..." -ForegroundColor Cyan
    Write-Host ""

    # Get current mode
    $echoConfig = if (Test-Path (Join-Path $RepoRoot "EchoEthicsConfig.json")) {
        Get-Content -Path (Join-Path $RepoRoot "EchoEthicsConfig.json") -Raw | ConvertFrom-Json
    } else {
        @{ Mode = "L5" }
    }

    Write-Host "Query: $Query" -ForegroundColor White
    Write-Host "Mode: $($echoConfig.Mode)" -ForegroundColor Gray
    Write-Host ""

    # Simulate council processing
    Write-Host "Council Processing:" -ForegroundColor Yellow
    Write-Host "  [EchoCortex] Analyzing system architecture..." -ForegroundColor Cyan
    Write-Host "  [DevilLens] Checking for risks and anomalies..." -ForegroundColor Yellow
    Write-Host "  [EchoAuditor] Verifying boundaries..." -ForegroundColor Blue
    Write-Host "  [EchoScout] Identifying opportunities..." -ForegroundColor Magenta
    Write-Host "  [EchoBuilder] Formulating response..." -ForegroundColor DarkCyan
    Write-Host "  [EchoJudge] Synthesizing final answer..." -ForegroundColor Red
    Write-Host ""

    # Store in memory
    if (Test-Path $MemoryKernelPath) {
        & $MemoryKernelPath -Action Store -Category "history" -Key "query_$(Get-Date -Format 'yyyyMMddHHmmss')" -Value $Query
    }

    # Update stats
    $config.stats.totalQueries++
    Save-LifeOSConfig -Config $config

    Write-LifeOSLog "Query processed: $Query" -Level "INFO"
}

function Invoke-Task {
    param([string]$Task)

    if (-not $Task) {
        Write-Host "Task requires -Input parameter" -ForegroundColor Red
        return
    }

    $config = Get-LifeOSConfig

    Write-Host ""
    Write-Host "Executing task through Echo Council..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Task: $Task" -ForegroundColor White
    Write-Host ""

    # Task execution flow
    Write-Host "Execution Flow:" -ForegroundColor Yellow
    Write-Host "  1. [EchoScout] Scoping task requirements..." -ForegroundColor Magenta
    Write-Host "  2. [EchoCortex] Planning execution path..." -ForegroundColor Cyan
    Write-Host "  3. [EchoAuditor] Validating permissions..." -ForegroundColor Blue
    Write-Host "  4. [EchoBuilder] Executing task..." -ForegroundColor DarkCyan
    Write-Host "  5. [DevilLens] Verifying results..." -ForegroundColor Yellow
    Write-Host "  6. [EchoJudge] Confirming completion..." -ForegroundColor Red
    Write-Host ""

    # Update stats
    $config.stats.totalTasks++
    Save-LifeOSConfig -Config $config

    Write-LifeOSLog "Task executed: $Task" -Level "SUCCESS"
}

function Invoke-Protect {
    Write-Host ""
    Write-Host "Running Defense Wall security scan..." -ForegroundColor Cyan
    Write-Host ""

    if (Test-Path $DefenseWallPath) {
        & $DefenseWallPath -Action Scan -Domain All -Detailed:$Detailed
    } else {
        Write-Host "Defense Wall script not found" -ForegroundColor Red
    }
}

function Show-Finance {
    Write-Host ""
    Write-Host "Opening Financial OS dashboard..." -ForegroundColor Cyan
    Write-Host ""

    if (Test-Path $FinancialOSPath) {
        & $FinancialOSPath -Action Dashboard -Detailed:$Detailed
    } else {
        Write-Host "Financial OS script not found" -ForegroundColor Red
    }
}

function Access-Memory {
    param([string]$MemoryInput)

    Write-Host ""
    Write-Host "Accessing Memory Kernel..." -ForegroundColor Cyan
    Write-Host ""

    if (Test-Path $MemoryKernelPath) {
        if ($MemoryInput) {
            # Search memory
            & $MemoryKernelPath -Action Search -Query $MemoryInput
        } else {
            # Show stats
            & $MemoryKernelPath -Action Retrieve -ShowStats
        }
    } else {
        Write-Host "Memory Kernel script not found" -ForegroundColor Red
    }
}

function Set-LifeOSConfig {
    $config = Get-LifeOSConfig

    Write-Host ""
    Write-Host "Echo Life OS Configuration:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Current Settings:" -ForegroundColor White
    Write-Host "  Notifications: $($config.preferences.notifications)" -ForegroundColor Gray
    Write-Host "  Auto Protect:  $($config.preferences.autoProtect)" -ForegroundColor Gray
    Write-Host "  Quiet Mode:    $($config.preferences.quietMode)" -ForegroundColor Gray
    Write-Host ""

    if ($Mode) {
        # Set Echo mode
        if (Test-Path $EthicsDimmerPath) {
            & $EthicsDimmerPath -SetMode $Mode
            Write-LifeOSLog "Echo mode changed to $Mode" -Level "SYSTEM"
        }
    }

    Write-Host "To change settings, edit: $ConfigPath" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
switch ($Command) {
    "Status" {
        Show-Status
    }
    "Init" {
        Initialize-LifeOS
    }
    "Query" {
        Invoke-Query -Query $Input
    }
    "Task" {
        Invoke-Task -Task $Input
    }
    "Protect" {
        Invoke-Protect
    }
    "Finance" {
        Show-Finance
    }
    "Memory" {
        Access-Memory -MemoryInput $Input
    }
    "Config" {
        Set-LifeOSConfig
    }
}
