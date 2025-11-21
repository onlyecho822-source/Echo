# OMEGA Echo - Testing Guide

## 🎯 Testing Strategy

This guide provides comprehensive testing procedures for validating the OMEGA Cosmic Pipeline.

---

## Quick Smoke Test (5 minutes)

### Prerequisites Check
```bash
# Verify Node.js version
node --version
# Expected: v18.x or later

# Verify npm
npm --version
# Expected: 8.x or later

# Check if dependencies are installed
npm list --depth=0
```

### Generate Test Credentials
```bash
# Generate OMEGA_SECRET_KEY (256-bit)
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Copy output to .env

# Set environment variables
export OMEGA_SECRET_KEY="<your-generated-key>"
export GITHUB_TOKEN="<your-github-token>"
export GITHUB_REPO="onlyecho822-source/Echo"
```

### Run Basic Test
```bash
# Test 1: Verify canary module loads
node -e "
const { initCanaryModule, writeCanary, checkCanary } = require('./lib/omegaCanary');
initCanaryModule(process.env.OMEGA_SECRET_KEY);
writeCanary();
const status = checkCanary();
console.log('Canary Status:', status);
process.exit(status === 'OK' ? 0 : 1);
"
# Expected output: "Canary Status: OK"
# Expected exit code: 0
```

---

## Component Testing

### 1. Test Canary System

Create a test file:

```javascript
// test-canary.js
require('dotenv').config();
const { initCanaryModule, writeCanary, checkCanary } = require('./lib/omegaCanary');
const fs = require('fs');

console.log('=== CANARY SYSTEM TEST ===\n');

// Test 1: Initialize
console.log('Test 1: Initialize canary module');
try {
    initCanaryModule(process.env.OMEGA_SECRET_KEY);
    console.log('✅ PASS: Module initialized\n');
} catch (error) {
    console.error('❌ FAIL:', error.message);
    process.exit(1);
}

// Test 2: Write canary
console.log('Test 2: Write canary file');
const writeResult = writeCanary();
if (writeResult === false) {
    console.error('❌ FAIL: Could not write canary');
    process.exit(1);
}
console.log('✅ PASS: Canary written\n');

// Test 3: Check canary (should be OK)
console.log('Test 3: Check canary integrity');
const status1 = checkCanary();
if (status1 !== 'OK') {
    console.error(`❌ FAIL: Expected OK, got ${status1}`);
    process.exit(1);
}
console.log('✅ PASS: Canary integrity OK\n');

// Test 4: Tamper with canary
console.log('Test 4: Detect tampering');
const canaryFile = './vault_canary.txt';
const original = fs.readFileSync(canaryFile, 'utf8');
const tampered = original.replace(/"timestamp"/, '"modified_timestamp"');
fs.writeFileSync(canaryFile, tampered, 'utf8');

const status2 = checkCanary();
if (status2 === 'OK') {
    console.error('❌ FAIL: Tampering not detected!');
    process.exit(1);
}
console.log(`✅ PASS: Tampering detected (${status2})\n`);

// Restore original
fs.writeFileSync(canaryFile, original, 'utf8');

console.log('=== ALL TESTS PASSED ===');
```

**Run test**:
```bash
node test-canary.js
```

**Expected output**:
```
=== CANARY SYSTEM TEST ===

Test 1: Initialize canary module
✅ PASS: Module initialized

Test 2: Write canary file
✅ PASS: Canary written

Test 3: Check canary integrity
✅ PASS: Canary integrity OK

Test 4: Detect tampering
✅ PASS: Tampering detected (ERROR)

=== ALL TESTS PASSED ===
```

---

### 2. Test Entropy Engine

Create test file:

