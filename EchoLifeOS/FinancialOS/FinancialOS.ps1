# FinancialOS.ps1
# Echo Life OS - Financial OS Engine
# Version: 1.0.0
#
# Personal financial intelligence layer providing:
# - Income tracking and optimization
# - Savings automation
# - Fraud detection
# - Opportunity identification
# - Financial modeling
# - Passive income automation

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Dashboard","Track","Analyze","Optimize","Alert","Model","Report")]
    [string]$Action = "Dashboard",

    [Parameter(Mandatory=$false)]
    [ValidateSet("Income","Expense","Savings","Investment","Debt","All")]
    [string]$Category = "All",

    [Parameter(Mandatory=$false)]
    [decimal]$Amount = 0,

    [Parameter(Mandatory=$false)]
    [string]$Description = "",

    [Parameter(Mandatory=$false)]
    [string]$Source = "",

    [Parameter(Mandatory=$false)]
    [switch]$Detailed
)

$ScriptRoot = $PSScriptRoot
$ParentRoot = Split-Path -Parent $ScriptRoot
$LogPath = Join-Path $ParentRoot "Logs"
$DataPath = Join-Path $ScriptRoot "financial_data.json"

# Ensure directories exist
if (-not (Test-Path $LogPath)) { New-Item -ItemType Directory -Path $LogPath | Out-Null }

# Initialize financial data structure
function Initialize-FinancialData {
    return @{
        version = "1.0.0"
        created = (Get-Date).ToString("o")
        lastUpdated = (Get-Date).ToString("o")
        accounts = @{
            income = @{
                entries = @()
                totalMonthly = 0
                sources = @{}
            }
            expenses = @{
                entries = @()
                totalMonthly = 0
                categories = @{}
            }
            savings = @{
                current = 0
                goal = 0
                rate = 0
                history = @()
            }
            investments = @{
                portfolio = @()
                totalValue = 0
                allocation = @{}
            }
            debt = @{
                accounts = @()
                totalOwed = 0
                monthlyPayment = 0
            }
        }
        metrics = @{
            netWorth = 0
            monthlyNetIncome = 0
            savingsRate = 0
            debtToIncome = 0
            emergencyFundMonths = 0
        }
        alerts = @()
        opportunities = @()
        automations = @()
    }
}

function Get-FinancialData {
    if (Test-Path $DataPath) {
        return Get-Content -Path $DataPath -Raw | ConvertFrom-Json
    }
    $data = Initialize-FinancialData
    Save-FinancialData -Data $data
    return $data
}

function Save-FinancialData {
    param($Data)
    $Data.lastUpdated = (Get-Date).ToString("o")
    $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $DataPath -Encoding UTF8
}

