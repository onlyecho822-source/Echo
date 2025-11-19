<#
.SYNOPSIS
    RenewalEngine.psm1 - Phoenix renewal cycle management

.DESCRIPTION
    Manages the Phoenix-style renewal cycles:
    - State reset and cleanup
    - Cache clearing
    - Pattern pruning
    - Rebirth initialization

.NOTES
    Module: RenewalEngine
    Version: 2.1.0
#>

# Script-level renewal state
$script:RenewalConfig = $null
$script:LastRenewalTime = $null
$script:RenewalCount = 0
$script:CyclesSinceRenewal = 0

function Initialize-RenewalEngine {
    <#
    .SYNOPSIS
        Initializes the renewal engine
    #>
    param(
        [hashtable]$Config
    )

    $script:RenewalConfig = $Config
    $script:LastRenewalTime = Get-Date
    $script:RenewalCount = 0
    $script:CyclesSinceRenewal = 0

    Write-Verbose "Renewal engine initialized"
}

function Test-RenewalConditions {
    <#
    .SYNOPSIS
        Tests if renewal is needed based on configured conditions
    #>
    param(
        [hashtable]$Config
    )

    # Check scheduled interval
    $hoursSinceRenewal = ((Get-Date) - $script:LastRenewalTime).TotalHours
    if ($hoursSinceRenewal -ge $Config.ScheduledIntervalHours) {
        Write-Verbose "Renewal triggered: scheduled interval exceeded"
        return $true
    }

    # Check memory pressure
    $capsuleStatus = Get-CapsuleStatus
    foreach ($capsule in $capsuleStatus.Values) {
        if ($capsule.SizeMB -gt 0) {
            $capsuleUsage = ($capsule.SizeMB / 10) * 100  # Approximate check
            if ($capsuleUsage -ge $Config.MemoryPressurePercent) {
                Write-Verbose "Renewal triggered: memory pressure"
                return $true
            }
        }
    }

    # Check pattern staleness
    if ($script:CyclesSinceRenewal -ge $Config.StalePatternCycles) {
        Write-Verbose "Renewal triggered: pattern staleness"
        return $true
    }

    return $false
}

function Invoke-Renewal {
    <#
    .SYNOPSIS
        Executes the renewal process
    #>
    param(
        [switch]$PreservePatterns,
        [switch]$PreserveThresholds
    )

    Write-TelemetryLog -Message "Renewal process starting" -Level "Info"

    try {
        # Clear capsules based on preservation settings
        if (-not $PreservePatterns) {
            Clear-Capsule -CapsuleType 'Pattern'
        }

        Clear-Capsule -CapsuleType 'Event'
        Clear-Capsule -CapsuleType 'Metric'
        Clear-Capsule -CapsuleType 'Alert'

        if (-not $PreserveThresholds) {
            Clear-Capsule -CapsuleType 'Threshold'
        }

        # Reset counters
        $script:LastRenewalTime = Get-Date
        $script:RenewalCount++
        $script:CyclesSinceRenewal = 0

        # Clear old logs
        Clear-OldLogs

        Write-TelemetryLog -Message "Renewal complete (count: $($script:RenewalCount))" -Level "Info"

        return $true
    } catch {
        Write-TelemetryLog -Message "Renewal failed: $_" -Level "Error"
        return $false
    }
}

function Invoke-PartialRenewal {
    <#
    .SYNOPSIS
        Performs a partial renewal (clears non-critical data only)
    #>

    Write-TelemetryLog -Message "Partial renewal starting" -Level "Info"

    try {
        # Only clear event and metric capsules
        Clear-Capsule -CapsuleType 'Event'
        Clear-Capsule -CapsuleType 'Metric'

        # Prune pattern capsule instead of clearing
        $patternSize = Get-CapsuleSizeMB -CapsuleType 'Pattern'
        if ($patternSize -gt 5) {
            # Prune to 50% capacity
            # This would require the Prune-Capsule function to be exported
        }

        $script:CyclesSinceRenewal = [math]::Floor($script:CyclesSinceRenewal / 2)

        Write-TelemetryLog -Message "Partial renewal complete" -Level "Info"

        return $true
    } catch {
        Write-TelemetryLog -Message "Partial renewal failed: $_" -Level "Error"
        return $false
    }
}

function Get-RenewalStatus {
    <#
    .SYNOPSIS
        Returns the current renewal engine status
    #>

    return @{
        LastRenewalTime = $script:LastRenewalTime
        RenewalCount = $script:RenewalCount
        CyclesSinceRenewal = $script:CyclesSinceRenewal
        HoursSinceRenewal = if ($script:LastRenewalTime) {
            [math]::Round(((Get-Date) - $script:LastRenewalTime).TotalHours, 2)
        } else { 0 }
        Config = $script:RenewalConfig
    }
}

function Increment-CycleCounter {
    <#
    .SYNOPSIS
        Increments the cycle counter (called each heartbeat)
    #>

    $script:CyclesSinceRenewal++
}

function Reset-CycleCounter {
    <#
    .SYNOPSIS
        Resets the cycle counter
    #>

    $script:CyclesSinceRenewal = 0
}

function Get-RenewalRecommendation {
    <#
    .SYNOPSIS
        Returns a recommendation on whether renewal should occur
    #>
    param(
        [hashtable]$Config
    )

    $status = Get-RenewalStatus
    $recommendations = @()

    # Check time-based
    if ($status.HoursSinceRenewal -ge ($Config.ScheduledIntervalHours * 0.9)) {
        $recommendations += @{
            Reason = "Approaching scheduled renewal interval"
            Urgency = "Medium"
            TimeUntilRequired = [math]::Round(($Config.ScheduledIntervalHours - $status.HoursSinceRenewal), 2)
        }
    }

    # Check cycle-based
    $cycleProgress = $status.CyclesSinceRenewal / $Config.StalePatternCycles
    if ($cycleProgress -ge 0.8) {
        $recommendations += @{
            Reason = "Pattern data becoming stale"
            Urgency = "Medium"
            CyclesRemaining = $Config.StalePatternCycles - $status.CyclesSinceRenewal
        }
    }

    return @{
        ShouldRenew = $recommendations.Count -gt 0
        Recommendations = $recommendations
        Status = $status
    }
}

# Export module members
Export-ModuleMember -Function @(
    'Initialize-RenewalEngine',
    'Test-RenewalConditions',
    'Invoke-Renewal',
    'Invoke-PartialRenewal',
    'Get-RenewalStatus',
    'Increment-CycleCounter',
    'Reset-CycleCounter',
    'Get-RenewalRecommendation'
)