```javascript
// test-entropy.js
const {
    calculateEntropy,
    calculateGitHubChaos,
    calculateCanaryChaos,
    getEntropyLevel,
    shouldTriggerRitual
} = require('./lib/omegaEntropy');

console.log('=== ENTROPY ENGINE TEST ===\n');

// Test 1: Basic entropy calculation
console.log('Test 1: Calculate entropy with zero inputs');
const entropy1 = calculateEntropy(0, 0, 0, 0);
console.log(`Entropy: ${entropy1}`);
if (entropy1 !== 0) {
    console.error('❌ FAIL: Expected 0');
    process.exit(1);
}
console.log('✅ PASS\n');

// Test 2: Maximum entropy
console.log('Test 2: Calculate entropy with max inputs');
const entropy2 = calculateEntropy(1, 1, 1, 1);
console.log(`Entropy: ${entropy2}`);
if (entropy2 !== 1) {
    console.error('❌ FAIL: Expected 1');
    process.exit(1);
}
console.log('✅ PASS\n');

// Test 3: GitHub chaos calculation
console.log('Test 3: Calculate GitHub chaos factor');
const mockGitHub = {
    openIssues: 50,
    latestWorkflowStatus: 'failure',
    branchProtection: {
        status: 'Not Configured or No Scope',
        enforceAdmins: false
    },
    webhooks: [],
    lastPush: new Date(Date.now() - 40 * 24 * 60 * 60 * 1000).toISOString() // 40 days ago
};
const githubChaos = calculateGitHubChaos(mockGitHub);
console.log(`GitHub Chaos: ${githubChaos}`);
if (githubChaos < 0.5) {
    console.error('❌ FAIL: Expected high chaos (>0.5) for failing CI + no protection');
    process.exit(1);
}
console.log('✅ PASS\n');

// Test 4: Canary chaos mapping
console.log('Test 4: Canary chaos mapping');
const tests = [
    ['OK', 0.0],
    ['STALE', 0.3],
    ['MISSING', 0.8],
    ['TAMPERED_HASH', 1.0]
];

for (const [status, expected] of tests) {
    const chaos = calculateCanaryChaos(status);
    if (chaos !== expected) {
        console.error(`❌ FAIL: ${status} expected ${expected}, got ${chaos}`);
        process.exit(1);
    }
    console.log(`  ${status} → ${chaos} ✓`);
}
console.log('✅ PASS\n');

// Test 5: Entropy levels
console.log('Test 5: Entropy level classification');
const levelTests = [
    [0.1, 'STABLE'],
    [0.3, 'LOW_CHAOS'],
    [0.5, 'MODERATE_CHAOS'],
    [0.7, 'HIGH_CHAOS'],
    [0.9, 'CRITICAL_CHAOS']
];

for (const [entropy, expectedLevel] of levelTests) {
    const level = getEntropyLevel(entropy);
    if (level !== expectedLevel) {
        console.error(`❌ FAIL: Entropy ${entropy} expected ${expectedLevel}, got ${level}`);
        process.exit(1);
    }
    console.log(`  ${entropy} → ${level} ✓`);
}
console.log('✅ PASS\n');

// Test 6: Ritual trigger threshold
console.log('Test 6: Ritual trigger threshold');
if (shouldTriggerRitual(0.4, 0.5) !== false) {
    console.error('❌ FAIL: Should not trigger at 0.4');
    process.exit(1);
}
if (shouldTriggerRitual(0.6, 0.5) !== true) {
    console.error('❌ FAIL: Should trigger at 0.6');
    process.exit(1);
}
console.log('✅ PASS\n');

console.log('=== ALL TESTS PASSED ===');
```

**Run test**:
```bash
node test-entropy.js
```

---

### 3. Test Metabolic Noise

```javascript
// test-noise.js
const {
    runMetabolicNoise,
    getNoiseStats,
    resetNoiseStats
} = require('./lib/omegaVaultNoise');

console.log('=== METABOLIC NOISE TEST ===\n');

// Test 1: Reset stats
console.log('Test 1: Reset noise statistics');
resetNoiseStats();
const stats1 = getNoiseStats();
if (stats1.dummyReadsTotal !== 0) {
    console.error('❌ FAIL: Stats not reset');
    process.exit(1);
}
console.log('✅ PASS\n');

// Test 2: Run noise cycle
console.log('Test 2: Run metabolic noise cycle');
runMetabolicNoise();
const stats2 = getNoiseStats();
console.log(`Stats:`, stats2);
if (stats2.dummyReadsTotal < 2) {
    console.error('❌ FAIL: Expected at least 2 dummy reads');
    process.exit(1);
}
if (stats2.noiseGeneratedBytes === 0) {
    console.error('❌ FAIL: Expected noise generation');
    process.exit(1);
}
console.log('✅ PASS\n');

console.log('=== ALL TESTS PASSED ===');
```

