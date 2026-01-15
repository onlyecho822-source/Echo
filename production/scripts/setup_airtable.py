#!/usr/bin/env python3
"""
Echo Phoenix - Airtable Setup Script

This script creates all required tables in your Airtable base.
Run this once during initial setup.

Usage:
    export AIRTABLE_API_KEY="your_api_key"
    export AIRTABLE_BASE_ID="your_base_id"
    python scripts/setup_airtable.py
"""

import os
import json
import time
import httpx
from typing import Dict, List, Any

# Configuration
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
BASE_URL = "https://api.airtable.com/v0"
META_URL = "https://api.airtable.com/v0/meta/bases"

# Table schemas
TABLES = [
    {
        "name": "system_throttle",
        "description": "Current throttle state and control parameters",
        "fields": [
            {"name": "timestamp", "type": "dateTime"},
            {"name": "throttle_pct", "type": "number", "options": {"precision": 4}},
            {"name": "reason", "type": "singleLineText"},
            {"name": "urgency", "type": "singleSelect", "options": {"choices": [
                {"name": "normal", "color": "greenLight2"},
                {"name": "high", "color": "yellowLight2"},
                {"name": "critical", "color": "redLight2"}
            ]}},
            {"name": "operator", "type": "singleLineText"},
            {"name": "active", "type": "checkbox"}
        ]
    },
    {
        "name": "system_state",
        "description": "Historical system state observations",
        "fields": [
            {"name": "timestamp", "type": "dateTime"},
            {"name": "throttle_pct", "type": "number", "options": {"precision": 4}},
            {"name": "error_rate", "type": "number", "options": {"precision": 6}},
            {"name": "latency_p99_ms", "type": "number", "options": {"precision": 2}},
            {"name": "requests_per_minute", "type": "number", "options": {"precision": 2}},
            {"name": "phi_static", "type": "number", "options": {"precision": 4}},
            {"name": "phi_dynamic", "type": "number", "options": {"precision": 4}},
            {"name": "temperature", "type": "number", "options": {"precision": 4}},
            {"name": "susceptibility", "type": "number", "options": {"precision": 4}},
            {"name": "health", "type": "singleSelect", "options": {"choices": [
                {"name": "healthy", "color": "greenLight2"},
                {"name": "degraded", "color": "yellowLight2"},
                {"name": "critical", "color": "redLight2"},
                {"name": "killed", "color": "grayLight2"}
            ]}}
        ]
    },
    {
        "name": "used_nonces",
        "description": "Deduplication store for idempotency",
        "fields": [
            {"name": "nonce", "type": "singleLineText"},
            {"name": "type", "type": "singleSelect", "options": {"choices": [
                {"name": "idempotency_key", "color": "blueLight2"},
                {"name": "webhook_event", "color": "purpleLight2"},
                {"name": "control_action", "color": "cyanLight2"}
            ]}},
            {"name": "result_id", "type": "singleLineText"},
            {"name": "created_at", "type": "dateTime"},
            {"name": "expires_at", "type": "dateTime"}
        ]
    },
    {
        "name": "payment_ledger",
        "description": "Evidence & Integrity Ledger for payments",
        "fields": [
            {"name": "ledger_id", "type": "singleLineText"},
            {"name": "stripe_id", "type": "singleLineText"},
            {"name": "order_id", "type": "singleLineText"},
            {"name": "amount", "type": "number", "options": {"precision": 0}},
            {"name": "currency", "type": "singleLineText"},
            {"name": "state", "type": "singleSelect", "options": {"choices": [
                {"name": "pending", "color": "grayLight2"},
                {"name": "created", "color": "blueLight2"},
                {"name": "action_required", "color": "yellowLight2"},
                {"name": "succeeded", "color": "greenLight2"},
                {"name": "failed", "color": "redLight2"},
                {"name": "refunded", "color": "purpleLight2"}
            ]}},
            {"name": "created_at", "type": "dateTime"},
            {"name": "updated_at", "type": "dateTime"},
            {"name": "idempotency_key", "type": "singleLineText"},
            {"name": "metadata", "type": "multilineText"},
            {"name": "events", "type": "multilineText"}
        ]
    },
    {
        "name": "audit_log",
        "description": "Complete audit trail for all operations",
        "fields": [
            {"name": "timestamp", "type": "dateTime"},
            {"name": "action", "type": "singleLineText"},
            {"name": "actor", "type": "singleLineText"},
            {"name": "resource_type", "type": "singleSelect", "options": {"choices": [
                {"name": "payment", "color": "greenLight2"},
                {"name": "throttle", "color": "blueLight2"},
                {"name": "state", "color": "cyanLight2"},
                {"name": "webhook", "color": "purpleLight2"},
                {"name": "kill", "color": "redLight2"}
            ]}},
            {"name": "resource_id", "type": "singleLineText"},
            {"name": "details", "type": "multilineText"},
            {"name": "result", "type": "singleSelect", "options": {"choices": [
                {"name": "success", "color": "greenLight2"},
                {"name": "failure", "color": "redLight2"},
                {"name": "skipped", "color": "grayLight2"}
            ]}}
        ]
    },
    {
        "name": "reconciliation_runs",
        "description": "Reconciliation job history",
        "fields": [
            {"name": "run_id", "type": "singleLineText"},
            {"name": "started_at", "type": "dateTime"},
            {"name": "completed_at", "type": "dateTime"},
            {"name": "events_checked", "type": "number", "options": {"precision": 0}},
            {"name": "gaps_detected", "type": "number", "options": {"precision": 0}},
            {"name": "gaps_repaired", "type": "number", "options": {"precision": 0}},
            {"name": "missing_entries", "type": "number", "options": {"precision": 0}},
            {"name": "status", "type": "singleSelect", "options": {"choices": [
                {"name": "healthy", "color": "greenLight2"},
                {"name": "needs_repair", "color": "yellowLight2"},
                {"name": "failed", "color": "redLight2"}
            ]}},
            {"name": "details", "type": "multilineText"}
        ]
    }
]


