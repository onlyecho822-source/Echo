#!/bin/bash
#
# OMEGA Echo - Test Demo
# Simulates a full test run without requiring real credentials
#

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   🌌 OMEGA ECHO - TEST DEMONSTRATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if lib directory exists
if [ ! -d "lib" ]; then
    echo "✖ Error: lib/ directory not found"
    echo "  Are you in the Echo project root?"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install --silent
    echo ""
fi

# Generate test credentials
echo "→ Generating test credentials..."
TEST_KEY=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")
export OMEGA_SECRET_KEY=$TEST_KEY
export GITHUB_TOKEN="ghp_test_token_for_demonstration"
export GITHUB_REPO="test/demo"
echo "  ✔ Test credentials generated"
echo ""

# Test 1: Module loading
echo "━━━ Test 1: Module Loading ━━━"
echo "→ Loading core modules..."
node -e "
const canary = require('./lib/omegaCanary');
const entropy = require('./lib/omegaEntropy');
const noise = require('./lib/omegaVaultNoise');
console.log('  ✔ omegaCanary.js loaded');
console.log('  ✔ omegaEntropy.js loaded');
console.log('  ✔ omegaVaultNoise.js loaded');
" || exit 1
echo ""

# Test 2: Canary initialization
echo "━━━ Test 2: Canary System ━━━"
node -e "
const { initCanaryModule, writeCanary, checkCanary } = require('./lib/omegaCanary');
try {
    initCanaryModule(process.env.OMEGA_SECRET_KEY);
    console.log('  ✔ Canary module initialized');

    writeCanary();
    console.log('  ✔ Canary file written');

    const status = checkCanary();
    console.log('  ✔ Canary integrity: ' + status);
} catch (error) {
    console.error('  ✖ Error:', error.message);
    process.exit(1);
}
" || exit 1
echo ""

# Test 3: Entropy calculation
echo "━━━ Test 3: Entropy Engine ━━━"
node -e "
const { calculateEntropy, getEntropyLevel } = require('./lib/omegaEntropy');

const entropy1 = calculateEntropy(0, 0, 0, 0);
console.log('  ✔ Zero entropy:', entropy1.toFixed(3));

const entropy2 = calculateEntropy(1, 1, 1, 1);
console.log('  ✔ Max entropy:', entropy2.toFixed(3));

const entropy3 = calculateEntropy(0.5, 0.3, 0.4, 0.2);
console.log('  ✔ Mixed entropy:', entropy3.toFixed(3), '(' + getEntropyLevel(entropy3) + ')');
" || exit 1
echo ""

# Test 4: Metabolic noise
echo "━━━ Test 4: Metabolic Noise ━━━"
node -e "
const { runMetabolicNoise, getNoiseStats } = require('./lib/omegaVaultNoise');

runMetabolicNoise();
const stats = getNoiseStats();
console.log('  ✔ Noise cycle complete');
console.log('  ✔ Dummy reads:', stats.dummyReadsTotal);
console.log('  ✔ Noise generated:', (stats.noiseGeneratedBytes / 1024).toFixed(1), 'KB');
" || exit 1
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ DEMONSTRATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "All core systems operational!"
echo ""
echo "Next steps:"
echo "  1. Add real credentials to .env"
echo "  2. Run: ./run-tests.sh"
echo "  3. Start embryo: node index.js"
echo ""
