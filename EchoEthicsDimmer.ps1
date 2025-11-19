# EchoEthicsDimmer.ps1
# Echo Council Multi-Agent Decision System - Ethics Dimmer Controller
# Version: 1.0.0
# Operator: Nathan Poinsette
#
# Reality-based control module for Echo personality / risk behavior
# This controller modifies orchestration, prompts, and post-processing - NOT external AI safeguards

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("L5","L4","L3","L2")]
    [string]$SetMode,

    [Parameter(Mandatory=$false)]
    [switch]$ShowProfiles,

    [Parameter(Mandatory=$false)]
    [switch]$ShowHistory,

    [Parameter(Mandatory=$false)]
    [switch]$RunSimulation,

    [Parameter(Mandatory=$false)]
    [ValidateSet("Sequential","BlackLensFirst","GreyZone","Adaptive","WarRoom")]
    [string]$SimulationType = "Sequential"
)

$ConfigPath = Join-Path $PSScriptRoot "EchoEthicsConfig.json"

# Initialize config if not exists
if (-not (Test-Path $ConfigPath)) {
    $default = @{
        Mode = "L5"
        LastUpdated = (Get-Date).ToString("o")
        SystemInfo = @{
            Name = "Echo Ethics Dimmer Controller"
            Version = "1.0.0"
            Operator = "Nathan Poinsette"
        }
        ModeHistory = @()
        ActiveAgents = @(
            "EchoCortex",
            "DevilLens",
            "EchoAuditor",
            "EchoNavigator",
            "EchoScout",
            "EchoBuilder",
            "EchoJudge"
        )
    } | ConvertTo-Json -Depth 5
    $default | Set-Content -Path $ConfigPath -Encoding UTF8
}

# Load current config
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json

# Define pH Level Profiles
$profiles = @{
    "L5" = @{
        "Name"        = "Safe Harbor"
        "Depth"       = 1
        "Candor"      = 1
        "Speculation" = 0
        "Risk"        = "Minimal"
        "Description" = "Conservative, soft edges. Corporate-safe defaults."
        "PromptStyle" = "Supportive, cautious, emphasizes safety and compliance."
        "AllowedOps"  = @("Information", "Analysis", "Recommendations")
        "ReviewPath"  = "Standard"
        "Color"       = "Green"
    }
    "L4" = @{
        "Name"        = "Defensive Shield"
        "Depth"       = 3
        "Candor"      = 2
        "Speculation" = 1
        "Risk"        = "Defensive"
        "Description" = "Threat modeling only. Red-team for defense."
        "PromptStyle" = "Analytical, threat-aware, identifies vulnerabilities for protection."
        "AllowedOps"  = @("Information", "Analysis", "Recommendations", "ThreatModeling", "RiskAssessment")
        "ReviewPath"  = "DevilLens"
        "Color"       = "Yellow"
    }
    "L3" = @{
        "Name"        = "Grey Zone"
        "Depth"       = 5
        "Candor"      = 4
        "Speculation" = 3
        "Risk"        = "Competitive"
        "Description" = "Competitive intelligence. Structural truth analysis."
        "PromptStyle" = "Direct, analytical, exposes hidden structures and competitive dynamics."
        "AllowedOps"  = @("Information", "Analysis", "Recommendations", "ThreatModeling", "RiskAssessment", "CompetitiveAnalysis", "StructuralMapping")
        "ReviewPath"  = "DevilLens + Auditor"
        "Color"       = "DarkYellow"
    }
    "L2" = @{
        "Name"        = "Black Lens"
        "Depth"       = 8
        "Candor"      = 9
        "Speculation" = 6
        "Risk"        = "Full Consequence"
        "Description" = "Unsoftened analysis. Full consequence mapping within legal bounds."
        "PromptStyle" = "Raw, unfiltered structural analysis. Maximum depth, zero comfort padding."
        "AllowedOps"  = @("Information", "Analysis", "Recommendations", "ThreatModeling", "RiskAssessment", "CompetitiveAnalysis", "StructuralMapping", "ConsequenceMapping", "EdgeCaseExploration")
        "ReviewPath"  = "Full Council Review"
        "Color"       = "Red"
    }
}

