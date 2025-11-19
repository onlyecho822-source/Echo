<#
.SYNOPSIS
    MemoryCapsule.psm1 - RAM-only volatile memory management

.DESCRIPTION
    Provides RAM-only capsule storage for Echo Baby system.
    All data is volatile and cleared on session end.

.NOTES
    Module: MemoryCapsule
    Version: 2.1.0
#>

# Script-level capsule storage (RAM-only)
$script:Capsules = @{
    Pattern = @{
        Data = @{}
        MaxSizeMB = 10
        Created = $null
    }
    Event = @{
        Data = [System.Collections.ArrayList]::new()
        MaxSizeMB = 5
        RetentionMinutes = 5
        Created = $null
    }
    Threshold = @{
        Data = @{}
        Created = $null
    }
    Metric = @{
        Data = @{}
        Created = $null
    }
    Alert = @{
        Data = [System.Collections.ArrayList]::new()
        MaxSizeKB = 512
        Created = $null
    }
}

$script:CapsuleConfig = $null

function Initialize-MemoryCapsules {
    <#
    .SYNOPSIS
        Initializes all memory capsules
    #>
    param(
        [hashtable]$Config
    )

    $script:CapsuleConfig = $Config
    $now = Get-Date

    # Initialize each capsule
    $script:Capsules.Pattern.Created = $now
    $script:Capsules.Pattern.MaxSizeMB = $Config.MaxPatternSizeMB

    $script:Capsules.Event.Created = $now
    $script:Capsules.Event.MaxSizeMB = $Config.MaxEventSizeMB
    $script:Capsules.Event.RetentionMinutes = $Config.EventRetentionMinutes

    $script:Capsules.Threshold.Created = $now
    $script:Capsules.Metric.Created = $now
    $script:Capsules.Alert.Created = $now

    Write-Verbose "Memory capsules initialized"
}

function Store-PatternData {
    <#
    .SYNOPSIS
        Stores pattern data in the Pattern capsule
    #>
    param(
        [Parameter(Mandatory)]
        $Data,

        [Parameter(Mandatory)]
        [ValidateSet('Pattern', 'Event', 'Threshold', 'Metric', 'Alert')]
        [string]$CapsuleType
    )

    $capsule = $script:Capsules[$CapsuleType]

    switch ($CapsuleType) {
        'Pattern' {
            $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
            $capsule.Data[$timestamp] = $Data

            # Prune if over size limit
            $currentSize = Get-CapsuleSizeMB -CapsuleType 'Pattern'
            if ($currentSize -gt $capsule.MaxSizeMB) {
                Prune-Capsule -CapsuleType 'Pattern' -TargetSizeMB ($capsule.MaxSizeMB * 0.8)
            }
        }
        'Event' {
            [void]$capsule.Data.Add(@{
                Timestamp = Get-Date
                Data = $Data
            })

            # Prune old events
            Prune-EventCapsule
        }
        'Threshold' {
            foreach ($key in $Data.Keys) {
                $capsule.Data[$key] = $Data[$key]
            }
        }
        'Metric' {
            $capsule.Data = $Data
            $capsule.LastUpdated = Get-Date
        }
        'Alert' {
            [void]$capsule.Data.Add(@{
                Timestamp = Get-Date
                Alert = $Data
            })
        }
    }
}

function Get-CapsuleData {
    <#
    .SYNOPSIS
        Retrieves data from a capsule
    #>
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Pattern', 'Event', 'Threshold', 'Metric', 'Alert')]
        [string]$CapsuleType,

        [string]$Key
    )

    $capsule = $script:Capsules[$CapsuleType]

    if ($Key) {
        return $capsule.Data[$Key]
    }

    return $capsule.Data
}

function Get-CapsuleStatus {
    <#
    .SYNOPSIS
        Returns status of all capsules
    #>

    $status = @{}

    foreach ($capsuleType in $script:Capsules.Keys) {
        $capsule = $script:Capsules[$capsuleType]

        $status[$capsuleType] = @{
            Created = $capsule.Created
            ItemCount = if ($capsule.Data -is [hashtable]) {
                $capsule.Data.Count
            } else {
                $capsule.Data.Count
            }
            SizeMB = Get-CapsuleSizeMB -CapsuleType $capsuleType
        }
    }

    return $status
}