**Run test**:
```bash
node test-noise.js
```

---

### 4. Test GitHub Integration

```javascript
// test-github.js
require('dotenv').config();
const { Octokit } = require('@octokit/rest');

console.log('=== GITHUB INTEGRATION TEST ===\n');

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

async function testGitHub() {
    // Test 1: Authenticate
    console.log('Test 1: GitHub authentication');
    try {
        const { data: user } = await octokit.users.getAuthenticated();
        console.log(`✅ PASS: Authenticated as ${user.login}\n`);
    } catch (error) {
        console.error('❌ FAIL:', error.message);
        process.exit(1);
    }

    // Test 2: Fetch repository
    if (!process.env.GITHUB_REPO) {
        console.log('⚠️ SKIP: GITHUB_REPO not set\n');
        return;
    }

    const [owner, repo] = process.env.GITHUB_REPO.split('/');

    console.log(`Test 2: Fetch repository ${owner}/${repo}`);
    try {
        const { data: repoData } = await octokit.repos.get({ owner, repo });
        console.log(`  Name: ${repoData.full_name}`);
        console.log(`  Private: ${repoData.private}`);
        console.log(`  Default branch: ${repoData.default_branch}`);
        console.log(`  Open issues: ${repoData.open_issues_count}`);
        console.log('✅ PASS\n');
    } catch (error) {
        console.error('❌ FAIL:', error.message);
        process.exit(1);
    }

    // Test 3: Check workflows (may not exist)
    console.log('Test 3: Fetch workflow runs');
    try {
        const { data: workflowRuns } = await octokit.actions.listWorkflowRunsForRepo({
            owner,
            repo,
            per_page: 1,
        });
        console.log(`  Workflow runs: ${workflowRuns.total_count}`);
        console.log('✅ PASS\n');
    } catch (error) {
        console.log('⚠️ SKIP: Workflows not accessible or not configured\n');
    }

    console.log('=== ALL TESTS PASSED ===');
}

testGitHub();
```

**Run test**:
```bash
node test-github.js
```

---

### 5. Test PowerShell Guardian

**Windows PowerShell / PowerShell Core**:
```powershell
# Test with dry-run (validate checks but don't launch)
# We'll create a test version

# Test 1: Check script loads
Get-Command .\scripts\Run-Embryo-Pipeline.ps1
# Expected: CommandType = ExternalScript

# Test 2: Validate parameters
Get-Help .\scripts\Run-Embryo-Pipeline.ps1 -Parameter Repo
# Expected: Parameter details displayed

# Test 3: Run with invalid repo (should fail gracefully)
$env:GITHUB_TOKEN = "invalid_token"
$env:OMEGA_SECRET_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

.\scripts\Run-Embryo-Pipeline.ps1 -Repo "fake/repo" -SkipSystemChecks
# Expected: "GitHub authentication failed" error
```

---

### 6. Test Docker Container

```bash
# Test 1: Build container
echo "Test 1: Build Docker image"
docker build -t echo/omega-embryo:test .
# Expected: Successfully built

# Test 2: Inspect image
echo "Test 2: Inspect image properties"
docker image inspect echo/omega-embryo:test | grep -E "User|WorkingDir"
# Expected: User=omega, WorkingDir=/app

# Test 3: Test container without secrets (should fail)
echo "Test 3: Run without secrets (expected to fail)"
docker run --rm echo/omega-embryo:test
# Expected: "Missing required environment variables"

# Test 4: Run with valid secrets
echo "Test 4: Run with valid secrets"
docker run --rm \
  -e OMEGA_SECRET_KEY="$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -e GITHUB_REPO="onlyecho822-source/Echo" \
  -v $(pwd)/cosmic_status:/app/cosmic_status \
  -v $(pwd)/vault_canary.txt:/app/vault_canary.txt \
  echo/omega-embryo:test
# Press Ctrl+C after a few seconds
# Expected: Dashboard appears, no errors

# Clean up
docker rmi echo/omega-embryo:test
```