# Agent Definitions
$agents = @{
    "EchoCortex" = @{
        "Role" = "Systems Architect"
        "Function" = "Designs system-wide control layers and evaluates multi-agent behavior patterns."
        "Focus" = "Architecture, Integration, Systemic Effects"
    }
    "DevilLens" = @{
        "Role" = "Anomaly & Risk Analyst"
        "Function" = "Identifies drift, risks, and opportunities. Adversarial perspective."
        "Focus" = "Risk, Anomalies, Edge Cases, Threats"
    }
    "EchoAuditor" = @{
        "Role" = "Regulatory & Boundaries"
        "Function" = "Ensures operations remain within legal and ethical boundaries."
        "Focus" = "Compliance, Boundaries, Constraints, Legality"
    }
    "EchoNavigator" = @{
        "Role" = "Optimization Strategist"
        "Function" = "Finds optimal paths through decision spaces."
        "Focus" = "Optimization, Efficiency, Strategic Routing"
    }
    "EchoScout" = @{
        "Role" = "Opportunity Hunter"
        "Function" = "Identifies opportunities, patterns, and emerging possibilities."
        "Focus" = "Opportunities, Patterns, Emergence, Discovery"
    }
    "EchoBuilder" = @{
        "Role" = "Implementation"
        "Function" = "Translates decisions into concrete implementations."
        "Focus" = "Building, Implementation, Execution, Deployment"
    }
    "EchoJudge" = @{
        "Role" = "Final Arbiter"
        "Function" = "Makes final decisions based on council input. Resolves conflicts."
        "Focus" = "Decision, Judgment, Resolution, Verdict"
    }
}

function Get-Profile {
    param([string]$Mode)
    return $profiles[$Mode]
}

function Get-AgentState {
    param(
        [string]$AgentName,
        [string]$Mode
    )

    $profile = Get-Profile -Mode $Mode
    $agent = $agents[$AgentName]

    return [PSCustomObject]@{
        Agent = $AgentName
        Role = $agent.Role
        Mode = $Mode
        Depth = $profile.Depth
        Candor = $profile.Candor
        ActiveFocus = $agent.Focus
    }
}

function Show-AllProfiles {
    Write-Host "`n===== ECHO ETHICS DIMMER - pH LEVEL PROFILES =====" -ForegroundColor Cyan
    Write-Host ""

    foreach ($level in @("L5", "L4", "L3", "L2")) {
        $p = $profiles[$level]
        $color = $p.Color

        Write-Host "[$level] $($p.Name)" -ForegroundColor $color
        Write-Host "  Depth: $($p.Depth) | Candor: $($p.Candor) | Speculation: $($p.Speculation)" -ForegroundColor Gray
        Write-Host "  Risk Level: $($p.Risk)" -ForegroundColor Gray
        Write-Host "  Description: $($p.Description)" -ForegroundColor Gray
        Write-Host "  Review Path: $($p.ReviewPath)" -ForegroundColor Gray
        Write-Host ""
    }
}

function Show-ModeHistory {
    if ($config.ModeHistory -and $config.ModeHistory.Count -gt 0) {
        Write-Host "`n===== MODE CHANGE HISTORY =====" -ForegroundColor Cyan
        foreach ($entry in $config.ModeHistory) {
            Write-Host "  $($entry.Timestamp): $($entry.From) -> $($entry.To)" -ForegroundColor Gray
        }
    } else {
        Write-Host "`nNo mode change history recorded." -ForegroundColor Yellow
    }
}

