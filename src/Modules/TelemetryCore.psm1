<#
.SYNOPSIS
    TelemetryCore.psm1 - Logging and metric collection

.DESCRIPTION
    Provides transparent telemetry, logging, and metric collection.
    All operations are auditable and stored locally.

.NOTES
    Module: TelemetryCore
    Version: 2.1.0
#>

# Script-level telemetry state
$script:TelemetryConfig = $null
$script:TelemetryBuffer = [System.Collections.ArrayList]::new()
$script:TelemetryStats = @{
    MessagesLogged = 0
    ErrorsLogged = 0
    WarningsLogged = 0
    StartTime = $null
}

function Initialize-TelemetryCore {
    <#
    .SYNOPSIS
        Initializes the telemetry subsystem
    #>
    param(
        [hashtable]$Config
    )

    $script:TelemetryConfig = $Config
    $script:TelemetryStats.StartTime = Get-Date

    # Ensure log directory exists
    if ($Config.Enabled -and $Config.LogPath) {
        if (-not (Test-Path $Config.LogPath)) {
            New-Item -Path $Config.LogPath -ItemType Directory -Force | Out-Null
        }
    }

    Write-Verbose "Telemetry core initialized"
}

function Write-TelemetryLog {
    <#
    .SYNOPSIS
        Writes a log entry to telemetry
    #>
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [Parameter()]
        [ValidateSet('Debug', 'Info', 'Warning', 'Error', 'Critical')]
        [string]$Level = 'Info',

        [Parameter()]
        [hashtable]$Data
    )

    $entry = @{
        Timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss.fff')
        TimestampUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss.fff')
        Level = $Level
        Message = $Message
        Data = $Data
    }

    # Update stats
    $script:TelemetryStats.MessagesLogged++
    if ($Level -eq 'Error' -or $Level -eq 'Critical') {
        $script:TelemetryStats.ErrorsLogged++
    } elseif ($Level -eq 'Warning') {
        $script:TelemetryStats.WarningsLogged++
    }

    # Add to buffer
    [void]$script:TelemetryBuffer.Add($entry)

    # Write to log file if enabled
    if ($script:TelemetryConfig.Enabled) {
        Write-ToLogFile -Entry $entry
    }

    # Output to console for important messages
    if ($Level -in @('Warning', 'Error', 'Critical')) {
        $color = switch ($Level) {
            'Warning' { 'Yellow' }
            'Error' { 'Red' }
            'Critical' { 'Magenta' }
        }
        Write-Host "[$Level] $Message" -ForegroundColor $color
    }
}

function Write-ToLogFile {
    <#
    .SYNOPSIS
        Writes entry to log file
    #>
    param(
        [hashtable]$Entry
    )

    if (-not $script:TelemetryConfig.LogPath) { return }

    $logFile = Join-Path $script:TelemetryConfig.LogPath "echo-baby-$(Get-Date -Format 'yyyy-MM-dd').log"

    $line = "[$($Entry.TimestampUtc)] [$($Entry.Level)] $($Entry.Message)"
    if ($Entry.Data) {
        $line += " | Data: $($Entry.Data | ConvertTo-Json -Compress)"
    }

    try {
        Add-Content -Path $logFile -Value $line -ErrorAction Stop
    } catch {
        # Fail silently - don't break system for logging issues
    }
}

function Get-TelemetryStats {
    <#
    .SYNOPSIS
        Returns telemetry statistics
    #>

    return @{
        MessagesLogged = $script:TelemetryStats.MessagesLogged
        ErrorsLogged = $script:TelemetryStats.ErrorsLogged
        WarningsLogged = $script:TelemetryStats.WarningsLogged
        StartTime = $script:TelemetryStats.StartTime
        BufferSize = $script:TelemetryBuffer.Count
        Enabled = $script:TelemetryConfig.Enabled
    }
}

function Get-TelemetryBuffer {
    <#
    .SYNOPSIS
        Returns the telemetry buffer contents
    #>
    param(
        [int]$Last = 100,
        [string]$Level
    )

    $result = $script:TelemetryBuffer

    if ($Level) {
        $result = $result | Where-Object { $_.Level -eq $Level }
    }

    if ($Last -gt 0) {
        $result = $result | Select-Object -Last $Last
    }

    return $result
}

function Flush-TelemetryBuffer {
    <#
    .SYNOPSIS
        Flushes the telemetry buffer
    #>

    # Write any remaining buffered entries
    foreach ($entry in $script:TelemetryBuffer) {
        Write-ToLogFile -Entry $entry
    }

    $script:TelemetryBuffer.Clear()
    Write-Verbose "Telemetry buffer flushed"
}

function Clear-OldLogs {
    <#
    .SYNOPSIS
        Removes logs older than retention period
    #>

    if (-not $script:TelemetryConfig.LogPath) { return }

    $cutoffDate = (Get-Date).AddDays(-$script:TelemetryConfig.RetentionDays)

    Get-ChildItem -Path $script:TelemetryConfig.LogPath -Filter "echo-baby-*.log" |
        Where-Object { $_.LastWriteTime -lt $cutoffDate } |
        ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Verbose "Removed old log: $($_.Name)"
        }
}

function Send-Alert {
    <#
    .SYNOPSIS
        Sends an alert through the telemetry system
    #>
    param(
        [Parameter(Mandatory)]
        [hashtable]$Alert
    )

    # Log the alert
    Write-TelemetryLog -Message "ALERT: $($Alert.Message)" -Level $Alert.Level -Data @{
        AlertType = $Alert.Type
        Threshold = $Alert.Threshold
        CurrentValue = $Alert.CurrentValue
    }

    # Store in alert capsule
    Store-PatternData -Data $Alert -CapsuleType 'Alert'

    # Could be extended to send notifications (email, webhook, etc.)
}

function Get-MetricSnapshot {
    <#
    .SYNOPSIS
        Creates a snapshot of current metrics
    #>
    param(
        [hashtable]$ScanData
    )

    if (-not $ScanData) { return $null }

    return @{
        Timestamp = Get-Date
        CPU = @{
            UsagePercent = $ScanData.CPU.UsagePercent
        }
        Memory = @{
            UsagePercent = $ScanData.Memory.UsagePercent
            UsedGB = $ScanData.Memory.UsedGB
            AvailableGB = $ScanData.Memory.AvailableGB
        }
        Disk = $ScanData.Disk | ForEach-Object {
            @{
                Drive = $_.Drive
                UsagePercent = $_.UsagePercent
            }
        }
        ProcessCount = $ScanData.Processes.Count
    }
}

function Write-MetricToTelemetry {
    <#
    .SYNOPSIS
        Records metrics to telemetry
    #>
    param(
        [hashtable]$Metrics
    )

    Write-TelemetryLog -Message "Metric snapshot recorded" -Level "Debug" -Data $Metrics
}

# Export module members
Export-ModuleMember -Function @(
    'Initialize-TelemetryCore',
    'Write-TelemetryLog',
    'Get-TelemetryStats',
    'Get-TelemetryBuffer',
    'Flush-TelemetryBuffer',
    'Clear-OldLogs',
    'Send-Alert',
    'Get-MetricSnapshot',
    'Write-MetricToTelemetry'
)
