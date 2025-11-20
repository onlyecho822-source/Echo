#!/usr/bin/env node

/**
 * OMEGA Echo - Hardened GitHub Integration Embryo
 *
 * This is the main entry point for the Echo Cosmic Pipeline.
 * It integrates with GitHub, monitors repository health, calculates entropy,
 * and provides real-time status reporting.
 *
 * Security Features:
 * - Encrypted canary system for vault integrity
 * - Metabolic noise generation for operational security
 * - Comprehensive GitHub integration monitoring
 * - Real-time entropy calculation
 * - Self-reporting health status
 */

require('dotenv').config();

const { initCanaryModule, writeCanary, checkCanary, rotateCanary } = require('./lib/omegaCanary');
const { runMetabolicNoise, startPeriodicNoise, getNoiseStats } = require('./lib/omegaVaultNoise');
const {
    calculateEntropy,
    calculateGitHubChaos,
    calculateCanaryChaos,
    getEntropyLevel,
    shouldTriggerRitual
} = require('./lib/omegaEntropy');
const dashboard = require('./lib/dashboard');
const { Octokit } = require('@octokit/rest');
const fs = require('fs');
const path = require('path');

// ==========================================
// CONFIGURATION
// ==========================================

const GITHUB_REPO = process.env.GITHUB_REPO;
const EMBRYO_STATUS_DIR = path.join(process.cwd(), 'cosmic_status');
const EMBRYO_STATUS_FILE = path.join(EMBRYO_STATUS_DIR, 'embryo_status.json');
const MONITORING_INTERVAL_MS = 5000; // 5 seconds
const CANARY_ROTATION_INTERVAL_MS = 900000; // 15 minutes
const NOISE_INTERVAL_MS = 60000; // 1 minute

// ==========================================
// ENVIRONMENT VALIDATION
// ==========================================

const requiredEnvVars = ['OMEGA_SECRET_KEY', 'GITHUB_TOKEN'];
const missingVars = requiredEnvVars.filter((key) => !process.env[key]);

if (missingVars.length > 0) {
    console.error(`🚨 [OMEGA] FATAL: Missing required environment variables: ${missingVars.join(', ')}`);
    console.error(`🚨 [OMEGA] Please set these in your .env file or environment.`);
    process.exit(1);
}

if (!GITHUB_REPO) {
    console.warn(`⚠ [OMEGA] WARNING: GITHUB_REPO not set. GitHub monitoring will be limited.`);
}

// ==========================================
// GITHUB CLIENT INITIALIZATION
// ==========================================

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

dashboard.log('{green-fg}✔ GitHub client initialized{/}');

// ==========================================
// CANARY INITIALIZATION
// ==========================================

try {
    initCanaryModule(process.env.OMEGA_SECRET_KEY);
    dashboard.log('{green-fg}✔ Canary module initialized{/}');

    // Write initial canary
    writeCanary();
    dashboard.log('{green-fg}✔ Initial canary written{/}');

    // Check initial canary status
    const initialCanaryStatus = checkCanary();
    dashboard.updateStatus({ canary: initialCanaryStatus });
} catch (error) {
    console.error(`🚨 [OMEGA] FATAL: Canary initialization failed: ${error.message}`);
    dashboard.log(`{red-fg}✖ Canary initialization failed: ${error.message}{/}`);
    process.exit(1);
}

// ==========================================
// METABOLIC NOISE INITIALIZATION
// ==========================================

// Run initial noise cycle
runMetabolicNoise();
dashboard.log('{green-fg}✔ Initial metabolic noise cycle complete{/}');

// Start periodic noise generation
const noiseInterval = startPeriodicNoise(NOISE_INTERVAL_MS);
dashboard.log(`{green-fg}✔ Periodic metabolic noise started (${NOISE_INTERVAL_MS}ms){/}`);

// ==========================================
// GITHUB METRICS FETCHING
// ==========================================

