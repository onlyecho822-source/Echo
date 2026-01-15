# Echo Phoenix Control Service - Go-Live Checklist

**Version:** 2.4.0  
**Date:** January 14, 2026  
**Status:** Ready for Deployment

---

## Pre-Flight Checklist

### Phase 0: Prerequisites ✓

- [ ] **GitHub Access**
  - [ ] Repository cloned: `gh repo clone onlyecho822-source/Echo`
  - [ ] Branch created: `feature/phoenix-production`
  - [ ] All files committed

- [ ] **Accounts Ready**
  - [ ] Airtable account (Pro plan recommended)
  - [ ] Stripe account (Live mode enabled)
  - [ ] Zapier account (Professional plan required)
  - [ ] Fly.io or Railway account

- [ ] **API Keys Obtained**
  - [ ] Airtable Personal Access Token
  - [ ] Stripe Secret Key (live)
  - [ ] Stripe Webhook Signing Secret

---

## Phase 1: Airtable Setup (15 minutes)

### 1.1 Create Base

- [ ] Go to [airtable.com](https://airtable.com)
- [ ] Create new base: "Echo Production"
- [ ] Copy Base ID from URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`

### 1.2 Run Setup Script

```bash
export AIRTABLE_API_KEY="pat_your_token"
export AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"
cd /home/ubuntu/echo-production
python scripts/setup_airtable.py
```

### 1.3 Verify Tables Created

- [ ] `system_throttle` - with initial record (throttle=0, active=true)
- [ ] `system_state` - empty
- [ ] `used_nonces` - empty
- [ ] `payment_ledger` - empty
- [ ] `audit_log` - empty
- [ ] `reconciliation_runs` - empty

---

## Phase 2: Deploy Phoenix Control Service (10 minutes)

### 2.1 Set Environment Variables

```bash
export AIRTABLE_API_KEY="pat_your_token"
export AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"
export STRIPE_SECRET_KEY="sk_live_your_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_secret"
export ENVIRONMENT="production"
```

### 2.2 Deploy to Fly.io

```bash
cd /home/ubuntu/echo-production
./scripts/deploy.sh fly
```

### 2.3 Verify Deployment

```bash
# Health check
curl https://echo-phoenix.fly.dev/health

# Expected response:
# {"status":"healthy","version":"2.4.0","environment":"production",...}
```

- [ ] Health endpoint returns 200
- [ ] Status is "healthy"
- [ ] Version is "2.4.0"

### 2.4 Record Deployment URL

**Phoenix API URL:** `https://________________________.fly.dev`

---

## Phase 3: Configure Stripe Webhooks (10 minutes)

### 3.1 Add Webhook Endpoint

- [ ] Go to [Stripe Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)
- [ ] Click "Add endpoint"
- [ ] Endpoint URL: `https://YOUR_APP.fly.dev/webhook/stripe`
- [ ] Select events:
  - [ ] `payment_intent.succeeded`
  - [ ] `payment_intent.payment_failed`
  - [ ] `payment_intent.requires_action`
  - [ ] `charge.refunded`
  - [ ] `charge.dispute.created`
  - [ ] `customer.subscription.updated`

### 3.2 Copy Signing Secret

- [ ] Click on the webhook endpoint
- [ ] Reveal signing secret
- [ ] Update environment variable: `STRIPE_WEBHOOK_SECRET`

### 3.3 Test Webhook

- [ ] Click "Send test webhook"
- [ ] Select `payment_intent.succeeded`
- [ ] Verify 200 response

---

## Phase 4: Configure Zapier Automations (30 minutes)

### 4.1 State Observer Zap

- [ ] Create new Zap: "Echo State Observer"
- [ ] Trigger: Schedule by Zapier → Every 5 Minutes
- [ ] Action 1: Webhooks → POST to `https://YOUR_APP.fly.dev/observe`
- [ ] Action 2: Airtable → Create Record in `system_state`
- [ ] Action 3: Filter → Only continue if health ≠ "healthy"
- [ ] Action 4: Slack → Send to #echo-alerts
- [ ] Turn ON

### 4.2 Throttle Gate Zap

- [ ] Create new Zap: "Echo Throttle Gate"
- [ ] Trigger: Webhooks → Catch Hook
- [ ] Action 1: Airtable → Find Record in `system_throttle` (view: Active)
- [ ] Action 2: Code → JavaScript throttle logic
- [ ] Action 3: Filter → Only continue if should_proceed = true
- [ ] Action 4: Webhooks → POST callback
- [ ] Turn ON
- [ ] Record webhook URL: `https://hooks.zapier.com/hooks/catch/______/______`

### 4.3 Controller Executor Zap

- [ ] Create new Zap: "Echo Controller Executor"
- [ ] Trigger: Airtable → New Record in `system_state` (view: Degraded)
- [ ] Action 1: Webhooks → POST to `https://YOUR_APP.fly.dev/control`
- [ ] Action 2: Airtable → Update Record in `system_throttle`
- [ ] Action 3: Airtable → Create Record in `system_throttle`
- [ ] Action 4: Airtable → Create Record in `audit_log`
- [ ] Turn ON

### 4.4 Stripe Webhook Handler Zap

- [ ] Create new Zap: "Stripe Webhook Handler"
- [ ] Trigger: Webhooks → Catch Hook
- [ ] Action 1: Airtable → Find Record in `used_nonces`
- [ ] Action 2: Filter → Only continue if NOT found
- [ ] Action 3: Webhooks → POST to `https://YOUR_APP.fly.dev/webhook/stripe`
- [ ] Action 4: Airtable → Create Record in `used_nonces`
- [ ] Action 5: Airtable → Create Record in `audit_log`
- [ ] Turn ON

### 4.5 Daily Reconciliation Zap

- [ ] Create new Zap: "Daily Reconciliation"
- [ ] Trigger: Schedule by Zapier → Every Day at 2:00 AM
- [ ] Action 1: Webhooks → POST to `https://YOUR_APP.fly.dev/reconcile`
- [ ] Action 2: Airtable → Create Record in `reconciliation_runs`
- [ ] Action 3: Filter → Only continue if status = "needs_repair"
- [ ] Action 4: Slack → Send to #echo-alerts
- [ ] Turn ON

### 4.6 Kill Switch Handler Zap

- [ ] Create new Zap: "Kill Switch Handler"
- [ ] Trigger: Webhooks → Catch Hook
- [ ] Action 1: Webhooks → POST to `https://YOUR_APP.fly.dev/kill`
- [ ] Action 2: Airtable → Create Record in `system_throttle`
- [ ] Action 3: Airtable → Create Record in `audit_log`
- [ ] Action 4: Slack → Send to #echo-critical
- [ ] Action 5: Email → Send to emergency contact
- [ ] Turn ON
- [ ] Record webhook URL: `https://hooks.zapier.com/hooks/catch/______/______`

---

## Phase 5: Verification Tests (20 minutes)

### 5.1 Throttle Gate Test

```bash
# Test at 0% throttle (should always proceed)
curl -X POST https://YOUR_THROTTLE_GATE_WEBHOOK \
  -H "Content-Type: application/json" \
  -d '{"callback_url": "https://httpbin.org/post"}'

# Verify: Request proceeds
```

- [ ] 0% throttle: All requests proceed
- [ ] 50% throttle: ~50% of requests proceed
- [ ] 100% throttle: No requests proceed

### 5.2 State Observation Test

```bash
# Trigger observation
curl -X POST https://YOUR_APP.fly.dev/observe \
  -H "Content-Type: application/json" \
  -d '{"source": "verification_test"}'
```

- [ ] Response includes state with all metrics
- [ ] Record created in `system_state` table
- [ ] Health status is correct

### 5.3 Control Loop Test

```bash
# Simulate degraded state
curl -X POST https://YOUR_APP.fly.dev/control \
  -H "Content-Type: application/json" \
  -d '{
    "current_state": {
      "timestamp": "2026-01-14T12:00:00Z",
      "throttle_pct": 0.0,
      "error_rate": 0.15,
      "latency_p99_ms": 500,
      "requests_per_minute": 100,
      "phi_static": 0.5,
      "phi_dynamic": 0.45,
      "temperature": 0.85,
      "susceptibility": 2.0
    }
  }'
```

- [ ] Response includes control action
- [ ] Throttle increased due to high error rate
- [ ] Urgency is "high" or "critical"

### 5.4 Kill Switch Test

```bash
# Activate kill switch
curl -X POST https://YOUR_APP.fly.dev/kill \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Verification test",
    "operator": "go_live_checklist",
    "confirmation": "CONFIRM_KILL"
  }'

# Verify killed
curl https://YOUR_APP.fly.dev/health
# Should return: {"status": "killed", ...}

# Revive
curl -X POST "https://YOUR_APP.fly.dev/revive?operator=go_live_checklist"

# Verify revived
curl https://YOUR_APP.fly.dev/health
# Should return: {"status": "healthy", ...}
```

- [ ] Kill switch activates correctly
- [ ] Health shows "killed" status
- [ ] Revive restores "healthy" status

### 5.5 Stripe Webhook Test

- [ ] Send test webhook from Stripe Dashboard
- [ ] Verify record created in `used_nonces`
- [ ] Verify record created in `audit_log`
- [ ] Verify duplicate is rejected

---

## Phase 6: Go Live (5 minutes)

### 6.1 Final Configuration

```bash
# Ensure throttle is at 0%
curl -X POST https://YOUR_APP.fly.dev/control \
  -H "Content-Type: application/json" \
  -d '{"current_state": {...}, "target_throttle": 0.0}'
```

- [ ] Throttle set to 0% (full operation)
- [ ] All Zapier Zaps are ON
- [ ] Slack notifications configured
- [ ] Emergency contacts set

### 6.2 Monitoring Setup

- [ ] Prometheus/Grafana connected to `/metrics`
- [ ] Slack #echo-alerts channel created
- [ ] Slack #echo-critical channel created
- [ ] On-call schedule established

### 6.3 Go Live Confirmation

- [ ] **All verification tests passed**
- [ ] **All Zaps running**
- [ ] **Monitoring active**
- [ ] **Documentation complete**

**GO LIVE AUTHORIZED BY:** ________________________

**DATE/TIME:** ________________________

---

## Phase 7: Post-Launch Monitoring (24 hours)

### Hour 0-1

- [ ] Monitor `/health` every 5 minutes
- [ ] Check Airtable for state records
- [ ] Verify no unexpected throttle changes

### Hour 1-6

- [ ] Review error rates
- [ ] Check Stripe webhook delivery
- [ ] Verify reconciliation not needed

### Hour 6-24

- [ ] Monitor for anomalies
- [ ] Review audit log
- [ ] Document any issues

### 24-Hour Review

- [ ] All systems nominal
- [ ] No critical alerts
- [ ] Reconciliation healthy
- [ ] Documentation updated

---

## Emergency Procedures

### Kill Switch Activation

```bash
# Via API
curl -X POST https://YOUR_APP.fly.dev/kill \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "DESCRIBE REASON",
    "operator": "YOUR_NAME",
    "confirmation": "CONFIRM_KILL"
  }'

# Via Zapier webhook
curl -X POST https://YOUR_KILL_SWITCH_WEBHOOK \
  -H "Content-Type: application/json" \
  -d '{"reason": "DESCRIBE REASON", "operator": "YOUR_NAME"}'
```

### Rollback Procedure

1. Activate kill switch
2. Set throttle to 100% in Airtable
3. Disable all Zapier Zaps
4. Investigate root cause
5. Fix and redeploy
6. Re-enable Zaps
7. Gradually reduce throttle
8. Revive system

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Engineer | | | |
| Reviewer | | | |
| Approver | | | |

---

**Checklist Complete. System is LIVE.**
