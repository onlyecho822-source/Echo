# Seal-Artifact.ps1
# Aletheia Ingest + Sealing CLI Tool
# Version: 1.0.0
#
# Takes raw files and produces sealed manifest.json with:
# - Content hash (SHA-256)
# - Metadata extraction
# - Chain of custody entry
# - Signature
# - Trusted timestamp
#
# Usage: .\Seal-Artifact.ps1 -FilePath "path/to/file" -FileType "FASTQ" -Operator "Name"

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,

    [Parameter(Mandatory=$true)]
    [ValidateSet("FASTQ","VCF","BAM","IIIF","TIFF","XRF-CSV","TEI-XML","SPECTRA","RADIOCARBON","OTHER")]
    [string]$FileType,

    [Parameter(Mandatory=$true)]
    [string]$Operator,

    [Parameter(Mandatory=$false)]
    [string]$Description = "",

    [Parameter(Mandatory=$false)]
    [string]$CaptureDevice = "",

    [Parameter(Mandatory=$false)]
    [ValidateSet("PUBLIC","RESTRICTED","CONFIDENTIAL","INDIGENOUS-PROTECTED")]
    [string]$SensitivityLevel = "RESTRICTED",

    [Parameter(Mandatory=$false)]
    [string[]]$Tags = @(),

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "",

    [Parameter(Mandatory=$false)]
    [switch]$CopyToVault,

    [Parameter(Mandatory=$false)]
    [string]$SignerKeyPath = "",

    [Parameter(Mandatory=$false)]
    [switch]$SkipTimestamp
)

$ScriptRoot = Split-Path -Parent $PSScriptRoot
$VaultPath = Join-Path $ScriptRoot "Vault"
$LogsPath = Join-Path $ScriptRoot "Logs"
$ConfigPath = Join-Path (Split-Path -Parent $ScriptRoot) "EchoEthicsConfig.json"

# Ensure directories exist
if (-not (Test-Path $VaultPath)) { New-Item -ItemType Directory -Path $VaultPath | Out-Null }
if (-not (Test-Path $LogsPath)) { New-Item -ItemType Directory -Path $LogsPath | Out-Null }

# Load Echo Ethics Config for mode awareness
$echoConfig = if (Test-Path $ConfigPath) {
    Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
} else {
    @{ Mode = "L5" }
}

