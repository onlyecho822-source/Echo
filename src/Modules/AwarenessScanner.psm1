<#
.SYNOPSIS
    AwarenessScanner.psm1 - System intelligence and monitoring

.DESCRIPTION
    Performs diagnostic-only system scanning for:
    - CPU utilization
    - Memory status
    - Disk usage
    - Network statistics
    - Process enumeration

    READ-ONLY: No system modifications performed.

.NOTES
    Module: AwarenessScanner
    Version: 2.1.0
#>

# Script-level scanner state
$script:ScannerConfig = $null
$script:LastScanTime = $null
$script:Thresholds = @{}

function Initialize-AwarenessScanner {
    <#
    .SYNOPSIS
        Initializes the awareness scanner
    #>
    param(
        [hashtable]$Thresholds
    )

    $script:Thresholds = $Thresholds
    $script:ScannerConfig = @{
        Initialized = $true
        InitTime = Get-Date
    }

    Write-Verbose "Awareness scanner initialized with thresholds"
}

function Invoke-AwarenessScan {
    <#
    .SYNOPSIS
        Performs a system awareness scan
    #>
    param(
        [Parameter()]
        [ValidateSet('Quick', 'Full')]
        [string]$ScanType = 'Quick'
    )

    $script:LastScanTime = Get-Date

    $result = @{
        Timestamp = $script:LastScanTime
        ScanType = $ScanType
        CPU = Get-CPUMetrics
        Memory = Get-MemoryMetrics
        Disk = Get-DiskMetrics
        Processes = @()
        Network = @{}
    }

    if ($ScanType -eq 'Full') {
        $result.Processes = Get-ProcessMetrics
        $result.Network = Get-NetworkMetrics
    }

    return $result
}

function Get-CPUMetrics {
    <#
    .SYNOPSIS
        Gets CPU utilization metrics
    #>

    try {
        if ($IsWindows -or $env:OS -match 'Windows') {
            $cpu = Get-CimInstance -ClassName Win32_Processor -ErrorAction Stop |
                Measure-Object -Property LoadPercentage -Average

            return @{
                UsagePercent = [math]::Round($cpu.Average, 2)
                Timestamp = Get-Date
            }
        } else {
            # Linux/macOS fallback
            $loadAvg = Get-Content /proc/loadavg -ErrorAction SilentlyContinue
            if ($loadAvg) {
                $load = [double]($loadAvg -split ' ')[0]
                $cores = (Get-CimInstance -ClassName CIM_Processor -ErrorAction SilentlyContinue).NumberOfCores
                if (-not $cores) { $cores = 1 }
                $usage = [math]::Min(100, [math]::Round(($load / $cores) * 100, 2))

                return @{
                    UsagePercent = $usage
                    Timestamp = Get-Date
                }
            }
        }
    } catch {
        Write-Verbose "CPU metric collection failed: $_"
    }

    return @{
        UsagePercent = 0
        Timestamp = Get-Date
        Error = "Collection failed"
    }
}

function Get-MemoryMetrics {
    <#
    .SYNOPSIS
        Gets memory utilization metrics
    #>

    try {
        if ($IsWindows -or $env:OS -match 'Windows') {
            $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop

            $totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
            $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
            $usedGB = $totalGB - $freeGB
            $usagePercent = [math]::Round(($usedGB / $totalGB) * 100, 2)

            return @{
                TotalGB = $totalGB
                UsedGB = $usedGB
                AvailableGB = $freeGB
                UsagePercent = $usagePercent
                Timestamp = Get-Date
            }
        } else {
            # Linux fallback
            $memInfo = Get-Content /proc/meminfo -ErrorAction SilentlyContinue
            if ($memInfo) {
                $total = [double](($memInfo | Select-String "MemTotal:" | ForEach-Object { $_ -replace '[^0-9]', '' }))
                $available = [double](($memInfo | Select-String "MemAvailable:" | ForEach-Object { $_ -replace '[^0-9]', '' }))

                $totalGB = [math]::Round($total / 1MB, 2)
                $availableGB = [math]::Round($available / 1MB, 2)
                $usedGB = $totalGB - $availableGB

                return @{
                    TotalGB = $totalGB
                    UsedGB = $usedGB
                    AvailableGB = $availableGB
                    UsagePercent = [math]::Round(($usedGB / $totalGB) * 100, 2)
                    Timestamp = Get-Date
                }
            }
        }
    } catch {
        Write-Verbose "Memory metric collection failed: $_"
    }

    return @{
        TotalGB = 0
        UsedGB = 0
        AvailableGB = 0
        UsagePercent = 0
        Timestamp = Get-Date
        Error = "Collection failed"
    }
}

function Get-DiskMetrics {
    <#
    .SYNOPSIS
        Gets disk utilization metrics
    #>

    $disks = @()

    try {
        if ($IsWindows -or $env:OS -match 'Windows') {
            Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3" -ErrorAction Stop |
                ForEach-Object {
                    $totalGB = [math]::Round($_.Size / 1GB, 2)
                    $freeGB = [math]::Round($_.FreeSpace / 1GB, 2)
                    $usedGB = $totalGB - $freeGB
                    $usagePercent = if ($totalGB -gt 0) {
                        [math]::Round(($usedGB / $totalGB) * 100, 2)
                    } else { 0 }

                    $disks += @{
                        Drive = $_.DeviceID
                        TotalGB = $totalGB
                        UsedGB = $usedGB
                        FreeGB = $freeGB
                        UsagePercent = $usagePercent
                    }
                }
        } else {
            # Linux/macOS fallback
            $dfOutput = df -BG 2>/dev/null | Select-Object -Skip 1
            foreach ($line in $dfOutput) {
                $parts = $line -split '\s+'
                if ($parts.Count -ge 5) {
                    $disks += @{
                        Drive = $parts[0]
                        TotalGB = [double]($parts[1] -replace 'G', '')
                        UsedGB = [double]($parts[2] -replace 'G', '')
                        FreeGB = [double]($parts[3] -replace 'G', '')
                        UsagePercent = [double]($parts[4] -replace '%', '')
                    }
                }
            }
        }
    } catch {
        Write-Verbose "Disk metric collection failed: $_"
    }

    return $disks
}

