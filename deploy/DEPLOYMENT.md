# Echo Baby Rebirth v2.1 — Deployment Checklist

## Team D Deliverable: Deployment & Execution Flow

---

## Pre-Deployment Requirements

### System Requirements

- [ ] PowerShell 7.0 or higher installed
- [ ] Windows 10/11 or Windows Server 2016+
- [ ] Minimum 4GB RAM available
- [ ] 100MB free disk space for logs
- [ ] Administrator privileges (for full system metrics)

### Verify PowerShell Version

```powershell
$PSVersionTable.PSVersion
# Should show 7.0.0 or higher
```

### Directory Structure Verification

```
Echo/
├── src/
│   ├── EchoBabyRebirth.ps1      # Main entry point
│   └── Modules/
│       ├── MemoryCapsule.psm1    # RAM-only storage
│       ├── TelemetryCore.psm1    # Logging & metrics
│       ├── AwarenessScanner.psm1 # System monitoring
│       ├── RenewalEngine.psm1    # Phoenix cycles
│       └── HeartbeatNode.psm1    # Health monitoring
├── docs/
│   ├── ARCHITECTURE.md
│   └── SAFETY.md
├── deploy/
│   └── DEPLOYMENT.md (this file)
├── logs/                         # Created at runtime
└── tests/
```

---

## Deployment Steps

### Step 1: Clone/Download Repository

```powershell
git clone <repository-url>
cd Echo
```

### Step 2: Verify Module Integrity

```powershell
# Test that all modules can be loaded
$modules = @(
    "MemoryCapsule",
    "TelemetryCore",
    "AwarenessScanner",
    "RenewalEngine",
    "HeartbeatNode"
)

foreach ($module in $modules) {
    $path = "./src/Modules/$module.psm1"
    if (Test-Path $path) {
        Write-Host "[OK] $module" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $module" -ForegroundColor Red
    }
}
```

### Step 3: Set Execution Policy (if needed)

```powershell
# Check current policy
Get-ExecutionPolicy

# If needed, set to allow local scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Create Configuration (Optional)

Create a custom configuration file at `config/echo-config.json`:

```json
{
    "Heartbeat": {
        "IntervalSeconds": 30,
        "TimeoutMs": 5000,
        "MaxRetries": 3
    },
    "Capsules": {
        "MaxPatternSizeMB": 10,
        "MaxEventSizeMB": 5,
        "EventRetentionMinutes": 5
    },
    "Thresholds": {
        "CPUWarning": 70,
        "CPUCritical": 90,
        "MemoryWarning": 75,
        "MemoryCritical": 90,
        "DiskWarning": 80,
        "DiskCritical": 95
    },
    "Renewal": {
        "ScheduledIntervalHours": 6,
        "MemoryPressurePercent": 80,
        "StalePatternCycles": 1000
    },
    "Telemetry": {
        "Enabled": true,
        "LogPath": "./logs",
        "RetentionDays": 7
    }
}
```

---

## Execution Flow

### First Run: Initialization

```powershell
# Navigate to source directory
cd src

# Start Echo Baby with default configuration
./EchoBabyRebirth.ps1 -Action Start

# Or with custom configuration
./EchoBabyRebirth.ps1 -Action Start -ConfigPath "../config/echo-config.json"
```

### Expected Initialization Output

```
Initializing Echo Baby Rebirth v2.1.0...
  [1/5] Initializing memory capsules...
  [2/5] Starting telemetry core...
  [3/5] Calibrating awareness scanner...
  [4/5] Preparing renewal engine...
  [5/5] Starting heartbeat node...
Echo Baby initialized successfully!

Echo Baby is now ACTIVE - entering Wave phase
Performing initial system scan...
Initial scan complete - baselines established

Starting heartbeat loop (Ctrl+C to stop)...
```

### Available Actions

| Action | Command | Description |
|--------|---------|-------------|
| Start | `./EchoBabyRebirth.ps1 -Action Start` | Start the monitoring system |
| Stop | `./EchoBabyRebirth.ps1 -Action Stop` | Gracefully stop the system |
| Status | `./EchoBabyRebirth.ps1 -Action Status` | Get current system status |
| Renew | `./EchoBabyRebirth.ps1 -Action Renew` | Trigger Phoenix renewal cycle |
| Scan | `./EchoBabyRebirth.ps1 -Action Scan` | Perform manual system scan |

---

## Post-Deployment Verification

### Step 5: Verify First Scan

After starting, verify the initial scan completed:

```powershell
# Check the logs directory was created
Test-Path ./logs

# View recent log entries
Get-Content ./logs/echo-baby-*.log -Tail 20
```

### Step 6: Verify First Heartbeat

The system should begin heartbeat monitoring:

- Heartbeat interval: 30 seconds (default)
- Console shows no errors
- Log file shows "Heartbeat loop started"

### Step 7: Test Manual Scan

```powershell
./EchoBabyRebirth.ps1 -Action Scan
```

Expected output:

```
Performing manual system scan...