---

## Integration Testing

### End-to-End Test (Full Pipeline)

```bash
# Test the complete workflow
echo "=== OMEGA COSMIC PIPELINE - INTEGRATION TEST ==="

# 1. Setup
echo "Step 1: Setup environment"
cp .env.example .env
# Manually edit .env with valid credentials

# 2. Install dependencies
echo "Step 2: Install dependencies"
npm install

# 3. Run component tests
echo "Step 3: Run component tests"
node test-canary.js || exit 1
node test-entropy.js || exit 1
node test-noise.js || exit 1
node test-github.js || exit 1

# 4. Launch embryo (5 second test)
echo "Step 4: Launch embryo for 5 seconds"
timeout 5s node index.js || true

# 5. Verify outputs
echo "Step 5: Verify outputs"
if [ ! -f "vault_canary.txt" ]; then
    echo "❌ FAIL: Canary file not created"
    exit 1
fi
if [ ! -f "cosmic_status/embryo_status.json" ]; then
    echo "❌ FAIL: Status file not created"
    exit 1
fi

# 6. Validate status file
echo "Step 6: Validate status file"
node -e "
const fs = require('fs');
const status = JSON.parse(fs.readFileSync('cosmic_status/embryo_status.json', 'utf8'));
if (!status.timestamp || !status.entropy || !status.canaryFileIntegrity) {
    console.error('❌ FAIL: Status file malformed');
    process.exit(1);
}
console.log('✅ PASS: Status file valid');
console.log(JSON.stringify(status, null, 2));
"

echo ""
echo "=== INTEGRATION TEST COMPLETE ==="
```

---

## Security Testing

### 1. Test Canary Tamper Detection

```bash
# Start embryo in background
node index.js &
EMBRYO_PID=$!

# Wait for canary creation
sleep 3

# Tamper with canary
echo "Tampering with canary..."
echo '{"fake": "data"}' > vault_canary.txt

# Wait for next canary check (5 seconds)
sleep 6

# Check status - should show TAMPERED
cat cosmic_status/embryo_status.json | grep canaryFileIntegrity
# Expected: "canaryFileIntegrity": "ERROR" or "TAMPERED_HASH"

# Kill embryo
kill $EMBRYO_PID
```

### 2. Test Entropy Spike Detection

```javascript
// test-entropy-spike.js
require('dotenv').config();

const { calculateEntropy, calculateGitHubChaos, shouldTriggerRitual } = require('./lib/omegaEntropy');

// Simulate failing GitHub state
const badGitHub = {
    openIssues: 100,
    latestWorkflowStatus: 'failure',
    branchProtection: { status: 'Not Configured or No Scope' },
    webhooks: [{ active: false }]
};

const githubChaos = calculateGitHubChaos(badGitHub);
const entropy = calculateEntropy(0.5, 0.5, githubChaos, 1.0); // Max canary chaos too

console.log('Simulated Crisis State:');
console.log(`  GitHub Chaos: ${githubChaos.toFixed(3)}`);
console.log(`  Total Entropy: ${entropy.toFixed(3)}`);
console.log(`  Should trigger ritual: ${shouldTriggerRitual(entropy)}`);

if (entropy < 0.7) {
    console.error('❌ FAIL: Expected HIGH entropy (>0.7) for crisis state');
    process.exit(1);
}

console.log('✅ PASS: Crisis state correctly detected');
```

---

## Performance Testing

### 1. Canary Performance

