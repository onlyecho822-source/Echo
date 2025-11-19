<#
.SYNOPSIS
    HeartbeatNode.psm1 - Pulse generator and health monitoring

.DESCRIPTION
    Manages the heartbeat loop:
    - Periodic health checks
    - Pulse generation
    - Threshold monitoring
    - Alert dispatch

.NOTES
    Module: HeartbeatNode
    Version: 2.1.0
#>

# Script-level heartbeat state
$script:HeartbeatConfig = $null
$script:HeartbeatRunning = $false
$script:HeartbeatCount = 0
$script:LastHeartbeatTime = $null
$script:HeartbeatStats = @{
    TotalBeats = 0
    SuccessfulBeats = 0
    FailedBeats = 0
    AverageLatencyMs = 0
}

function Initialize-HeartbeatNode {
    <#
    .SYNOPSIS
        Initializes the heartbeat node
    #>
    param(
        [hashtable]$Config
    )

    $script:HeartbeatConfig = $Config
    $script:HeartbeatRunning = $false
    $script:HeartbeatCount = 0
    $script:HeartbeatStats = @{
        TotalBeats = 0
        SuccessfulBeats = 0
        FailedBeats = 0
        AverageLatencyMs = 0
    }

    Write-Verbose "Heartbeat node initialized (interval: $($Config.IntervalSeconds)s)"
}

function Start-HeartbeatLoop {
    <#
    .SYNOPSIS
        Starts the main heartbeat loop
    #>
    param(
        [Parameter(Mandatory)]
        [hashtable]$Config,

        [Parameter(Mandatory)]
        [scriptblock]$OnHeartbeat
    )

    $script:HeartbeatRunning = $true
    $intervalMs = $script:HeartbeatConfig.IntervalSeconds * 1000

    Write-TelemetryLog -Message "Heartbeat loop started (interval: $($script:HeartbeatConfig.IntervalSeconds)s)" -Level "Info"

    try {
        while ($script:HeartbeatRunning) {
            $beatStart = Get-Date

            try {
                # Execute heartbeat
                $heartbeatData = Invoke-Heartbeat

                # Call the callback with heartbeat data
                & $OnHeartbeat -HeartbeatData $heartbeatData

                # Update stats
                $script:HeartbeatStats.SuccessfulBeats++

                # Increment renewal cycle counter
                Increment-CycleCounter

            } catch {
                $script:HeartbeatStats.FailedBeats++
                Write-TelemetryLog -Message "Heartbeat failed: $_" -Level "Error"

                # Attempt retry if configured
                if ($script:HeartbeatConfig.MaxRetries -gt 0) {
                    Invoke-HeartbeatRetry -MaxRetries $script:HeartbeatConfig.MaxRetries
                }
            }

            $beatEnd = Get-Date
            $latencyMs = ($beatEnd - $beatStart).TotalMilliseconds

            # Update average latency
            Update-LatencyStats -LatencyMs $latencyMs

            # Sleep until next beat
            $sleepMs = [math]::Max(0, $intervalMs - $latencyMs)
            if ($sleepMs -gt 0 -and $script:HeartbeatRunning) {
                Start-Sleep -Milliseconds $sleepMs
            }
        }
    } finally {
        $script:HeartbeatRunning = $false
        Write-TelemetryLog -Message "Heartbeat loop stopped" -Level "Info"
    }
}

function Invoke-Heartbeat {
    <#
    .SYNOPSIS
        Executes a single heartbeat pulse
    #>

    $script:HeartbeatCount++
    $script:HeartbeatStats.TotalBeats++
    $script:LastHeartbeatTime = Get-Date

    $heartbeatData = @{
        BeatNumber = $script:HeartbeatCount
        Timestamp = $script:LastHeartbeatTime
        Status = "OK"
    }

    # Quick health check
    $health = Test-SystemHealth

    if (-not $health.Healthy) {
        $heartbeatData.Status = "DEGRADED"
        $heartbeatData.Issues = $health.Issues
    }

    return $heartbeatData
}

