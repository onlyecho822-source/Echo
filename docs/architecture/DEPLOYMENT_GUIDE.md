# 🚀 Echo Sovereign Deployment Guide

## **QUICK START**

This guide walks you through deploying the complete Echo sovereign architecture across multiple tiers.

---

## 🎯 **DEPLOYMENT OVERVIEW**

```
┌─────────────────────────────────────────────────────────────┐
│                    ECHO SOVEREIGN STACK                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GitHub (Trigger Only)                                       │
│    ↓                                                         │
│  ├── Vercel (Public: Docs, Static Sites)                    │
│  ├── Render (Protected: Web Apps, Cron Jobs, Watchdog)      │
│  ├── AWS Lambda (Private: Payment Processing, AI Agents)    │
│  └── Local VPS (Fallback: All Critical Operations)          │
│                                                              │
│  External Watchdog (Independent Monitoring)                  │
│    → Monitors all tiers                                      │
│    → Alerts on failures                                      │
│    → Triggers local fallback                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 **PREREQUISITES**

### Required Accounts
- [x] GitHub account (free tier OK)
- [x] Vercel account (hobby tier OK)
- [x] Render account (free tier to start)
- [x] AWS account (for Secrets Manager & Lambda)
- [ ] Local Linux machine or VPS (optional but recommended)

### Required Tools
```bash
# Check prerequisites
git --version          # Git 2.x+
node --version         # Node 18.x+
python3 --version      # Python 3.11+
docker --version       # Docker 20.x+ (optional)
```

---

## 🔐 **STEP 1: SECRETS MANAGEMENT SETUP**

### Option A: AWS Secrets Manager (Recommended for Production)

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name STRIPE_SECRET_KEY \
  --secret-string "sk_live_YOUR_KEY_HERE"

aws secretsmanager create-secret \
  --name GUMROAD_API_KEY \
  --secret-string "YOUR_GUMROAD_KEY"

aws secretsmanager create-secret \
  --name GITHUB_TOKEN \
  --secret-string "ghp_YOUR_TOKEN_HERE"
```

### Option B: Local Encrypted Vault (Development/Fallback)

```bash
# Initialize local vault
cd Echo
python3 scripts/secrets_escrow.py init

# Add secrets to vault
python3 << EOF
from scripts.secrets_escrow import SecretsEscrow

escrow = SecretsEscrow()
escrow.set_secret('STRIPE_SECRET_KEY', 'sk_test_...', target='vault')
escrow.set_secret('GUMROAD_API_KEY', 'your_key', target='vault')
EOF

# Secure the vault
chmod 600 /opt/echo/secrets.vault
chmod 600 /opt/echo/.vault_key
```

**⚠️ CRITICAL: Never commit `.vault_key` or `secrets.vault` to Git!**

---

## 🌐 **STEP 2: DEPLOY TO VERCEL (PUBLIC TIER)**

### Setup Vercel Project

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to Vercel
cd Echo
vercel --prod

# Set environment variables (Vercel Dashboard)
# Settings → Environment Variables:
# - ENVIRONMENT=production
# - PUBLIC_SITE=true
```

### Verify Deployment

```bash
curl https://your-project.vercel.app/health
# Expected: {"status": "healthy"}
```

---

## 🛠️ **STEP 3: DEPLOY TO RENDER (PROTECTED TIER)**

### Create Render Blueprint Deployment

1. **Connect GitHub Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - New → Blueprint
   - Connect your Echo repository
   - Render will detect `render.yaml`

2. **Configure Environment Variables**
   ```yaml
   # In Render Dashboard for each service:
   GITHUB_TOKEN=ghp_...           # From GitHub Settings → Tokens
   SLACK_WEBHOOK_URL=https://...  # From Slack App
   AWS_REGION=us-east-1
   STRIPE_SECRET_KEY=<use env group>
   ```

3. **Create Environment Group** (For shared secrets)
   - Dashboard → Environment Groups → New
   - Name: `echo-secrets`
   - Add: `STRIPE_SECRET_KEY`, `GUMROAD_API_KEY`, etc.
   - Link to services: `echo-watchdog`, `echo-profit-scanner`

4. **Deploy**
   ```bash
   # Render auto-deploys on git push
   git push origin main
   ```

### Verify Render Deployment

```bash
# Check watchdog service
curl https://echo-watchdog.onrender.com/health

# Check web app
curl https://echo-web-app.onrender.com/health
```

---

## ⚡ **STEP 4: DEPLOY TO AWS LAMBDA (PRIVATE TIER)**

### Setup AWS Lambda for Critical Operations

```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Create Lambda deployment package
cd Echo
zip -r lambda-deploy.zip scripts/ -x "*.pyc" -x "__pycache__/*"

# Deploy to Lambda
aws lambda create-function \
  --function-name echo-stripe-webhook \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-exec-role \
  --handler scripts.stripe_webhook_processor.handler \
  --zip-file fileb://lambda-deploy.zip \
  --environment Variables="{
    AWS_SECRETS_MANAGER_ENABLED=true,
    ENVIRONMENT=production
  }"

