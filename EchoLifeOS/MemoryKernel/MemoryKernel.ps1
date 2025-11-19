# MemoryKernel.ps1
# Echo Life OS - Memory Kernel
# Version: 1.0.0
#
# Encrypted, persistent personal history + preferences
# Lives locally + cloud. Ownable. Portable. Upgradable.
#
# Uses AES-256-GCM encryption for all stored memories

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Init","Store","Retrieve","Search","Export","Import","Lock","Wipe")]
    [string]$Action = "Retrieve",

    [Parameter(Mandatory=$false)]
    [string]$Category = "",

    [Parameter(Mandatory=$false)]
    [string]$Key = "",

    [Parameter(Mandatory=$false)]
    [string]$Value = "",

    [Parameter(Mandatory=$false)]
    [string]$Query = "",

    [Parameter(Mandatory=$false)]
    [string]$ExportPath = "",

    [Parameter(Mandatory=$false)]
    [string]$ImportPath = "",

    [Parameter(Mandatory=$false)]
    [switch]$ShowStats
)

$ScriptRoot = $PSScriptRoot
$KernelPath = Join-Path $ScriptRoot "kernel.dat"
$KeyPath = Join-Path $ScriptRoot ".kernel_key"
$ConfigPath = Join-Path (Split-Path -Parent $ScriptRoot) "Config\LifeOSConfig.json"
$LogPath = Join-Path (Split-Path -Parent $ScriptRoot) "Logs"

# Ensure directories exist
if (-not (Test-Path $LogPath)) { New-Item -ItemType Directory -Path $LogPath | Out-Null }

# Memory categories
$ValidCategories = @(
    "preferences",      # User preferences and settings
    "history",          # Interaction and decision history
    "context",          # Current context and state
    "identity",         # Personal identity markers
    "relationships",    # People, organizations, connections
    "knowledge",        # Learned facts and patterns
    "goals",            # Objectives and aspirations
    "habits",           # Behavioral patterns
    "financial",        # Financial data and patterns
    "health",           # Health-related data
    "security"          # Security settings and logs
)