function Get-CapsuleSizeMB {
    <#
    .SYNOPSIS
        Estimates capsule size in MB
    #>
    param(
        [string]$CapsuleType
    )

    $capsule = $script:Capsules[$CapsuleType]
    $json = $capsule.Data | ConvertTo-Json -Depth 10 -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetByteCount($json)

    return [math]::Round($bytes / 1MB, 2)
}

function Prune-Capsule {
    <#
    .SYNOPSIS
        Prunes capsule data to target size
    #>
    param(
        [string]$CapsuleType,
        [double]$TargetSizeMB
    )

    $capsule = $script:Capsules[$CapsuleType]

    if ($capsule.Data -is [hashtable]) {
        # Remove oldest entries
        $sortedKeys = $capsule.Data.Keys | Sort-Object

        while ((Get-CapsuleSizeMB -CapsuleType $CapsuleType) -gt $TargetSizeMB -and $sortedKeys.Count -gt 0) {
            $oldestKey = $sortedKeys[0]
            $capsule.Data.Remove($oldestKey)
            $sortedKeys = $sortedKeys | Select-Object -Skip 1
        }
    }

    Write-Verbose "Pruned $CapsuleType capsule to ~$TargetSizeMB MB"
}

function Prune-EventCapsule {
    <#
    .SYNOPSIS
        Removes events older than retention period
    #>

    $capsule = $script:Capsules.Event
    $cutoff = (Get-Date).AddMinutes(-$capsule.RetentionMinutes)

    $toRemove = @()
    for ($i = 0; $i -lt $capsule.Data.Count; $i++) {
        if ($capsule.Data[$i].Timestamp -lt $cutoff) {
            $toRemove += $i
        }
    }

    # Remove in reverse order to maintain indices
    for ($i = $toRemove.Count - 1; $i -ge 0; $i--) {
        $capsule.Data.RemoveAt($toRemove[$i])
    }
}

function Clear-Capsule {
    <#
    .SYNOPSIS
        Clears a specific capsule
    #>
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Pattern', 'Event', 'Threshold', 'Metric', 'Alert')]
        [string]$CapsuleType
    )

    $capsule = $script:Capsules[$CapsuleType]

    if ($capsule.Data -is [hashtable]) {
        $capsule.Data = @{}
    } else {
        $capsule.Data.Clear()
    }

    Write-Verbose "Cleared $CapsuleType capsule"
}

function Clear-AllCapsules {
    <#
    .SYNOPSIS
        Clears all capsules (used during shutdown/renewal)
    #>

    foreach ($capsuleType in $script:Capsules.Keys) {
        Clear-Capsule -CapsuleType $capsuleType
    }

    Write-Verbose "All capsules cleared"
}

function Get-CriticalStateSnapshot {
    <#
    .SYNOPSIS
        Creates a snapshot of critical state for renewal
    #>

    return @{
        Timestamp = Get-Date
        Thresholds = $script:Capsules.Threshold.Data.Clone()
        RecentPatterns = @{}  # Optionally preserve recent patterns
    }
}

function Restore-CriticalState {
    <#
    .SYNOPSIS
        Restores critical state after renewal
    #>
    param(
        [hashtable]$Snapshot
    )

    if ($Snapshot.Thresholds) {
        $script:Capsules.Threshold.Data = $Snapshot.Thresholds
    }

    Write-Verbose "Critical state restored from snapshot"
}

function Update-Patterns {
    <#
    .SYNOPSIS
        Updates pattern data with new observations
    #>
    param(
        $NewData
    )

    if (-not $NewData) { return }

    $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $script:Capsules.Pattern.Data[$timestamp] = $NewData

    # Maintain size limits
    $currentSize = Get-CapsuleSizeMB -CapsuleType 'Pattern'
    $maxSize = $script:Capsules.Pattern.MaxSizeMB

    if ($currentSize -gt $maxSize) {
        Prune-Capsule -CapsuleType 'Pattern' -TargetSizeMB ($maxSize * 0.8)
    }
}

# Export module members
Export-ModuleMember -Function @(
    'Initialize-MemoryCapsules',
    'Store-PatternData',
    'Get-CapsuleData',
    'Get-CapsuleStatus',
    'Get-CapsuleSizeMB',
    'Clear-Capsule',
    'Clear-AllCapsules',
    'Get-CriticalStateSnapshot',
    'Restore-CriticalState',
    'Update-Patterns'
)
