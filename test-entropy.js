#!/usr/bin/env node
/**
 * OMEGA Echo - Entropy Engine Test
 * Tests entropy calculation and chaos factor algorithms
 */

const {
    calculateEntropy,
    calculateGitHubChaos,
    calculateCanaryChaos,
    getEntropyLevel,
    shouldTriggerRitual
} = require('./lib/omegaEntropy');

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('   🧪 ENTROPY ENGINE TEST');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

let testsPassed = 0;
let testsFailed = 0;

function pass(message) {
    console.log(`✅ PASS: ${message}`);
    testsPassed++;
}

function fail(message) {
    console.error(`❌ FAIL: ${message}`);
    testsFailed++;
}

function assertClose(actual, expected, tolerance = 0.001, label = '') {
    if (Math.abs(actual - expected) <= tolerance) {
        pass(`${label} (${actual.toFixed(3)} ≈ ${expected})`);
        return true;
    } else {
        fail(`${label}: expected ${expected}, got ${actual.toFixed(3)}`);
        return false;
    }
}

// Test 1: Zero entropy
console.log('Test 1: Calculate entropy with zero inputs');
const entropy1 = calculateEntropy(0, 0, 0, 0);
assertClose(entropy1, 0, 0.001, 'Zero entropy');
console.log('');

// Test 2: Maximum entropy
console.log('Test 2: Calculate entropy with maximum inputs');
const entropy2 = calculateEntropy(1, 1, 1, 1);
assertClose(entropy2, 1.0, 0.001, 'Maximum entropy');
console.log('');

// Test 3: Weighted entropy calculation
console.log('Test 3: Verify weighted entropy calculation');
// Weights: signal=0.15, latency=0.20, github=0.45, canary=0.20
const entropy3 = calculateEntropy(1, 0, 0, 0); // Only signal
assertClose(entropy3, 0.15, 0.001, 'Signal-only entropy');

const entropy4 = calculateEntropy(0, 1, 0, 0); // Only latency
assertClose(entropy4, 0.20, 0.001, 'Latency-only entropy');

const entropy5 = calculateEntropy(0, 0, 1, 0); // Only GitHub
assertClose(entropy5, 0.45, 0.001, 'GitHub-only entropy');

const entropy6 = calculateEntropy(0, 0, 0, 1); // Only canary
assertClose(entropy6, 0.20, 0.001, 'Canary-only entropy');
console.log('');

// Test 4: Input clamping (values >1 should clamp to 1)
console.log('Test 4: Verify input clamping');
const entropy7 = calculateEntropy(5, 5, 5, 5);
assertClose(entropy7, 1.0, 0.001, 'Clamped entropy');
console.log('');

// Test 5: GitHub chaos calculation - healthy repo
console.log('Test 5: GitHub chaos - healthy repository');
const healthyGitHub = {
    openIssues: 5,
    latestWorkflowStatus: 'success',
    branchProtection: {
        status: 'Configured',
        enforceAdmins: true
    },
    webhooks: [
        { active: true, lastDeliveryStatus: 'success' }
    ],
    lastPush: new Date().toISOString()
};
const healthyChaos = calculateGitHubChaos(healthyGitHub);
console.log(`  Healthy repo chaos: ${healthyChaos.toFixed(3)}`);
if (healthyChaos < 0.3) {
    pass('Healthy repo has low chaos');
} else {
    fail(`Expected low chaos (<0.3), got ${healthyChaos.toFixed(3)}`);
}
console.log('');

// Test 6: GitHub chaos calculation - unhealthy repo
console.log('Test 6: GitHub chaos - unhealthy repository');
const unhealthyGitHub = {
    openIssues: 100,
    latestWorkflowStatus: 'failure',
    branchProtection: {
        status: 'Not Configured or No Scope',
        enforceAdmins: false
    },
    webhooks: [
        { active: false, lastDeliveryStatus: 'failed' }
    ],
    lastPush: new Date(Date.now() - 40 * 24 * 60 * 60 * 1000).toISOString() // 40 days ago
};
const unhealthyChaos = calculateGitHubChaos(unhealthyGitHub);
console.log(`  Unhealthy repo chaos: ${unhealthyChaos.toFixed(3)}`);
if (unhealthyChaos > 0.6) {
    pass('Unhealthy repo has high chaos');
} else {
    fail(`Expected high chaos (>0.6), got ${unhealthyChaos.toFixed(3)}`);
}
console.log('');

// Test 7: GitHub chaos - error state
console.log('Test 7: GitHub chaos - error/unavailable state');
const errorGitHub = { error: 'API unavailable' };
const errorChaos = calculateGitHubChaos(errorGitHub);
assertClose(errorChaos, 1.0, 0.001, 'Error state chaos');
console.log('');