function Get-ProcessMetrics {
    <#
    .SYNOPSIS
        Gets process information (read-only enumeration)
    #>

    try {
        $processes = Get-Process -ErrorAction Stop |
            Sort-Object WorkingSet64 -Descending |
            Select-Object -First 20 |
            ForEach-Object {
                @{
                    Name = $_.ProcessName
                    Id = $_.Id
                    CPU = [math]::Round($_.CPU, 2)
                    MemoryMB = [math]::Round($_.WorkingSet64 / 1MB, 2)
                    Threads = $_.Threads.Count
                }
            }

        return $processes
    } catch {
        Write-Verbose "Process metric collection failed: $_"
        return @()
    }
}

function Get-NetworkMetrics {
    <#
    .SYNOPSIS
        Gets network statistics (read-only)
    #>

    try {
        if ($IsWindows -or $env:OS -match 'Windows') {
            $stats = Get-NetAdapterStatistics -ErrorAction Stop |
                Select-Object -First 1

            return @{
                ReceivedBytes = $stats.ReceivedBytes
                SentBytes = $stats.SentBytes
                Timestamp = Get-Date
            }
        } else {
            # Linux fallback - read from /proc/net/dev
            return @{
                ReceivedBytes = 0
                SentBytes = 0
                Timestamp = Get-Date
                Note = "Linux metrics placeholder"
            }
        }
    } catch {
        Write-Verbose "Network metric collection failed: $_"
        return @{
            ReceivedBytes = 0
            SentBytes = 0
            Timestamp = Get-Date
            Error = "Collection failed"
        }
    }
}

function Test-ThresholdBreaches {
    <#
    .SYNOPSIS
        Tests scan data against configured thresholds
    #>
    param(
        [Parameter(Mandatory)]
        [hashtable]$ScanData,

        [Parameter(Mandatory)]
        [hashtable]$Thresholds
    )

    $alerts = @()

    # CPU checks
    if ($ScanData.CPU.UsagePercent -ge $Thresholds.CPUCritical) {
        $alerts += @{
            Type = "CPU"
            Level = "Critical"
            Message = "CPU usage critical: $($ScanData.CPU.UsagePercent)%"
            Threshold = $Thresholds.CPUCritical
            CurrentValue = $ScanData.CPU.UsagePercent
        }
    } elseif ($ScanData.CPU.UsagePercent -ge $Thresholds.CPUWarning) {
        $alerts += @{
            Type = "CPU"
            Level = "Warning"
            Message = "CPU usage high: $($ScanData.CPU.UsagePercent)%"
            Threshold = $Thresholds.CPUWarning
            CurrentValue = $ScanData.CPU.UsagePercent
        }
    }

    # Memory checks
    if ($ScanData.Memory.UsagePercent -ge $Thresholds.MemoryCritical) {
        $alerts += @{
            Type = "Memory"
            Level = "Critical"
            Message = "Memory usage critical: $($ScanData.Memory.UsagePercent)%"
            Threshold = $Thresholds.MemoryCritical
            CurrentValue = $ScanData.Memory.UsagePercent
        }
    } elseif ($ScanData.Memory.UsagePercent -ge $Thresholds.MemoryWarning) {
        $alerts += @{
            Type = "Memory"
            Level = "Warning"
            Message = "Memory usage high: $($ScanData.Memory.UsagePercent)%"
            Threshold = $Thresholds.MemoryWarning
            CurrentValue = $ScanData.Memory.UsagePercent
        }
    }

    # Disk checks
    foreach ($disk in $ScanData.Disk) {
        if ($disk.UsagePercent -ge $Thresholds.DiskCritical) {
            $alerts += @{
                Type = "Disk"
                Level = "Critical"
                Message = "Disk $($disk.Drive) usage critical: $($disk.UsagePercent)%"
                Threshold = $Thresholds.DiskCritical
                CurrentValue = $disk.UsagePercent
            }
        } elseif ($disk.UsagePercent -ge $Thresholds.DiskWarning) {
            $alerts += @{
                Type = "Disk"
                Level = "Warning"
                Message = "Disk $($disk.Drive) usage high: $($disk.UsagePercent)%"
                Threshold = $Thresholds.DiskWarning
                CurrentValue = $disk.UsagePercent
            }
        }
    }

    return $alerts
}

function Get-LastScanTime {
    <#
    .SYNOPSIS
        Returns the timestamp of the last scan
    #>

    return $script:LastScanTime
}

# Export module members
Export-ModuleMember -Function @(
    'Initialize-AwarenessScanner',
    'Invoke-AwarenessScan',
    'Get-CPUMetrics',
    'Get-MemoryMetrics',
    'Get-DiskMetrics',
    'Get-ProcessMetrics',
    'Get-NetworkMetrics',
    'Test-ThresholdBreaches',
    'Get-LastScanTime'
)
