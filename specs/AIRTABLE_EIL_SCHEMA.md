# Airtable EIL Schema: Formal Specification

**Specification:** Echo Integration Topology v1.0  
**Author:** Manus AI  
**Date:** 2026-01-14

---

## Overview

This document defines the formal schema for the Evidence & Integrity Ledger (EIL) hosted on Airtable. This schema must be created **before** any Zap is configured. The schema implements hash chaining for tamper-evidence within Airtable's constraints.

---

## Base Configuration

**Base Name:** `Echo EIL`

---

## Table 1: `raw_events`

This is the primary append-only log of all incoming events.

| Field Name | Type | Description | Required |
|---|---|---|---|
| `Event ID` | Single line text | Unique identifier from source (e.g., GitHub event ID). **Primary key for idempotency.** | Yes |
| `Sequence` | Auto Number | Auto-incrementing sequence number. | Auto |
| `Event Type` | Single select | `push`, `pull_request`, `issue`, `commit_comment`, `other` | Yes |
| `Payload` | Long text | Full JSON payload (truncated if >90k chars). | Yes |
| `Payload Hash` | Single line text | SHA-256 hash of the original, untruncated payload. | Yes |
| `Payload URL` | URL | Link to the original event in GitHub API (for full payload retrieval). | No |
| `Source` | Single select | `github`, `manus`, `slack`, `webhook`, `other` | Yes |
| `Actor` | Single line text | Username or system that triggered the event. | Yes |
| `Previous Hash` | Single line text | The `Record Hash` of the immediately preceding record. Links the chain. | Yes |
| `Record Hash` | Single line text | SHA-256 of (`Previous Hash` + `Payload Hash` + `Sequence`). | Yes |
| `Created At` | Date/Time | Timestamp of when the record was created. | Yes |
| `Processed` | Checkbox | Flag for downstream processing. Default: `false`. | No |

**Hash Chaining Logic:**
```
Record Hash = SHA256(Previous Hash || Payload Hash || Sequence)
```
The first record uses a genesis hash: `0000000000000000000000000000000000000000000000000000000000000000`.

---

## Table 2: `verified_outputs`

This table stores the verified outputs from compute Zaps (e.g., A-CMAP).

| Field Name | Type | Description | Required |
|---|---|---|---|
| `Output ID` | Single line text | Unique ID for this output record. | Yes |
| `Source Task ID` | Single line text | Links back to the originating task (e.g., PR ID, Intent ID). | Yes |
| `Output` | Long text | The final, verified output from the compute process. | Yes |
| `Evidence Links` | Linked record | Links to one or more records in `raw_events` that support this output. | No |
| `Consensus Score` | Number | The final consensus score (e.g., from A-CMAP). | No |
| `Sealed At` | Date/Time | Timestamp when the record was sealed. | Yes |
| `Sealed Hash` | Single line text | HMAC-SHA256 of the `Output` field, using a secret key. | Yes |
| `Sealed By` | Single line text | The system or user that sealed the record. | Yes |

**Immutability Enforcement:**
Records in this table should **not** be edited after `Sealed At` is set. Any modification to a sealed record is a violation and should trigger an alert. This can be monitored via Airtable's revision history or a separate audit Zap.

---

## Table 3: `unrouted_intents` (Dead-Letter Queue)

This table captures any webhook payload that could not be routed by the `INTENT-Router`.

| Field Name | Type | Description | Required |
|---|---|---|---|
| `DLQ ID` | Auto Number | Auto-incrementing ID. | Auto |
| `Raw Payload` | Long text | The full, unprocessed JSON payload from the webhook. | Yes |
| `Error Reason` | Single line text | Why the intent was not routed (e.g., `unknown_intent`, `malformed_json`). | Yes |
| `Received At` | Date/Time | Timestamp of when the webhook was received. | Yes |
| `Resolved` | Checkbox | Flag to mark if the issue has been manually investigated. Default: `false`. | No |

---

## Table 4: `chain_state` (Helper Table)

This small table stores the current state of the hash chain for the `raw_events` table. It allows Zaps to quickly look up the `last_hash` without scanning the entire table.

| Field Name | Type | Description | Required |
|---|---|---|---|
| `Chain ID` | Single line text | Identifier for the chain (e.g., `raw_events_main`). | Yes |
| `Last Sequence` | Number | The sequence number of the last record in the chain. | Yes |
| `Last Hash` | Single line text | The `Record Hash` of the last record in the chain. | Yes |
| `Updated At` | Date/Time | Timestamp of the last update. | Yes |

**Usage:**
1. The `GH-All-Activity-Logger` Zap first reads from `chain_state` to get `Last Hash`.
2. It uses this as the `Previous Hash` for the new record.
3. After creating the new record in `raw_events`, it updates `chain_state` with the new `Last Hash` and `Last Sequence`.

---

## Table 5: `gkp_audit_log`

This table logs all Global Kill Plane activations and resumptions.

| Field Name | Type | Description | Required |
|---|---|---|---|
| `Log ID` | Auto Number | Auto-incrementing ID. | Auto |
| `Event Type` | Single select | `KILL_ACTIVATED`, `KILL_RESUMED` | Yes |
| `Reason` | Long text | The reason provided for the activation/resumption. | Yes |
| `Triggered By` | Single line text | The system or admin ID that triggered the event. | Yes |
| `Timestamp` | Date/Time | Timestamp of the event. | Yes |
| `Acknowledged` | Checkbox | Whether the PagerDuty incident was acknowledged. | No |

---

## Implementation Checklist

Before building any Zap, complete this checklist:

- [ ] Create Airtable Base: `Echo EIL`
- [ ] Create Table: `raw_events` with all fields
- [ ] Create Table: `verified_outputs` with all fields
- [ ] Create Table: `unrouted_intents` with all fields
- [ ] Create Table: `chain_state` with all fields
- [ ] Create Table: `gkp_audit_log` with all fields
- [ ] Initialize `chain_state` with a genesis record:
  - `Chain ID`: `raw_events_main`
  - `Last Sequence`: `0`
  - `Last Hash`: `0000000000000000000000000000000000000000000000000000000000000000`
- [ ] Set environment variables in Zapier:
  - `ZAPIER_WEBHOOK_SECRET`
  - `EIL_SEAL_SECRET`