// Test 8: Canary chaos mapping
console.log('Test 8: Canary chaos status mapping');
const canaryTests = [
    ['OK', 0.0],
    ['STALE', 0.3],
    ['MISSING', 0.8],
    ['TAMPERED_HASH', 1.0],
    ['TAMPERED_CONTENT', 1.0],
    ['ERROR', 0.6],
    ['UNKNOWN', 0.5] // Default case
];

for (const [status, expected] of canaryTests) {
    const chaos = calculateCanaryChaos(status);
    if (Math.abs(chaos - expected) < 0.001) {
        console.log(`  ${status.padEnd(18)} → ${chaos.toFixed(1)} ✓`);
        testsPassed++;
    } else {
        console.error(`  ${status.padEnd(18)} → ${chaos.toFixed(1)} ✗ (expected ${expected})`);
        testsFailed++;
    }
}
console.log('');

// Test 9: Entropy level classification
console.log('Test 9: Entropy level classification');
const levelTests = [
    [0.0, 'STABLE'],
    [0.1, 'STABLE'],
    [0.2, 'LOW_CHAOS'],
    [0.3, 'LOW_CHAOS'],
    [0.4, 'MODERATE_CHAOS'],
    [0.5, 'MODERATE_CHAOS'],
    [0.6, 'HIGH_CHAOS'],
    [0.7, 'HIGH_CHAOS'],
    [0.8, 'CRITICAL_CHAOS'],
    [0.9, 'CRITICAL_CHAOS'],
    [1.0, 'CRITICAL_CHAOS']
];

let levelTestsOK = true;
for (const [entropy, expectedLevel] of levelTests) {
    const level = getEntropyLevel(entropy);
    if (level === expectedLevel) {
        console.log(`  ${entropy.toFixed(1)} → ${level.padEnd(18)} ✓`);
        testsPassed++;
    } else {
        console.error(`  ${entropy.toFixed(1)} → ${level.padEnd(18)} ✗ (expected ${expectedLevel})`);
        testsFailed++;
        levelTestsOK = false;
    }
}
console.log('');

// Test 10: Ritual trigger threshold
console.log('Test 10: Ritual trigger threshold');
const ritualTests = [
    [0.3, 0.5, false],
    [0.4, 0.5, false],
    [0.5, 0.5, true],  // Exactly at threshold
    [0.6, 0.5, true],
    [0.8, 0.5, true],
    [0.7, 0.8, false], // Below custom threshold
    [0.8, 0.8, true],  // At custom threshold
];

let ritualTestsOK = true;
for (const [entropy, threshold, expectedTrigger] of ritualTests) {
    const shouldTrigger = shouldTriggerRitual(entropy, threshold);
    const result = shouldTrigger === expectedTrigger ? '✓' : '✗';
    console.log(`  Entropy ${entropy} (threshold ${threshold}) → ${shouldTrigger} ${result}`);

    if (shouldTrigger === expectedTrigger) {
        testsPassed++;
    } else {
        testsFailed++;
        ritualTestsOK = false;
    }
}
console.log('');

// Test 11: Real-world scenario - CI failure spike
console.log('Test 11: Real-world scenario - CI failure spike');
const ciFailureGitHub = {
    openIssues: 50,
    latestWorkflowStatus: 'failure',
    branchProtection: { status: 'Configured', enforceAdmins: true },
    webhooks: [{ active: true }],
    lastPush: new Date().toISOString()
};
const ciFailureChaos = calculateGitHubChaos(ciFailureGitHub);
const ciFailureEntropy = calculateEntropy(0.2, 0.3, ciFailureChaos, 0.0);

console.log(`  GitHub chaos: ${ciFailureChaos.toFixed(3)}`);
console.log(`  Total entropy: ${ciFailureEntropy.toFixed(3)}`);
console.log(`  Entropy level: ${getEntropyLevel(ciFailureEntropy)}`);
console.log(`  Trigger ritual: ${shouldTriggerRitual(ciFailureEntropy)}`);

if (ciFailureEntropy > 0.4 && ciFailureEntropy < 0.7) {
    pass('CI failure scenario produces moderate-to-high entropy');
} else {
    fail(`Expected 0.4-0.7 entropy, got ${ciFailureEntropy.toFixed(3)}`);
}
console.log('');

// Summary
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`   Tests Passed: ${testsPassed}`);
console.log(`   Tests Failed: ${testsFailed}`);
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

process.exit(testsFailed > 0 ? 1 : 0);