def get_headers() -> Dict[str, str]:
    """Get API headers."""
    return {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }


def list_existing_tables() -> List[str]:
    """List existing tables in the base."""
    url = f"{META_URL}/{AIRTABLE_BASE_ID}/tables"
    response = httpx.get(url, headers=get_headers())
    
    if response.status_code != 200:
        print(f"Warning: Could not list tables: {response.text}")
        return []
    
    data = response.json()
    return [table["name"] for table in data.get("tables", [])]


def create_table(table_config: Dict[str, Any]) -> bool:
    """Create a single table."""
    url = f"{META_URL}/{AIRTABLE_BASE_ID}/tables"
    
    payload = {
        "name": table_config["name"],
        "description": table_config.get("description", ""),
        "fields": table_config["fields"]
    }
    
    response = httpx.post(url, headers=get_headers(), json=payload)
    
    if response.status_code == 200:
        print(f"  ✓ Created table: {table_config['name']}")
        return True
    else:
        print(f"  ✗ Failed to create {table_config['name']}: {response.text}")
        return False


def create_initial_throttle_record():
    """Create the initial throttle record (active = true, throttle = 0)."""
    url = f"{BASE_URL}/{AIRTABLE_BASE_ID}/system_throttle"
    
    payload = {
        "records": [{
            "fields": {
                "timestamp": "2026-01-14T00:00:00.000Z",
                "throttle_pct": 0.0,
                "reason": "Initial setup - system operational",
                "urgency": "normal",
                "operator": "setup_script",
                "active": True
            }
        }]
    }
    
    response = httpx.post(url, headers=get_headers(), json=payload)
    
    if response.status_code == 200:
        print("  ✓ Created initial throttle record (0% throttle, active)")
        return True
    else:
        print(f"  ✗ Failed to create initial record: {response.text}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("Echo Phoenix - Airtable Setup")
    print("=" * 60)
    print()
    
    # Validate configuration
    if not AIRTABLE_API_KEY:
        print("ERROR: AIRTABLE_API_KEY environment variable not set")
        print("Run: export AIRTABLE_API_KEY='your_api_key'")
        return False
    
    if not AIRTABLE_BASE_ID:
        print("ERROR: AIRTABLE_BASE_ID environment variable not set")
        print("Run: export AIRTABLE_BASE_ID='your_base_id'")
        return False
    
    print(f"Base ID: {AIRTABLE_BASE_ID}")
    print()
    
    # Check existing tables
    print("Checking existing tables...")
    existing = list_existing_tables()
    print(f"Found {len(existing)} existing tables: {existing}")
    print()
    
    # Create tables
    print("Creating tables...")
    created = 0
    skipped = 0
    failed = 0
    
    for table in TABLES:
        if table["name"] in existing:
            print(f"  - Skipped (exists): {table['name']}")
            skipped += 1
        else:
            if create_table(table):
                created += 1
            else:
                failed += 1
            # Rate limiting
            time.sleep(0.5)
    
    print()
    print(f"Results: {created} created, {skipped} skipped, {failed} failed")
    print()
    
    # Create initial throttle record
    if "system_throttle" not in existing:
        print("Creating initial throttle record...")
        create_initial_throttle_record()
        print()
    
    # Summary
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Verify tables in Airtable UI")
    print("2. Configure Zapier automations")
    print("3. Deploy the Phoenix Control Service")
    print()
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
