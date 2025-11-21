#!/usr/bin/env node
/**
 * OMEGA Echo - GitHub Integration Test
 * Tests GitHub API connectivity and repository access
 */

require('dotenv').config();
const { Octokit } = require('@octokit/rest');

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('   🧪 GITHUB INTEGRATION TEST');
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

function skip(message) {
    console.log(`⚠️  SKIP: ${message}`);
}

// Verify environment
if (!process.env.GITHUB_TOKEN) {
    fail('GITHUB_TOKEN not set in environment');
    console.log('\nGenerate a token at: https://github.com/settings/tokens');
    console.log('Required scopes: repo, workflow');
    process.exit(1);
}

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

async function runTests() {
    // Test 1: Authenticate to GitHub
    console.log('Test 1: GitHub API authentication');
    try {
        const { data: user } = await octokit.users.getAuthenticated();
        pass(`Authenticated as ${user.login}`);
        console.log(`  Account type: ${user.type}`);
        console.log(`  Profile: ${user.html_url}`);
    } catch (error) {
        fail(`Authentication failed: ${error.message}`);
        if (error.status === 401) {
            console.log('  Hint: Token may be invalid or expired');
        }
        process.exit(1);
    }
    console.log('');

    // Test 2: Verify token scopes
    console.log('Test 2: Verify token scopes');
    try {
        const response = await octokit.request('GET /user');
        const scopes = response.headers['x-oauth-scopes'];

        if (scopes) {
            console.log(`  Scopes: ${scopes}`);

            const scopeList = scopes.split(', ').map(s => s.trim());
            const hasRepo = scopeList.includes('repo');
            const hasWorkflow = scopeList.includes('workflow');

            if (hasRepo && hasWorkflow) {
                pass('Token has required scopes (repo, workflow)');
            } else {
                fail(`Missing required scopes. Has: ${scopes}`);
                console.log('  Required: repo, workflow');
            }
        } else {
            skip('Could not determine token scopes (may be fine-grained token)');
        }
    } catch (error) {
        skip(`Scope check failed: ${error.message}`);
    }
    console.log('');

    // Test 3: Rate limit check
    console.log('Test 3: Check API rate limits');
    try {
        const { data: rateLimit } = await octokit.rateLimit.get();
        const core = rateLimit.resources.core;

        console.log(`  Remaining: ${core.remaining}/${core.limit}`);
        console.log(`  Resets at: ${new Date(core.reset * 1000).toLocaleTimeString()}`);

        if (core.remaining > 100) {
            pass('Sufficient API rate limit remaining');
        } else if (core.remaining > 10) {
            pass('API rate limit OK (but running low)');
            console.log(`  Warning: Only ${core.remaining} requests remaining`);
        } else {
            fail(`API rate limit critically low: ${core.remaining}`);
        }
    } catch (error) {
        fail(`Rate limit check failed: ${error.message}`);
    }
    console.log('');

    // Test 4: Repository access (if GITHUB_REPO is set)
    if (!process.env.GITHUB_REPO) {
        skip('GITHUB_REPO not set, skipping repository tests');
        console.log('  Set GITHUB_REPO=owner/repo to test repository access\n');
        return;
    }

    const [owner, repo] = process.env.GITHUB_REPO.split('/');

    if (!owner || !repo) {
        fail(`Invalid GITHUB_REPO format: ${process.env.GITHUB_REPO}`);
        console.log('  Expected format: owner/repo\n');
        return;
    }

    console.log(`Test 4: Access repository ${owner}/${repo}`);
    try {
        const { data: repoData } = await octokit.repos.get({ owner, repo });

        pass('Repository accessible');
        console.log(`  Full name: ${repoData.full_name}`);
        console.log(`  Private: ${repoData.private}`);
        console.log(`  Default branch: ${repoData.default_branch}`);
        console.log(`  Open issues: ${repoData.open_issues_count}`);
        console.log(`  Last push: ${repoData.pushed_at}`);
    } catch (error) {
        fail(`Repository access failed: ${error.message}`);
        if (error.status === 404) {
            console.log('  Hint: Repository not found or token lacks access');
        }
        return;
    }
    console.log('');

    // Test 5: Workflow runs (if Actions is enabled)
    console.log('Test 5: Fetch workflow runs');
    try {
        const { data: workflowRuns } = await octokit.actions.listWorkflowRunsForRepo({
            owner,
            repo,
            per_page: 5,
        });

        if (workflowRuns.total_count > 0) {
            pass(`Found ${workflowRuns.total_count} workflow runs`);
            console.log(`  Latest run: ${workflowRuns.workflow_runs[0].name}`);
            console.log(`  Status: ${workflowRuns.workflow_runs[0].status}`);
            console.log(`  Conclusion: ${workflowRuns.workflow_runs[0].conclusion || 'N/A'}`);
        } else {
            skip('No workflow runs found (Actions may not be configured)');
        }
    } catch (error) {
        skip(`Workflow runs not accessible: ${error.message}`);
    }
    console.log('');

    // Test 6: Branch protection (requires admin access)
    console.log('Test 6: Check branch protection');
    try {
        const { data: repoData } = await octokit.repos.get({ owner, repo });
        const defaultBranch = repoData.default_branch;

        const { data: protection } = await octokit.repos.getBranchProtection({
            owner,
            repo,
            branch: defaultBranch,
        });

        pass(`Branch protection configured on ${defaultBranch}`);
        console.log(`  Required status checks: ${protection.required_status_checks ? 'Yes' : 'No'}`);
        console.log(`  Enforce admins: ${protection.enforce_admins?.enabled ? 'Yes' : 'No'}`);
        console.log(`  Restrictions: ${protection.restrictions ? 'Yes' : 'No'}`);
    } catch (error) {
        if (error.status === 404) {
            skip('No branch protection configured (or no access)');
        } else {
            skip(`Branch protection check failed: ${error.message}`);
        }
    }
    console.log('');

    // Test 7: Webhooks (requires admin access)
    console.log('Test 7: List webhooks');
    try {
        const { data: webhooks } = await octokit.repos.listWebhooks({ owner, repo });

        if (webhooks.length > 0) {
            pass(`Found ${webhooks.length} webhook(s)`);
            webhooks.forEach((hook, i) => {
                console.log(`  ${i + 1}. ${hook.name} (active: ${hook.active})`);
                console.log(`     Events: ${hook.events.join(', ')}`);
            });
        } else {
            skip('No webhooks configured');
        }
    } catch (error) {
        skip(`Webhooks not accessible: ${error.message}`);
    }
    console.log('');

    // Test 8: Issues access
    console.log('Test 8: List recent issues');
    try {
        const { data: issues } = await octokit.issues.listForRepo({
            owner,
            repo,
            state: 'all',
            per_page: 3,
        });

        if (issues.length > 0) {
            pass(`Found ${issues.length} recent issue(s)`);
            issues.forEach((issue, i) => {
                console.log(`  ${i + 1}. #${issue.number}: ${issue.title} (${issue.state})`);
            });
        } else {
            skip('No issues found');
        }
    } catch (error) {
        fail(`Issues access failed: ${error.message}`);
    }
    console.log('');

    // Summary
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`   Tests Passed: ${testsPassed}`);
    console.log(`   Tests Failed: ${testsFailed}`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    process.exit(testsFailed > 0 ? 1 : 0);
}

runTests().catch((error) => {
    console.error('\n❌ Unexpected error:', error.message);
    process.exit(1);
});
