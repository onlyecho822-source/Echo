# Truth Ledger

**Independent API Status Verification with Cryptographic Proof**

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** January 21, 2026

---

## Overview

Truth Ledger is an immutable monitoring system that verifies API uptime claims by directly testing endpoints and comparing against official status pages. Every check is cryptographically hashed and chained, creating an irreversible record of truth.

> "Anyone can write the code; nobody can buy last month's data if they didn't record it."

---

## The Problem

- API providers claim "99.99% uptime" but measure selectively
- Official status pages show "all systems operational" during outages
- No independent verification of uptime claims
- Historical data can be rewritten
- Users have no proof when services fail

---

## The Solution

Truth Ledger creates an **immutable baseline** by:

1. **Direct Testing:** Checks 20 critical APIs every hour
2. **Cryptographic Hashing:** Each check is SHA-256 hashed and chained
3. **Multi-Source Verification:** Compares measurements vs. official claims
4. **Discrepancy Detection:** Flags variances >2% automatically
5. **Public Proof:** All data stored in immutable SQLite database

---

## Features

### Core Monitoring
- Monitors 20 critical APIs (Stripe, OpenAI, GitHub, AWS, etc.)
- Hourly checks with configurable intervals
- Response time measurement
- Status code tracking
- Timeout and error detection

### Immutable Ledger
- SQLite database with cryptographic hashing
- Blockchain-like chain of checks
- Each check links to previous via SHA-256
- Database cannot be modified retroactively
- Integrity verification built-in

### Discrepancy Detection
- Compares measurements vs. official status pages
- Flags variances >2%
- Severity classification (low, medium, high, critical)
- Automated daily reports
- Cryptographic proof of discrepancies

### Production Ready
- Systemd service for continuous operation
- Automated daily backups
- Comprehensive logging
- Error handling and retry logic
- Low resource usage (~50 MB RAM)

---

## Architecture

```
truth_ledger.py          → Main monitoring script
database.py              → Immutable SQLite operations
api_sources.py           → API configurations
reveal_truth.py          → Discrepancy detection
dashboard.html           → Public status page
setup.sh                 → Automated deployment
```

### Database Schema

```sql
checks (
    id, timestamp, api_name, endpoint, status,
    response_time_ms, status_code, source,
    check_hash, previous_hash  ← Blockchain-like chain
)

discrepancies (
    timestamp, api_name, claimed_status, actual_status,
    claimed_uptime, measured_uptime, variance_percent,
    proof_hashes, severity
)

sources (
    api_name, source_type, source_url,
    verification_method, reliability_score
)
```

### Cryptographic Verification

Each check is hashed using:

```python
SHA256(
    timestamp + api_name + endpoint + status +
    response_time + status_code + previous_hash
)
```

This creates a chain where modifying any historical check breaks all subsequent hashes.

---

## Monitored APIs

| API | Endpoint | Frequency |
|-----|----------|-----------|
| Stripe | api.stripe.com | Every hour |
| OpenAI | api.openai.com | Every hour |
| GitHub | api.github.com | Every hour |
| AWS | status.aws.amazon.com | Every hour |
| Vercel | api.vercel.com | Every hour |
| Cloudflare | api.cloudflare.com | Every hour |
| Binance | api.binance.com | Every hour |
| CoinGecko | api.coingecko.com | Every hour |
| Alpha Vantage | www.alphavantage.co | Every hour |
| IEX Cloud | cloud.iexapis.com | Every hour |
| Finnhub | finnhub.io | Every hour |
| Twitter/X | api.twitter.com | Every hour |
| Reddit | www.reddit.com | Every hour |
| Google Cloud | status.cloud.google.com | Every hour |
| Azure | status.azure.com | Every hour |
| Heroku | api.heroku.com | Every hour |
| Railway | backboard.railway.app | Every hour |
| Render | api.render.com | Every hour |
| Supabase | api.supabase.com | Every hour |
| PlanetScale | api.planetscale.com | Every hour |

---

## Quick Start

### Prerequisites

- Ubuntu 22.04+ / Debian 11+ / Raspberry Pi OS
- Python 3.8+
- 1 GB RAM
- 10 GB storage

### Installation (5 minutes)

```bash
# 1. Upload files to your server
scp -r truth-ledger/ root@YOUR_SERVER:/root/

# 2. SSH to server
ssh root@YOUR_SERVER

# 3. Run setup script
cd /root/truth-ledger
chmod +x setup.sh
sudo ./setup.sh

# 4. Verify it's running
systemctl status truth-ledger
```

---

## Usage

### Monitor APIs

```bash
# Continuous monitoring (default: every hour)
python3 truth_ledger.py

# Run once and exit
python3 truth_ledger.py --once

# Custom interval (30 minutes)
python3 truth_ledger.py --interval 1800

# View statistics
python3 truth_ledger.py --stats

# Verify chain integrity
python3 truth_ledger.py --verify
```

### Detect Discrepancies

```bash
# Check all APIs for discrepancies
python3 reveal_truth.py

# Check specific API
python3 reveal_truth.py --api stripe

# Analyze last 7 days
python3 reveal_truth.py --hours 168

# Generate report
python3 reveal_truth.py --report my_report.md
```

---

## Technical Specifications

### Performance
- **Memory:** ~50 MB RAM
- **CPU:** <1% average
- **Disk:** ~50 MB/month database growth
- **Network:** ~100 KB/hour bandwidth

### Dependencies

```
requests==2.31.0        # HTTP client
beautifulsoup4==4.12.3  # HTML parsing
lxml==5.1.0             # XML/HTML parser
```

### Security
- Runs as non-root user truth-ledger
- No external dependencies in production
- Database stored locally only
- No credentials required for most APIs

---

## Deployment Options

| Option | Cost | Setup Time | Reliability |
|--------|------|------------|-------------|
| DigitalOcean | $6/month | 5 minutes | High |
| Linode | $6/month | 5 minutes | High |
| AWS Lightsail | $5/month | 10 minutes | High |
| Raspberry Pi | $35-50 one-time | 15 minutes | Depends on home internet |

---

## Philosophy

Truth Ledger is not about fancy features or dashboards. It is about:

1. **Starting today** - Every hour we delay is data lost
2. **The baseline** - Irreplaceable historical record
3. **Independence** - No one can rewrite what we've recorded
4. **Proof** - Cryptographic verification, not trust

**The silence is where the value grows.**

---

## Related Documents

- [INSTITUTIONAL_ROADMAP.md](../roadmaps/INSTITUTIONAL_ROADMAP.md) - Phase 1-4 trajectory
- [PROJECT_MANAGEMENT_PLAN.md](../roadmaps/PROJECT_MANAGEMENT_PLAN.md) - Execution plan
- [BUSINESS_MODEL.md](../roadmaps/BUSINESS_MODEL.md) - Revenue strategy

---

## License

MIT License - See LICENSE file
