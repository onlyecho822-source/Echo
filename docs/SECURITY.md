# OMEGA Echo - Security Architecture

## 🔐 Security Overview

The OMEGA Echo Cosmic Pipeline implements defense-in-depth security with multiple layers of protection:

1. **Cryptographic Canary System** - Detects vault tampering
2. **Process Isolation** - Container-based execution
3. **Pre-flight Security Checks** - PowerShell guardian validates environment
4. **Metabolic Noise Generation** - Obscures operational patterns
5. **Entropy-Based Monitoring** - Detects system anomalies

---

## 🛡️ Security Features

### 1. Canary System (Vault Integrity Monitoring)

**Purpose**: Detect unauthorized access or tampering of secrets vault.

**How it works**:
- A canary file (`vault_canary.txt`) contains an encrypted payload
- The payload is encrypted with AES-256-GCM
- A SHA-256 hash of the encrypted payload is stored alongside it
- A timestamp tracks freshness
- Any modification triggers immediate detection

**Security Properties**:
- ✅ Plaintext never stored on disk
- ✅ Tampering detected via hash mismatch
- ✅ Decryption failure indicates key compromise
- ✅ Staleness detection (>30 minutes = warning)

**Implementation**:
```javascript
// lib/omegaCanary.js
writeCanary()   // Creates encrypted canary with hash
checkCanary()   // Verifies integrity and freshness
```

**PowerShell Verification**:
```powershell
# scripts/Run-Embryo-Pipeline.ps1
Test-CanaryIntegrity()  // Hash verification
```

---

### 2. Process Isolation

**Purpose**: Contain the embryo in a restricted environment to minimize attack surface.

**Container Security**:
- Alpine Linux base (minimal attack surface)
- Non-root user execution (UID 1001)
- Read-only root filesystem
- Resource limits (CPU: 1 core, RAM: 512MB)
- No new privileges escalation
- Isolated tmpfs for temporary files

**Threat Mitigation**:
| Threat | Mitigation |
|--------|-----------|
| Container escape | Read-only FS + no-new-privileges |
| Resource exhaustion | Hard CPU/memory limits |
| Privilege escalation | Non-root user + dropped capabilities |
| File tampering | Read-only root FS |

---

### 3. Pre-Flight Security Checks

The PowerShell guardian performs comprehensive checks before launching the embryo:

#### Local Environment
- ✅ Node.js, npm, git, gh CLI installed
- ✅ OMEGA_SECRET_KEY present and valid (64-char hex)

#### Canary Integrity
- ✅ Canary file exists
- ✅ Hash matches encrypted payload
- ✅ Timestamp is fresh (<30 minutes)

#### Process Integrity
- ✅ No rogue Node.js processes running
- ✅ No suspicious processes (mimikatz, procdump, etc.)
- ✅ No unusual network connections (optional, requires admin)

#### GitHub Authentication
- ✅ GITHUB_TOKEN is valid
- ✅ Repository is accessible

---

### 4. Metabolic Noise Generation

**Purpose**: Create plausible deniability by obscuring real operations with dummy activity.

**Techniques**:
- Dummy vault read operations (random paths)
- CPU noise (crypto operations with random data)
- I/O noise (temp file writes/deletes)
- Randomized timing (jitter ±20%)

**Example**:
```javascript
// lib/omegaVaultNoise.js
runMetabolicNoise()  // Runs every 60 seconds with jitter
```

**Effect**: Attackers monitoring system activity cannot distinguish real from noise.

---

### 5. Entropy-Based Anomaly Detection

**Purpose**: Detect system instability, attacks, or operational issues.

**Entropy Calculation**:
```
Entropy = (0.15 * signal_frequency) +
          (0.20 * api_latency) +
          (0.45 * github_chaos_factor) +
          (0.20 * canary_status)
```

**GitHub Chaos Factors**:
- Open issues count (normalized)
- CI/CD workflow failures
- Missing branch protection
- Inactive or failed webhooks
- Repository staleness

