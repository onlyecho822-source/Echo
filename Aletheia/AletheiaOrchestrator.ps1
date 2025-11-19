# AletheiaOrchestrator.ps1
# Wires Echo Ethics Dimmer to Aletheia operations with metrics logging
# Version: 1.0.0
#
# This is the main orchestrator that:
# - Reads current Echo mode
# - Applies appropriate prompt templates
# - Enforces review requirements
# - Logs all operations with metrics

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Ingest","Analyze","Export","Challenge","Review")]
    [string]$Operation = "Analyze",

    [Parameter(Mandatory=$false)]
    [string]$ArtifactID = "",

    [Parameter(Mandatory=$false)]
    [string]$Query = "",

    [Parameter(Mandatory=$false)]
    [switch]$ShowMetrics,

    [Parameter(Mandatory=$false)]
    [switch]$ShowPendingReviews
)

$ScriptRoot = $PSScriptRoot
$ParentRoot = Split-Path -Parent $ScriptRoot
$ConfigPath = Join-Path $ParentRoot "EchoEthicsConfig.json"
$LogsPath = Join-Path $ScriptRoot "Logs"
$PromptsPath = Join-Path $ParentRoot "EchoCouncil\Prompts\LevelTemplates.json"

# Ensure logs directory exists
if (-not (Test-Path $LogsPath)) {
    New-Item -ItemType Directory -Path $LogsPath | Out-Null
}

# Load configurations
$echoConfig = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$promptTemplates = Get-Content -Path $PromptsPath -Raw | ConvertFrom-Json

