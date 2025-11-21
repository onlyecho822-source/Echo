#!/usr/bin/env node
/**
 * OMEGA Echo - Canary System Test
 * Tests the cryptographic canary integrity monitoring system
 */

require('dotenv').config();
const { initCanaryModule, writeCanary, checkCanary } = require('./lib/omegaCanary');
const fs = require('fs');

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('   🧪 CANARY SYSTEM TEST');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

let testsPassed = 0;
let testsFailed = 0;
const CANARY_FILE = './vault_canary.txt';

function pass(message) {
    console.log(`✅ PASS: ${message}`);
    testsPassed++;
}

function fail(message) {
    console.error(`❌ FAIL: ${message}`);
    testsFailed++;
}

// Verify environment
if (!process.env.OMEGA_SECRET_KEY) {
    fail('OMEGA_SECRET_KEY not set in environment');
    console.log('\nGenerate one with:');
    console.log('  node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"');
    process.exit(1);
}

if (process.env.OMEGA_SECRET_KEY.length !== 64) {
    fail('OMEGA_SECRET_KEY must be 64 characters (32 bytes hex)');
    process.exit(1);
}

// Test 1: Initialize module
console.log('Test 1: Initialize canary module');
try {
    initCanaryModule(process.env.OMEGA_SECRET_KEY);
    pass('Module initialized successfully');
} catch (error) {
    fail(`Initialization failed: ${error.message}`);
    process.exit(1);
}
console.log('');

// Test 2: Write canary
console.log('Test 2: Write canary file');
try {
    const result = writeCanary();
    if (result === false) {
        fail('writeCanary() returned false');
        process.exit(1);
    }
    if (!fs.existsSync(CANARY_FILE)) {
        fail('Canary file not created');
        process.exit(1);
    }
    pass('Canary file written successfully');
} catch (error) {
    fail(`Write failed: ${error.message}`);
    process.exit(1);
}
console.log('');

// Test 3: Check canary integrity (should be OK)
console.log('Test 3: Check canary integrity (fresh)');
const status1 = checkCanary();
if (status1 === 'OK') {
    pass('Canary integrity verified (OK)');
} else {
    fail(`Expected OK, got ${status1}`);
    process.exit(1);
}
console.log('');

// Test 4: Verify canary file structure
console.log('Test 4: Verify canary file structure');
try {
    const canaryData = JSON.parse(fs.readFileSync(CANARY_FILE, 'utf8'));

    if (!canaryData.encryptedPayload) {
        fail('Missing encryptedPayload field');
    } else if (!canaryData.hashOfEncryptedPayload) {
        fail('Missing hashOfEncryptedPayload field');
    } else if (!canaryData.timestamp) {
        fail('Missing timestamp field');
    } else if (!canaryData.version) {
        fail('Missing version field');
    } else {
        pass('Canary file structure is valid');
        console.log(`  Version: ${canaryData.version}`);
        console.log(`  Timestamp: ${canaryData.timestamp}`);
        console.log(`  Hash: ${canaryData.hashOfEncryptedPayload.substring(0, 16)}...`);
    }
} catch (error) {
    fail(`File structure check failed: ${error.message}`);
}
console.log('');

// Test 5: Detect tampering (hash modification)
console.log('Test 5: Detect tampering (hash modification)');
const original = fs.readFileSync(CANARY_FILE, 'utf8');
const tampered = JSON.parse(original);
tampered.hashOfEncryptedPayload = 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff';
fs.writeFileSync(CANARY_FILE, JSON.stringify(tampered, null, 2), 'utf8');

const status2 = checkCanary();
if (status2 === 'TAMPERED_HASH' || status2 === 'ERROR') {
    pass(`Tampering detected (${status2})`);
} else {
    fail(`Expected TAMPERED_HASH or ERROR, got ${status2}`);
}

// Restore original
fs.writeFileSync(CANARY_FILE, original, 'utf8');
console.log('');

// Test 6: Detect tampering (payload modification)
console.log('Test 6: Detect tampering (payload modification)');
const tampered2 = JSON.parse(original);
tampered2.encryptedPayload = 'abcd1234:efgh5678:ijkl9012';
fs.writeFileSync(CANARY_FILE, JSON.stringify(tampered2, null, 2), 'utf8');

const status3 = checkCanary();
if (status3 === 'TAMPERED_HASH' || status3 === 'ERROR') {
    pass(`Tampering detected (${status3})`);
} else {
    fail(`Expected TAMPERED_HASH or ERROR, got ${status3}`);
}

// Restore original
fs.writeFileSync(CANARY_FILE, original, 'utf8');
console.log('');

// Test 7: Multiple write/check cycles
console.log('Test 7: Multiple write/check cycles (10 iterations)');
let cyclesOK = true;
for (let i = 0; i < 10; i++) {
    writeCanary();
    const status = checkCanary();
    if (status !== 'OK') {
        fail(`Cycle ${i + 1} failed: ${status}`);
        cyclesOK = false;
        break;
    }
}
if (cyclesOK) {
    pass('All 10 cycles completed successfully');
}
console.log('');

// Summary
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`   Tests Passed: ${testsPassed}`);
console.log(`   Tests Failed: ${testsFailed}`);
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

process.exit(testsFailed > 0 ? 1 : 0);
