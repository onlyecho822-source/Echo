# Echo Phoenix Control Service - Operations Runbook

**Version:** 2.4.0  
**Last Updated:** January 14, 2026  
**Author:** Manus AI

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Deployment](#3-deployment)
4. [Configuration](#4-configuration)
5. [Monitoring](#5-monitoring)
6. [Operations](#6-operations)
7. [Incident Response](#7-incident-response)
8. [Maintenance](#8-maintenance)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. System Overview

The Echo Phoenix Control Service is a continuous control system for the Echo AI framework. It implements:

- **State Observation**: Real-time monitoring of system health and viability metrics
- **Continuous Control**: Proportional control loop for throttle management
- **Global Kill Plane**: Emergency shutdown capability
- **Stripe Integration**: Exactly-once payment processing
- **Evidence Ledger**: Complete audit trail for all operations

### Key Metrics

| Metric | Description | Target Range |
|--------|-------------|--------------|
| `throttle_pct` | Current throttle percentage | 0.0 - 0.1 (normal) |
| `error_rate` | Error rate in last window | < 0.01 |
| `latency_p99_ms` | P99 latency | < 500ms |
| `phi_static` | Static viability | 0.4 - 0.6 |
| `phi_dynamic` | Dynamic viability | 0.4 - 0.6 |
| `temperature` | Effective system temperature | 0.8 - 1.0 (near T_c) |
| `susceptibility` | System responsiveness | 1.5 - 2.5 |

### Critical Temperature

Based on the Viability-Evolvability Theory, the optimal operating point is at the critical temperature **T_c ≈ 0.9**. The system should maintain temperature near this value for maximum adaptability.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ECHO PHOENIX                              │
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

### Components

1. **FastAPI Service** (`src/api.py`): Core API exposing observe, control, and kill endpoints
2. **Stripe Wrapper** (`src/stripe_wrapper.py`): Exactly-once payment processing
3. **Zapier Automations**: State observer, controller executor, webhook handlers
4. **Airtable**: Evidence & Integrity Ledger, state history, audit log

---

## 3. Deployment

### Prerequisites

- Docker installed
- Fly.io or Railway account (for cloud deployment)
- Airtable account with base created
- Stripe account with API keys
- Zapier account with premium plan

### Environment Variables

```bash
# Required
AIRTABLE_API_KEY=pat_xxxxxxxxxxxxx
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Optional
ENVIRONMENT=production
T_CRITICAL=0.9
TARGET_THROTTLE=0.0
MAX_THROTTLE=1.0
CONTROL_GAIN=0.1
WEBHOOK_SECRET=your_webhook_secret
```

### Deployment Commands

```bash
# Local deployment
./scripts/deploy.sh local

# Fly.io deployment
./scripts/deploy.sh fly

# Railway deployment
./scripts/deploy.sh railway
```

### Post-Deployment Verification

```bash
# Check health
curl https://your-app.fly.dev/health

# Test observe
curl -X POST https://your-app.fly.dev/observe \
  -H "Content-Type: application/json" \
  -d '{"source": "verification"}'

# Check metrics
curl https://your-app.fly.dev/metrics
```

---

## 4. Configuration

### Airtable Setup

1. Create a new base named "Echo Production"
2. Import schema from `config/airtable_schema.json`
3. Create the following tables:
   - `system_throttle`
   - `system_state`
   - `used_nonces`
   - `payment_ledger`
   - `audit_log`
   - `reconciliation_runs`

### Zapier Setup

1. Import Zap configurations from `config/zapier_zaps.json`
2. Configure the following Zaps:
   - **Echo State Observer**: Runs every 5 minutes
   - **Echo Throttle Gate**: Webhook trigger
   - **Echo Controller Executor**: Triggered by degraded state
   - **Stripe Webhook Handler**: Processes Stripe events
   - **Daily Reconciliation**: Runs at 2:00 AM
   - **Kill Switch Handler**: Emergency shutdown

3. Update variables in each Zap:
   - `PHOENIX_API_URL`: Your deployed API URL
   - `AIRTABLE_BASE_ID`: Your Airtable base ID

### Stripe Webhook Setup

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-app.fly.dev/webhook/stripe`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.requires_action`
   - `charge.refunded`
   - `charge.dispute.created`
   - `customer.subscription.updated`

---

## 5. Monitoring

### Health Checks

The `/health` endpoint returns:

```json
{
  "status": "healthy",
  "version": "2.4.0",
  "environment": "production",
  "uptime_seconds": 3600.5,
  "last_observation": "2026-01-14T12:00:00Z",
  "last_control": "2026-01-14T11:55:00Z"
}
```

Status values:
- `healthy`: Normal operation
- `degraded`: Elevated error rate or throttle
- `critical`: Emergency conditions
- `killed`: Kill switch active

### Prometheus Metrics

The `/metrics` endpoint exposes:

```
echo_throttle_pct 0.0
echo_error_rate 0.01
echo_latency_p99_ms 150.0
echo_phi_static 0.5
echo_phi_dynamic 0.45
echo_temperature 0.85
echo_kill_active 0
```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| `error_rate` | > 0.05 | > 0.10 |
| `throttle_pct` | > 0.20 | > 0.50 |
| `latency_p99_ms` | > 500 | > 1000 |
| `adaptability_ratio` | < 0.8 | < 0.5 |

---

## 6. Operations

### Normal Operations

The system operates autonomously through the control loop:

1. **Observer** captures state every 5 minutes
2. **Controller** computes control action if needed
3. **Executor** applies throttle changes
4. **Reconciliation** runs daily at 2:00 AM

### Manual Throttle Adjustment

```bash
# Set throttle to 50%
curl -X POST https://your-app.fly.dev/control \
  -H "Content-Type: application/json" \
  -d '{
    "current_state": {...},
    "target_throttle": 0.5
  }'
```

### Kill Switch Activation

**WARNING: This halts all operations immediately.**

```bash
curl -X POST https://your-app.fly.dev/kill \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Emergency shutdown - describe reason",
    "operator": "your_name",
    "confirmation": "CONFIRM_KILL"
  }'
```

### Kill Switch Deactivation

```bash
curl -X POST https://your-app.fly.dev/revive?operator=your_name
```

---

## 7. Incident Response

### Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| SEV1 | Critical | Immediate | Kill switch active, payment failures |
| SEV2 | High | 15 minutes | Error rate > 10%, throttle > 50% |
| SEV3 | Medium | 1 hour | Elevated latency, reconciliation failures |
| SEV4 | Low | 24 hours | Minor anomalies, non-critical alerts |

### SEV1 Playbook: Kill Switch Active

1. **Assess**: Check `/health` endpoint for status
2. **Communicate**: Notify stakeholders via Slack #echo-critical
3. **Investigate**: Review audit log in Airtable
4. **Resolve**: Fix root cause
5. **Revive**: Call `/revive` endpoint
6. **Verify**: Confirm system returns to healthy state
7. **Document**: Create incident report

### SEV2 Playbook: High Error Rate

1. **Assess**: Check `/observe` for current state
2. **Throttle**: Increase throttle if needed
3. **Investigate**: Check Stripe dashboard, Airtable logs
4. **Resolve**: Address root cause
5. **Reduce Throttle**: Gradually return to normal
6. **Monitor**: Watch for 30 minutes

### Payment Failure Investigation

1. Check `payment_ledger` table in Airtable
2. Find the failed payment by `order_id`
3. Check `events` field for webhook history
4. Cross-reference with Stripe dashboard
5. Check `reconciliation_runs` for any gaps

---

## 8. Maintenance

### Daily Tasks

- [ ] Review `/health` status
- [ ] Check Slack #echo-alerts for notifications
- [ ] Verify reconciliation completed successfully

### Weekly Tasks

- [ ] Review error rate trends in Airtable
- [ ] Check Stripe webhook delivery rate
- [ ] Verify Zapier automations are running
- [ ] Review audit log for anomalies

### Monthly Tasks

- [ ] Review and rotate API keys
- [ ] Update dependencies
- [ ] Performance review of control loop
- [ ] Capacity planning

### Quarterly Tasks

- [ ] Stripe API version update review
- [ ] Security audit
- [ ] Disaster recovery test
- [ ] Documentation update

---

## 9. Troubleshooting

### Common Issues

#### Issue: Zapier automation not triggering

**Symptoms**: State not being observed, control not applied

**Resolution**:
1. Check Zapier dashboard for errors
2. Verify webhook URLs are correct
3. Check Airtable connection
4. Re-enable the Zap

#### Issue: Duplicate payments

**Symptoms**: Customer charged twice

**Resolution**:
1. Check `used_nonces` table for idempotency key
2. Verify webhook deduplication is working
3. Check `payment_ledger` for duplicate entries
4. Issue refund via Stripe dashboard

#### Issue: Reconciliation gaps

**Symptoms**: `reconciliation_runs` shows `needs_repair`

**Resolution**:
1. Check Stripe webhook delivery
2. Manually trigger reconciliation
3. Review `missing_entries` in reconciliation details
4. Create missing ledger entries manually if needed

#### Issue: High latency

**Symptoms**: `latency_p99_ms` > 500

**Resolution**:
1. Check Fly.io/Railway metrics
2. Review recent deployments
3. Check Airtable API rate limits
4. Scale up if needed

#### Issue: Kill switch won't deactivate

**Symptoms**: `/revive` returns error

**Resolution**:
1. Check API logs for errors
2. Verify operator has permission
3. Manually update `system_throttle` in Airtable
4. Restart the service if needed

---

## Appendix A: API Reference

### POST /observe

Request:
```json
{
  "source": "string",
  "include_metrics": true
}
```

Response:
```json
{
  "state": {
    "timestamp": "2026-01-14T12:00:00Z",
    "throttle_pct": 0.0,
    "error_rate": 0.01,
    "latency_p99_ms": 150.0,
    "phi_static": 0.5,
    "phi_dynamic": 0.45,
    "temperature": 0.85,
    "susceptibility": 2.0,
    "requests_per_minute": 100.0
  },
  "health": "healthy",
  "recommendations": []
}
```

### POST /control

Request:
```json
{
  "current_state": {...},
  "target_throttle": 0.0,
  "override": false
}
```

Response:
```json
{
  "action": {
    "timestamp": "2026-01-14T12:00:00Z",
    "throttle_delta": 0.0,
    "new_throttle": 0.0,
    "reason": "Adjusting toward target 0.00",
    "urgency": "normal"
  },
  "applied": true,
  "state_after": {...}
}
```

### POST /kill

Request:
```json
{
  "reason": "Emergency shutdown",
  "operator": "admin",
  "confirmation": "CONFIRM_KILL"
}
```

Response:
```json
{
  "status": "killed",
  "reason": "Emergency shutdown",
  "operator": "admin",
  "timestamp": "2026-01-14T12:00:00Z",
  "message": "Global Kill Plane activated. All operations halted."
}
```

---

## Appendix B: Viability-Evolvability Quick Reference

The system implements the Unified Theory of Viability-Evolvability Duality:

**Formula**: `Λ = f(T) × (Φ_d / Φ_s)`

Where:
- **Λ** = Evolvability (adaptability)
- **f(T)** = Temperature coupling function (peaks at T_c)
- **Φ_d** = Dynamic viability (gradient strength)
- **Φ_s** = Static viability (attractor depth)

**Key Insight**: The system should operate near the critical temperature (T_c ≈ 0.9) for maximum adaptability while maintaining the adaptability ratio (Φ_d/Φ_s) above 0.8.

---

## Appendix C: Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| On-Call Engineer | Slack #echo-oncall | PagerDuty |
| Platform Lead | @platform-lead | Direct message |
| Security | security@example.com | Immediate for breaches |
| Stripe Support | Stripe Dashboard | For payment issues |

---

**End of Runbook**