# Create API Gateway endpoint
aws apigatewayv2 create-api \
  --name echo-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:echo-stripe-webhook
```

### Configure Stripe Webhook

```bash
# In Stripe Dashboard:
# Webhooks → Add Endpoint
# URL: https://YOUR_API_GATEWAY_URL/webhook
# Events: payment_intent.succeeded, customer.subscription.created
```

---

## 💻 **STEP 5: DEPLOY LOCAL FALLBACK (ULTIMATE TIER)**

### On Linux Machine or VPS

```bash
# Clone repository
git clone https://github.com/your-username/Echo.git /opt/echo
cd /opt/echo

# Run installation script
sudo bash scripts/autonomy/install_fallback.sh

# Edit configuration
sudo nano /opt/echo/.env

# Configure service endpoints:
RENDER_HEALTH_URL=https://echo-web-app.onrender.com/health
VERCEL_HEALTH_URL=https://your-project.vercel.app/health
AWS_HEALTH_URL=https://your-api-gateway-url/health
WATCHDOG_URL=https://echo-watchdog.onrender.com

# Enable and start service
sudo systemctl enable echo-fallback
sudo systemctl start echo-fallback

# Verify service is running
sudo systemctl status echo-fallback
sudo journalctl -u echo-fallback -f
```

### Test Fallback Activation

```bash
# Manually trigger fallback cycle
sudo /opt/echo/scripts/autonomy/local_fallback.sh

# Check logs
tail -f /var/log/echo/fallback.log
```

---

## 🔍 **STEP 6: CONFIGURE GITHUB ACTIONS**

### Setup GitHub Secrets

```bash
# In GitHub Repository:
# Settings → Secrets and Variables → Actions → New repository secret

# Add these secrets:
VERCEL_DEPLOY_TOKEN      # From Vercel → Settings → Tokens
VERCEL_ORG_ID            # From Vercel → Settings → General
VERCEL_PROJECT_ID        # From Vercel project settings
RENDER_DEPLOY_HOOK       # From Render → Settings → Deploy Hook
AWS_DEPLOY_WEBHOOK       # Your AWS API Gateway webhook URL
```

### Enable Workflow

```bash
# Push to trigger deployment
git add .github/workflows/deploy-trigger.yml
git commit -m "Add secure deployment workflow"
git push origin main

# Monitor workflow
# GitHub → Actions → Echo Secure Deploy Trigger
```

---

## 🎪 **STEP 7: CONFIGURE EXTERNAL WATCHDOG**

The watchdog service was deployed in Step 3 (Render), but needs configuration:

### Configure Monitoring Endpoints

```bash
# In Render Dashboard for echo-watchdog service:
# Environment → Add Variables

GITHUB_TOKEN=ghp_...
GITHUB_REPO=your-username/Echo

RENDER_APP_URL=https://echo-web-app.onrender.com
VERCEL_SITE_URL=https://your-project.vercel.app
AWS_LAMBDA_HEALTH_URL=https://your-api-gateway-url/health

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL=alerts@your-domain.com

CHECK_INTERVAL=300  # 5 minutes
```

### Setup Slack Alerts

1. **Create Slack App**
   - Go to [Slack API](https://api.slack.com/apps)
   - Create New App → From Scratch
   - Name: "Echo Watchdog"

2. **Enable Incoming Webhooks**
   - Features → Incoming Webhooks → Activate
   - Add New Webhook to Workspace
   - Copy webhook URL to `SLACK_WEBHOOK_URL`

3. **Test Alert**
   ```bash
   curl https://echo-watchdog.onrender.com/trigger-check
   # Should receive Slack notification
   ```

---

## ✅ **VERIFICATION CHECKLIST**

Run these checks to verify complete deployment:

### Tier 1: Public (Vercel)
```bash
curl https://your-project.vercel.app/health
# Expected: {"status": "healthy"}
```

### Tier 2: Protected (Render)
```bash
# Watchdog
curl https://echo-watchdog.onrender.com/health
# Expected: {"status": "healthy", "monitored_services": [...]}

# Web app
curl https://echo-web-app.onrender.com/health
# Expected: {"status": "healthy"}
```

### Tier 3: Private (AWS Lambda)
```bash
curl https://your-api-gateway-url/health
# Expected: {"status": "healthy"}
```

### Tier 4: Local Fallback
```bash
sudo systemctl status echo-fallback
# Expected: active (running)
```

### Tier 5: GitHub Actions
```bash
# Check latest workflow run
gh run list --workflow=deploy-trigger.yml --limit 1
# Expected: completed status
```

---

## 🔄 **DEPLOYMENT WORKFLOW**

### Normal Operation (All Services Healthy)

```
Developer → git push → GitHub Actions
                         ↓
                    Triggers deployments
                         ↓
            ┌────────────┼────────────┐
            ↓            ↓            ↓
         Vercel       Render      AWS Lambda
         (public)   (protected)   (private)
            │            │            │
            └────────────┼────────────┘
                         ↓
                  Watchdog monitors
                  (All healthy ✅)