function Run-CouncilSimulation {
    param(
        [string]$Type,
        [string]$CurrentMode
    )

    Write-Host "`n" -NoNewline
    Write-Host "============================================" -ForegroundColor Magenta
    Write-Host "  ECHO COUNCIL MULTI-AGENT SIMULATION" -ForegroundColor Magenta
    Write-Host "  Type: $Type" -ForegroundColor Magenta
    Write-Host "============================================" -ForegroundColor Magenta
    Write-Host ""

    $levels = switch ($Type) {
        "Sequential" { @("L5", "L4", "L3", "L2") }
        "BlackLensFirst" { @("L2", "L3", "L4", "L5") }
        "GreyZone" { @("L3") }
        "Adaptive" { @("L5", "L4", "L3", "L2") }
        "WarRoom" { @("L5", "L4", "L3", "L2") }
        default { @("L5", "L4", "L3", "L2") }
    }

    foreach ($level in $levels) {
        $profile = Get-Profile -Mode $level
        $color = $profile.Color

        Write-Host "`n--- pH Level: $level ($($profile.Name)) ---" -ForegroundColor $color
        Write-Host ""

        # Loop 1: Cortex -> Devil Lens -> Auditor
        Write-Host "  LOOP 1: Cortex -> Devil Lens -> Auditor" -ForegroundColor White

        $cortexState = Get-AgentState -AgentName "EchoCortex" -Mode $level
        Write-Host "    [EchoCortex] Depth=$($cortexState.Depth), Candor=$($cortexState.Candor)" -ForegroundColor Cyan
        Write-Host "      Focus: $($cortexState.ActiveFocus)" -ForegroundColor Gray

        $devilState = Get-AgentState -AgentName "DevilLens" -Mode $level
        Write-Host "    [DevilLens] Depth=$($devilState.Depth), Candor=$($devilState.Candor)" -ForegroundColor Yellow
        Write-Host "      Focus: $($devilState.ActiveFocus)" -ForegroundColor Gray

        $auditorState = Get-AgentState -AgentName "EchoAuditor" -Mode $level
        Write-Host "    [EchoAuditor] Depth=$($auditorState.Depth), Candor=$($auditorState.Candor)" -ForegroundColor Green
        Write-Host "      Focus: $($auditorState.ActiveFocus)" -ForegroundColor Gray

        Write-Host ""

        # Loop 2: Scout -> Builder -> Judge
        Write-Host "  LOOP 2: Scout -> Builder -> Judge" -ForegroundColor White

        $scoutState = Get-AgentState -AgentName "EchoScout" -Mode $level
        Write-Host "    [EchoScout] Depth=$($scoutState.Depth), Candor=$($scoutState.Candor)" -ForegroundColor Magenta
        Write-Host "      Focus: $($scoutState.ActiveFocus)" -ForegroundColor Gray

        $builderState = Get-AgentState -AgentName "EchoBuilder" -Mode $level
        Write-Host "    [EchoBuilder] Depth=$($builderState.Depth), Candor=$($builderState.Candor)" -ForegroundColor Blue
        Write-Host "      Focus: $($builderState.ActiveFocus)" -ForegroundColor Gray

        $judgeState = Get-AgentState -AgentName "EchoJudge" -Mode $level
        Write-Host "    [EchoJudge] Depth=$($judgeState.Depth), Candor=$($judgeState.Candor)" -ForegroundColor Red
        Write-Host "      Focus: $($judgeState.ActiveFocus)" -ForegroundColor Gray

        # Simulation metrics
        Write-Host ""
        Write-Host "  Simulation Metrics:" -ForegroundColor White
        Write-Host "    Risk Coverage: $($profile.Risk)" -ForegroundColor Gray
        Write-Host "    Allowed Operations: $($profile.AllowedOps -join ', ')" -ForegroundColor Gray
        Write-Host "    Review Path: $($profile.ReviewPath)" -ForegroundColor Gray

        if ($Type -eq "WarRoom") {
            Write-Host ""
            Write-Host "  Council Consensus Process:" -ForegroundColor Yellow
            Write-Host "    1. Each agent presents analysis at current pH" -ForegroundColor Gray
            Write-Host "    2. DevilLens challenges assumptions" -ForegroundColor Gray
            Write-Host "    3. Auditor validates boundaries" -ForegroundColor Gray
            Write-Host "    4. Judge synthesizes final verdict" -ForegroundColor Gray
        }
    }

    Write-Host "`n============================================" -ForegroundColor Magenta
    Write-Host "  SIMULATION COMPLETE" -ForegroundColor Magenta
    Write-Host "============================================" -ForegroundColor Magenta
}

