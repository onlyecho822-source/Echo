# Echo Council Multi-Agent Decision System

## Overview

The Echo Ethics Dimmer Controller is a reality-based orchestration layer that modifies how Echo agents behave across different "pH levels" (L5 to L2). This system controls prompts, analysis depth, and review paths - not external AI safeguards.

## Quick Start

### Check Current Mode
```powershell
.\EchoEthicsDimmer.ps1
```

### Set Mode
```powershell
.\EchoEthicsDimmer.ps1 -SetMode L4
```

### View All pH Profiles
```powershell
.\EchoEthicsDimmer.ps1 -ShowProfiles
```

### Run Multi-Agent Simulation
```powershell
.\EchoEthicsDimmer.ps1 -RunSimulation -SimulationType Sequential
```

## pH Levels

| Level | Name | Depth | Risk | Description |
|-------|------|-------|------|-------------|
| L5 | Safe Harbor | 1 | Minimal | Conservative, corporate-safe |
| L4 | Defensive Shield | 3 | Defensive | Threat modeling for protection |
| L3 | Grey Zone | 5 | Competitive | Structural truth analysis |
| L2 | Black Lens | 8 | Full | Unsoftened consequence mapping |

## Simulation Types

- **Sequential**: L5 -> L4 -> L3 -> L2 (full spectrum)
- **BlackLensFirst**: L2 -> L3 -> L4 -> L5 (max intensity first)
- **GreyZone**: L3 only (competitive intelligence)
- **Adaptive**: Each agent chooses pH
- **WarRoom**: Full council debate mode

## Council Agents

### Loop 1: Analysis Triad
1. **Echo Cortex** - Systems Architect
2. **Devil Lens** - Risk Analyst
3. **Echo Auditor** - Compliance Guardian

### Loop 2: Execution Triad
4. **Echo Scout** - Opportunity Hunter
5. **Echo Builder** - Implementation
6. **Echo Judge** - Final Arbiter

## Integration

Other scripts can consume the ethics state:

```powershell
$ethics = & ".\EchoEthicsDimmer.ps1"

switch ($ethics.Mode) {
    "L5" { # Safe prompts }
    "L4" { # Defensive prompts }
    "L3" { # Aggressive analysis }
    "L2" { # Full consequence mapping }
}
```

## Reality Check

This system controls YOUR orchestration layer:
- Prompts and system messages
- Analysis depth and style
- Review paths and logging
- Output filtering and routing

It does NOT bypass external AI provider safeguards.

---
*Chain sealed. Truth preserved.*