=== SCAN RESULTS ===

CPU:
  Usage: XX%

Memory:
  Used: X.XX GB
  Available: X.XX GB
  Usage: XX%

Disk:
  C:: XX% used

Processes: XX
```

### Step 8: Verify Threshold Monitoring

Check that threshold alerts work by observing system under load:

- CPU Warning at 70%
- CPU Critical at 90%
- Memory Warning at 75%
- Memory Critical at 90%
- Disk Warning at 80%
- Disk Critical at 95%

### Step 9: Test Renewal Cycle

```powershell
./EchoBabyRebirth.ps1 -Action Renew
```

Expected output:

```
=== PHOENIX RENEWAL CYCLE ===
  [1/4] Preparing for renewal...
  [2/4] Snapshotting critical state...
  [3/4] Executing renewal...
  [4/4] Restoring and restarting...
Phoenix renewal complete - reborn!
```

### Step 10: Check System Status

```powershell
./EchoBabyRebirth.ps1 -Action Status
```

Returns JSON with:
- Version
- State
- Uptime
- Capsule status
- Heartbeat status
- Telemetry stats

---

## Threshold Calibration

### Adjusting Thresholds

Modify thresholds based on your system's normal operation:

1. Run the system for 24 hours
2. Review baseline metrics in logs
3. Adjust thresholds in configuration:

```json
{
    "Thresholds": {
        "CPUWarning": 80,      // Increase if normally high
        "CPUCritical": 95,
        "MemoryWarning": 80,
        "MemoryCritical": 92,
        "DiskWarning": 85,
        "DiskCritical": 95
    }
}
```

4. Restart Echo Baby with new configuration

### Adaptive Thresholds

Echo Baby learns patterns over time. After several renewal cycles:
- Thresholds auto-adjust based on observed patterns
- Anomaly detection becomes more accurate
- False positives decrease

---

## Commander Interface

### Interactive Commands

While running, Echo Baby responds to:

- **Ctrl+C**: Graceful shutdown
- **Manual Actions**: Use separate PowerShell window

### Monitoring Dashboard

View real-time status:

```powershell
# In a separate terminal
while ($true) {
    Clear-Host
    ./EchoBabyRebirth.ps1 -Action Status | ConvertFrom-Json | Format-List
    Start-Sleep -Seconds 10
}
```

---

## Event Listener Activation

### Windows Event Integration (Optional)

To respond to Windows events:

```powershell
# Register for system events
Register-WmiEvent -Query "SELECT * FROM Win32_ProcessStartTrace" -Action {
    # Echo Baby can process these events
}
```

### Scheduled Task Setup

Run Echo Baby as a scheduled task:

```powershell
$action = New-ScheduledTaskAction -Execute "pwsh.exe" `
    -Argument "-File C:\Echo\src\EchoBabyRebirth.ps1 -Action Start"

$trigger = New-ScheduledTaskTrigger -AtStartup

Register-ScheduledTask -TaskName "EchoBabyRebirth" `
    -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Module not found" | Verify modules exist in `src/Modules/` |
| "Access denied" | Run as Administrator |
| No metrics collected | Check WMI/CIM service is running |
| High CPU from Echo Baby | Increase heartbeat interval |
| Logs not created | Check write permissions on logs directory |

### Debug Mode

Run with verbose output:

```powershell
./EchoBabyRebirth.ps1 -Action Start -Verbose
```

### Log Analysis

```powershell
# Find errors in logs
Select-String -Path ./logs/*.log -Pattern "\[Error\]|\[Critical\]"

# Count alerts by type
Select-String -Path ./logs/*.log -Pattern "ALERT:" |
    Group-Object { $_ -match 'CPU|Memory|Disk' }
```

---

## Shutdown Procedure

### Graceful Shutdown

1. Press **Ctrl+C** in the running terminal
2. Or run: `./EchoBabyRebirth.ps1 -Action Stop`

### Expected Shutdown Output

```
Stopping Echo Baby...
Echo Baby stopped. Uptime: 02:15:33
```

### Verify Clean Shutdown

- All capsules cleared (RAM freed)
- Telemetry buffer flushed to logs
- No orphan processes

---

## Maintenance

### Daily

- Review alert logs for anomalies
- Check disk space for log storage

### Weekly

- Archive old logs
- Review threshold appropriateness
- Check renewal cycle frequency

### Monthly

- Full system audit
- Update thresholds based on patterns
- Test all manual actions

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2024 | Initial release with Phoenix renewal |

---

**Deployment Version**: 2.1.0
**Team D Seal**: APPROVED
