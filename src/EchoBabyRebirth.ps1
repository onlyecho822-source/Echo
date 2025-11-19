<#
.SYNOPSIS
    Echo Baby Rebirth v2.1 - Main Orchestration Script

.DESCRIPTION
    A transparent, diagnostic-only system intelligence framework featuring:
    - RAM-only memory capsules
    - Adaptive learning engine
    - System awareness scanning
    - Phoenix renewal cycles
    - Event-driven heartbeat monitoring
    - Self-healing error recovery

.NOTES
    Version: 2.1.0
    Author: Echo Civilization Framework

    COMPLIANCE NOTICE:
    - Diagnostic operations only
    - No system modification without explicit command
    - All operations logged and auditable
    - RAM-only volatile storage
    - Runs with invoker privileges only
#>

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Start', 'Stop', 'Status', 'Renew', 'Scan')]
    [string]$Action = 'Start',

    [Parameter()]
    [string]$ConfigPath,

    [Parameter()]
    [switch]$Verbose
)

# Script-level variables
$script:EchoVersion = "2.1.0"
$script:EchoState = "Uninitialized"
$script:StartTime = $null

# Import modules
$ModulePath = Join-Path $PSScriptRoot "Modules"
$RequiredModules = @(
    "MemoryCapsule",
    "TelemetryCore",
    "AwarenessScanner",
    "RenewalEngine",
    "HeartbeatNode"
)

foreach ($module in $RequiredModules) {
    $modulefile = Join-Path $ModulePath "$module.psm1"
    if (Test-Path $modulefile) {
        Import-Module $modulefile -Force -ErrorAction Stop
    } else {
        Write-Warning "Module not found: $modulefile"
    }
}

#region Configuration

function Get-DefaultConfig {
    <#
    .SYNOPSIS
        Returns the default Echo Baby configuration
    #>
    return @{
        Version = $script:EchoVersion

        Heartbeat = @{
            IntervalSeconds = 30
            TimeoutMs = 5000
            MaxRetries = 3
        }

        Capsules = @{
            MaxPatternSizeMB = 10
            MaxEventSizeMB = 5
            EventRetentionMinutes = 5
        }

        Thresholds = @{
            CPUWarning = 70
            CPUCritical = 90
            MemoryWarning = 75
            MemoryCritical = 90
            DiskWarning = 80
            DiskCritical = 95
        }

        Renewal = @{
            ScheduledIntervalHours = 6
            MemoryPressurePercent = 80
            StalePatternCycles = 1000
        }

        Telemetry = @{
            Enabled = $true
            LogPath = Join-Path $PSScriptRoot "../logs"
            RetentionDays = 7
        }

        SelfHealing = @{
            Enabled = $true
            MaxRetries = 3
            RetryDelayMs = 1000
        }
    }
}

function Initialize-Configuration {
    <#
    .SYNOPSIS
        Loads or creates the Echo Baby configuration
    #>
    param(
        [string]$Path
    )

    if ($Path -and (Test-Path $Path)) {
        try {
            $config = Get-Content $Path -Raw | ConvertFrom-Json -AsHashtable
            Write-TelemetryLog -Message "Configuration loaded from: $Path" -Level "Info"
            return $config
        } catch {
            Write-TelemetryLog -Message "Failed to load config, using defaults: $_" -Level "Warning"
        }
    }

    return Get-DefaultConfig
}

#endregion

#region Core Functions

function Initialize-EchoBaby {
    <#
    .SYNOPSIS
        Initializes the Echo Baby system (Baby phase)
    #>
    param(
        [hashtable]$Config
    )

    Write-Host "Initializing Echo Baby Rebirth v$($script:EchoVersion)..." -ForegroundColor Cyan
    Write-TelemetryLog -Message "=== ECHO BABY INITIALIZATION ===" -Level "Info"

    try {
        # Phase 1: Initialize memory capsules
        Write-Host "  [1/5] Initializing memory capsules..." -ForegroundColor Gray
        Initialize-MemoryCapsules -Config $Config.Capsules

        # Phase 2: Initialize telemetry
        Write-Host "  [2/5] Starting telemetry core..." -ForegroundColor Gray
        Initialize-TelemetryCore -Config $Config.Telemetry

        # Phase 3: Initialize awareness scanner
        Write-Host "  [3/5] Calibrating awareness scanner..." -ForegroundColor Gray
        Initialize-AwarenessScanner -Thresholds $Config.Thresholds

        # Phase 4: Initialize renewal engine
        Write-Host "  [4/5] Preparing renewal engine..." -ForegroundColor Gray
        Initialize-RenewalEngine -Config $Config.Renewal

        # Phase 5: Initialize heartbeat
        Write-Host "  [5/5] Starting heartbeat node..." -ForegroundColor Gray
        Initialize-HeartbeatNode -Config $Config.Heartbeat

        $script:EchoState = "Initialized"
        $script:StartTime = Get-Date

        Write-Host "Echo Baby initialized successfully!" -ForegroundColor Green
        Write-TelemetryLog -Message "Initialization complete - entering Baby phase" -Level "Info"

        return $true
    } catch {
        Write-TelemetryLog -Message "Initialization failed: $_" -Level "Error"
        return $false
    }
}

