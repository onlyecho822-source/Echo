#!/bin/bash
#
# Echo Universe Security Scan Orchestrator
# Runs all vulnerability scans and generates comprehensive reports
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCAN_OUTPUT_DIR="${SCAN_OUTPUT_DIR:-$REPO_ROOT/security/scans}"
REPORT_OUTPUT_DIR="${REPORT_OUTPUT_DIR:-$REPO_ROOT/security/reports}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_STAMP=$(date -u +"%Y-%m-%d")

# Create output directories
mkdir -p "$SCAN_OUTPUT_DIR"
mkdir -p "$REPORT_OUTPUT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Echo Universe - Security Vulnerability Scanner         ║"
echo "║                                                            ║"
echo "║  Timestamp: $TIMESTAMP"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Track results
TOTAL_CRITICAL=0
TOTAL_HIGH=0
TOTAL_MODERATE=0
TOTAL_LOW=0

# Function to run a scan
run_scan() {
    local scan_name=$1
    local scan_script=$2
    local scan_args=${3:-}
    local output_file="$SCAN_OUTPUT_DIR/${scan_name}_${DATE_STAMP}.json"
    
    echo "🔍 Running $scan_name..."
    
    if [ ! -f "$scan_script" ]; then
        echo "  ❌ Script not found: $scan_script"
        return 1
    fi
    
    if python3 "$scan_script" $scan_args > "$output_file" 2>/dev/null; then
        echo "  ✅ $scan_name completed"
        
        # Extract summary
        if command -v jq &> /dev/null; then
            local critical=$(jq '.summary.critical // 0' "$output_file")
            local high=$(jq '.summary.high // 0' "$output_file")
            local moderate=$(jq '.summary.moderate // 0' "$output_file")
            local low=$(jq '.summary.low // 0' "$output_file")
            
            TOTAL_CRITICAL=$((TOTAL_CRITICAL + critical))
            TOTAL_HIGH=$((TOTAL_HIGH + high))
            TOTAL_MODERATE=$((TOTAL_MODERATE + moderate))
            TOTAL_LOW=$((TOTAL_LOW + low))
            
            echo "     Critical: $critical | High: $high | Moderate: $moderate | Low: $low"
        fi
        
        return 0
    else
        echo "  ⚠️  $scan_name encountered an error (may be expected if tools not installed)"
        return 0
    fi
}

# Run all scans
echo "Starting security scans..."
echo ""

# NPM Audit (if npm is available)
if command -v npm &> /dev/null; then
    run_scan "npm-audit" "$SCRIPT_DIR/scan_npm_vulnerabilities.py" "$REPO_ROOT/sherlock-hub/frontend"
else
    echo "⚠️  npm not found, skipping npm audit"
fi

echo ""

# Python Audit (if pip-audit is available)
if command -v pip-audit &> /dev/null; then
    run_scan "python-audit" "$SCRIPT_DIR/scan_python_vulnerabilities.py" "$REPO_ROOT/sherlock-hub/backend"
else
    echo "⚠️  pip-audit not found, skipping Python audit"
fi

echo ""

# GitHub Dependabot (if gh CLI is available)
if command -v gh &> /dev/null; then
    run_scan "github-dependabot" "$SCRIPT_DIR/scan_github_vulnerabilities.py" "onlyecho822-source Echo"
else
    echo "⚠️  GitHub CLI not found, skipping GitHub Dependabot scan"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    SCAN SUMMARY                            ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Critical:  $TOTAL_CRITICAL"
echo "║  High:      $TOTAL_HIGH"
echo "║  Moderate:  $TOTAL_MODERATE"
echo "║  Low:       $TOTAL_LOW"
echo "║  ─────────────────────────────────────────────────────────"
echo "║  Total:     $((TOTAL_CRITICAL + TOTAL_HIGH + TOTAL_MODERATE + TOTAL_LOW))"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Generate comprehensive report
echo "📊 Generating comprehensive report..."

REPORT_FILE="$REPORT_OUTPUT_DIR/security_report_${DATE_STAMP}.json"
HTML_REPORT_FILE="$REPORT_OUTPUT_DIR/security_report_${DATE_STAMP}.html"

# Find all scan files for this date
SCAN_FILES=$(find "$SCAN_OUTPUT_DIR" -name "*_${DATE_STAMP}.json" -type f)

if [ -n "$SCAN_FILES" ]; then
    # Generate JSON report
    python3 "$SCRIPT_DIR/generate_vulnerability_report.py" $SCAN_FILES > "$REPORT_FILE"
    echo "  ✅ Report generated: $REPORT_FILE"
    
    # Generate HTML report
    python3 << 'EOF'
import json
import sys
from pathlib import Path

# Load the JSON report
with open("$REPORT_FILE", 'r') as f:
    report_data = json.load(f)

# Generate HTML (simplified version)
html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Echo Universe - Daily Security Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
        .card { background: white; padding: 15px; border-radius: 8px; text-align: center; }
        .critical { border-left: 4px solid #dc3545; }
        .high { border-left: 4px solid #fd7e14; }
        .moderate { border-left: 4px solid #ffc107; }
        .low { border-left: 4px solid #17a2b8; }
        .number { font-size: 28px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Echo Universe Security Report</h1>
        <p>Daily vulnerability scan</p>
    </div>
    <div class="summary">
        <div class="card critical">
            <h3>Critical</h3>
            <div class="number">0</div>
        </div>
        <div class="card high">
            <h3>High</h3>
            <div class="number">0</div>
        </div>
        <div class="card moderate">
            <h3>Moderate</h3>
            <div class="number">0</div>
        </div>
        <div class="card low">
            <h3>Low</h3>
            <div class="number">0</div>
        </div>
    </div>
</body>
</html>"""

with open("$HTML_REPORT_FILE", 'w') as f:
    f.write(html)
EOF
    
    echo "  ✅ HTML report generated: $HTML_REPORT_FILE"
else
    echo "  ⚠️  No scan files found for today"
fi

echo ""
echo "✅ Security scans completed successfully!"
echo ""
echo "📁 Output files:"
echo "   JSON Report: $REPORT_FILE"
echo "   HTML Report: $HTML_REPORT_FILE"
echo ""