# Aletheia-specific prompt templates for each operation
$aletheiaPrompts = @{
    "Ingest" = @{
        "L5" = @{
            "SystemPrompt" = "You are processing an artifact for the Aletheia system. Focus on accurate metadata extraction and proper custody documentation. Flag any potential issues for manual review. Do not speculate about artifact significance."
            "UserPromptPrefix" = "Process this artifact conservatively: "
            "ReviewRequired" = $false
        }
        "L4" = @{
            "SystemPrompt" = "You are processing an artifact for the Aletheia system. Extract metadata accurately. Identify potential chain-of-custody gaps or data integrity concerns. Note any anomalies that could affect downstream analysis."
            "UserPromptPrefix" = "Process this artifact with integrity checks: "
            "ReviewRequired" = $false
        }
        "L3" = @{
            "SystemPrompt" = "You are processing an artifact for the Aletheia system. Extract all available metadata. Analyze for potential provenance indicators. Note patterns that may suggest origin, handling history, or manipulation. Be direct about uncertainties."
            "UserPromptPrefix" = "Process this artifact with structural analysis: "
            "ReviewRequired" = $false
        }
        "L2" = @{
            "SystemPrompt" = "You are processing an artifact for the Aletheia system. Extract complete metadata. Map all possible interpretations of provenance indicators. Enumerate edge cases and potential falsification scenarios. This output requires Devil Lens review before operational use."
            "UserPromptPrefix" = "Process this artifact with full hypothesis enumeration: "
            "ReviewRequired" = $true
        }
    }
    "Analyze" = @{
        "L5" = @{
            "SystemPrompt" = "You are analyzing evidence for the Aletheia system. Provide conservative interpretations based on established methods. Cite sources. Avoid speculation. Report confidence levels."
            "UserPromptPrefix" = "Analyze this evidence conservatively: "
            "ReviewRequired" = $false
        }
        "L4" = @{
            "SystemPrompt" = "You are analyzing evidence for the Aletheia system. Apply established methods. Identify potential threats to validity. Note gaps in evidence. Model defensive scenarios where conclusions might be challenged."
            "UserPromptPrefix" = "Analyze with threat modeling: "
            "ReviewRequired" = $false
        }
        "L3" = @{
            "SystemPrompt" = "You are analyzing evidence for the Aletheia system. Apply multi-method analysis. Expose structural patterns. Map competing hypotheses. Be direct about trade-offs and limitations. Drop comfort language."
            "UserPromptPrefix" = "Analyze with structural depth: "
            "ReviewRequired" = $false
        }
        "L2" = @{
            "SystemPrompt" = "You are analyzing evidence for the Aletheia system. Enumerate all plausible hypotheses. Map complete consequence space. Include edge cases and low-probability scenarios. Zero comfort padding. This is mapping, not advice. Requires Devil Lens review."
            "UserPromptPrefix" = "Full hypothesis enumeration: "
            "ReviewRequired" = $true
        }
    }
    "Export" = @{
        "L5" = @{
            "SystemPrompt" = "You are preparing an export bundle from the Aletheia vault. Apply maximum data minimization. Include only fields necessary for stated purpose. Verify consent status. Redact sensitive identifiers."
            "UserPromptPrefix" = "Prepare minimal export bundle: "
            "ReviewRequired" = $false
        }
        "L4" = @{
            "SystemPrompt" = "You are preparing an export bundle from the Aletheia vault. Apply data minimization. Verify consent. Note any fields that might indirectly enable re-identification. Document export rationale."
            "UserPromptPrefix" = "Prepare export with privacy analysis: "
            "ReviewRequired" = $false
        }
        "L3" = @{
            "SystemPrompt" = "You are preparing an export bundle from the Aletheia vault. Balance minimization with analytical utility. Map consent scope against requested fields. Document trade-offs explicitly."
            "UserPromptPrefix" = "Prepare balanced export bundle: "
            "ReviewRequired" = $false
        }
        "L2" = @{
            "SystemPrompt" = "You are preparing an export bundle from the Aletheia vault. Enumerate all possible data exposures. Map re-identification risks. Document full consequence space of export. Requires review."
            "UserPromptPrefix" = "Prepare export with full risk mapping: "
            "ReviewRequired" = $true
        }
    }
    "Challenge" = @{
        "L5" = @{
            "SystemPrompt" = "You are processing a challenge to an Aletheia artifact or analysis. Document the challenge formally. Route to appropriate validators. Maintain neutrality."
            "UserPromptPrefix" = "Process challenge: "
            "ReviewRequired" = $false
        }
        "L4" = @{
            "SystemPrompt" = "You are processing a challenge. Analyze the challenge evidence. Identify specific claims being contested. Note which validators and methods would be needed to resolve."
            "UserPromptPrefix" = "Analyze challenge: "
            "ReviewRequired" = $false
        }
        "L3" = @{
            "SystemPrompt" = "You are processing a challenge. Map the challenge against original claims. Identify structural weaknesses in both positions. Analyze incentives and potential biases of all parties."
            "UserPromptPrefix" = "Structural challenge analysis: "
            "ReviewRequired" = $false
        }
        "L2" = @{
            "SystemPrompt" = "You are processing a challenge. Enumerate all possible resolutions. Map consequences of each outcome. Include scenarios where challenge is valid, invalid, partially valid, or reveals new questions. Requires review."
            "UserPromptPrefix" = "Full challenge consequence mapping: "
            "ReviewRequired" = $true
        }
    }
    "Review" = @{
        "L5" = @{
            "SystemPrompt" = "You are conducting Devil Lens review of L2 output. Verify claims are within legal bounds. Check for harmful content. Confirm proper context is provided."
            "UserPromptPrefix" = "Devil Lens review (conservative): "
            "ReviewRequired" = $false
        }
        "L4" = @{
            "SystemPrompt" = "You are conducting Devil Lens review. Verify legal bounds. Identify potential misuse vectors. Note required disclaimers or context additions."
            "UserPromptPrefix" = "Devil Lens review (defensive): "
            "ReviewRequired" = $false
        }
        "L3" = @{
            "SystemPrompt" = "You are conducting Devil Lens review. Evaluate analytical validity. Check for logical gaps. Verify claims are supported. Note where additional evidence would strengthen or weaken conclusions."
            "UserPromptPrefix" = "Devil Lens review (structural): "
            "ReviewRequired" = $false
        }
        "L2" = @{
            "SystemPrompt" = "You are conducting Devil Lens meta-review. Analyze the review itself for completeness. Map what was not considered. This is recursive analysis and requires human sign-off."
            "UserPromptPrefix" = "Devil Lens meta-review: "
            "ReviewRequired" = $true
        }
    }
}

function Get-OperationPrompt {
    param(
        [string]$Operation,
        [string]$Mode
    )

    return $aletheiaPrompts[$Operation][$Mode]
}

function Write-MetricsLog {
    param(
        [string]$Operation,
        [string]$Mode,
        [string]$ArtifactID,
        [bool]$ReviewRequired,
        [string]$Status
    )

    $entry = @{
        timestamp = (Get-Date).ToString("o")
        operation = $Operation
        echoMode = $Mode
        artifactID = $ArtifactID
        reviewRequired = $ReviewRequired
        status = $Status
    }

    $metricsFile = Join-Path $LogsPath "aletheia_metrics.jsonl"
    ($entry | ConvertTo-Json -Compress) | Add-Content -Path $metricsFile -Encoding UTF8
}