**Canary Chaos Mapping**:
- OK → 0.0
- STALE → 0.3
- MISSING → 0.8
- TAMPERED → 1.0

**Entropy Levels**:
| Entropy | Level | Action |
|---------|-------|--------|
| 0.0-0.2 | STABLE | No action |
| 0.2-0.4 | LOW_CHAOS | Log warning |
| 0.4-0.6 | MODERATE_CHAOS | Alert recommended |
| 0.6-0.8 | HIGH_CHAOS | Trigger ritual |
| 0.8-1.0 | CRITICAL_CHAOS | Emergency procedures |

---

## 🚨 Threat Model & Mitigations

### Threat 1: Token Exposure
**Scenario**: GITHUB_TOKEN leaked via logs, memory dump, or code repository.

**Mitigations**:
- ✅ Token stored in environment variable only (not in code)
- ✅ .env file in .gitignore
- ✅ Container uses secret management (future: Vault/KMS)
- ✅ Short-lived tokens recommended (GitHub App installation tokens)

**Future Improvement**: Use GitHub OIDC tokens (1-hour lifetime).

---

### Threat 2: Supply Chain Attack
**Scenario**: Malicious dependency in npm package.

**Mitigations**:
- ✅ package-lock.json committed (reproducible builds)
- ✅ npm ci --only=production (no dev dependencies in container)
- ✅ Alpine base image (minimal packages)
- ⚠️ Manual: Run npm audit before deployment

**Future Improvement**: Implement Sigstore/cosign for dependency signing.

---

### Threat 3: Container Escape
**Scenario**: Attacker breaks out of Docker container to host.

**Mitigations**:
- ✅ Non-root user
- ✅ Read-only root filesystem
- ✅ no-new-privileges security opt
- ✅ Resource limits
- ✅ tmpfs for /tmp (no execution)

**Future Improvement**: Use gVisor or Kata Containers for VM-level isolation.

---

### Threat 4: Vault Compromise
**Scenario**: Attacker gains access to OMEGA_SECRET_KEY.

**Mitigations**:
- ✅ Canary system detects tampering (hash mismatch)
- ✅ Key rotation possible (regenerate canary)
- ⚠️ Manual: Store key in HSM or cloud KMS

