# Zapier Implementation Guide: Echo System v2.2

**Specification:** Echo Integration Topology v1.0  
**Author:** Manus AI  
**Date:** 2026-01-14

---

## Executive Summary

This document provides the detailed, step-by-step build specifications for the five core Zaps that form the central nervous system of the Echo system. These specifications translate the architectural design into an actionable implementation plan for Zapier.

---

## Core Zap Specifications

### 1. Zap: `GH-All-Activity-Logger`

| | |
|---|---|
| **Objective** | Create an immutable, append-only audit trail of all significant GitHub activity in the Evidence & Integrity Ledger (EIL) hosted on Airtable. |
| **Pathway Type** | Linear → Aggregation |
| **Success Metric** | 100% of specified GitHub events are logged to Airtable within 60 seconds. |

#### Trigger

- **App:** GitHub
- **Event:** New Activity (This is a conceptual trigger. In practice, you will create **separate Zaps for each critical event** and merge them into a single workflow or log them with a common format.)
  - `New Push`
  - `New Pull Request`
  - `New Issue`
  - `New Commit Comment`

#### Actions

**Step 1: Create EIL Record in Airtable**
- **App:** Airtable
- **Action:** Create Record
- **Base:** `Echo EIL`
- **Table:** `raw_events`
- **Field Mapping:**
  | Airtable Field | GitHub Data | Notes |
  |---|---|---|
  | `event_id` | `{{github_event_id}}` | Use the unique ID from the GitHub event for idempotency. |
  | `event_type` | `{{github_event_type}}` | e.g., `push`, `pull_request` |
  | `payload` | `{{github_full_payload}}` | Store the entire JSON payload from GitHub for full auditability. |
  | `source` | `github` | Hardcoded value. |
  | `created_by` | `{{github_actor_username}}` | The user who triggered the event. |
  | `created_at` | `{{zap_meta_human_now}}` | Zapier's timestamp. |

**Step 2: Post Audit Log to Slack**
- **App:** Slack
- **Action:** Send Channel Message
- **Channel:** `#github-audit`
- **Message Text:** `New GitHub Event: *{{github_event_type}}* by *{{github_actor_username}}*. EIL Record: {{airtable_record_id}}`

---

### 2. Zap: `INTENT-Router`

| | |
|---|---|
| **Objective** | Act as the central routing hub for intents emitted by Manus AI, directing tasks to the appropriate compute or storage layer. |
| **Pathway Type** | Branching (Deterministic) |
| **Success Metric** | 99.9% of incoming webhooks are correctly routed to a path within 5 seconds. |

#### Trigger

- **App:** Webhooks by Zapier
- **Event:** Catch Hook
- **Configuration:** Zapier generates a unique URL. Manus AI will send a POST request to this URL with a JSON payload.
- **Example Payload:**
  ```json
  {
    "intent": "ANALYSIS",
    "data": "Analyze the sentiment of this text...",
    "source_task_id": "manus_task_123"
  }
  ```

#### Actions

**Step 1: Zapier Paths**
- Create paths based on the `intent` field from the webhook payload.

**Path A: `intent` is `ANALYSIS`**
- **Action:** Send prompt to OpenAI.
- **App:** OpenAI
- **Action:** Send Prompt
- **Prompt:** `{{webhook_data}}`

**Path B: `intent` is `VERIFY`**
- **Action:** Send prompt to Anthropic Claude.
- **App:** Anthropic (Claude)
- **Action:** Send Prompt
- **Prompt:** `{{webhook_data}}`

**Path C: `intent` is `ARCHIVE`**
- **Action:** Create a record in Airtable.
- **App:** Airtable
- **Action:** Create Record
- **Base:** `Echo EIL`
- **Table:** `manual_archives`
- **Field Mapping:** Map `data` and `source_task_id` from webhook.

---

### 3. Zap: `A-CMAP-Review`

| | |
|---|---|
| **Objective** | Implement the Adversarial Consensus Protocol for Byzantine fault-tolerant code review. |
| **Pathway Type** | Parallel → Aggregation → Branching |
| **Success Metric** | Automatically flag a genuine code disagreement between OpenAI and Claude with >2 variance. |

#### Trigger

- **App:** GitHub
- **Event:** New Pull Request