/**
 * Fetch comprehensive GitHub repository metrics
 * @param {string} repoFullName - Repository in "owner/repo" format
 * @returns {Promise<Object|null>} - Repository metrics or null on error
 */
async function fetchGitHubRepoMetrics(repoFullName) {
    if (!repoFullName) {
        return { error: 'No repository specified' };
    }

    try {
        const [owner, repo] = repoFullName.split('/');

        if (!owner || !repo) {
            throw new Error(`Invalid GITHUB_REPO format: ${repoFullName}. Expected 'owner/repo'.`);
        }

        // 1. Basic repo data
        const { data: repoData } = await octokit.repos.get({ owner, repo });

        // 2. Latest workflow run status
        let latestWorkflowStatus = 'no_runs';
        try {
            const { data: workflowRuns } = await octokit.actions.listWorkflowRunsForRepo({
                owner,
                repo,
                per_page: 1,
            });

            if (workflowRuns.workflow_runs.length > 0) {
                latestWorkflowStatus = workflowRuns.workflow_runs[0].conclusion || 'running';
            }
        } catch (workflowError) {
            dashboard.log(`{yellow-fg}⚠ Could not fetch workflow runs: ${workflowError.message}{/}`);
        }

        // 3. Branch protection (for default branch)
        let branchProtection = { status: 'Not Configured or No Scope' };
        try {
            const { data: protectionData } = await octokit.repos.getBranchProtection({
                owner,
                repo,
                branch: repoData.default_branch,
            });

            branchProtection = {
                status: 'Configured',
                requiredStatusChecks: protectionData.required_status_checks
                    ? protectionData.required_status_checks.enforcement_level
                    : 'none',
                enforceAdmins: protectionData.enforce_admins?.enabled || false,
                restrictions: !!protectionData.restrictions,
            };
        } catch (bpError) {
            // This often fails if no protection is set or token lacks scope
            dashboard.log(
                `{yellow-fg}⚠ No branch protection on ${repoData.default_branch} or insufficient scope{/}`
            );
        }

        // 4. Webhooks
        let webhooks = [];
        try {
            const { data: hooksData } = await octokit.repos.listWebhooks({ owner, repo });
            webhooks = hooksData.map((hook) => ({
                id: hook.id,
                name: hook.name,
                active: hook.active,
                events: hook.events,
                configUrl: hook.config?.url,
            }));
        } catch (whError) {
            dashboard.log(`{yellow-fg}⚠ Could not list webhooks: ${whError.message}{/}`);
        }

        return {
            repoName: repoData.full_name,
            private: repoData.private,
            defaultBranch: repoData.default_branch,
            openIssues: repoData.open_issues_count,
            lastPush: repoData.pushed_at,
            latestWorkflowStatus,
            branchProtection,
            webhooks,
        };
    } catch (error) {
        dashboard.log(`{red-fg}✖ GitHub metrics fetch failed: ${error.message}{/}`);
        return { error: error.message };
    }
}

// ==========================================
// STATUS REPORTING
// ==========================================

/**
 * Write current embryo status to file for PowerShell consumption
 * @param {Object} status - Status object
 */
async function writeEmbryoStatus(status) {
    try {
        // Ensure directory exists
        if (!fs.existsSync(EMBRYO_STATUS_DIR)) {
            fs.mkdirSync(EMBRYO_STATUS_DIR, { recursive: true });
        }

        // Write status file
        fs.writeFileSync(EMBRYO_STATUS_FILE, JSON.stringify(status, null, 2), 'utf8');
    } catch (error) {
        dashboard.log(`{red-fg}✖ Failed to write status file: ${error.message}{/}`);
    }
}

// ==========================================
// RITUAL SYSTEM (Placeholder)
// ==========================================

let ritualsTriggered = 0;

/**
 * Execute a ritual based on entropy level
 * @param {number} entropy - Current entropy value
 */
