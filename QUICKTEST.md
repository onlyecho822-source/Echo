# 🧪 Quick Test Guide

## ⚡ 60-Second Test

```bash
# 1. Setup (first time only)
npm install
cp .env.example .env

# 2. Generate secret key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Copy output and add to .env as OMEGA_SECRET_KEY

# 3. Add your GitHub token to .env
# Get token at: https://github.com/settings/tokens

# 4. Run all tests
./run-tests.sh
```

Expected output:
```
🌌 OMEGA ECHO - MASTER TEST SUITE

→ Running Canary System Test...
✔ Canary System Test PASSED

→ Running Entropy Engine Test...
✔ Entropy Engine Test PASSED

→ Running GitHub Integration Test...
✔ GitHub Integration Test PASSED

TEST SUMMARY
  Tests Run: 3
  Tests Passed: 3
  Tests Failed: 0

✅ ALL TESTS PASSED
```

---

## 🎯 Individual Component Tests

### Test Canary System
```bash
node test-canary.js
```
Tests:
- ✅ Module initialization
- ✅ Canary file creation
- ✅ Integrity verification
- ✅ Tampering detection (hash modification)
- ✅ Tampering detection (payload modification)
- ✅ Multiple write/check cycles

---

### Test Entropy Engine
```bash
node test-entropy.js
```
Tests:
- ✅ Zero and maximum entropy calculation
- ✅ Weighted entropy algorithm
- ✅ Input clamping (>1 values)
- ✅ GitHub chaos calculation (healthy/unhealthy repos)
- ✅ Canary chaos mapping
- ✅ Entropy level classification
- ✅ Ritual trigger thresholds
- ✅ Real-world CI failure scenario

---

### Test GitHub Integration
```bash
node test-github.js
```
Tests:
- ✅ GitHub API authentication
- ✅ Token scope verification
- ✅ API rate limit check
- ✅ Repository access (if GITHUB_REPO set)
- ✅ Workflow runs
- ✅ Branch protection status
- ✅ Webhooks configuration
- ✅ Issues access

---

## 🚀 Full System Test

### Option 1: Direct Node.js
```bash
# Run embryo for 10 seconds
timeout 10s node index.js || true

# Check outputs
cat vault_canary.txt
cat cosmic_status/embryo_status.json
```

### Option 2: With PowerShell Guardian
```powershell
# Windows PowerShell / PowerShell Core
.\scripts\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo"
```

### Option 3: Docker Container
```bash
# Build and run
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
cat cosmic_status/embryo_status.json

# Stop
docker-compose down
```

---

## 🔧 Troubleshooting

### "Module not found"
```bash
npm install
```

### "OMEGA_SECRET_KEY must be 64 characters"
```bash
# Generate new key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Add to .env
```

### "GitHub authentication failed"
```bash
# Check token
echo $GITHUB_TOKEN

# Generate new token at:
# https://github.com/settings/tokens
# Required scopes: repo, workflow
```

### Tests pass but embryo won't start
```bash
# Check for port conflicts
lsof -i :3000

# Check logs
cat cosmic_status/embryo_status.json
```

---

## 📊 Expected Test Results

### All Tests Passing (Healthy)
```
🧪 CANARY SYSTEM TEST
  Tests Passed: 7
  Tests Failed: 0

🧪 ENTROPY ENGINE TEST
  Tests Passed: 45
  Tests Failed: 0

🧪 GITHUB INTEGRATION TEST
  Tests Passed: 5-8
  Tests Failed: 0
```

### Healthy System Status
```json
{
  "timestamp": "2025-11-20T12:34:56.789Z",
  "entropy": 0.234,
  "entropyLevel": "LOW_CHAOS",
  "canaryFileIntegrity": "OK",
  "githubStatus": {
    "repoName": "onlyecho822-source/Echo",
    "latestWorkflowStatus": "success"
  }
}
```

---

## 🎓 What Each Test Validates

| Test | What It Checks | Why It Matters |
|------|----------------|----------------|
| **Canary** | Encryption, hash verification, tampering detection | Ensures vault integrity monitoring works |
| **Entropy** | Chaos calculation, GitHub metrics, trigger thresholds | Validates anomaly detection algorithm |
| **GitHub** | API access, token scopes, repo permissions | Confirms GitHub integration is operational |

---

## 🏁 Next Steps After Testing

1. ✅ **All tests pass** → You're ready for production!
   ```bash
   # Deploy with Docker
   docker-compose up -d
   ```

2. ⚠️ **Some tests fail** → Check docs/TESTING.md for detailed troubleshooting

3. 📈 **Tests pass, want more** → See docs/SETUP.md for:
   - GitHub Actions integration
   - SIEM monitoring setup
   - Custom ritual actions
   - Multi-environment deployment

---

**Test Duration**: ~30 seconds (all 3 tests)
**Last Updated**: 2025-11-20