function Write-AletheiaLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = (Get-Date).ToString("o")
    $logEntry = "[$timestamp] [$Level] $Message"

    $logFile = Join-Path $LogsPath "ingest_$(Get-Date -Format 'yyyyMMdd').log"
    $logEntry | Add-Content -Path $logFile -Encoding UTF8

    $color = switch ($Level) {
        "INFO" { "White" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        default { "Gray" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

function Get-FileHash256 {
    param([string]$Path)

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $hashBytes = $sha256.ComputeHash($stream)
        return [BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()
    }
    finally {
        $stream.Close()
        $sha256.Dispose()
    }
}

function Get-StableID {
    param(
        [string]$FileType,
        [string]$Hash
    )

    $typeKey = $FileType.ToLower().Replace("-", "")
    return "aletheia:${typeKey}:${Hash}"
}

function Get-SimpleSignature {
    param(
        [string]$Data,
        [string]$KeyPath
    )

    # In production, use actual cryptographic signing (ED25519, RSA, etc.)
    # This is a placeholder that creates a hash-based signature
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $dataBytes = [System.Text.Encoding]::UTF8.GetBytes($Data)
    $hashBytes = $sha256.ComputeHash($dataBytes)
    $signature = [Convert]::ToBase64String($hashBytes)
    $sha256.Dispose()

    return @{
        algorithm = "SHA256-HMAC-PLACEHOLDER"
        value = $signature
        note = "Replace with ED25519 or RSA signature in production"
    }
}

function Get-TimestampToken {
    param([string]$Hash)

    # In production, call RFC 3161 TSA or blockchain witness
    # This is a placeholder that records local time with hash
    $timestamp = (Get-Date).ToString("o")

    return @{
        authority = "local-witness"
        value = "PLACEHOLDER:${Hash}:${timestamp}"
        issuedAt = $timestamp
        proofType = "WITNESS-SIGNATURE"
        note = "Replace with RFC3161 TSA response in production"
    }
}

# Validate file exists
if (-not (Test-Path $FilePath)) {
    Write-AletheiaLog "File not found: $FilePath" -Level "ERROR"
    exit 1
}

$file = Get-Item $FilePath
Write-AletheiaLog "Starting artifact sealing: $($file.Name)" -Level "INFO"
Write-AletheiaLog "Echo Mode: $($echoConfig.Mode)" -Level "INFO"

# Step 1: Compute content hash
Write-AletheiaLog "Computing SHA-256 hash..." -Level "INFO"
$contentHash = Get-FileHash256 -Path $FilePath
Write-AletheiaLog "Hash: $contentHash" -Level "INFO"

# Step 2: Generate stable ID
$stableID = Get-StableID -FileType $FileType -Hash $contentHash
Write-AletheiaLog "Stable ID: $stableID" -Level "INFO"

# Step 3: Build metadata
$metadata = @{
    fileType = $FileType
    originalFilename = $file.Name
    byteSize = $file.Length
    captureDate = $file.CreationTimeUtc.ToString("o")
    captureOperator = $Operator
    sensitivityLevel = $SensitivityLevel
}

if ($Description) { $metadata.description = $Description }
if ($CaptureDevice) { $metadata.captureDevice = $CaptureDevice }
if ($Tags.Count -gt 0) { $metadata.tags = $Tags }

# Step 4: Create custody chain entry
$custodyEntry = @{
    party = $Operator
    role = "CUSTODIAN"
    action = "SEALED"
    timestamp = (Get-Date).ToString("o")
    notes = "Initial sealing via Aletheia CLI"
}

$custody = @{
    chain = @($custodyEntry)
    currentCustodian = $Operator
}

# Step 5: Create signature
Write-AletheiaLog "Creating signature..." -Level "INFO"
$signatureData = "$stableID|$contentHash|$($metadata.captureDate)"
$sigResult = Get-SimpleSignature -Data $signatureData -KeyPath $SignerKeyPath

$signature = @{
    algorithm = $sigResult.algorithm
    value = $sigResult.value
    signer = $Operator
    signedAt = (Get-Date).ToString("o")
}

# Step 6: Get trusted timestamp
$timestampToken = $null
if (-not $SkipTimestamp) {
    Write-AletheiaLog "Obtaining timestamp..." -Level "INFO"
    $timestampToken = Get-TimestampToken -Hash $contentHash
}
else {
    $timestampToken = @{
        authority = "SKIPPED"
        value = "TIMESTAMP_SKIPPED"
        issuedAt = (Get-Date).ToString("o")
        proofType = "NONE"
    }
}

# Step 7: Build manifest
$manifest = [ordered]@{
    schemaVersion = "1.0.0"
    stableID = $stableID
    contentHash = @{
        algorithm = "SHA-256"
        value = $contentHash
    }
    metadata = $metadata
    custody = $custody
    signature = $signature
    timestamp = $timestampToken
    echoMode = @{
        level = $echoConfig.Mode
        reviewRequired = ($echoConfig.Mode -eq "L2")
    }
}

# Step 8: Output manifest
$outputFilename = "$($file.BaseName)_manifest.json"
$outputPath = if ($OutputDir) {
    Join-Path $OutputDir $outputFilename
} else {
    Join-Path $file.DirectoryName $outputFilename
}

$manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $outputPath -Encoding UTF8
Write-AletheiaLog "Manifest written: $outputPath" -Level "SUCCESS"

# Step 9: Copy to vault if requested
if ($CopyToVault) {
    $vaultDir = Join-Path $VaultPath $contentHash.Substring(0, 8)
    if (-not (Test-Path $vaultDir)) {
        New-Item -ItemType Directory -Path $vaultDir | Out-Null
    }

    $vaultFilePath = Join-Path $vaultDir $file.Name
    $vaultManifestPath = Join-Path $vaultDir $outputFilename

    Copy-Item -Path $FilePath -Destination $vaultFilePath
    Copy-Item -Path $outputPath -Destination $vaultManifestPath

    Write-AletheiaLog "Artifact copied to vault: $vaultDir" -Level "SUCCESS"
}

# Step 10: Log metrics
$metricsEntry = @{
    timestamp = (Get-Date).ToString("o")
    operation = "SEAL"
    stableID = $stableID
    fileType = $FileType
    byteSize = $file.Length
    echoMode = $echoConfig.Mode
    success = $true
}

$metricsFile = Join-Path $LogsPath "metrics.jsonl"
($metricsEntry | ConvertTo-Json -Compress) | Add-Content -Path $metricsFile -Encoding UTF8

# Output summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ARTIFACT SEALED SUCCESSFULLY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stable ID:    $stableID" -ForegroundColor White
Write-Host "Content Hash: $contentHash" -ForegroundColor Gray
Write-Host "File Type:    $FileType" -ForegroundColor Gray
Write-Host "Size:         $($file.Length) bytes" -ForegroundColor Gray
Write-Host "Manifest:     $outputPath" -ForegroundColor Green
Write-Host ""

if ($echoConfig.Mode -eq "L2") {
    Write-Host "WARNING: L2 Black Lens mode active." -ForegroundColor Red
    Write-Host "This artifact requires Devil Lens review before operational use." -ForegroundColor Yellow
    Write-Host ""
}

# Return manifest object for pipeline use
return $manifest
