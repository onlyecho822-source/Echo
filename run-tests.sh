#!/bin/bash
#
# OMEGA Echo - Master Test Runner
# Runs all component tests in sequence
#

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}   🌌 OMEGA ECHO - MASTER TEST SUITE${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✖ Error: .env file not found${NC}"
    echo ""
    echo "Please create a .env file with:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then generate your OMEGA_SECRET_KEY:"
    echo "  node -e \"console.log(require('crypto').randomBytes(32).toString('hex'))\""
    echo ""
    exit 1
fi

# Source .env file
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
MISSING_VARS=()

if [ -z "$OMEGA_SECRET_KEY" ]; then
    MISSING_VARS+=("OMEGA_SECRET_KEY")
fi

if [ -z "$GITHUB_TOKEN" ]; then
    MISSING_VARS+=("GITHUB_TOKEN")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}✖ Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ node_modules not found, installing dependencies...${NC}"
    npm install
    echo ""
fi

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_file=$2

    echo -e "${CYAN}→ Running ${test_name}...${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))

    if node "$test_file"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✔ ${test_name} PASSED${NC}"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✖ ${test_name} FAILED${NC}"
        # Continue with other tests instead of exiting
    fi

    echo ""
}

# Run tests
run_test "Canary System Test" "test-canary.js"
run_test "Entropy Engine Test" "test-entropy.js"
run_test "GitHub Integration Test" "test-github.js"

# Summary
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}   TEST SUMMARY${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Tests Run: $TESTS_RUN"
echo -e "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  Tests Failed: ${RED}$TESTS_FAILED${NC}"
else
    echo -e "  Tests Failed: $TESTS_FAILED"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}✖ SOME TESTS FAILED${NC}"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    exit 0
fi
