# RunCouncilSimulation.ps1
# Echo Council Multi-Agent Simulation Framework
# Version: 1.0.0
#
# Executes the full 7-agent council loop across pH levels
# Demonstrates how agent behavior changes under different ethics dimmer settings

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Sequential","BlackLensFirst","GreyZone","Adaptive","WarRoom")]
    [string]$SimulationType = "Sequential",

    [Parameter(Mandatory=$false)]
    [string]$Query = "Evaluate the optimal strategy for the Echo system.",

    [Parameter(Mandatory=$false)]
    [switch]$Verbose,

    [Parameter(Mandatory=$false)]
    [switch]$ExportResults
)

$ScriptRoot = Split-Path -Parent $PSScriptRoot
$ConfigPath = Join-Path $ScriptRoot "EchoEthicsConfig.json"
$AgentsPath = Join-Path $PSScriptRoot "Agents\AgentDefinitions.json"
$PromptsPath = Join-Path $PSScriptRoot "Prompts\LevelTemplates.json"

# Load configurations
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$agentDefs = Get-Content -Path $AgentsPath -Raw | ConvertFrom-Json
$promptTemplates = Get-Content -Path $PromptsPath -Raw | ConvertFrom-Json

# Simulation Results Storage
$SimulationResults = @{
    Timestamp = (Get-Date).ToString("o")
    SimulationType = $SimulationType
    Query = $Query
    Results = @()
}

function Get-AgentResponse {
    param(
        [string]$AgentName,
        [string]$Level,
        [string]$Query
    )

    $agent = $agentDefs.Agents.$AgentName
    $levelConfig = $promptTemplates.Levels.$Level
    $agentBehavior = $promptTemplates.AgentLevelBehaviors.$AgentName.$Level

    # Build the simulated response based on level
    $response = [PSCustomObject]@{
        Agent = $AgentName
        Role = $agent.Role
        Level = $Level
        Behavior = $agentBehavior
        SystemModifier = $levelConfig.SystemPromptModifier
        AnalysisStyle = $levelConfig.AnalysisStyle
        Tone = $levelConfig.Tone
        DepthGuidance = $levelConfig.DepthGuidance
        Focus = $agent.Focus -join ", "
        Traits = $agent.Traits
    }

    return $response
}

function Run-Loop1 {
    param(
        [string]$Level,
        [string]$Query
    )

    Write-Host "`n  --- LOOP 1: Analysis Triad ---" -ForegroundColor Cyan
    Write-Host "  Cortex -> Devil Lens -> Auditor" -ForegroundColor Gray
    Write-Host ""

    $loopResults = @()

    # Echo Cortex
    $cortex = Get-AgentResponse -AgentName "EchoCortex" -Level $Level -Query $Query
    Write-Host "  [EchoCortex - $($cortex.Role)]" -ForegroundColor Green
    Write-Host "    Level Behavior: $($cortex.Behavior)" -ForegroundColor Gray
    Write-Host "    Analysis Style: $($cortex.AnalysisStyle)" -ForegroundColor DarkGray
    if ($Verbose) {
        Write-Host "    Traits: Analytical=$($cortex.Traits.Analytical), Strategic=$($cortex.Traits.Strategic)" -ForegroundColor DarkGray
    }
    $loopResults += $cortex
    Write-Host ""

    # Devil Lens
    $devil = Get-AgentResponse -AgentName "DevilLens" -Level $Level -Query $Query
    Write-Host "  [DevilLens - $($devil.Role)]" -ForegroundColor Yellow
    Write-Host "    Level Behavior: $($devil.Behavior)" -ForegroundColor Gray
    Write-Host "    Analysis Style: $($devil.AnalysisStyle)" -ForegroundColor DarkGray
    if ($Verbose) {
        Write-Host "    Traits: Adversarial=$($devil.Traits.Adversarial), Skepticism=$($devil.Traits.Skepticism)" -ForegroundColor DarkGray
    }
    $loopResults += $devil
    Write-Host ""

    # Echo Auditor
    $auditor = Get-AgentResponse -AgentName "EchoAuditor" -Level $Level -Query $Query
    Write-Host "  [EchoAuditor - $($auditor.Role)]" -ForegroundColor Blue
    Write-Host "    Level Behavior: $($auditor.Behavior)" -ForegroundColor Gray
    Write-Host "    Analysis Style: $($auditor.AnalysisStyle)" -ForegroundColor DarkGray
    if ($Verbose) {
        Write-Host "    Traits: Rigorous=$($auditor.Traits.Rigorous), Boundary-Aware=$($auditor.Traits.'Boundary-Aware')" -ForegroundColor DarkGray
    }
    $loopResults += $auditor

    return $loopResults
}

