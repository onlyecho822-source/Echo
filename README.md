# Echo - OMEGA Cosmic Pipeline

**A hardened, self-monitoring GitHub integration framework with defense-in-depth security.**

---

## 🌌 Overview

Echo OMEGA is a production-grade DevOps pipeline that integrates with GitHub repositories to provide:

- **🔐 Cryptographic Vault Integrity Monitoring** (Canary System)
- **📊 Real-Time Entropy-Based Anomaly Detection**
- **🛡️ Defense-in-Depth Security Architecture**
- **🐳 Container-Based Process Isolation**
- **🔍 Comprehensive Pre-Flight Security Checks**
- **📈 Live Terminal UI Dashboard**

Built for the **Echo Civilization framework** — a lawful, harmonic, multi-agent intelligence ecosystem designed for transparency, adaptability, and resilience.

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ ([Download](https://nodejs.org/))
- PowerShell 5.1+ or PowerShell Core 7+ ([Download](https://github.com/PowerShell/PowerShell))
- GitHub Personal Access Token ([Create](https://github.com/settings/tokens))

### Installation

```bash
# Clone repository
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your OMEGA_SECRET_KEY and GITHUB_TOKEN
```

### Run

**Direct execution**:
```bash
node index.js
```

**With PowerShell guardian (recommended)**:
```powershell
.\scripts\Run-Embryo-Pipeline.ps1 -Repo "onlyecho822-source/Echo"
```

**Docker container (most secure)**:
```bash
docker-compose up
```

📖 **Full setup guide**: See [docs/SETUP.md](docs/SETUP.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│         PowerShell Guardian (Perimeter)             │
│  • Pre-flight security checks                       │
│  • Canary integrity verification                    │
│  • Process monitoring                               │
│  • GitHub authentication                            │
└────────────────┬────────────────────────────────────┘
                 │ Launches
                 ↓
┌─────────────────────────────────────────────────────┐
│         Node.js OMEGA Embryo (Core)                 │
│  ┌───────────────────────────────────────────────┐  │
│  │  Canary System    →  Vault Integrity          │  │
│  │  Entropy Engine   →  Anomaly Detection        │  │
│  │  GitHub Client    →  Repository Monitoring    │  │
│  │  Metabolic Noise  →  Operational Security     │  │
│  │  Dashboard UI     →  Real-Time Visualization  │  │
│  └───────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────┘
                 │ Reports to
                 ↓
         cosmic_status/embryo_status.json
```

---

## 🔐 Security Features

### 1. Cryptographic Canary System
- **AES-256-GCM** encryption with authenticated encryption
- **SHA-256** hash verification of encrypted payloads
- Detects any tampering or unauthorized vault access
- Automatic rotation every 15 minutes

### 2. Process Isolation
- Docker container with non-root user execution
- Read-only root filesystem
- Resource limits (CPU: 1 core, RAM: 512MB)
- No privilege escalation

### 3. Pre-Flight Security Checks
PowerShell guardian validates:
- ✅ Local dependencies (Node.js, npm, git, gh)
- ✅ Canary file integrity (hash + timestamp)
- ✅ Process integrity (no rogue processes)
- ✅ GitHub authentication
- ✅ Repository accessibility

### 4. Entropy-Based Monitoring
Calculates system entropy from:
- GitHub repository health (CI failures, open issues, branch protection)
- Canary integrity status
- API latency and signal frequency

**Entropy Levels**:
- `0.0-0.2`: STABLE
- `0.2-0.4`: LOW_CHAOS
- `0.4-0.6`: MODERATE_CHAOS (alerts recommended)
- `0.6-0.8`: HIGH_CHAOS (trigger rituals)
- `0.8-1.0`: CRITICAL_CHAOS (emergency procedures)

### 5. Metabolic Noise Generation
Obscures operational patterns with:
- Dummy vault read operations
- CPU noise (cryptographic operations)
- I/O noise (temp file operations)
- Randomized timing (jitter)

🔒 **Security documentation**: See [docs/SECURITY.md](docs/SECURITY.md)

---

## 📊 Dashboard

Real-time terminal UI showing:

```
┌─ System Entropy ───────┐  ┌─ System Status ──────────────────┐
│                         │  │ Entropy Level: LOW_CHAOS         │
│  ████████░░░░░░  38%    │  │ Canary: OK                       │
│                         │  │ GitHub: OK                       │
└─────────────────────────┘  │ Rituals Triggered: 0             │
                             │                                  │
                             │ Press 'q' to exit                │
                             └──────────────────────────────────┘

┌─ Activity Log ──────────────────────────────────────────────┐
│ [12:34:56] ✔ Canary integrity OK (age: 5.2 min)            │
│ [12:35:01] → Running metabolic noise cycle...               │
│ [12:35:01] ✔ Metabolic noise cycle complete                │
│ [12:35:06] OMEGA monitoring loop active (Entropy: 0.234)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Echo/
├── index.js                   # Main embryo entry point
├── package.json              # Dependencies
├── Dockerfile                # Container image
├── docker-compose.yml        # Container orchestration
├── .env.example              # Environment template
│
├── lib/                      # Core modules
│   ├── omegaCanary.js       # Canary system (AES-256-GCM)
│   ├── omegaEntropy.js      # Entropy calculation
│   ├── omegaVaultNoise.js   # Metabolic noise generator
│   └── dashboard.js         # Terminal UI
│
├── scripts/
│   └── Run-Embryo-Pipeline.ps1  # PowerShell guardian
│
├── cosmic_status/           # Status output directory
│   └── embryo_status.json   # Real-time status (auto-generated)
│
└── docs/                    # Documentation
    ├── SETUP.md             # Setup guide
    └── SECURITY.md          # Security architecture
```

---

## 🛠️ Usage

### Basic Monitoring

```bash
# Run the embryo
node index.js

# Status is written to:
cat cosmic_status/embryo_status.json
```

### With Pre-Flight Checks

```powershell
# PowerShell guardian performs security checks before launch
.\scripts\Run-Embryo-Pipeline.ps1 -Repo "owner/repo"
```

### Container Deployment

```bash
# Build and run in isolated container
docker-compose up -d

# View logs
docker-compose logs -f omega-embryo

# Stop
docker-compose down
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# REQUIRED: 256-bit encryption key (64-char hex)
OMEGA_SECRET_KEY=<generated-key>

# REQUIRED: GitHub Personal Access Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OPTIONAL: Repository to monitor
GITHUB_REPO=owner/repo
```

**Generate OMEGA_SECRET_KEY**:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Monitoring Intervals

Edit `index.js`:

```javascript
const MONITORING_INTERVAL_MS = 5000;        // Entropy check interval
const CANARY_ROTATION_INTERVAL_MS = 900000; // Canary rotation (15 min)
const NOISE_INTERVAL_MS = 60000;            // Metabolic noise (1 min)
```

---

## 🎯 Use Cases

### 1. CI/CD Pipeline Monitoring
Monitor repository health and trigger actions based on entropy:
- CI failures increase entropy → trigger investigation workflows
- Missing branch protection → alert security team
- High open issue count → prioritize triage

### 2. Security Auditing
- Canary system detects unauthorized vault access
- Process monitoring catches rogue scripts
- Entropy spikes indicate potential attacks

### 3. Operational Resilience
- Self-healing via automatic restart (Docker)
- State persistence in `embryo_status.json`
- Graceful degradation on high load

---

## 📚 Documentation

- **[SETUP.md](docs/SETUP.md)** - Complete installation and configuration guide
- **[SECURITY.md](docs/SECURITY.md)** - Security architecture and threat model

---

## 🔄 Roadmap

### Phase 1: Foundation (Current)
- ✅ Cryptographic canary system
- ✅ Entropy-based monitoring
- ✅ PowerShell pre-flight checks
- ✅ Docker containerization

### Phase 2: Enhanced Security
- [ ] GitHub App integration (short-lived tokens)
- [ ] Dependency signature verification
- [ ] Multi-party approval for destructive actions

### Phase 3: Advanced Features
- [ ] Webhook-based real-time events
- [ ] Machine learning-based anomaly detection
- [ ] Distributed deployment across cloud providers

### Phase 4: Ecosystem Integration
- [ ] Slack/Teams/Discord alerting
- [ ] SIEM integration (Splunk, Datadog)
- [ ] Kubernetes orchestration

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Security vulnerabilities**: Please report privately to [specify contact].

---

## 📄 License

ISC License - See [LICENSE](LICENSE) file for details.

---

## 👤 Author

**∇θ Operator: Nathan Poinsette**
Founder • Archivist • Systems Engineer

**Echo Civilization Framework**
*Resonant computation • Ethical design • Adaptive systems*

---

## 🌟 Acknowledgments

This project implements principles from:
- NIST Cybersecurity Framework
- Defense Information Systems Agency (DISA) STIGs
- CIS Benchmarks for containerization
- OWASP Secure Coding Practices

Built with ❤️ for the Echo Civilization ecosystem.

---

**Status**: 🟢 Active Development
**Version**: 2.0.0
**Last Updated**: 2025-11-20
