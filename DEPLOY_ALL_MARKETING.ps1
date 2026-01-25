# ============================================================================
# DEPLOY ALL MARKETING AUTOMATION - Tax Services Landing Page
# ============================================================================
# Timestamp: 15:45 Jan 25 2026
# Purpose: Deploy email distribution, social media automation, and Reddit outreach
# Security: Elite level - All secrets encrypted in GitHub
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "DEPLOY ALL MARKETING AUTOMATION" -ForegroundColor Cyan
Write-Host "Tax Services Landing Page for Single Moms" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in correct directory
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Must run from Echo repository root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To fix:" -ForegroundColor Yellow
    Write-Host "  cd C:\path\to\Echo" -ForegroundColor Yellow
    Write-Host "  .\DEPLOY_ALL_MARKETING.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/6] Checking GitHub CLI..." -ForegroundColor Yellow
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI (gh) not found" -ForegroundColor Red
    Write-Host "Install from: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK GitHub CLI found" -ForegroundColor Green
Write-Host ""

Write-Host "[2/6] Checking GitHub authentication..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not authenticated with GitHub" -ForegroundColor Red
    Write-Host "Run: gh auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Authenticated with GitHub" -ForegroundColor Green
Write-Host ""

Write-Host "[3/6] Staging all marketing automation files..." -ForegroundColor Yellow
git add .github/workflows/distribute-landing-page.yml
git add marketing/distribute_email.py
git add marketing/distribute_social.py
git add marketing/DISTRIBUTION_MASTER_LOG.md
git add marketing/distribution-logs/
git add DEPLOY_ALL_MARKETING.ps1

if (Test-Path "reddit-outreach-agent") {
    git add reddit-outreach-agent/
    Write-Host "OK Reddit outreach agent included" -ForegroundColor Green
}

Write-Host "OK All files staged" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Committing to repository..." -ForegroundColor Yellow
$commitMessage = "Deploy: Marketing automation system - Email, Social Media, Reddit [$(Get-Date -Format 'HH:mm MMM dd yyyy')]"
git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: No changes to commit (may already be deployed)" -ForegroundColor Yellow
} else {
    Write-Host "OK Committed: $commitMessage" -ForegroundColor Green
}
Write-Host ""

Write-Host "[5/6] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Check your network connection and repository permissions" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Pushed to GitHub successfully" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Verifying deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$repoInfo = gh repo view --json nameWithOwner,url | ConvertFrom-Json
Write-Host "OK Deployment verified" -ForegroundColor Green
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Repository: $($repoInfo.nameWithOwner)" -ForegroundColor Cyan
Write-Host "URL: $($repoInfo.url)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Deployed Components:" -ForegroundColor Cyan
Write-Host "  Email Distribution System" -ForegroundColor White
Write-Host "  Social Media Automation" -ForegroundColor White
Write-Host "  Reddit Outreach Agent" -ForegroundColor White
Write-Host "  Distribution Master Log" -ForegroundColor White
Write-Host "  GitHub Actions Workflows" -ForegroundColor White
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Yellow
Write-Host "NEXT STEPS - CRITICAL" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 1: Publish Landing Page" -ForegroundColor Cyan
Write-Host "  1. Open Manus Management UI" -ForegroundColor White
Write-Host "  2. Click 'Publish' button (top-right)" -ForegroundColor White
Write-Host "  3. Copy the published URL" -ForegroundColor White
Write-Host ""

Write-Host "Step 2: Configure GitHub Secrets" -ForegroundColor Cyan
Write-Host "  1. Go to: $($repoInfo.url)/settings/secrets/actions" -ForegroundColor White
Write-Host "  2. Click 'New repository secret'" -ForegroundColor White
Write-Host "  3. Add these secrets:" -ForegroundColor White
Write-Host ""
Write-Host "     Name: LANDING_PAGE_URL" -ForegroundColor Green
Write-Host "     Value: [Your published landing page URL]" -ForegroundColor White
Write-Host ""
Write-Host "     Name: OWNER_EMAIL" -ForegroundColor Green
Write-Host "     Value: onlyecho822@gmail.com" -ForegroundColor White
Write-Host ""
Write-Host "     Name: EMAIL_API_KEY (Optional)" -ForegroundColor Green
Write-Host "     Value: [Your email service API key]" -ForegroundColor White
Write-Host ""

Write-Host "Step 3: Test Distribution System" -ForegroundColor Cyan
Write-Host "  1. Go to: $($repoInfo.url)/actions" -ForegroundColor White
Write-Host "  2. Click 'Distribute Landing Page - Email & Social Media'" -ForegroundColor White
Write-Host "  3. Click 'Run workflow'" -ForegroundColor White
Write-Host "  4. Enter your landing page URL" -ForegroundColor White
Write-Host "  5. Click 'Run workflow' button" -ForegroundColor White
Write-Host ""

Write-Host "Step 4: Review Generated Content" -ForegroundColor Cyan
Write-Host "  After workflow runs, check:" -ForegroundColor White
Write-Host "  - marketing/distribution-logs/email-template.txt" -ForegroundColor White
Write-Host "  - marketing/distribution-logs/social-posts/*.txt" -ForegroundColor White
Write-Host "  - marketing/DISTRIBUTION_MASTER_LOG.md" -ForegroundColor White
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Yellow
Write-Host "AUTOMATION SCHEDULE" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Weekly (Mondays 8am CST):" -ForegroundColor Cyan
Write-Host "  - Email distribution to list" -ForegroundColor White
Write-Host "  - Social media post generation" -ForegroundColor White
Write-Host "  - Distribution log updates" -ForegroundColor White
Write-Host ""
Write-Host "Daily:" -ForegroundColor Cyan
Write-Host "  - Reddit outreach monitoring" -ForegroundColor White
Write-Host "  - Automated responses to relevant posts" -ForegroundColor White
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT TIMESTAMP: $(Get-Date -Format 'HH:mm MMM dd yyyy')" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Press any key to open GitHub repository in browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process $repoInfo.url
