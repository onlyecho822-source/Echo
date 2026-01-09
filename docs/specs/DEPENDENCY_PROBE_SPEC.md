# Specification: Dependency Mapping Probe & Network Path Pod

**Document Status:** DRAFT
**Version:** 1.0
**Author:** Manus AI
**Date:** December 19, 2025

---

## 1. Overview

This document provides the technical specification for the first operational component of Echo's Global Dependency Graph: the **Dependency Mapping Probe**. It also defines the data structure for the **Network Path Pod**, the immutable, verifiable data artifact that the probe generates.

This initiative directly addresses the core problem of **hidden dependencies** by creating a verifiable, independent map of the internet's critical infrastructure paths. It is the first step in making the invisible architecture of systemic failure visible and actionable.

## 2. Probe Functional Specification

The Dependency Mapping Probe is a script designed to be executed from multiple, geographically and topologically diverse vantage points within the Echo Universe. Its purpose is to trace and record the network paths to a list of critical internet domains.

### 2.1. Core Logic

The probe will perform the following sequence of actions:

1.  **Ingest Target List:** Load a predefined list of critical domain names (e.g., top 100 financial services, top 50 SaaS providers).
2.  **Perform DNS Resolution:** For each domain, resolve its IP address using a designated DNS resolver (e.g., Google DNS `8.8.8.8`, Cloudflare `1.1.1.1`). Record the resulting IP address(es).
3.  **Execute Network Trace:** Perform a traceroute from the probe's vantage point to the resolved IP address. The traceroute must capture every hop, including IP address, hostname (if available), and round-trip time (RTT).
4.  **Identify Final Hop:** Isolate and flag the final hop in the trace, which represents the target's hosting provider or CDN edge.
5.  **Package Results:** Assemble all collected data (target domain, resolved IP, full traceroute path, final hop) into a structured format.
6.  **Seal the Pod:** Encapsulate the structured data into a **Network Path Pod**, sign it with the probe's cryptographic key, and submit it to the Echo Library for storage and analysis.

### 2.2. Configuration Parameters

The probe's behavior will be configurable via a separate configuration file or environment variables:

| Parameter | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `TARGET_LIST_URL` | URL | URL to a text file containing the list of domains to probe. | `https://echo.universe/lists/financial_targets_v1.txt` |
| `DNS_RESOLVER` | IP Address | The IP address of the DNS resolver to use for the test. | `8.8.8.8` |
| `TRACE_METHOD` | String | The traceroute methodology to use (`udp`, `icmp`, `tcp`). | `icmp` |
| `PROBE_ID` | String | A unique identifier for the probe instance. | `echo-probe-aws-us-east-1-01` |
| `ECHO_LIBRARY_ENDPOINT` | URL | The API endpoint for submitting sealed pods. | `https://api.echo.universe/v1/pods` |

---

## 3. Network Path Pod Schema

The Network Path Pod is the fundamental unit of data for the Global Dependency Graph. It is a JSON object containing the complete, verifiable results of a single probe run for a single target. This schema ensures that all data is structured, consistent, and ready for analysis.

### 3.1. JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Echo Network Path Pod",
  "description": "An immutable, verifiable record of the network path from a specific vantage point to a target domain at a specific point in time.",
  "type": "object",
  "properties": {
    "pod_id": {
      "description": "Unique identifier for the pod (e.g., a UUID or content hash).",
      "type": "string"
    },
    "probe_id": {
      "description": "Identifier of the probe that generated this pod.",
      "type": "string"
    },
    "timestamp_utc": {
      "description": "ISO 8601 timestamp of when the probe was executed.",
      "type": "string",
      "format": "date-time"
    },
    "target_domain": {
      "description": "The target domain that was probed.",
      "type": "string"
    },
    "dns_resolver": {
      "description": "The DNS resolver used for the test.",
      "type": "string",
      "format": "ipv4"
    },
    "resolved_ip": {
      "description": "The IP address the target domain resolved to.",
      "type": "string",
      "format": "ipv4"
    },
    "trace_path": {
      "description": "An ordered array of network hops from the probe to the target.",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "hop": {"type": "integer"},
          "ip": {"type": "string"},
          "hostname": {"type": "string"},
          "rtt_ms": {"type": "number"}
        },
        "required": ["hop", "ip", "rtt_ms"]
      }
    },
    "final_hop_provider": {
        "description": "The identified network provider of the final hop (e.g., 'Cloudflare', 'AWS Global Accelerator').",
        "type": "string"
    }
  },
  "required": [
    "pod_id",
    "probe_id",
    "timestamp_utc",
    "target_domain",
    "dns_resolver",
    "resolved_ip",
    "trace_path"
  ]
}
```

### 3.2. Signature Envelope

Before submission, the generated JSON object will be serialized, hashed, and signed by the probe's private key. The final submitted artifact will be a signature envelope containing the pod data and the signature.

```json
{
  "pod_data": { ... The Network Path Pod JSON object ... },
  "signature": "... cryptographic signature of the pod_data hash ...",
  "algorithm": "ECDSA-secp256k1"
}
```

---

## 4. Connection to Echo Principles

This specification is a direct implementation of the foundational principles of the Echo Universe:

*   **Observe Reality:** The probe captures the *actual* network path, providing ground-truth data that is independent of any provider's claims or documentation. It creates a verifiable record of the internet *as it is*.
*   **Detect Conflict:** By running probes from multiple vantage points and over time, the system will automatically detect discrepancies, route changes, and dependency concentrations that represent points of systemic risk.
*   **Transform Demand into Product:** The widespread demand for visibility into internet infrastructure is proven by every major outage. This specification defines the first tangible product to meet that demand: **verifiable visibility**. The resulting Global Dependency Graph is not just a tool; it is the first entry in the Echo Library, a product in its own right.

## 5. Next Steps

With this specification defined, the next phase is to begin implementation of the probe script and the backend systems required to ingest, verify, and store the Network Path Pods.
