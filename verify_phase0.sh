#!/bin/bash
# Phase 0 Verification Script
# Run this to verify lockdown is complete

echo "=========================================="
echo "PHASE 0 VERIFICATION"
echo "=========================================="
echo ""

# Check 1: Branch Protection
echo "Check 1: Branch Protection Status"
echo "------------------------------------------"

if ! command -v gh &> /dev/null; then
    echo "⚠️  WARNING: GitHub CLI (gh) not installed"
    echo "   Install: brew install gh (Mac) or apt install gh (Linux)"
    echo "   Manual check: https://github.com/onlyecho822-source/Echo/settings/branches"
else
    gh api repos/onlyecho822-source/Echo/branches/main/protection &> /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ PASS: Branch protection is enabled"
    else
        echo "❌ FAIL: Branch protection is NOT enabled"
        echo "   Action: Go to https://github.com/onlyecho822-source/Echo/settings/branches"
    fi
fi
echo ""

# Check 2: Direct Commit Test
echo "Check 2: Direct Commit Prevention"
echo "------------------------------------------"
echo "Testing if direct commits to main are blocked..."

# Create a temporary change
echo "# Test" >> .phase0_test
git add .phase0_test 2>/dev/null

if git diff --staged --quiet; then
    echo "⚠️  WARNING: No changes to test"
else
    git commit -m "test: Phase 0 verification" &> /dev/null
    
    # Try to push
    git push origin main &> /tmp/push_test.log 2>&1
    
    if grep -q "protected branch" /tmp/push_test.log || grep -q "GH006" /tmp/push_test.log; then
        echo "✅ PASS: Direct commits are blocked"
        # Clean up
        git reset HEAD~1 &> /dev/null
        rm .phase0_test
    else
        echo "❌ FAIL: Direct commits are NOT blocked"
        echo "   Branch protection may not be configured correctly"
        # Clean up
        git reset HEAD~1 &> /dev/null
        rm .phase0_test
    fi
fi
echo ""

# Check 3: Dependabot Status
echo "Check 3: Dependabot Status"
echo "------------------------------------------"
if command -v gh &> /dev/null; then
    # Check if Dependabot alerts are enabled
    gh api repos/onlyecho822-source/Echo &> /tmp/repo_check.json
    
    if grep -q '"has_vulnerability_alerts":\s*true' /tmp/repo_check.json; then
        echo "✅ PASS: Dependabot alerts are enabled"
    else
        echo "❌ FAIL: Dependabot alerts are NOT enabled"
        echo "   Action: Go to https://github.com/onlyecho822-source/Echo/settings/security_analysis"
    fi
else
    echo "⚠️  WARNING: Cannot verify (gh CLI not installed)"
    echo "   Manual check: https://github.com/onlyecho822-source/Echo/settings/security_analysis"
fi
echo ""

# Summary
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo ""
echo "If all checks show ✅ PASS, Phase 0 is complete."
echo "If any show ❌ FAIL, fix those issues before proceeding."
echo ""
echo "Next step: Run Phase 1 implementation"
echo ""