#### Actions

**Step 1: Zapier Paths (Parallel Fork)**
- Create two parallel paths that run simultaneously.

**Path A: OpenAI Review**
- **Action:** Get Pull Request Diff from GitHub.
- **Action:** Send PR diff to OpenAI with a prompt asking for a review and a score from 1-10.

**Path B: Claude Review**
- **Action:** Get Pull Request Diff from GitHub.
- **Action:** Send the *same* PR diff to Anthropic Claude with an identical prompt.

**Step 2: Code by Zapier (Aggregation & Consensus)**
- **App:** Code by Zapier
- **Action:** Run Javascript
- **Input Data:**
  - `openaiScore`: The score from Path A.
  - `claudeScore`: The score from Path B.
  - `commitHash`: The commit hash from the GitHub trigger.
- **Code:**
  ```javascript
  let variance = Math.abs(inputData.openaiScore - inputData.claudeScore);
  let consensus = (parseFloat(inputData.openaiScore) + parseFloat(inputData.claudeScore)) / 2;
  let threshold = 2;

  let output = { variance: variance, consensus: consensus, action: 'none' };

  if (variance > threshold) {
      output.action = 'alert';
  } else if (consensus > 7) {
      output.action = 'merge';
  } else {
      output.action = 'revision';
  }

  return output;
  ```

**Step 3: Zapier Paths (Action Routing)**
- Create paths based on the `action` field from the Javascript step.

**Path A: `action` is `alert`**
- **Action:** Send message to Slack channel `#dissent-alert` with details.

**Path B: `action` is `merge`**
- **Action:** (Future) Trigger auto-merge workflow.

**Path C: `action` is `revision`**
- **Action:** Create a comment on the GitHub PR requesting revisions.

---

### 4. Zap: `Evidence-Binder`

| | |
|---|---|
| **Objective** | Close the loop by logging the verified output of any compute Zap back to the EIL. |
| **Pathway Type** | Linear |
| **Success Metric** | A compute task from the `INTENT-Router` results in a `verified_outputs` record linked to the source task. |

#### Trigger

- **App:** Webhooks by Zapier
- **Event:** Catch Hook
- **Configuration:** Called by `A-CMAP-Review` or other compute Zaps.
- **Example Payload:**
  ```json
  {
    "source_task_id": "pr_review_456",
    "consensus_output": "LGTM, merge.",
    "evidence_hashes": ["hash1", "hash2"]
  }
  ```

#### Actions

**Step 1: Create Record in Airtable**
- **App:** Airtable
- **Action:** Create Record
- **Base:** `Echo EIL`
- **Table:** `verified_outputs`
- **Field Mapping:**
  | Airtable Field | Webhook Data |
  |---|---|
  | `source_task_id` | `{{source_task_id}}` |
  | `output` | `{{consensus_output}}` |
  | `evidence_links` | `{{evidence_hashes}}` |

---

### 5. Zap: `Global-Kill-Trigger`

| | |
|---|---|
| **Objective** | Provide an immediate, multi-channel emergency broadcast system to halt operations. |
| **Pathway Type** | Broadcast |
| **Success Metric** | A manual webhook call results in a PagerDuty alert and Slack message within 15 seconds. |

#### Trigger

- **App:** Webhooks by Zapier
- **Event:** Catch Hook
- **Configuration:** A secret, high-entropy URL known only to authorized systems/personnel.

#### Actions

**Step 1: Create PagerDuty Incident**
- **App:** PagerDuty
- **Action:** Create Incident
- **Urgency:** High
- **Title:** `GKP ACTIVATED: {{webhook_reason}}`

**Step 2: Post to Slack**
- **App:** Slack
- **Action:** Send Channel Message
- **Channel:** `#gkp-active`
- **Message Text:** `@channel **GLOBAL KILL PLANE ACTIVATED**\nReason: {{webhook_reason}}\nTimestamp: {{zap_meta_human_now}}`

**Step 3: Log to Immutable Sheet**
- **App:** Google Sheets
- **Action:** Create Spreadsheet Row
- **Spreadsheet:** `GKP Audit Log`
- **Worksheet:** `Activations`
- **Row:** `{{zap_meta_human_now}}`, `{{webhook_reason}}`, `{{webhook_source}}`