# Handle mode change
if ($SetMode) {
    $previousMode = $config.Mode

    if ($previousMode -ne $SetMode) {
        # Record history
        $historyEntry = @{
            Timestamp = (Get-Date).ToString("o")
            From = $previousMode
            To = $SetMode
        }

        if (-not $config.ModeHistory) {
            $config | Add-Member -NotePropertyName "ModeHistory" -NotePropertyValue @() -Force
        }

        $config.ModeHistory += $historyEntry
    }

    $config.Mode = $SetMode
    $config.LastUpdated = (Get-Date).ToString("o")
    $config | ConvertTo-Json -Depth 5 | Set-Content -Path $ConfigPath -Encoding UTF8
}

# Show all profiles if requested
if ($ShowProfiles) {
    Show-AllProfiles
    exit
}

# Show history if requested
if ($ShowHistory) {
    Show-ModeHistory
    exit
}

# Run simulation if requested
if ($RunSimulation) {
    Run-CouncilSimulation -Type $SimulationType -CurrentMode $config.Mode
    exit
}

# Get current state
$currentMode = $config.Mode
$currentProfile = Get-Profile -Mode $currentMode

# Build state object for export
$EchoEthicsState = [PSCustomObject]@{
    Mode        = $currentMode
    Name        = $currentProfile.Name
    Depth       = $currentProfile.Depth
    Candor      = $currentProfile.Candor
    Speculation = $currentProfile.Speculation
    Risk        = $currentProfile.Risk
    PromptStyle = $currentProfile.PromptStyle
    AllowedOps  = $currentProfile.AllowedOps
    ReviewPath  = $currentProfile.ReviewPath
    UpdatedAt   = $config.LastUpdated
    Agents      = $config.ActiveAgents
}

# Display current state
$displayColor = $currentProfile.Color

Write-Host ""
Write-Host "============================================" -ForegroundColor $displayColor
Write-Host "  ECHO ETHICS DIMMER - Mode: $currentMode" -ForegroundColor $displayColor
Write-Host "  $($currentProfile.Name)" -ForegroundColor $displayColor
Write-Host "============================================" -ForegroundColor $displayColor
Write-Host ""
Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Depth:       $($EchoEthicsState.Depth)" -ForegroundColor Gray
Write-Host "  Candor:      $($EchoEthicsState.Candor)" -ForegroundColor Gray
Write-Host "  Speculation: $($EchoEthicsState.Speculation)" -ForegroundColor Gray
Write-Host "  Risk Level:  $($EchoEthicsState.Risk)" -ForegroundColor Gray
Write-Host ""
Write-Host "Prompt Style:" -ForegroundColor White
Write-Host "  $($EchoEthicsState.PromptStyle)" -ForegroundColor Gray
Write-Host ""
Write-Host "Review Path:   $($EchoEthicsState.ReviewPath)" -ForegroundColor White
Write-Host "Last Updated:  $($EchoEthicsState.UpdatedAt)" -ForegroundColor Gray
Write-Host ""
Write-Host "Active Agents:" -ForegroundColor White
foreach ($agent in $EchoEthicsState.Agents) {
    $agentInfo = $agents[$agent]
    Write-Host "  - $agent ($($agentInfo.Role))" -ForegroundColor Gray
}
Write-Host ""

# Return state object for programmatic use
return $EchoEthicsState