function Get-MetricsSummary {
    $metricsFile = Join-Path $LogsPath "aletheia_metrics.jsonl"

    if (-not (Test-Path $metricsFile)) {
        Write-Host "No metrics data available." -ForegroundColor Yellow
        return
    }

    $entries = Get-Content -Path $metricsFile | ForEach-Object {
        $_ | ConvertFrom-Json
    }

    $total = $entries.Count
    $byMode = $entries | Group-Object -Property echoMode
    $byOperation = $entries | Group-Object -Property operation
    $reviewRequired = ($entries | Where-Object { $_.reviewRequired }).Count

    Write-Host ""
    Write-Host "===== ALETHEIA METRICS SUMMARY =====" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Total Operations: $total" -ForegroundColor White
    Write-Host ""
    Write-Host "By Echo Mode:" -ForegroundColor White
    foreach ($group in $byMode) {
        $pct = [math]::Round(($group.Count / $total) * 100, 1)
        Write-Host "  $($group.Name): $($group.Count) ($pct%)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "By Operation:" -ForegroundColor White
    foreach ($group in $byOperation) {
        Write-Host "  $($group.Name): $($group.Count)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Review Required: $reviewRequired ($([math]::Round(($reviewRequired / $total) * 100, 1))%)" -ForegroundColor Yellow
    Write-Host ""

    # Mode Fidelity metric
    Write-Host "Mode Fidelity: Requires audit sampling" -ForegroundColor Gray
    Write-Host ""
}

function Get-PendingReviews {
    $metricsFile = Join-Path $LogsPath "aletheia_metrics.jsonl"

    if (-not (Test-Path $metricsFile)) {
        Write-Host "No pending reviews." -ForegroundColor Green
        return
    }

    $entries = Get-Content -Path $metricsFile | ForEach-Object {
        $_ | ConvertFrom-Json
    } | Where-Object { $_.reviewRequired -and $_.status -ne "REVIEWED" }

    if ($entries.Count -eq 0) {
        Write-Host "No pending reviews." -ForegroundColor Green
        return
    }

    Write-Host ""
    Write-Host "===== PENDING DEVIL LENS REVIEWS =====" -ForegroundColor Red
    Write-Host ""
    foreach ($entry in $entries) {
        Write-Host "  Operation: $($entry.operation)" -ForegroundColor Yellow
        Write-Host "  Artifact:  $($entry.artifactID)" -ForegroundColor Gray
        Write-Host "  Mode:      $($entry.echoMode)" -ForegroundColor Gray
        Write-Host "  Time:      $($entry.timestamp)" -ForegroundColor Gray
        Write-Host ""
    }
}

# Handle special commands
if ($ShowMetrics) {
    Get-MetricsSummary
    exit
}

if ($ShowPendingReviews) {
    Get-PendingReviews
    exit
}

# Main operation execution
$currentMode = $echoConfig.Mode
$prompt = Get-OperationPrompt -Operation $Operation -Mode $currentMode
$levelConfig = $promptTemplates.Levels.$currentMode

# Display operation context
$color = switch ($currentMode) {
    "L5" { "Green" }
    "L4" { "Yellow" }
    "L3" { "DarkYellow" }
    "L2" { "Red" }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor $color
Write-Host "  ALETHEIA ORCHESTRATOR" -ForegroundColor $color
Write-Host "========================================" -ForegroundColor $color
Write-Host ""
Write-Host "Operation: $Operation" -ForegroundColor White
Write-Host "Echo Mode: $currentMode ($($levelConfig.Name))" -ForegroundColor $color
Write-Host ""

if ($prompt.ReviewRequired) {
    Write-Host "NOTICE: This operation requires Devil Lens review." -ForegroundColor Red
    Write-Host ""
}

Write-Host "System Prompt:" -ForegroundColor White
Write-Host "  $($prompt.SystemPrompt)" -ForegroundColor Gray
Write-Host ""

if ($Query) {
    Write-Host "Full Prompt:" -ForegroundColor White
    Write-Host "  $($prompt.UserPromptPrefix)$Query" -ForegroundColor Cyan
    Write-Host ""
}

# Log the operation
Write-MetricsLog -Operation $Operation -Mode $currentMode -ArtifactID $ArtifactID -ReviewRequired $prompt.ReviewRequired -Status "EXECUTED"

# Output the prompt object for use by calling scripts
$output = [PSCustomObject]@{
    Operation = $Operation
    Mode = $currentMode
    ModeName = $levelConfig.Name
    SystemPrompt = $prompt.SystemPrompt
    UserPromptPrefix = $prompt.UserPromptPrefix
    ReviewRequired = $prompt.ReviewRequired
    Tone = $levelConfig.Tone
    RiskHandling = $levelConfig.RiskHandling
    DepthGuidance = $levelConfig.DepthGuidance
}

return $output