**Future Improvement**: Multi-party computation (Shamir's Secret Sharing).

---

### Threat 5: Side-Channel Attack
**Scenario**: Timing analysis reveals operational patterns.

**Mitigations**:
- ✅ Metabolic noise generation
- ✅ Randomized intervals (jitter)
- ✅ Dummy operations mixed with real ones

**Future Improvement**: Constant-time cryptography, cover traffic.

---

### Threat 6: Insider Threat
**Scenario**: Authorized user misuses access.

**Mitigations**:
- ✅ Audit logs in embryo_status.json
- ✅ Ritual actions logged to dashboard
- ⚠️ Manual: Implement multi-person approval

**Future Improvement**: Require YubiKey for destructive operations.

---

### Threat 7: Denial of Service
**Scenario**: Flood of requests or high entropy crashes system.

**Mitigations**:
- ✅ Container resource limits (CPU/RAM)
- ✅ Rate limiting in entropy calculation
- ✅ Graceful degradation (skip checks if overloaded)

**Future Improvement**: Circuit breakers, queue-based processing.

---

## 🔑 Secret Management Best Practices

### Current Implementation

1. **Environment Variables**: Secrets loaded from `.env` file
2. **Canary Encryption**: OMEGA_SECRET_KEY encrypts canary file
3. **No Hardcoded Secrets**: All sensitive data from environment

### Recommended Practices

#### For Development
```bash
# Generate a secure OMEGA_SECRET_KEY
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Create .env file (never commit!)
cp .env.example .env
# Edit .env with your values
```

#### For Production

**Option 1: HashiCorp Vault**
```javascript
// Future enhancement
const vaultClient = require('node-vault')({ endpoint: 'https://vault.example.com' });
const secret = await vaultClient.read('secret/data/omega');
process.env.OMEGA_SECRET_KEY = secret.data.key;
```

**Option 2: Cloud KMS (AWS/Azure/GCP)**
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id omega-key --query SecretString --output text

# Azure Key Vault
az keyvault secret show --vault-name omega-vault --name omega-key --query value -o tsv

# GCP Secret Manager
gcloud secrets versions access latest --secret="omega-key"
```

**Option 3: GitHub Encrypted Secrets**
```yaml
# .github/workflows/deploy.yml
env:
  OMEGA_SECRET_KEY: ${{ secrets.OMEGA_SECRET_KEY }}
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🔒 Encryption Details

### Algorithm: AES-256-GCM

**Why GCM (Galois/Counter Mode)?**
- ✅ Authenticated encryption (confidentiality + integrity)
- ✅ Detects tampering via authentication tag
- ✅ Parallelizable (faster than CBC)
- ✅ Industry standard (TLS 1.3, NIST recommended)

**Key Properties**:
- Key size: 256 bits (32 bytes)
- IV size: 128 bits (16 bytes, randomly generated)
- Authentication tag: 128 bits

**Implementation**:
```javascript
const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
const encrypted = cipher.update(plaintext, 'utf8', 'hex') + cipher.final('hex');
const authTag = cipher.getAuthTag().toString('hex');
```

### Hash Function: SHA-256

**Why SHA-256?**
- ✅ Cryptographically secure (collision resistant)
- ✅ Fast and widely supported
- ✅ FIPS 140-2 compliant

**Usage**: Hash verification of encrypted payload to detect file tampering.

---

## 📊 Security Monitoring

### Real-Time Monitoring
- **Dashboard**: Terminal UI shows entropy, canary status, GitHub health
- **Status File**: `cosmic_status/embryo_status.json` for external monitoring
- **Logs**: Activity log in dashboard, JSON logs for SIEM integration

### Recommended External Monitoring

**SIEM Integration**:
```bash
# Example: Forward logs to Splunk
tail -f cosmic_status/embryo_status.json | \
  splunk add oneshot - -sourcetype json
```

**Alerting Rules**:
- Entropy > 0.8 for > 5 minutes → Critical alert
- Canary status = TAMPERED → Immediate page
- GitHub auth failure → Alert security team

---

## 🚀 Security Roadmap

### Short-Term (Next Release)
- [ ] GitHub App integration (short-lived tokens)
- [ ] Dependency signature verification (npm audit signatures)
- [ ] Automated security scanning (Snyk/Dependabot)

### Medium-Term
- [ ] Hardware Security Module (HSM) support
- [ ] Multi-party approval for destructive actions
- [ ] Blockchain-based audit log (immutable)

### Long-Term
- [ ] Zero-trust architecture with mutual TLS
- [ ] Quantum-resistant encryption (post-quantum crypto)
- [ ] AI-based anomaly detection for entropy

---

## 📞 Security Contact

**For security issues**: DO NOT open public GitHub issues.

**Report vulnerabilities to**:
- Email: [Specify security contact email]
- PGP Key: [If available]

**Expected Response Time**: 48 hours

---

## ✅ Security Checklist

Before deploying to production:

- [ ] OMEGA_SECRET_KEY is 64-char hex (256-bit entropy)
- [ ] GITHUB_TOKEN has minimum required scopes only
- [ ] .env file is NOT committed to git
- [ ] Container runs as non-root user
- [ ] Resource limits configured in docker-compose.yml
- [ ] Pre-flight checks enabled in PowerShell script
- [ ] Canary rotation interval set (default: 15 minutes)
- [ ] External monitoring configured (SIEM/alerts)
- [ ] Backup of OMEGA_SECRET_KEY stored securely
- [ ] Incident response plan documented

---

**Last Updated**: 2025-11-20
**Security Version**: 2.0.0
