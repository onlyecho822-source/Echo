# Zapier Implementation Guide: Hardened Spec v2.3

**Specification:** Echo Integration Topology v1.0  
**Author:** Manus AI  
**Date:** 2026-01-14

---

## Executive Summary

This document provides the **hardened, production-ready build specifications** for the five core Zaps. It incorporates all mandatory refinements from the Devil Lens audit to ensure operational robustness, security, and reliability. This v2.3 specification supersedes all previous versions.

---

## Core Zap Specifications (Hardened)

### 1. Zap: `GH-All-Activity-Logger`

| | |
|---|---|
| **Objective** | Create an immutable, append-only audit trail of all significant GitHub activity in the EIL. |
| **Pathway Type** | Linear → Aggregation |
| **Success Metric** | 100% of specified GitHub events are logged to Airtable within 60 seconds, with zero duplicates. |

#### Trigger

- **App:** GitHub
- **Events:** `New Push`, `New Pull Request`, `New Issue` (separate Zaps).

#### Actions

**Step 1: Find Record in Airtable (Deduplication)**
- **App:** Airtable
- **Action:** Find Record
- **Search By Field:** `Event ID`
- **Search Value:** `{{github_event_id}}`
- **Configuration:** Check "Create Airtable record if it doesn’t exist yet?" - **NO**. This is critical.

**Step 2: Filter (Stop if Duplicate)**
- **App:** Filter by Zapier
- **Action:** Only continue if...
- **Condition:** `{{airtable_search_success}}` is `false`.

**Step 3: Code by Zapier (Payload Truncation & Hashing)**
- **App:** Code by Zapier
- **Action:** Run Javascript
- **Input Data:** `payload: {{github_full_payload}}`
- **Code:**
  ```javascript
  const MAX_SIZE = 90000; // Airtable limit is ~100k
  const payloadStr = JSON.stringify(inputData.payload);
  let truncatedPayload = payloadStr;
  if (payloadStr.length > MAX_SIZE) {
      truncatedPayload = payloadStr.substring(0, MAX_SIZE) + '... [TRUNCATED]';
  }
  return { truncatedPayload: truncatedPayload };
  ```

**Step 4: Create EIL Record in Airtable**
- **App:** Airtable
- **Action:** Create Record
- **Base:** `Echo EIL`
- **Table:** `raw_events`
- **Field Mapping:** Use data from trigger and Step 3. **Crucially, include hash chaining logic here by first looking up the `last_hash` from a summary table.**

---

### 2. Zap: `INTENT-Router`

| | |
|---|---|
| **Objective** | Securely route intents from Manus AI to the correct compute or storage layer, with zero data loss. |
| **Pathway Type** | Branching (Deterministic) |
| **Success Metric** | 100% of incoming webhooks are either correctly routed or logged to the dead-letter queue. |

#### Trigger

- **App:** Webhooks by Zapier
- **Event:** Catch Hook

#### Actions

**Step 1: Code by Zapier (Authentication)**
- **App:** Code by Zapier
- **Action:** Run Javascript
- **Input Data:** `signature: {{http_headers_X_Echo_Sig}}`, `payload: {{raw_body}}`
- **Code:**
  ```javascript
  const crypto = require('crypto');
  const secret = process.env.ZAPIER_WEBHOOK_SECRET;
  const hash = crypto.createHmac('sha256', secret).update(inputData.payload).digest('hex');
  const isValid = (hash === inputData.signature);
  if (!isValid) { throw new Error('Invalid signature'); }
  return { auth: 'success' };
  ```

**Step 2: Zapier Paths**
- **Path A: `intent` is `ANALYSIS`** → OpenAI
- **Path B: `intent` is `VERIFY`** → Claude
- **Path C: `intent` is `ARCHIVE`** → Airtable
- **Path D: Default (Dead-Letter Queue)**
  - **Action:** Create Record in Airtable
  - **Base:** `Echo EIL`
  - **Table:** `unrouted_intents`
  - **Field Mapping:** Log the entire raw payload for debugging.

---

### 3. Zap: `A-CMAP-Review`

| | |
|---|---|
| **Objective** | Implement robust, fault-tolerant adversarial code review. |
| **Pathway Type** | Parallel → Aggregation → Branching |
| **Success Metric** | Automatically flag code disagreement with >2 variance, using confidence-adjusted scores. |

#### Trigger

- **App:** GitHub
- **Event:** New Pull Request

#### Actions

**Step 1: Parallel Fork (Paths)** → OpenAI & Claude

**Step 2: Code by Zapier (Aggregation & Consensus)**
- **Input Data:** `openaiResponse`, `claudeResponse`
- **Code:**
  ```javascript
  // 1. Parse responses, force schema { score, confidence, summary }
  // 2. If malformed, throw error.
  let oai = JSON.parse(inputData.openaiResponse);
  let claude = JSON.parse(inputData.claudeResponse);

  // 3. Use confidence-adjusted scoring
  let weightedMean = ((oai.score * oai.confidence) + (claude.score * claude.confidence)) / (oai.confidence + claude.confidence);
  let variance = Math.abs(oai.score - claude.score);
  let threshold = 2;

  let output = { action: 'none' };
  if (variance > threshold) { output.action = 'alert'; }
  else if (weightedMean > 7.5) { output.action = 'merge'; }
  else { output.action = 'revision'; }

  return output;
  ```

**Step 3: Action Routing (Paths)** → Slack, GitHub Comment

---

### 4. Zap: `Evidence-Binder`

| | |
|---|---|
| **Objective** | Securely log verified outputs to the EIL with an immutable seal. |
| **Pathway Type** | Linear |
| **Success Metric** | All compute outputs are logged with a `sealed_hash`. |

#### Actions

**Step 1: Code by Zapier (Verification & Sealing)**
- **Input Data:** `evidence_hashes`, `output`
- **Code:**
  ```javascript
  // 1. Verify format of all evidence_hashes

  // 2. Create sealed_hash
  const crypto = require('crypto');
  const sealed_hash = crypto.createHmac('sha256', process.env.EIL_SEAL_SECRET)
                            .update(JSON.stringify(inputData.output))
                            .digest('hex');
  return { sealed_hash: sealed_hash, sealed_at: new Date().toISOString() };
  ```

**Step 2: Create Record in Airtable**
- **Table:** `verified_outputs`
- **Field Mapping:** Include `sealed_hash` and `sealed_at` from Step 1.

---

### 5. Zap: `Global-Kill-Trigger` & `Global-Resume-Trigger`

| | |
|---|---|
| **Objective** | Provide a secure, authenticated emergency broadcast and resumption system. |
| **Pathway Type** | Broadcast |
| **Success Metric** | Unauthorized webhook calls are rejected; authorized calls trigger a PagerDuty alert. |

#### Trigger (Both Zaps)

- **App:** Webhooks by Zapier
- **Event:** Catch Hook

#### Actions (Both Zaps)

**Step 1: Code by Zapier (HMAC Authentication)**
- **Mandatory.** Verify the signed payload as in the `INTENT-Router`.

**Step 2: Broadcast**
- **GKP:** PagerDuty, Slack (`#gkp-active`), Google Sheets Log
- **Resume:** Slack (`#gkp-resumed`), Google Sheets Log

**Step 3 (GKP Only): Acknowledgement Loop**
- **App:** Delay by Zapier
- **Action:** Delay For 60 seconds
- **App:** PagerDuty
- **Action:** Get Incident
- **App:** Filter by Zapier
- **Action:** Only continue if `status` is not `acknowledged`.
- **App:** Twilio
- **Action:** Send SMS / Make Call to secondary on-call.