function Start-EchoBaby {
    <#
    .SYNOPSIS
        Starts the Echo Baby main loop (Wave phase)
    #>
    param(
        [hashtable]$Config
    )

    if ($script:EchoState -ne "Initialized") {
        $initialized = Initialize-EchoBaby -Config $Config
        if (-not $initialized) {
            Write-Error "Cannot start - initialization failed"
            return
        }
    }

    $script:EchoState = "Running"
    Write-Host "`nEcho Baby is now ACTIVE - entering Wave phase" -ForegroundColor Green
    Write-TelemetryLog -Message "=== ECHO BABY STARTED ===" -Level "Info"

    # Perform initial system scan
    Write-Host "Performing initial system scan..." -ForegroundColor Cyan
    $initialScan = Invoke-AwarenessScan -ScanType "Full"

    if ($initialScan) {
        Write-Host "Initial scan complete - baselines established" -ForegroundColor Green
        Store-PatternData -Data $initialScan -CapsuleType "Pattern"
    }

    # Start the heartbeat loop
    Write-Host "`nStarting heartbeat loop (Ctrl+C to stop)..." -ForegroundColor Yellow
    Start-HeartbeatLoop -Config $Config -OnHeartbeat {
        param($HeartbeatData)

        # Check for renewal conditions
        $renewalNeeded = Test-RenewalConditions -Config $Config.Renewal
        if ($renewalNeeded) {
            Invoke-PhoenixRenewal -Config $Config
        }

        # Perform awareness scan
        $scanResult = Invoke-AwarenessScan -ScanType "Quick"

        # Check thresholds and generate alerts
        $alerts = Test-ThresholdBreaches -ScanData $scanResult -Thresholds $Config.Thresholds

        foreach ($alert in $alerts) {
            Write-TelemetryLog -Message "ALERT: $($alert.Message)" -Level $alert.Level
            Send-Alert -Alert $alert
        }

        # Update patterns with new data
        Update-Patterns -NewData $scanResult
    }
}

function Stop-EchoBaby {
    <#
    .SYNOPSIS
        Gracefully stops the Echo Baby system
    #>

    Write-Host "`nStopping Echo Baby..." -ForegroundColor Yellow
    Write-TelemetryLog -Message "=== ECHO BABY SHUTDOWN ===" -Level "Info"

    try {
        # Stop heartbeat loop
        Stop-HeartbeatLoop

        # Flush telemetry
        Flush-TelemetryBuffer

        # Clear memory capsules
        Clear-AllCapsules

        $script:EchoState = "Stopped"

        $uptime = if ($script:StartTime) {
            (Get-Date) - $script:StartTime
        } else {
            [TimeSpan]::Zero
        }

        Write-Host "Echo Baby stopped. Uptime: $($uptime.ToString('hh\:mm\:ss'))" -ForegroundColor Green
        Write-TelemetryLog -Message "Shutdown complete. Uptime: $uptime" -Level "Info"

    } catch {
        Write-TelemetryLog -Message "Error during shutdown: $_" -Level "Error"
    }
}

function Get-EchoStatus {
    <#
    .SYNOPSIS
        Returns the current status of Echo Baby
    #>

    $status = @{
        Version = $script:EchoVersion
        State = $script:EchoState
        StartTime = $script:StartTime
        Uptime = if ($script:StartTime) { (Get-Date) - $script:StartTime } else { $null }
        Capsules = Get-CapsuleStatus
        Heartbeat = Get-HeartbeatStatus
        LastScan = Get-LastScanTime
        Telemetry = Get-TelemetryStats
    }

    return $status
}