function Invoke-HeartbeatRetry {
    <#
    .SYNOPSIS
        Retries a failed heartbeat
    #>
    param(
        [int]$MaxRetries
    )

    for ($i = 1; $i -le $MaxRetries; $i++) {
        Write-Verbose "Heartbeat retry attempt $i of $MaxRetries"
        Start-Sleep -Milliseconds ($script:HeartbeatConfig.TimeoutMs / 2)

        try {
            $heartbeatData = Invoke-Heartbeat
            Write-TelemetryLog -Message "Heartbeat retry $i successful" -Level "Info"
            return $heartbeatData
        } catch {
            if ($i -eq $MaxRetries) {
                Write-TelemetryLog -Message "All heartbeat retries failed" -Level "Error"
            }
        }
    }

    return $null
}

function Stop-HeartbeatLoop {
    <#
    .SYNOPSIS
        Stops the heartbeat loop gracefully
    #>

    $script:HeartbeatRunning = $false
    Write-Verbose "Heartbeat stop requested"
}

function Test-SystemHealth {
    <#
    .SYNOPSIS
        Performs a quick system health check
    #>

    $health = @{
        Healthy = $true
        Issues = @()
    }

    try {
        # Quick CPU check
        $cpu = Get-CPUMetrics
        if ($cpu.UsagePercent -gt 95) {
            $health.Healthy = $false
            $health.Issues += "CPU usage critical: $($cpu.UsagePercent)%"
        }

        # Quick memory check
        $memory = Get-MemoryMetrics
        if ($memory.UsagePercent -gt 95) {
            $health.Healthy = $false
            $health.Issues += "Memory usage critical: $($memory.UsagePercent)%"
        }

    } catch {
        $health.Healthy = $false
        $health.Issues += "Health check failed: $_"
    }

    return $health
}

function Get-HeartbeatStatus {
    <#
    .SYNOPSIS
        Returns current heartbeat status
    #>

    return @{
        Running = $script:HeartbeatRunning
        TotalBeats = $script:HeartbeatStats.TotalBeats
        SuccessfulBeats = $script:HeartbeatStats.SuccessfulBeats
        FailedBeats = $script:HeartbeatStats.FailedBeats
        AverageLatencyMs = [math]::Round($script:HeartbeatStats.AverageLatencyMs, 2)
        LastHeartbeat = $script:LastHeartbeatTime
        Config = $script:HeartbeatConfig
    }
}

function Update-LatencyStats {
    <#
    .SYNOPSIS
        Updates the running average latency
    #>
    param(
        [double]$LatencyMs
    )

    $total = $script:HeartbeatStats.TotalBeats
    if ($total -le 1) {
        $script:HeartbeatStats.AverageLatencyMs = $LatencyMs
    } else {
        # Running average
        $currentAvg = $script:HeartbeatStats.AverageLatencyMs
        $script:HeartbeatStats.AverageLatencyMs = $currentAvg + (($LatencyMs - $currentAvg) / $total)
    }
}

function Send-HeartbeatAlert {
    <#
    .SYNOPSIS
        Sends an alert related to heartbeat issues
    #>
    param(
        [string]$Message,
        [string]$Severity = "Warning"
    )

    $alert = @{
        Type = "Heartbeat"
        Level = $Severity
        Message = $Message
        Timestamp = Get-Date
        HeartbeatCount = $script:HeartbeatCount
    }

    Send-Alert -Alert $alert
}

function Get-HeartbeatMetrics {
    <#
    .SYNOPSIS
        Returns detailed heartbeat metrics for telemetry
    #>

    $status = Get-HeartbeatStatus

    return @{
        Timestamp = Get-Date
        BeatCount = $status.TotalBeats
        SuccessRate = if ($status.TotalBeats -gt 0) {
            [math]::Round(($status.SuccessfulBeats / $status.TotalBeats) * 100, 2)
        } else { 100 }
        AverageLatencyMs = $status.AverageLatencyMs
        Running = $status.Running
    }
}

# Export module members
Export-ModuleMember -Function @(
    'Initialize-HeartbeatNode',
    'Start-HeartbeatLoop',
    'Stop-HeartbeatLoop',
    'Invoke-Heartbeat',
    'Test-SystemHealth',
    'Get-HeartbeatStatus',
    'Send-HeartbeatAlert',
    'Get-HeartbeatMetrics'
)