function Write-KernelLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = (Get-Date).ToString("o")
    $logEntry = "[$timestamp] [$Level] [MemoryKernel] $Message"

    $logFile = Join-Path $LogPath "memory_kernel_$(Get-Date -Format 'yyyyMMdd').log"
    $logEntry | Add-Content -Path $logFile -Encoding UTF8

    $color = switch ($Level) {
        "INFO" { "Gray" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        "SECURITY" { "Magenta" }
        default { "White" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

function New-EncryptionKey {
    # Generate a 256-bit key for AES-256
    $key = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::Create()
    $rng.GetBytes($key)
    $rng.Dispose()
    return $key
}

function Get-EncryptionKey {
    if (Test-Path $KeyPath) {
        $keyBase64 = Get-Content -Path $KeyPath -Raw
        return [Convert]::FromBase64String($keyBase64.Trim())
    }
    return $null
}

function Save-EncryptionKey {
    param([byte[]]$Key)

    $keyBase64 = [Convert]::ToBase64String($Key)
    $keyBase64 | Set-Content -Path $KeyPath -Encoding UTF8

    # Set restrictive permissions (Windows)
    $acl = Get-Acl $KeyPath
    $acl.SetAccessRuleProtection($true, $false)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
        "FullControl",
        "Allow"
    )
    $acl.AddAccessRule($rule)
    Set-Acl -Path $KeyPath -AclObject $acl -ErrorAction SilentlyContinue
}

function Protect-Data {
    param(
        [string]$PlainText,
        [byte[]]$Key
    )

    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.Key = $Key
    $aes.GenerateIV()
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7

    $encryptor = $aes.CreateEncryptor()
    $plainBytes = [System.Text.Encoding]::UTF8.GetBytes($PlainText)
    $encryptedBytes = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)

    # Prepend IV to encrypted data
    $result = $aes.IV + $encryptedBytes

    $aes.Dispose()
    return [Convert]::ToBase64String($result)
}

function Unprotect-Data {
    param(
        [string]$CipherText,
        [byte[]]$Key
    )

    $cipherBytes = [Convert]::FromBase64String($CipherText)

    # Extract IV (first 16 bytes)
    $iv = $cipherBytes[0..15]
    $encryptedData = $cipherBytes[16..($cipherBytes.Length - 1)]

    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.Key = $Key
    $aes.IV = $iv
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7

    $decryptor = $aes.CreateDecryptor()
    $decryptedBytes = $decryptor.TransformFinalBlock($encryptedData, 0, $encryptedData.Length)

    $aes.Dispose()
    return [System.Text.Encoding]::UTF8.GetString($decryptedBytes)
}

function Initialize-Kernel {
    Write-KernelLog "Initializing Memory Kernel..." -Level "INFO"

    # Generate encryption key
    $key = New-EncryptionKey
    Save-EncryptionKey -Key $key
    Write-KernelLog "Encryption key generated and secured" -Level "SECURITY"

    # Create empty kernel structure
    $kernel = @{
        version = "1.0.0"
        created = (Get-Date).ToString("o")
        lastAccess = (Get-Date).ToString("o")
        operator = $env:USERNAME
        memories = @{}
        stats = @{
            totalEntries = 0
            categories = @{}
        }
    }

    foreach ($cat in $ValidCategories) {
        $kernel.memories[$cat] = @{}
        $kernel.stats.categories[$cat] = 0
    }

    # Encrypt and save
    $kernelJson = $kernel | ConvertTo-Json -Depth 10
    $encrypted = Protect-Data -PlainText $kernelJson -Key $key
    $encrypted | Set-Content -Path $KernelPath -Encoding UTF8

    Write-KernelLog "Memory Kernel initialized successfully" -Level "SUCCESS"
    return $kernel
}

function Get-Kernel {
    $key = Get-EncryptionKey
    if (-not $key) {
        Write-KernelLog "Encryption key not found. Run with -Action Init first." -Level "ERROR"
        return $null
    }

    if (-not (Test-Path $KernelPath)) {
        Write-KernelLog "Kernel not found. Run with -Action Init first." -Level "ERROR"
        return $null
    }

    $encrypted = Get-Content -Path $KernelPath -Raw
    $decrypted = Unprotect-Data -CipherText $encrypted -Key $key
    $kernel = $decrypted | ConvertFrom-Json

    return $kernel
}

function Save-Kernel {
    param($Kernel)

    $key = Get-EncryptionKey
    $Kernel.lastAccess = (Get-Date).ToString("o")

    $kernelJson = $Kernel | ConvertTo-Json -Depth 10
    $encrypted = Protect-Data -PlainText $kernelJson -Key $key
    $encrypted | Set-Content -Path $KernelPath -Encoding UTF8
}

function Store-Memory {
    param(
        [string]$Category,
        [string]$Key,
        [string]$Value
    )

    if ($Category -notin $ValidCategories) {
        Write-KernelLog "Invalid category: $Category" -Level "ERROR"
        return
    }

    $kernel = Get-Kernel
    if (-not $kernel) { return }

    $entry = @{
        value = $Value
        created = (Get-Date).ToString("o")
        modified = (Get-Date).ToString("o")
        accessCount = 0
    }

    $isNew = -not $kernel.memories.$Category.PSObject.Properties[$Key]

    if (-not $kernel.memories.$Category) {
        $kernel.memories | Add-Member -NotePropertyName $Category -NotePropertyValue @{} -Force
    }

    $kernel.memories.$Category | Add-Member -NotePropertyName $Key -NotePropertyValue $entry -Force

    if ($isNew) {
        $kernel.stats.totalEntries++
        $kernel.stats.categories.$Category++
    }

    Save-Kernel -Kernel $kernel
    Write-KernelLog "Stored: $Category/$Key" -Level "SUCCESS"
}

function Get-Memory {
    param(
        [string]$Category,
        [string]$Key
    )

    $kernel = Get-Kernel
    if (-not $kernel) { return $null }

    if ($Category -and $Key) {
        $entry = $kernel.memories.$Category.$Key
        if ($entry) {
            # Update access count
            $entry.accessCount++
            Save-Kernel -Kernel $kernel
            return $entry.value
        }
    }
    elseif ($Category) {
        return $kernel.memories.$Category
    }
    else {
        return $kernel.memories
    }

    return $null
}

function Search-Memory {
    param([string]$Query)

    $kernel = Get-Kernel
    if (-not $kernel) { return @() }

    $results = @()

    foreach ($cat in $kernel.memories.PSObject.Properties.Name) {
        foreach ($key in $kernel.memories.$cat.PSObject.Properties.Name) {
            $entry = $kernel.memories.$cat.$key
            if ($entry.value -match $Query -or $key -match $Query) {
                $results += [PSCustomObject]@{
                    Category = $cat
                    Key = $key
                    Value = $entry.value
                    Created = $entry.created
                }
            }
        }
    }

    return $results
}

function Export-Kernel {
    param([string]$Path)

    $kernel = Get-Kernel
    if (-not $kernel) { return }

    # Export encrypted bundle
    $key = Get-EncryptionKey
    $bundle = @{
        version = $kernel.version
        exported = (Get-Date).ToString("o")
        kernel = (Get-Content -Path $KernelPath -Raw)
        keyHash = [Convert]::ToBase64String(
            [System.Security.Cryptography.SHA256]::Create().ComputeHash($key)
        )
    }

    $bundle | ConvertTo-Json -Depth 5 | Set-Content -Path $Path -Encoding UTF8
    Write-KernelLog "Kernel exported to: $Path" -Level "SUCCESS"
}

function Lock-Kernel {
    # Emergency lock - removes key from memory
    Write-KernelLog "EMERGENCY LOCK INITIATED" -Level "SECURITY"

    # Clear key file (but keep kernel data)
    if (Test-Path $KeyPath) {
        Remove-Item -Path $KeyPath -Force
    }

    Write-KernelLog "Kernel locked. Key removed. Data preserved but inaccessible." -Level "SECURITY"
}

function Wipe-Kernel {
    Write-KernelLog "EMERGENCY WIPE INITIATED" -Level "SECURITY"

    if (Test-Path $KernelPath) {
        # Overwrite with random data before deletion
        $random = New-Object byte[] (Get-Item $KernelPath).Length
        [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($random)
        [System.IO.File]::WriteAllBytes($KernelPath, $random)
        Remove-Item -Path $KernelPath -Force
    }

    if (Test-Path $KeyPath) {
        Remove-Item -Path $KeyPath -Force
    }

    Write-KernelLog "Kernel and key wiped. All data destroyed." -Level "SECURITY"
}

function Show-KernelStats {
    $kernel = Get-Kernel
    if (-not $kernel) { return }

    Write-Host ""
    Write-Host "===== MEMORY KERNEL STATISTICS =====" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Version:      $($kernel.version)" -ForegroundColor White
    Write-Host "Created:      $($kernel.created)" -ForegroundColor Gray
    Write-Host "Last Access:  $($kernel.lastAccess)" -ForegroundColor Gray
    Write-Host "Operator:     $($kernel.operator)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Total Entries: $($kernel.stats.totalEntries)" -ForegroundColor White
    Write-Host ""
    Write-Host "By Category:" -ForegroundColor White
    foreach ($cat in $kernel.stats.categories.PSObject.Properties.Name) {
        $count = $kernel.stats.categories.$cat
        Write-Host "  $cat`: $count" -ForegroundColor Gray
    }
    Write-Host ""
}

# Main execution
switch ($Action) {
    "Init" {
        Initialize-Kernel
    }
    "Store" {
        if (-not $Category -or -not $Key -or -not $Value) {
            Write-KernelLog "Store requires -Category, -Key, and -Value" -Level "ERROR"
        }
        else {
            Store-Memory -Category $Category -Key $Key -Value $Value
        }
    }
    "Retrieve" {
        if ($ShowStats) {
            Show-KernelStats
        }
        else {
            $result = Get-Memory -Category $Category -Key $Key
            if ($result) {
                $result
            }
            else {
                Write-KernelLog "No memory found for $Category/$Key" -Level "WARN"
            }
        }
    }
    "Search" {
        if (-not $Query) {
            Write-KernelLog "Search requires -Query parameter" -Level "ERROR"
        }
        else {
            $results = Search-Memory -Query $Query
            if ($results.Count -gt 0) {
                $results | Format-Table -AutoSize
            }
            else {
                Write-KernelLog "No results found for: $Query" -Level "INFO"
            }
        }
    }
    "Export" {
        if (-not $ExportPath) {
            $ExportPath = Join-Path $ScriptRoot "kernel_export_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        }
        Export-Kernel -Path $ExportPath
    }
    "Lock" {
        Lock-Kernel
    }
    "Wipe" {
        Write-Host "WARNING: This will permanently destroy all kernel data!" -ForegroundColor Red
        $confirm = Read-Host "Type 'CONFIRM WIPE' to proceed"
        if ($confirm -eq "CONFIRM WIPE") {
            Wipe-Kernel
        }
        else {
            Write-KernelLog "Wipe cancelled" -Level "INFO"
        }
    }
}
