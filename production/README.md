# Echo Phoenix Control Service

**Version 2.4.0** | **Production Ready** | **26/26 Tests Passing**

---

## Overview

The Echo Phoenix Control Service is a **continuous control system** for the Echo AI framework, implementing real-time state observation, proportional control, and emergency shutdown capabilities. It integrates the **Unified Theory of Viability-Evolvability Duality** for optimal system adaptability.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **State Observation** | Real-time monitoring of system health, viability metrics (Φ_s, Φ_d), and temperature |
| **Continuous Control** | Proportional control loop for throttle management with configurable gain |
| **Global Kill Plane** | Emergency shutdown capability with confirmation safeguard |
| **Stripe Integration** | Exactly-once payment processing with idempotency and deduplication |
| **Evidence Ledger** | Complete audit trail for all operations via Airtable |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ECHO PHOENIX v2.4                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Zapier     │───▶│   FastAPI    │───▶│   Airtable   │       │
│  │  Automations │    │   Service    │    │   (EIL)      │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         │                   ▼                   │                │
│         │            ┌──────────────┐           │                │
│         │            │    Stripe    │           │                │
│         │            │   Wrapper    │           │                │
│         │            └──────────────┘           │                │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   CONTROL LOOP                           │    │
│  │  Observer ──▶ Controller ──▶ Executor ──▶ Observer       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd production
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export AIRTABLE_API_KEY="pat_your_token"
export AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"
export STRIPE_SECRET_KEY="sk_live_your_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_secret"
```

### 3. Run Tests

```bash
python -m pytest tests/test_system.py -v
# Expected: 26 passed
```

### 4. Deploy

```bash
# Local
./scripts/deploy.sh local

# Fly.io
./scripts/deploy.sh fly

# Railway
./scripts/deploy.sh railway
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/observe` | POST | Capture current system state |
| `/control` | POST | Compute and apply control action |
| `/kill` | POST | Emergency shutdown (requires confirmation) |
| `/revive` | POST | Deactivate kill switch |
| `/metrics` | GET | Prometheus-compatible metrics |
| `/webhook/stripe` | POST | Handle Stripe webhooks |

---

## Viability-Evolvability Theory

The system implements the **Unified Theory of Viability-Evolvability Duality**:

```
Λ = f(T) × (Φ_d / Φ_s)
```

Where:
- **Λ** = Evolvability (adaptability)
- **f(T)** = Temperature coupling function (peaks at T_c ≈ 0.9)
- **Φ_d** = Dynamic viability (gradient strength during learning)
- **Φ_s** = Static viability (attractor depth at equilibrium)

**Key Insight**: The system operates optimally near the critical temperature (T_c ≈ 0.9), where susceptibility to perturbation peaks and maximum adaptability is achieved.

---

## File Structure

```
production/
├── src/
│   ├── api.py                    # FastAPI Phoenix Control Service
│   ├── stripe_wrapper.py         # Exactly-once payment processing
│   └── models/
│       └── __init__.py           # Data models and schemas
├── config/
│   ├── airtable_schema.json      # Complete 6-table schema
│   ├── zapier_zaps.json          # 6 Zapier automation configs
│   └── environment.template      # Environment variables template
├── scripts/
│   ├── deploy.sh                 # One-command deployment
│   └── setup_airtable.py         # Airtable base creation
├── tests/
│   └── test_system.py            # Complete verification suite (26 tests)
├── docs/
│   ├── OPERATIONS_RUNBOOK.md     # Complete operations runbook
│   ├── GO_LIVE_CHECKLIST.md      # Step-by-step go-live checklist
│   └── STRIPE_PRIMITIVE_PROOF_NOTE.md  # Formal Stripe integration spec
├── Dockerfile                    # Production Docker image
├── requirements.txt              # Python dependencies
├── fly.toml                      # Fly.io deployment config
└── README.md                     # This file
```

---

## Airtable Schema

| Table | Purpose |
|-------|---------|
| `system_throttle` | Current throttle state and control parameters |
| `system_state` | Historical system state observations |
| `used_nonces` | Deduplication store for idempotency |
| `payment_ledger` | Evidence & Integrity Ledger for payments |
| `audit_log` | Complete audit trail for all operations |
| `reconciliation_runs` | Reconciliation job history |

---

## Zapier Automations

| Zap | Trigger | Purpose |
|-----|---------|---------|
| State Observer | Every 5 minutes | Capture system state |
| Throttle Gate | Webhook | Probabilistic request filtering |
| Controller Executor | Degraded state | Apply control actions |
| Stripe Webhook Handler | Webhook | Process Stripe events |
| Daily Reconciliation | 2:00 AM daily | Detect and repair gaps |
| Kill Switch Handler | Webhook | Emergency shutdown |

---

## Stripe Integration

The Stripe wrapper provides **exactly-once payment processing** through:

1. **Idempotency Engine**: Deterministic key derivation from order parameters
2. **Deduplication Layer**: Event store with watermark tracking
3. **Evidence Ledger**: Complete audit trail with monotonic state transitions
4. **Reconciliation Job**: Gap detection and repair

### PHI Safety Protocol

For clinic/healthcare use:
```python
from src.stripe_wrapper import ClinicPaymentProfile

# Hash patient reference (never store raw patient ID)
patient_ref = ClinicPaymentProfile.hash_patient_ref(
    patient_id="patient_123",
    practice_key="your_secret_key"
)
```

---

## Emergency Procedures

### Activate Kill Switch

```bash
curl -X POST https://your-app.fly.dev/kill \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "DESCRIBE REASON",
    "operator": "YOUR_NAME",
    "confirmation": "CONFIRM_KILL"
  }'
```

### Revive System

```bash
curl -X POST "https://your-app.fly.dev/revive?operator=YOUR_NAME"
```

---

## Monitoring

### Health Check

```bash
curl https://your-app.fly.dev/health
```

### Prometheus Metrics

```bash
curl https://your-app.fly.dev/metrics
```

### Key Metrics

| Metric | Target Range | Alert Threshold |
|--------|--------------|-----------------|
| `echo_throttle_pct` | 0.0 - 0.1 | > 0.20 |
| `echo_error_rate` | < 0.01 | > 0.05 |
| `echo_temperature` | 0.8 - 1.0 | Outside range |
| `echo_phi_static` | 0.4 - 0.6 | < 0.3 |
| `echo_phi_dynamic` | 0.4 - 0.6 | < 0.3 |

---

## License

Proprietary - Echo Framework

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.4.0 | 2026-01-14 | Production release with Stripe integration |
| 2.3.0 | 2026-01-13 | Viability-Evolvability Theory integration |
| 2.2.0 | 2026-01-12 | Zapier automation suite |
| 2.1.0 | 2026-01-11 | Airtable Evidence Ledger |
| 2.0.0 | 2026-01-10 | Phoenix Control Service |