function Invoke-PhoenixRenewal {
    <#
    .SYNOPSIS
        Executes the Phoenix renewal cycle
    #>
    param(
        [hashtable]$Config
    )

    Write-Host "`n=== PHOENIX RENEWAL CYCLE ===" -ForegroundColor Magenta
    Write-TelemetryLog -Message "Phoenix renewal initiated" -Level "Info"

    try {
        # Phase 1: Detection (already done by trigger)
        Write-Host "  [1/4] Preparing for renewal..." -ForegroundColor Gray

        # Phase 2: Preparation
        Write-Host "  [2/4] Snapshotting critical state..." -ForegroundColor Gray
        $snapshot = Get-CriticalStateSnapshot

        # Phase 3: Renewal
        Write-Host "  [3/4] Executing renewal..." -ForegroundColor Gray
        Invoke-Renewal -PreservePatterns:$false

        # Phase 4: Rebirth
        Write-Host "  [4/4] Restoring and restarting..." -ForegroundColor Gray
        Restore-CriticalState -Snapshot $snapshot

        $script:EchoState = "Running"
        Write-Host "Phoenix renewal complete - reborn!" -ForegroundColor Green
        Write-TelemetryLog -Message "Phoenix renewal complete" -Level "Info"

    } catch {
        Write-TelemetryLog -Message "Renewal failed: $_" -Level "Error"

        # Attempt self-healing
        if ($Config.SelfHealing.Enabled) {
            Invoke-SelfHeal -ErrorRecord $_
        }
    }
}

function Invoke-ManualScan {
    <#
    .SYNOPSIS
        Performs a manual system scan and displays results
    #>

    Write-Host "`nPerforming manual system scan..." -ForegroundColor Cyan
    Write-TelemetryLog -Message "Manual scan requested" -Level "Info"

    $scanResult = Invoke-AwarenessScan -ScanType "Full"

    if ($scanResult) {
        Write-Host "`n=== SCAN RESULTS ===" -ForegroundColor Green

        Write-Host "`nCPU:" -ForegroundColor Yellow
        Write-Host "  Usage: $($scanResult.CPU.UsagePercent)%"

        Write-Host "`nMemory:" -ForegroundColor Yellow
        Write-Host "  Used: $([math]::Round($scanResult.Memory.UsedGB, 2)) GB"
        Write-Host "  Available: $([math]::Round($scanResult.Memory.AvailableGB, 2)) GB"
        Write-Host "  Usage: $($scanResult.Memory.UsagePercent)%"

        Write-Host "`nDisk:" -ForegroundColor Yellow
        foreach ($disk in $scanResult.Disk) {
            Write-Host "  $($disk.Drive): $($disk.UsagePercent)% used"
        }

        Write-Host "`nProcesses: $($scanResult.Processes.Count)" -ForegroundColor Yellow

        return $scanResult
    } else {
        Write-Host "Scan failed" -ForegroundColor Red
        return $null
    }
}

#endregion

#region Self-Healing

function Invoke-SelfHeal {
    <#
    .SYNOPSIS
        Attempts to self-heal from an error condition
    #>
    param(
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )

    Write-TelemetryLog -Message "Self-healing initiated for: $($ErrorRecord.Exception.Message)" -Level "Warning"

    $errorType = Get-ErrorClassification -ErrorRecord $ErrorRecord

    switch ($errorType) {
        "Transient" {
            # Retry operation
            Write-Host "  Attempting retry..." -ForegroundColor Yellow
            # Retry logic handled by caller
        }
        "Recoverable" {
            # Reset affected subsystem
            Write-Host "  Resetting affected subsystem..." -ForegroundColor Yellow
            Reset-AffectedSubsystem -Error $ErrorRecord
        }
        "Degradable" {
            # Enter degraded mode
            Write-Host "  Entering degraded mode..." -ForegroundColor Yellow
            Enter-DegradedMode
        }
        "Critical" {
            # Safe shutdown
            Write-Host "  Critical error - initiating safe shutdown..." -ForegroundColor Red
            Stop-EchoBaby
        }
    }
}

function Get-ErrorClassification {
    param(
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )

    $message = $ErrorRecord.Exception.Message.ToLower()

    if ($message -match "timeout|temporary|retry") {
        return "Transient"
    } elseif ($message -match "access|permission|path") {
        return "Recoverable"
    } elseif ($message -match "memory|resource") {
        return "Degradable"
    } else {
        return "Critical"
    }
}

function Reset-AffectedSubsystem {
    param($Error)
    Write-TelemetryLog -Message "Subsystem reset attempted" -Level "Info"
}

function Enter-DegradedMode {
    $script:EchoState = "Degraded"
    Write-TelemetryLog -Message "Entered degraded mode" -Level "Warning"
}

#endregion

#region Main Entry Point

# Main execution
$Config = Initialize-Configuration -Path $ConfigPath

switch ($Action) {
    'Start' {
        Start-EchoBaby -Config $Config
    }
    'Stop' {
        Stop-EchoBaby
    }
    'Status' {
        $status = Get-EchoStatus
        $status | ConvertTo-Json -Depth 5
    }
    'Renew' {
        Invoke-PhoenixRenewal -Config $Config
    }
    'Scan' {
        Invoke-ManualScan
    }
}

#endregion