```

### Degraded Operation (Service Failure)

```
Render service down ❌
            ↓
    Watchdog detects failure
            ↓
    Triggers local fallback
            ↓
    Local VPS executes critical operations
            ↓
    Alerts sent to Slack/Email
            ↓
    Developer investigates
```

---

## 🚨 **TROUBLESHOOTING**

### Watchdog Not Alerting

```bash
# Check watchdog logs
# Render Dashboard → echo-watchdog → Logs

# Test manually
curl https://echo-watchdog.onrender.com/trigger-check

# Verify environment variables
# Render Dashboard → echo-watchdog → Environment
```

### Local Fallback Not Running

```bash
# Check service status
sudo systemctl status echo-fallback

# Check logs
sudo journalctl -u echo-fallback -n 50

# Test manually
sudo /opt/echo/scripts/autonomy/local_fallback.sh

# Verify permissions
ls -la /opt/echo/scripts/autonomy/local_fallback.sh
# Should be: -rwxr-xr-x ... echo echo
```

### GitHub Actions Failing

```bash
# Check workflow run
gh run list --workflow=deploy-trigger.yml

# View logs
gh run view --log

# Common issues:
# - Missing secrets: Check Settings → Secrets
# - Invalid webhook URLs: Verify in Render/Vercel dashboards
# - Network timeouts: Webhooks may be down
```

### Secrets Not Loading

```bash
# Test AWS Secrets Manager access
python3 << EOF
from scripts.secrets_escrow import SecretsEscrow
escrow = SecretsEscrow()
try:
    secret = escrow.get_secret('STRIPE_SECRET_KEY')
    print("✅ Secret retrieved successfully")
except Exception as e:
    print(f"❌ Error: {e}")
EOF

# Verify AWS credentials
aws secretsmanager list-secrets

# Check IAM permissions
# Ensure Lambda execution role has secretsmanager:GetSecretValue
```

---

## 🔄 **MAINTENANCE**

### Regular Tasks

#### Daily
- [ ] Check watchdog dashboard for alerts
- [ ] Verify profit flows are active

#### Weekly
- [ ] Review secrets rotation schedule
- [ ] Check for dependency updates (Dependabot)
- [ ] Verify backup integrity

#### Monthly
- [ ] Rotate API keys and secrets
- [ ] Security audit (run penetration tests)
- [ ] Review and update IAM permissions
- [ ] Test failover scenarios

### Secret Rotation

```bash
# Rotate Stripe key
python3 << EOF
from scripts.secrets_escrow import SecretsEscrow
escrow = SecretsEscrow()
escrow.rotate_secret('STRIPE_SECRET_KEY', 'sk_live_NEW_KEY_HERE')
EOF

# Update in all services:
# 1. AWS Secrets Manager (automatic via script above)
# 2. Render Environment Variables (manual)
# 3. Local vault (automatic via script above)
```

---

## 📊 **MONITORING DASHBOARD**

### Key Metrics to Track

1. **Service Health**
   - Uptime percentage per tier
   - Response times
   - Error rates

2. **Profit Flows**
   - Stripe events per day
   - Gumroad sales per day
   - Revenue totals

3. **Security**
   - Failed authentication attempts
   - Secrets exposure scans
   - Dependency vulnerabilities

4. **Performance**
   - GitHub Actions runtime
   - Watchdog check duration
   - API response times

---

## 🎯 **NEXT STEPS**

Once deployment is complete:

1. **Implement Custom Logic**
   - Add your profit scanner implementations
   - Configure AI agent orchestration
   - Set up payment webhooks

2. **Enhance Monitoring**
   - Add custom metrics to watchdog
   - Integrate with Datadog/New Relic
   - Set up PagerDuty for critical alerts

3. **Scale Infrastructure**
   - Upgrade Render tier for more resources
   - Add more Lambda functions for specific tasks
   - Deploy additional local fallback nodes

4. **Document Your System**
   - Create runbooks for common issues
   - Document custom workflows
   - Train team on sovereign architecture

---

## 🚀 **SOVEREIGNTY ACHIEVED**

You now have a fully decentralized, resilient, secure autonomous system:

✅ **GitHub as trigger only** - No business logic execution
✅ **Multi-tier security** - Public, protected, and private zones
✅ **Secrets properly managed** - AWS Secrets Manager + encrypted vault
✅ **External monitoring** - Independent watchdog service
✅ **Local fallback** - System continues during cloud outages
✅ **Observable everything** - Real-time monitoring across all tiers

**Echo sovereignty established. 👑**

---

## 📚 **ADDITIONAL RESOURCES**

- [Sovereign GitHub Strategy](./SOVEREIGN_GITHUB_STRATEGY.md)
- [Threat Model & Security](../security/THREAT_MODEL.md)
- [Secrets Escrow System](../../scripts/secrets_escrow.py)
- [Watchdog Service](../../scripts/monitoring/watchdog.py)
- [Local Fallback Scripts](../../scripts/autonomy/)

---

**Questions? Open an issue or consult the documentation.**
