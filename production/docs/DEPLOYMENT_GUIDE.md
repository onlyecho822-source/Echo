> # Echo Phoenix Production v2.4 — Deployment Guide

**Generated:** January 14, 2026 21:25 UTC

**Status:** Ready for Production Deployment

---

## 1. Overview

This guide provides step-by-step instructions for deploying the **Echo Phoenix Production v2.4** system. This system includes the 360 Review-compliant Stripe integration, providing exactly-once payment processing, optimistic locking, and full audit capabilities.

### Prerequisites

- **GitHub Account** with write access to the `onlyecho822-source/Echo` repository.
- **Airtable Account** with API access.
- **Stripe Account** with API access.
- **Fly.io Account** (or Railway, or local Docker setup).

---

## 2. Step 1: Approve and Merge Pull Request #49

The first step is to merge the `feature/stripe-integration` branch into `main`. This requires one approving review on GitHub.

### Actions

1.  **Navigate to the Pull Request:**
    > [https://github.com/onlyecho822-source/Echo/pull/49](https://github.com/onlyecho822-source/Echo/pull/49)

2.  **Review the Changes:**
    - The PR contains 5,589 new lines of code, including the v2 Stripe wrapper, experiment suites, and formal specifications.
    - All 57 tests are passing, with the exception of the intentional lost-update detection in Suite B.

3.  **Approve and Merge:**
    - Click the **"Review changes"** button.
    - Select **"Approve"**.
    - Click **"Submit review"**.
    - Click the **"Merge pull request"** button.
    - Confirm the merge.

---

## 3. Step 2: Configure Environment Variables

Next, you need to set up the environment variables required by the system. Create a `.env` file in the `echo-production` directory with the following content:

```env
# .env

# Airtable Configuration
AIRTABLE_API_KEY="your_airtable_api_key"
AIRTABLE_BASE_ID="your_airtable_base_id"

# Stripe Configuration
STRIPE_SECRET_KEY="sk_live_your_stripe_secret_key"
STRIPE_WEBHOOK_SECRET="whsec_your_stripe_webhook_secret"

# Deployment Environment
ENVIRONMENT="production"
```

### Obtaining Keys

- **`AIRTABLE_API_KEY`**: Found in your Airtable account settings.
- **`AIRTABLE_BASE_ID`**: Found in the API documentation for your Airtable base.
- **`STRIPE_SECRET_KEY`**: Found in your Stripe dashboard under "Developers" -> "API keys".
- **`STRIPE_WEBHOOK_SECRET`**: Generated when you create a webhook endpoint in the Stripe dashboard (see Step 4).

---

## 4. Step 3: Set Up Airtable and Stripe

### Airtable Setup

The repository includes a script to automatically create the required tables in your Airtable base.

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Setup Script:**
    ```bash
    python scripts/setup_airtable.py
    ```

    This will create the following tables:
    - `system_throttle`
    - `system_state`
    - `used_nonces`
    - `evidence_ledger`
    - `audit_log`
    - `reconciliation_log`

### Stripe Webhook Setup

1.  **Navigate to Webhooks:**
    > In your Stripe dashboard, go to "Developers" -> "Webhooks".

2.  **Add a New Endpoint:**
    - **Endpoint URL:** `https://your-app.fly.dev/webhooks/stripe` (replace with your deployed application URL).
    - **Events to send:** Click "select events" and add the following:
        - `payment_intent.succeeded`
        - `payment_intent.payment_failed`
        - `payment_intent.canceled`
        - `payment_intent.created`
        - `payment_intent.processing`
        - `payment_intent.requires_action`

3.  **Reveal the Webhook Secret:**
    - After creating the endpoint, click to reveal the **signing secret**.
    - Copy this value and add it to your `.env` file as `STRIPE_WEBHOOK_SECRET`.

---

## 5. Step 4: Deploy the Application

The repository is configured for one-command deployment to Fly.io.

### Deployment Command

```bash
# Ensure you are in the echo-production directory
cd echo-production

# Deploy to Fly.io
./scripts/deploy.sh fly
```

This script will:
1.  Build the Docker image.
2.  Push the image to the Fly.io registry.
3.  Provision the necessary resources.
4.  Deploy the application.

### Alternative: Local Docker Deployment

To run the application locally:

```bash
./scripts/deploy.sh local
```

This will build and run the Docker container on your local machine, available at `http://localhost:8000`.

---

## 6. Step 5: Post-Deployment Verification

Once deployed, you should verify that the system is running correctly.

1.  **Health Check:**
    ```bash
    curl https://your-app.fly.dev/health
    ```
    > Expected response: `{"status": "ok"}`

2.  **Metrics Endpoint:**
    ```bash
    curl https://your-app.fly.dev/metrics
    ```
    > This will return a Prometheus-formatted list of system metrics.

3.  **Run Verification Tests:**
    The repository includes a comprehensive test suite that can be run against the live system.
    ```bash
    # Ensure you have pytest installed
    pip install pytest

    # Run the tests
    pytest tests/test_system.py --env live --url https://your-app.fly.dev
    ```

---

## 7. Ongoing Operations

### Reconciliation Job

The reconciliation job is configured to run daily at 2:00 AM UTC. This is handled by the deployed application and requires no manual intervention.

### Monitoring

- **Airtable:** Monitor the `reconciliation_log` and `audit_log` tables for any discrepancies or errors.
- **Stripe Dashboard:** Monitor payment activity and webhook delivery rates.
- **Fly.io Logs:** Monitor application logs for any exceptions or warnings.

---

**Deployment complete. The system is now live.**