```javascript
// test-canary-perf.js
const { initCanaryModule, writeCanary, checkCanary } = require('./lib/omegaCanary');

initCanaryModule(process.env.OMEGA_SECRET_KEY);

console.log('=== CANARY PERFORMANCE TEST ===\n');

// Test write performance
console.log('Test 1: Write performance (100 iterations)');
const writeStart = Date.now();
for (let i = 0; i < 100; i++) {
    writeCanary();
}
const writeTime = Date.now() - writeStart;
console.log(`  Total: ${writeTime}ms`);
console.log(`  Average: ${(writeTime / 100).toFixed(2)}ms per write`);

// Test check performance
console.log('\nTest 2: Check performance (1000 iterations)');
const checkStart = Date.now();
for (let i = 0; i < 1000; i++) {
    checkCanary();
}
const checkTime = Date.now() - checkStart;
console.log(`  Total: ${checkTime}ms`);
console.log(`  Average: ${(checkTime / 1000).toFixed(2)}ms per check`);

// Performance targets
const writeTarget = 10; // 10ms per write
const checkTarget = 5;  // 5ms per check

if (writeTime / 100 > writeTarget) {
    console.warn(`⚠️ WARNING: Write performance below target (${writeTarget}ms)`);
}
if (checkTime / 1000 > checkTarget) {
    console.warn(`⚠️ WARNING: Check performance below target (${checkTarget}ms)`);
}

console.log('\n✅ Performance test complete');
```

---

## Expected Outputs

### Healthy System
```json
{
  "timestamp": "2025-11-20T12:34:56.789Z",
  "entropy": 0.234,
  "entropyLevel": "LOW_CHAOS",
  "ritualTriggered": false,
  "ritualsTotal": 0,
  "githubStatus": {
    "repoName": "onlyecho822-source/Echo",
    "private": false,
    "defaultBranch": "main",
    "openIssues": 2,
    "latestWorkflowStatus": "success",
    "branchProtection": {
      "status": "Configured",
      "enforceAdmins": true
    }
  },
  "canaryFileIntegrity": "OK",
  "metabolicNoiseLastRun": "2025-11-20T12:34:45.123Z"
}
```

### System Under Stress
```json
{
  "timestamp": "2025-11-20T12:45:00.000Z",
  "entropy": 0.789,
  "entropyLevel": "HIGH_CHAOS",
  "ritualTriggered": true,
  "ritualsTotal": 3,
  "githubStatus": {
    "repoName": "onlyecho822-source/Echo",
    "openIssues": 87,
    "latestWorkflowStatus": "failure",
    "branchProtection": {
      "status": "Not Configured or No Scope"
    }
  },
  "canaryFileIntegrity": "STALE"
}
```

---

## Troubleshooting Tests

### Test Fails: "Module not found"
```bash
# Solution: Install dependencies
npm install
```

### Test Fails: "OMEGA_SECRET_KEY must be 64 characters"
```bash
# Solution: Generate valid key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))" > .key
export OMEGA_SECRET_KEY=$(cat .key)
```

### Test Fails: "GitHub authentication failed"
```bash
# Solution: Check token
echo $GITHUB_TOKEN
# Verify at: https://github.com/settings/tokens
```

### Container Test Fails: "Permission denied"
```bash
# Solution: Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

---

## Automated Test Suite

Create a master test runner:

```bash
#!/bin/bash
# run-all-tests.sh

set -e  # Exit on any error

echo "==================================="
echo "OMEGA ECHO - AUTOMATED TEST SUITE"
echo "==================================="
echo ""

# Component tests
echo "→ Running component tests..."
node test-canary.js
node test-entropy.js
node test-noise.js
node test-github.js

echo ""
echo "→ Running performance tests..."
node test-canary-perf.js

echo ""
echo "→ Running security tests..."
node test-entropy-spike.js

echo ""
echo "==================================="
echo "✅ ALL TESTS PASSED"
echo "==================================="
```

Make executable:
```bash
chmod +x run-all-tests.sh
./run-all-tests.sh
```

---

## Continuous Testing

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: OMEGA Echo Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run component tests
        env:
          OMEGA_SECRET_KEY: ${{ secrets.OMEGA_SECRET_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          node test-canary.js
          node test-entropy.js
          node test-noise.js
```

---

**Testing complete!** You now have a comprehensive test suite covering all components of your cosmic playground.
