# OMEGA Echo - Setup Guide

## 🚀 Quick Start

This guide will help you set up and run the OMEGA Echo Cosmic Pipeline in minutes.

---

## Prerequisites

### Required Software
- **Node.js** 18.x or later ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Git** ([Download](https://git-scm.com/))
- **PowerShell** 5.1+ (Windows) or PowerShell Core 7+ (Cross-platform)

### Optional (for container deployment)
- **Docker** and **Docker Compose** ([Download](https://www.docker.com/))
- **GitHub CLI (gh)** ([Download](https://cli.github.com/))

### Verify Installation
```bash
node --version   # Should be v18.x or later
npm --version    # Should be 8.x or later
git --version    # Any recent version
```

---

## Step 1: Clone Repository

```bash
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo
```

---

## Step 2: Install Dependencies

```bash
npm install
```

This installs:
- `@octokit/rest` - GitHub API client
- `blessed` - Terminal UI framework
- `blessed-contrib` - Terminal UI widgets
- `dotenv` - Environment variable loader

---

## Step 3: Configure Environment

### 3.1 Create .env File

```bash
cp .env.example .env
```

### 3.2 Generate OMEGA_SECRET_KEY

This is a 256-bit (32-byte) encryption key for the canary system.

**Linux/macOS/PowerShell**:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Example output**:
```
a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
```

### 3.3 Get GitHub Personal Access Token

1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name (e.g., "OMEGA Echo Pipeline")
4. Select scopes:
   - ✅ `repo` (all)
   - ✅ `workflow`
   - ✅ `read:org` (if monitoring org repos)
5. Click **Generate token**
6. **Copy the token** (you won't see it again!)

### 3.4 Edit .env File

Open `.env` in a text editor and fill in:

```bash
# OMEGA SECRET KEY (REQUIRED)
OMEGA_SECRET_KEY=a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890

# GITHUB TOKEN (REQUIRED)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# GITHUB REPOSITORY (OPTIONAL)
GITHUB_REPO=onlyecho822-source/Echo
```

**⚠️ IMPORTANT**: Never commit `.env` to git! It's already in `.gitignore`.

---

## Step 4: Run the Pipeline

### Option A: Direct Node.js Execution

```bash
node index.js
```

You should see the OMEGA Echo dashboard with:
- System entropy gauge
- Canary status
- Activity log

**Press `Q` or `Ctrl+C` to exit.**

---

### Option B: PowerShell Guardian (Recommended)

The PowerShell script performs comprehensive pre-flight security checks before launching.

**Windows PowerShell**:
```powershell
$env:GITHUB_TOKEN = "ghp_xxxx..."
$env:OMEGA_SECRET_KEY = "a1b2c3d4..."

.\scripts\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo"
```

**PowerShell Core (Linux/macOS)**:
```bash
export GITHUB_TOKEN="ghp_xxxx..."
export OMEGA_SECRET_KEY="a1b2c3d4..."

pwsh ./scripts/Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo"
```

**Skip system checks (if not administrator)**:
```powershell
.\scripts\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo" -SkipSystemChecks
```

---

### Option C: Docker Container (Most Secure)

Build and run in an isolated container:

```bash
# Build the container
docker-compose build

# Run the container
docker-compose up
```

**To stop**:
```bash
docker-compose down
```

**View logs**:
```bash
docker-compose logs -f omega-embryo
```

---

## Step 5: Verify Operation

### Check Dashboard
If running directly, you'll see the terminal UI dashboard.

### Check Status File
The embryo writes its status to `cosmic_status/embryo_status.json`:

```bash
cat cosmic_status/embryo_status.json
```

**Example output**:
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
    "latestWorkflowStatus": "success"
  },
  "canaryFileIntegrity": "OK",
  "metabolicNoiseLastRun": "2025-11-20T12:34:45.123Z",
  "dummyVaultReadsTotal": 6,
  "noiseGeneratedBytes": 15360
}
```

### Check Canary File
The canary file should exist at `vault_canary.txt`:

```bash
cat vault_canary.txt
```

**Example output** (encrypted, not readable):
```json
{
  "encryptedPayload": "a1b2c3d4:e5f6a7b8:c9d0e1f2...",
  "hashOfEncryptedPayload": "f3e4d5c6b7a8...",
  "timestamp": "2025-11-20T12:30:00.000Z",
  "version": "2.0"
}
```

---

## Troubleshooting

### Error: "Missing required environment variable"

**Problem**: `.env` file not loaded or variables not set.

**Solution**:
```bash
# Check if .env exists
ls -la .env

# Verify contents
cat .env

# Ensure variables are set
echo $env:OMEGA_SECRET_KEY  # PowerShell
echo $OMEGA_SECRET_KEY      # Bash
```

---

### Error: "OMEGA_SECRET_KEY must be 64 characters"

**Problem**: Key is wrong length.

**Solution**: Regenerate key:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

### Error: "GitHub authentication failed"

**Problem**: Token is invalid or lacks required scopes.

**Solutions**:
1. Verify token hasn't expired
2. Check token scopes at [https://github.com/settings/tokens](https://github.com/settings/tokens)
3. Regenerate token with correct scopes (`repo`, `workflow`)

---

### Error: "Canary file MISSING"

**Problem**: First run, or file was deleted.

**Solution**: This is normal on first run. The embryo creates it automatically.

If it persists:
```bash
# Delete and let embryo recreate
rm vault_canary.txt
node index.js
```

---

### Error: "Module not found: blessed"

**Problem**: Dependencies not installed.

**Solution**:
```bash
npm install
```

---

### PowerShell: "Running scripts is disabled"

**Problem**: PowerShell execution policy blocks scripts.

**Solution** (Windows):
```powershell
# Allow scripts for current session (safe)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Then run the script
.\scripts\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo"
```

---

### Docker: "Permission denied"

**Problem**: Current user not in `docker` group (Linux).

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then:
docker-compose up
```

---

## Configuration Options

### Monitoring Intervals

Edit `index.js` to change intervals:

```javascript
const MONITORING_INTERVAL_MS = 5000;        // Check entropy every 5 seconds
const CANARY_ROTATION_INTERVAL_MS = 900000; // Rotate canary every 15 minutes
const NOISE_INTERVAL_MS = 60000;            // Run metabolic noise every minute
```

### Entropy Thresholds

Edit `lib/omegaEntropy.js` to adjust chaos weights:

```javascript
const weights = {
    signal: 0.15,   // Signal frequency weight
    latency: 0.20,  // API latency weight
    github: 0.45,   // GitHub chaos weight (highest)
    canary: 0.20    // Canary status weight
};
```

### Resource Limits (Docker)

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'     # Increase CPU limit
      memory: 1024M   # Increase RAM limit
```

---

## Next Steps

### 1. Set Up Monitoring

Forward status to external monitoring:

**Splunk**:
```bash
tail -f cosmic_status/embryo_status.json | \
  splunk add oneshot - -sourcetype json
```

**Datadog**:
```bash
# Install Datadog agent, then:
echo "logs_enabled: true" >> /etc/datadog-agent/datadog.yaml
```

### 2. Enable Alerting

Configure alerts based on entropy:

**Example (PagerDuty)**:
```bash
# Monitor entropy > 0.8
jq '.entropy' cosmic_status/embryo_status.json | \
  awk '$1 > 0.8 { print "HIGH ENTROPY ALERT" }'
```

### 3. Automate Deployment

Create a GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy OMEGA Echo

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and deploy
        env:
          OMEGA_SECRET_KEY: ${{ secrets.OMEGA_SECRET_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          docker-compose up -d
```

### 4. Implement Rituals

Edit `index.js` to add custom ritual actions:

```javascript
function executeRitual(entropy) {
    if (entropy > 0.8) {
        // Trigger emergency workflow
        octokit.actions.createWorkflowDispatch({
            owner: 'onlyecho822-source',
            repo: 'Echo',
            workflow_id: 'emergency.yml',
            ref: 'main'
        });
    }
}
```

---

## Security Best Practices

✅ **DO**:
- Keep `.env` file secure (never commit to git)
- Rotate OMEGA_SECRET_KEY periodically
- Use short-lived GitHub App tokens (not PATs)
- Monitor canary status daily
- Review entropy trends weekly

❌ **DON'T**:
- Hardcode secrets in code
- Use `repo:admin` scope unless absolutely needed
- Run as root/administrator
- Disable pre-flight checks (unless testing)
- Ignore HIGH_CHAOS or CRITICAL_CHAOS entropy levels

---

## Support

**Documentation**: See `docs/` directory
- `SECURITY.md` - Security architecture
- `ARCHITECTURE.md` - System design (if exists)

**Issues**: [GitHub Issues](https://github.com/onlyecho822-source/Echo/issues)

**Community**: [Discussions](https://github.com/onlyecho822-source/Echo/discussions)

---

**Last Updated**: 2025-11-20
**Version**: 2.0.0