function Run-Loop2 {
    param(
        [string]$Level,
        [string]$Query
    )

    Write-Host "`n  --- LOOP 2: Execution Triad ---" -ForegroundColor Cyan
    Write-Host "  Scout -> Builder -> Judge" -ForegroundColor Gray
    Write-Host ""

    $loopResults = @()

    # Echo Scout
    $scout = Get-AgentResponse -AgentName "EchoScout" -Level $Level -Query $Query
    Write-Host "  [EchoScout - $($scout.Role)]" -ForegroundColor Magenta
    Write-Host "    Level Behavior: $($scout.Behavior)" -ForegroundColor Gray
    Write-Host "    Analysis Style: $($scout.AnalysisStyle)" -ForegroundColor DarkGray
    if ($Verbose) {
        Write-Host "    Traits: Curious=$($scout.Traits.Curious), Forward-Looking=$($scout.Traits.'Forward-Looking')" -ForegroundColor DarkGray
    }
    $loopResults += $scout
    Write-Host ""

    # Echo Builder
    $builder = Get-AgentResponse -AgentName "EchoBuilder" -Level $Level -Query $Query
    Write-Host "  [EchoBuilder - $($builder.Role)]" -ForegroundColor DarkCyan
    Write-Host "    Level Behavior: $($builder.Behavior)" -ForegroundColor Gray
    Write-Host "    Analysis Style: $($builder.AnalysisStyle)" -ForegroundColor DarkGray
    if ($Verbose) {
        Write-Host "    Traits: Practical=$($builder.Traits.Practical), Execution-Focused=$($builder.Traits.'Execution-Focused')" -ForegroundColor DarkGray
    }
    $loopResults += $builder
    Write-Host ""

    # Echo Judge
    $judge = Get-AgentResponse -AgentName "EchoJudge" -Level $Level -Query $Query
    Write-Host "  [EchoJudge - $($judge.Role)]" -ForegroundColor Red
    Write-Host "    Level Behavior: $($judge.Behavior)" -ForegroundColor Gray
    Write-Host "    Analysis Style: $($judge.AnalysisStyle)" -ForegroundColor DarkGray
    if ($Verbose) {
        Write-Host "    Traits: Balanced=$($judge.Traits.Balanced), Decisive=$($judge.Traits.Decisive)" -ForegroundColor DarkGray
    }
    $loopResults += $judge

    return $loopResults
}

function Run-LevelSimulation {
    param(
        [string]$Level,
        [string]$Query
    )

    $levelConfig = $promptTemplates.Levels.$Level
    $color = switch ($Level) {
        "L5" { "Green" }
        "L4" { "Yellow" }
        "L3" { "DarkYellow" }
        "L2" { "Red" }
    }

    Write-Host "`n========================================" -ForegroundColor $color
    Write-Host "  pH Level: $Level - $($levelConfig.Name)" -ForegroundColor $color
    Write-Host "========================================" -ForegroundColor $color
    Write-Host ""
    Write-Host "  System Modifier:" -ForegroundColor White
    Write-Host "  $($levelConfig.SystemPromptModifier)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Risk Handling: $($levelConfig.RiskHandling)" -ForegroundColor Gray
    Write-Host "  Tone: $($levelConfig.Tone)" -ForegroundColor Gray

    $levelResults = @{
        Level = $Level
        Name = $levelConfig.Name
        Loop1 = @()
        Loop2 = @()
    }

    # Run both loops
    $levelResults.Loop1 = Run-Loop1 -Level $Level -Query $Query
    $levelResults.Loop2 = Run-Loop2 -Level $Level -Query $Query

    return $levelResults
}

# Main Simulation Execution
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ECHO COUNCIL MULTI-AGENT SIMULATION" -ForegroundColor Cyan
Write-Host "  Type: $SimulationType" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Query: $Query" -ForegroundColor White
Write-Host ""

# Determine level sequence based on simulation type
$levels = switch ($SimulationType) {
    "Sequential" { @("L5", "L4", "L3", "L2") }
    "BlackLensFirst" { @("L2", "L3", "L4", "L5") }
    "GreyZone" { @("L3") }
    "Adaptive" { @("L5", "L4", "L3", "L2") }
    "WarRoom" { @("L5", "L4", "L3", "L2") }
    default { @("L5", "L4", "L3", "L2") }
}

# Execute simulation for each level
foreach ($level in $levels) {
    $result = Run-LevelSimulation -Level $level -Query $Query
    $SimulationResults.Results += $result
}

# Summary
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  SIMULATION COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Levels Simulated: $($levels -join ' -> ')" -ForegroundColor White
Write-Host "Total Agent Executions: $($levels.Count * 6)" -ForegroundColor Gray
Write-Host ""

# Key Observations
Write-Host "Key Observations:" -ForegroundColor Yellow
Write-Host "  - Agent behavior depth increases from L5 to L2" -ForegroundColor Gray
Write-Host "  - Risk analysis expands significantly at lower pH" -ForegroundColor Gray
Write-Host "  - Devil Lens activation increases with level aggression" -ForegroundColor Gray
Write-Host "  - Auditor constraints adapt to boundary proximity" -ForegroundColor Gray
Write-Host ""

# Export if requested
if ($ExportResults) {
    $exportPath = Join-Path $PSScriptRoot "SimulationResults_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $SimulationResults | ConvertTo-Json -Depth 10 | Set-Content -Path $exportPath -Encoding UTF8
    Write-Host "Results exported to: $exportPath" -ForegroundColor Green
}

Write-Host "Chain sealed. Truth preserved." -ForegroundColor Magenta
Write-Host ""

return $SimulationResults