function Write-FinancialLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = (Get-Date).ToString("o")
    $logEntry = "[$timestamp] [$Level] [FinancialOS] $Message"

    $logFile = Join-Path $LogPath "financial_os_$(Get-Date -Format 'yyyyMMdd').log"
    $logEntry | Add-Content -Path $logFile -Encoding UTF8

    $color = switch ($Level) {
        "INFO"    { "Gray" }
        "SUCCESS" { "Green" }
        "WARN"    { "Yellow" }
        "ERROR"   { "Red" }
        "MONEY"   { "Cyan" }
        default   { "White" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

function Add-Transaction {
    param(
        [string]$Type,
        [decimal]$Amount,
        [string]$Description,
        [string]$Source
    )

    $data = Get-FinancialData

    $entry = @{
        id = [guid]::NewGuid().ToString()
        timestamp = (Get-Date).ToString("o")
        amount = $Amount
        description = $Description
        source = $Source
        recurring = $false
    }

    switch ($Type) {
        "Income" {
            $data.accounts.income.entries += $entry
            if (-not $data.accounts.income.sources.$Source) {
                $data.accounts.income.sources | Add-Member -NotePropertyName $Source -NotePropertyValue 0 -Force
            }
            $data.accounts.income.sources.$Source += $Amount
            Write-FinancialLog "Income recorded: $Amount from $Source" -Level "MONEY"
        }
        "Expense" {
            $data.accounts.expenses.entries += $entry
            if (-not $data.accounts.expenses.categories.$Source) {
                $data.accounts.expenses.categories | Add-Member -NotePropertyName $Source -NotePropertyValue 0 -Force
            }
            $data.accounts.expenses.categories.$Source += $Amount
            Write-FinancialLog "Expense recorded: $Amount for $Description" -Level "INFO"
        }
        "Savings" {
            $data.accounts.savings.current += $Amount
            $historyEntry = @{
                timestamp = (Get-Date).ToString("o")
                amount = $Amount
                balance = $data.accounts.savings.current
            }
            $data.accounts.savings.history += $historyEntry
            Write-FinancialLog "Savings deposit: $Amount (Total: $($data.accounts.savings.current))" -Level "SUCCESS"
        }
    }

    # Recalculate metrics
    Update-Metrics -Data $data

    Save-FinancialData -Data $data
    return $entry
}

function Update-Metrics {
    param($Data)

    # Calculate monthly income (last 30 days)
    $thirtyDaysAgo = (Get-Date).AddDays(-30)
    $recentIncome = $Data.accounts.income.entries | Where-Object {
        [datetime]$_.timestamp -gt $thirtyDaysAgo
    }
    $Data.accounts.income.totalMonthly = ($recentIncome | Measure-Object -Property amount -Sum).Sum
    if (-not $Data.accounts.income.totalMonthly) { $Data.accounts.income.totalMonthly = 0 }

    # Calculate monthly expenses
    $recentExpenses = $Data.accounts.expenses.entries | Where-Object {
        [datetime]$_.timestamp -gt $thirtyDaysAgo
    }
    $Data.accounts.expenses.totalMonthly = ($recentExpenses | Measure-Object -Property amount -Sum).Sum
    if (-not $Data.accounts.expenses.totalMonthly) { $Data.accounts.expenses.totalMonthly = 0 }

    # Calculate net metrics
    $Data.metrics.monthlyNetIncome = $Data.accounts.income.totalMonthly - $Data.accounts.expenses.totalMonthly

    if ($Data.accounts.income.totalMonthly -gt 0) {
        $Data.metrics.savingsRate = [math]::Round(($Data.metrics.monthlyNetIncome / $Data.accounts.income.totalMonthly) * 100, 2)
        $Data.metrics.debtToIncome = [math]::Round(($Data.accounts.debt.monthlyPayment / $Data.accounts.income.totalMonthly) * 100, 2)
    }

    if ($Data.accounts.expenses.totalMonthly -gt 0) {
        $Data.metrics.emergencyFundMonths = [math]::Round($Data.accounts.savings.current / $Data.accounts.expenses.totalMonthly, 1)
    }

    # Net worth
    $Data.metrics.netWorth = $Data.accounts.savings.current + $Data.accounts.investments.totalValue - $Data.accounts.debt.totalOwed
}

function Show-Dashboard {
    $data = Get-FinancialData

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  FINANCIAL OS - DASHBOARD" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Key metrics
    Write-Host "Key Metrics:" -ForegroundColor White
    Write-Host "  Net Worth:           $($data.metrics.netWorth.ToString('C'))" -ForegroundColor $(if ($data.metrics.netWorth -ge 0) { "Green" } else { "Red" })
    Write-Host "  Monthly Net Income:  $($data.metrics.monthlyNetIncome.ToString('C'))" -ForegroundColor $(if ($data.metrics.monthlyNetIncome -ge 0) { "Green" } else { "Red" })
    Write-Host "  Savings Rate:        $($data.metrics.savingsRate)%" -ForegroundColor $(if ($data.metrics.savingsRate -ge 20) { "Green" } elseif ($data.metrics.savingsRate -ge 10) { "Yellow" } else { "Red" })
    Write-Host "  Emergency Fund:      $($data.metrics.emergencyFundMonths) months" -ForegroundColor $(if ($data.metrics.emergencyFundMonths -ge 6) { "Green" } elseif ($data.metrics.emergencyFundMonths -ge 3) { "Yellow" } else { "Red" })
    Write-Host ""

    # Monthly summary
    Write-Host "Monthly Summary:" -ForegroundColor White
    Write-Host "  Income:    $($data.accounts.income.totalMonthly.ToString('C'))" -ForegroundColor Green
    Write-Host "  Expenses:  $($data.accounts.expenses.totalMonthly.ToString('C'))" -ForegroundColor Red
    Write-Host "  Savings:   $($data.accounts.savings.current.ToString('C'))" -ForegroundColor Cyan
    Write-Host ""

    if ($Detailed) {
        # Income sources
        if ($data.accounts.income.sources.PSObject.Properties.Count -gt 0) {
            Write-Host "Income Sources:" -ForegroundColor White
            foreach ($source in $data.accounts.income.sources.PSObject.Properties) {
                Write-Host "  $($source.Name): $($source.Value.ToString('C'))" -ForegroundColor Gray
            }
            Write-Host ""
        }

        # Expense categories
        if ($data.accounts.expenses.categories.PSObject.Properties.Count -gt 0) {
            Write-Host "Expense Categories:" -ForegroundColor White
            foreach ($cat in $data.accounts.expenses.categories.PSObject.Properties) {
                Write-Host "  $($cat.Name): $($cat.Value.ToString('C'))" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }

    # Alerts
    $activeAlerts = $data.alerts | Where-Object { $_.status -eq "ACTIVE" }
    if ($activeAlerts.Count -gt 0) {
        Write-Host "Active Alerts:" -ForegroundColor Yellow
        foreach ($alert in $activeAlerts) {
            Write-Host "  - $($alert.message)" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    # Opportunities
    if ($data.opportunities.Count -gt 0) {
        Write-Host "Opportunities Identified:" -ForegroundColor Green
        foreach ($opp in $data.opportunities | Select-Object -First 3) {
            Write-Host "  - $($opp.title)" -ForegroundColor Green
        }
        Write-Host ""
    }

    Write-Host "Last Updated: $($data.lastUpdated)" -ForegroundColor Gray
    Write-Host ""
}

function Analyze-Finances {
    $data = Get-FinancialData

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  FINANCIAL ANALYSIS" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Spending patterns
    Write-Host "Spending Analysis:" -ForegroundColor White

    if ($data.accounts.expenses.categories.PSObject.Properties.Count -gt 0) {
        $total = ($data.accounts.expenses.categories.PSObject.Properties.Value | Measure-Object -Sum).Sum
        foreach ($cat in $data.accounts.expenses.categories.PSObject.Properties | Sort-Object Value -Descending) {
            $pct = if ($total -gt 0) { [math]::Round(($cat.Value / $total) * 100, 1) } else { 0 }
            $bar = "█" * [math]::Min([math]::Floor($pct / 5), 20)
            Write-Host "  $($cat.Name): $pct% $bar" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No expense data available" -ForegroundColor Gray
    }
    Write-Host ""

    # Health indicators
    Write-Host "Financial Health Indicators:" -ForegroundColor White

    # 50/30/20 rule check
    $needsRatio = 50
    $wantsRatio = 30
    $savingsRatio = 20

    Write-Host "  Recommended Budget (50/30/20 Rule):" -ForegroundColor Gray
    Write-Host "    Needs (50%): $([math]::Round($data.accounts.income.totalMonthly * 0.5, 2).ToString('C'))" -ForegroundColor Gray
    Write-Host "    Wants (30%): $([math]::Round($data.accounts.income.totalMonthly * 0.3, 2).ToString('C'))" -ForegroundColor Gray
    Write-Host "    Savings (20%): $([math]::Round($data.accounts.income.totalMonthly * 0.2, 2).ToString('C'))" -ForegroundColor Gray
    Write-Host ""

    # Recommendations
    Write-Host "Recommendations:" -ForegroundColor White

    if ($data.metrics.emergencyFundMonths -lt 3) {
        Write-Host "  - Build emergency fund to at least 3 months expenses" -ForegroundColor Yellow
    }
    if ($data.metrics.savingsRate -lt 10) {
        Write-Host "  - Increase savings rate to at least 10%" -ForegroundColor Yellow
    }
    if ($data.metrics.debtToIncome -gt 36) {
        Write-Host "  - Reduce debt-to-income ratio below 36%" -ForegroundColor Yellow
    }
    if ($data.accounts.income.sources.PSObject.Properties.Count -le 1) {
        Write-Host "  - Diversify income sources" -ForegroundColor Yellow
    }

    Write-Host ""
}

function Find-Opportunities {
    $data = Get-FinancialData

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  OPTIMIZATION OPPORTUNITIES" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    $opportunities = @()

    # Check for optimization opportunities
    if ($data.accounts.income.totalMonthly -gt 0) {
        # High cash reserves
        if ($data.metrics.emergencyFundMonths -gt 12) {
            $opportunities += @{
                id = [guid]::NewGuid().ToString()
                title = "Excess Cash Reserves"
                description = "Emergency fund exceeds 12 months. Consider investing excess."
                potential = $data.accounts.savings.current - ($data.accounts.expenses.totalMonthly * 6)
                category = "Investment"
                priority = "MEDIUM"
            }
        }

        # Income diversification
        if ($data.accounts.income.sources.PSObject.Properties.Count -eq 1) {
            $opportunities += @{
                id = [guid]::NewGuid().ToString()
                title = "Single Income Source Risk"
                description = "All income from one source. Consider diversification."
                potential = $data.accounts.income.totalMonthly * 0.1
                category = "Income"
                priority = "HIGH"
            }
        }

        # Expense optimization
        $highestExpense = $data.accounts.expenses.categories.PSObject.Properties |
            Sort-Object Value -Descending | Select-Object -First 1
        if ($highestExpense -and $highestExpense.Value -gt ($data.accounts.income.totalMonthly * 0.3)) {
            $opportunities += @{
                id = [guid]::NewGuid().ToString()
                title = "High $($highestExpense.Name) Spending"
                description = "$($highestExpense.Name) exceeds 30% of income. Review for optimization."
                potential = $highestExpense.Value * 0.1
                category = "Expense"
                priority = "MEDIUM"
            }
        }
    }

    # Default opportunity
    if ($opportunities.Count -eq 0) {
        $opportunities += @{
            id = [guid]::NewGuid().ToString()
            title = "Track More Data"
            description = "Add income and expense data to unlock optimization insights."
            potential = 0
            category = "Data"
            priority = "HIGH"
        }
    }

    # Display opportunities
    foreach ($opp in $opportunities) {
        $color = switch ($opp.priority) {
            "HIGH"   { "Red" }
            "MEDIUM" { "Yellow" }
            "LOW"    { "Gray" }
            default  { "White" }
        }
        Write-Host "[$($opp.priority)] $($opp.title)" -ForegroundColor $color
        Write-Host "  $($opp.description)" -ForegroundColor Gray
        if ($opp.potential -gt 0) {
            Write-Host "  Potential: $($opp.potential.ToString('C'))/month" -ForegroundColor Green
        }
        Write-Host ""
    }

    # Save opportunities
    $data.opportunities = $opportunities
    Save-FinancialData -Data $data
}

function Show-FinancialReport {
    Show-Dashboard
    Analyze-Finances
    Find-Opportunities
}

# Main execution
switch ($Action) {
    "Dashboard" {
        Show-Dashboard
    }
    "Track" {
        if ($Amount -eq 0) {
            Write-FinancialLog "Track requires -Amount parameter" -Level "ERROR"
        }
        elseif ($Category -eq "All") {
            Write-FinancialLog "Track requires specific -Category (Income, Expense, Savings)" -Level "ERROR"
        }
        else {
            Add-Transaction -Type $Category -Amount $Amount -Description $Description -Source $Source
        }
    }
    "Analyze" {
        Analyze-Finances
    }
    "Optimize" {
        Find-Opportunities
    }
    "Report" {
        Show-FinancialReport
    }
    "Model" {
        Write-Host ""
        Write-Host "Financial Modeling:" -ForegroundColor Cyan
        Write-Host "  This feature will project future scenarios based on current data." -ForegroundColor Gray
        Write-Host "  Coming in v1.1" -ForegroundColor Yellow
        Write-Host ""
    }
}
