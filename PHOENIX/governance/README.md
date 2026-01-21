# PHOENIX Governance Scripts

**Autonomous System Governance and Monitoring**

**Version:** AC-STABLE-2.0  
**Status:** OPERATIONAL  
**Last Updated:** January 21, 2026

---

## Overview

The PHOENIX Governance system provides autonomous monitoring, self-healing, and Git synchronization capabilities. These scripts run as scheduled tasks to maintain system health without human intervention.

---

## Scripts

### Echo-PHOENIX-AC-Governor.ps1

The main governance script with two operational modes:

#### Sense Mode (Read-Only)

```powershell
.\Echo-PHOENIX-AC-Governor.ps1 -Mode Sense
```

**Output:**
```
PHOENIX AC Governance vAC-STABLE-2.0
[Sense Mode - Read Only]

Status:
Wi-Fi: [SSID] ([RSSI] dBm)
Signal: p95=[X]ms, jitter=[Y]ms, loss=[Z]%

Complete. Logs: C:\Users\[USER]\EchoUniverse\PHOENIX\logs
```

#### Govern Mode (Active)

```powershell
.\Echo-PHOENIX-AC-Governor.ps1 -Mode Govern
```

**Output:**
```
PHOENIX AC Governance vAC-STABLE-2.0

[AC Governance Cycle]
Wi-Fi: [SSID] (RSSI: [X] dBm)
1.1.1.1: p95=[X]ms, jitter=[Y]ms, loss=[Z]%
8.8.8.8: p95=[X]ms, jitter=[Y]ms, loss=[Z]%
Signal within parameters. No action required.

Complete. Logs: C:\Users\[USER]\EchoUniverse\PHOENIX\logs
```

---

### phoenix-git-sync.ps1

Git synchronization script for automated backups.

```powershell
.\phoenix-git-sync.ps1 -Mode SyncOnly
```

**Output:**
```
Git Sync: SyncOnly
```

---

## Scheduled Tasks

### PHOENIX-AC-Governance

| Property | Value |
|----------|-------|
| Task Name | PHOENIX-AC-Governance |
| State | Ready |
| Trigger | Scheduled (configurable) |
| Action | Run Echo-PHOENIX-AC-Governor.ps1 |

**Check Status:**
```powershell
Get-ScheduledTask -TaskName "PHOENIX-AC-Governance"
```

---

## Directory Structure

```
PHOENIX/
├── Echo-PHOENIX-AC-Governor.ps1    ← Main governance script
├── phoenix-git-sync.ps1            ← Git sync script
├── logs/                           ← Log files (NDJSON format)
│   └── phoenix-*.ndjson
└── backups/                        ← Local backups
```

---

## Configuration

### Config Object

```powershell
$Config = @{
    TaskName = "PHOENIX-AC-Governance"
    LogPath = "logs"
    GitRemote = "https://github.com/onlyecho822-source/Echo.git"
}
```

### Base Path

```powershell
$BasePath = "C:\Users\$env:USERNAME\EchoUniverse\PHOENIX"
```

---

## Setup

### Auto-Setup Script

```powershell
# Run the auto-setup
.\phoenix-auto-setup.ps1 -Mode Setup
```

**Modes:**
- `Setup` — Initialize environment, create scheduled task, init Git
- `Sense` — Run governance in read-only mode
- `Govern` — Run governance in active mode
- `Diagnose` — Show system diagnostics
- `Sync` — Run Git sync only
- `All` — Run all setup steps

---

## Diagnostics

### Show-Diagnostics Function

```powershell
.\phoenix-auto-setup.ps1 -Mode Diagnose
```

**Output includes:**
- System information (hostname, PowerShell version, admin status)
- Path verification
- Scheduled task status
- Latest log entries
- Git status
- Recommendations

---

## Logging

### Log Format (NDJSON)

```json
{"timestamp": "2026-01-21T01:30:00Z", "level": "INFO", "message": "Governance cycle started"}
{"timestamp": "2026-01-21T01:30:01Z", "level": "SUCCESS", "message": "Signal within parameters"}
```

### Log Location

```
C:\Users\[USER]\EchoUniverse\PHOENIX\logs\
```

### View Logs

```powershell
# View latest log
Get-Content "$BasePath\logs\*.ndjson" -Tail 10

# View specific date
Get-Content "$BasePath\logs\phoenix-20260121.ndjson"
```

---

## Git Integration

### .gitignore

```
logs/
backups/
*.tmp
*.log
*.bak
data/
```

### Initialize Git

```powershell
function Initialize-Git {
    Set-Location $BasePath
    
    if (-not (Test-Path ".git")) {
        git init
        git remote add origin $Config.GitRemote
    }
    
    git add .
    git commit -m "PHOENIX update $(Get-Date -Format 'yyyy-MM-dd')"
}
```

---

## Troubleshooting

### Script Not Found

```powershell
# Verify path
Test-Path "$BasePath\Echo-PHOENIX-AC-Governor.ps1"

# If missing, navigate to correct directory
cd "C:\Users\$env:USERNAME\EchoUniverse\PHOENIX"
```

### Scheduled Task Not Running

```powershell
# Check task status
Get-ScheduledTaskInfo -TaskName "PHOENIX-AC-Governance"

# Run manually
Start-ScheduledTask -TaskName "PHOENIX-AC-Governance"
```

### Git Sync Failing

```powershell
# Check remote
git remote -v

# Update remote
git remote set-url origin https://github.com/onlyecho822-source/Echo.git
```

---

## Security

- Scripts run as current user
- No elevated privileges required for Sense mode
- Admin required for Govern mode actions
- Logs stored locally only
- Git credentials managed by system credential manager

---

## Related Documents

- [PHOENIX README](../README.md)
- [Truth Ledger](../truth-ledger/README.md)
- [I'M TELLING](../news/README.md)

---

## Status

| Component | Status |
|-----------|--------|
| Governance Script | 🟢 OPERATIONAL |
| Git Sync | 🟢 OPERATIONAL |
| Scheduled Task | 🟢 READY |
| Logging | 🟢 ACTIVE |