function executeRitual(entropy) {
    ritualsTriggered++;

    const entropyLevel = getEntropyLevel(entropy);

    dashboard.log(`{magenta-fg}🌀 RITUAL TRIGGERED: ${entropyLevel} (Entropy: ${entropy.toFixed(3)}){/}`);

    // In a full implementation, this would trigger specific actions:
    // - Send alerts
    // - Trigger GitHub Actions workflows
    // - Execute emergency procedures
    // - Log to external monitoring systems

    dashboard.updateStatus({ rituals: ritualsTriggered });
}

// ==========================================
// MAIN MONITORING LOOP
// ==========================================

async function monitoringLoop() {
    // 1. Check canary status
    const canaryStatus = checkCanary();
    const canaryChaosFactor = calculateCanaryChaos(canaryStatus);

    // 2. Fetch GitHub metrics
    const githubMetrics = GITHUB_REPO ? await fetchGitHubRepoMetrics(GITHUB_REPO) : null;
    const githubChaosFactor = githubMetrics ? calculateGitHubChaos(githubMetrics) : 0;

    // 3. Get noise stats
    const noiseStats = getNoiseStats();

    // 4. Calculate entropy
    const signalFrequency = Math.random(); // Placeholder: replace with real signal
    const apiLatency = Math.random(); // Placeholder: replace with real latency measurement

    const entropy = calculateEntropy(signalFrequency, apiLatency, githubChaosFactor, canaryChaosFactor);

    // 5. Update dashboard
    dashboard.updateEntropy(entropy);
    dashboard.updateStatus({
        canary: canaryStatus,
        github: githubMetrics && !githubMetrics.error ? 'OK' : 'ERROR',
    });

    // 6. Trigger ritual if needed
    if (shouldTriggerRitual(entropy, 0.5)) {
        executeRitual(entropy);
    }

    // 7. Write status file for PowerShell
    const statusReport = {
        timestamp: new Date().toISOString(),
        entropy: parseFloat(entropy.toFixed(3)),
        entropyLevel: getEntropyLevel(entropy),
        ritualTriggered: shouldTriggerRitual(entropy, 0.5),
        ritualsTotal: ritualsTriggered,
        githubStatus: githubMetrics || { error: 'No repository configured' },
        canaryFileIntegrity: canaryStatus,
        metabolicNoiseLastRun: noiseStats.lastOperationTime,
        dummyVaultReadsTotal: noiseStats.dummyReadsTotal,
        noiseGeneratedBytes: noiseStats.noiseGeneratedBytes,
    };

    await writeEmbryoStatus(statusReport);
}

// Start monitoring loop
dashboard.log(`{cyan-fg}🌌 Starting OMEGA monitoring loop (${MONITORING_INTERVAL_MS}ms){/}`);
const monitoringInterval = setInterval(monitoringLoop, MONITORING_INTERVAL_MS);

// Run initial monitoring cycle
monitoringLoop();

// ==========================================
// CANARY ROTATION
// ==========================================

setInterval(() => {
    dashboard.log('{yellow-fg}🔄 Rotating canary...{/}');
    rotateCanary();
}, CANARY_ROTATION_INTERVAL_MS);

// ==========================================
// GRACEFUL SHUTDOWN
// ==========================================

process.on('SIGINT', () => {
    dashboard.log('{red-fg}🛑 Shutdown signal received. Cleaning up...{/}');

    // Stop intervals
    clearInterval(monitoringInterval);
    clearInterval(noiseInterval);

    // Write final status
    writeEmbryoStatus({
        timestamp: new Date().toISOString(),
        status: 'SHUTDOWN',
        message: 'Embryo terminated gracefully',
    });

    dashboard.log('{green-fg}✔ Shutdown complete. Goodbye.{/}');

    setTimeout(() => {
        process.exit(0);
    }, 500);
});

// ==========================================
// STARTUP COMPLETE
// ==========================================

dashboard.log('{green-fg}✅ OMEGA Echo Embryo fully operational{/}');
dashboard.log('{cyan-fg}Press Ctrl+C or Q to exit{/}');
