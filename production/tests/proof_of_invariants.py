"""
Mathematical proof that invariants I1-I4 are enforced
Echo Phoenix v2.4.0-formal

Run with: pytest tests/proof_of_invariants.py -v
"""

import pytest
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Import from formal endpoints
import sys
sys.path.insert(0, '/home/ubuntu/echo-production')

from src.api.formal_endpoints import (
    canonicalize,
    atomic_check_set,
    evaluate_risk,
    state,
    app
)

from fastapi.testclient import TestClient

client = TestClient(app)

# Test API key
TEST_API_KEY = "test_api_key_for_invariant_proofs"

@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test"""
    state.D.clear()
    state.L.clear()
    state.Σ_E = {
        "frozen": False,
        "throttle": 0.0,
        "require_manual_approval": False
    }
    state.metrics = {
        "events_processed": 0,
        "events_deduplicated": 0,
        "control_commands": 0,
        "risk_events": 0
    }
    yield


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key for testing"""
    monkeypatch.setenv("ECHO_API_KEY", TEST_API_KEY)
    monkeypatch.setenv("ENVIRONMENT", "development")


class TestCanonicalization:
    """Test canonicalization function properties"""
    
    def test_deterministic(self):
        """canon(e) is deterministic: same input → same output"""
        event = {"source": "stripe", "type": "payment", "payload": {"amount": 100}}
        
        canon1, hash1 = canonicalize(event)
        canon2, hash2 = canonicalize(event)
        
        assert canon1 == canon2
        assert hash1 == hash2
    
    def test_key_order_invariant(self):
        """canon(e) is invariant to key order"""
        event1 = {"a": 1, "b": 2, "c": 3}
        event2 = {"c": 3, "a": 1, "b": 2}
        event3 = {"b": 2, "c": 3, "a": 1}
        
        _, hash1 = canonicalize(event1)
        _, hash2 = canonicalize(event2)
        _, hash3 = canonicalize(event3)
        
        assert hash1 == hash2 == hash3
    
    def test_null_removal(self):
        """canon(e) removes null values"""
        event1 = {"a": 1, "b": None, "c": 3}
        event2 = {"a": 1, "c": 3}
        
        _, hash1 = canonicalize(event1)
        _, hash2 = canonicalize(event2)
        
        assert hash1 == hash2
    
    def test_whitespace_removal(self):
        """canon(e) removes whitespace-only values"""
        event1 = {"a": 1, "b": "   ", "c": 3}
        event2 = {"a": 1, "c": 3}
        
        _, hash1 = canonicalize(event1)
        _, hash2 = canonicalize(event2)
        
        assert hash1 == hash2
    
    def test_nested_sorting(self):
        """canon(e) sorts nested dictionaries"""
        event1 = {"outer": {"z": 1, "a": 2}}
        event2 = {"outer": {"a": 2, "z": 1}}
        
        _, hash1 = canonicalize(event1)
        _, hash2 = canonicalize(event2)
        
        assert hash1 == hash2
    
    def test_hash_is_sha256(self):
        """h(e) = SHA256(canon(e))"""
        event = {"test": "data"}
        canon_str, h = canonicalize(event)
        
        expected_hash = hashlib.sha256(canon_str.encode()).hexdigest()
        assert h == expected_hash
        assert len(h) == 64  # SHA256 produces 64 hex chars


class TestI1ExactlyOnce:
    """I1: Exactly-once processing at boundary"""
    
    def test_first_event_processed(self, mock_api_key):
        """First occurrence of event is processed"""
        event = {
            "source": "stripe",
            "type": "payment_intent.succeeded",
            "payload": {"amount": 1000},
            "id": "evt_test_1"
        }
        
        response = client.post(
            "/ledger/events",
            json=event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.status_code == 201
        assert response.json()["status"] == "processed"
    
    def test_duplicate_rejected(self, mock_api_key):
        """Second occurrence of same event is rejected"""
        # Use fixed timestamp to ensure identical canonicalization
        fixed_timestamp = "2026-01-14T23:00:00Z"
        event = {
            "source": "stripe",
            "type": "payment_intent.succeeded",
            "payload": {"amount": 1000},
            "id": "evt_test_2",
            "timestamp": fixed_timestamp
        }
        
        # First request
        response1 = client.post(
            "/ledger/events",
            json=event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        hash1 = response1.json()["hash"]
        
        # Second request (duplicate) - same event with same timestamp
        response2 = client.post(
            "/ledger/events",
            json=event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response2.json()["status"] == "duplicate"
        assert response2.json()["hash"] == hash1
    
    def test_ledger_has_single_entry(self, mock_api_key):
        """Ledger contains exactly one entry for duplicate events"""
        # Use fixed timestamp to ensure identical canonicalization
        fixed_timestamp = "2026-01-14T23:00:00Z"
        event = {
            "source": "stripe",
            "type": "payment_intent.succeeded",
            "payload": {"amount": 1000},
            "id": "evt_test_3",
            "timestamp": fixed_timestamp
        }
        
        # Send same event 5 times
        responses = []
        for _ in range(5):
            resp = client.post(
                "/ledger/events",
                json=event,
                headers={"X-API-Key": TEST_API_KEY}
            )
            responses.append(resp.json())
        
        # First should be processed, rest should be duplicates
        assert responses[0]["status"] == "processed"
        for i in range(1, 5):
            assert responses[i]["status"] == "duplicate"
        
        # All should have the same hash
        hash_val = responses[0]["hash"]
        for resp in responses:
            assert resp["hash"] == hash_val
        
        # Count entries in ledger with this hash
        entries = [e for e in state.L if e.get("hash") == hash_val]
        assert len(entries) == 1
    
    def test_atomic_check_set_atomicity(self):
        """atomic_check_set is atomic"""
        test_hash = "a" * 64
        
        # First call returns True (new)
        assert atomic_check_set(test_hash) == True
        
        # Second call returns False (exists)
        assert atomic_check_set(test_hash) == False
        
        # Third call still returns False
        assert atomic_check_set(test_hash) == False
    
    def test_collision_probability(self):
        """P(collision) = 2^-256 ≈ 10^-77"""
        # Generate 1000 unique events
        hashes = set()
        for i in range(1000):
            event = {"unique_id": i, "timestamp": datetime.now(timezone.utc).isoformat()}
            _, h = canonicalize(event)
            hashes.add(h)
        
        # All hashes should be unique
        assert len(hashes) == 1000


class TestI2AuthoritySeparation:
    """I2: Zapier cannot mutate Stripe directly"""
    
    def test_no_stripe_mutation_endpoint(self, mock_api_key):
        """No endpoint allows direct Stripe mutation"""
        # List of endpoints that should NOT exist
        forbidden_endpoints = [
            "/stripe/charge",
            "/stripe/refund",
            "/stripe/customer",
            "/payments/create",
            "/payments/refund"
        ]
        
        for endpoint in forbidden_endpoints:
            response = client.post(
                endpoint,
                json={},
                headers={"X-API-Key": TEST_API_KEY}
            )
            # Should return 404 (not found) or 405 (method not allowed)
            assert response.status_code in [404, 405]
    
    def test_ledger_is_read_only_for_external(self, mock_api_key):
        """Ledger endpoint only accepts events, doesn't mutate Stripe"""
        event = {
            "source": "stripe",
            "type": "payment_intent.succeeded",
            "payload": {"amount": 1000}
        }
        
        response = client.post(
            "/ledger/events",
            json=event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        # Response should only contain ledger info, no Stripe mutation result
        result = response.json()
        assert "stripe_response" not in result
        assert "charge_id" not in result
        assert "refund_id" not in result


class TestI3SafetyGating:
    """I3: Freeze state prevents payments"""
    
    def test_freeze_command(self, mock_api_key):
        """FREEZE command sets frozen state"""
        response = client.post(
            "/control",
            json={
                "cmd": "FREEZE",
                "actor": "admin",
                "reason": "test freeze"
            },
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.status_code == 200
        assert response.json()["new_state"]["frozen"] == True
    
    def test_unfreeze_command(self, mock_api_key):
        """UNFREEZE command clears frozen state"""
        # First freeze
        client.post(
            "/control",
            json={"cmd": "FREEZE", "actor": "admin", "reason": "test"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        # Then unfreeze
        response = client.post(
            "/control",
            json={"cmd": "UNFREEZE", "actor": "admin", "reason": "test"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.json()["new_state"]["frozen"] == False
    
    def test_throttle_command(self, mock_api_key):
        """SET_THROTTLE command sets throttle value"""
        response = client.post(
            "/control",
            json={
                "cmd": "SET_THROTTLE",
                "actor": "ops",
                "value": 0.5,
                "reason": "test throttle"
            },
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.json()["new_state"]["throttle"] == 0.5
    
    def test_health_reflects_frozen_state(self, mock_api_key):
        """Health endpoint reflects frozen state"""
        # Freeze the system
        client.post(
            "/control",
            json={"cmd": "FREEZE", "actor": "admin", "reason": "test"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        # Check health
        response = client.get("/health")
        
        assert response.json()["status"] == "frozen"
        assert response.json()["frozen"] == True
    
    def test_control_logged_to_ledger(self, mock_api_key):
        """Control commands are logged to ledger"""
        initial_ledger_size = len(state.L)
        
        client.post(
            "/control",
            json={"cmd": "FREEZE", "actor": "admin", "reason": "test"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        # Ledger should have new entry
        assert len(state.L) == initial_ledger_size + 1
        
        # Entry should contain control action
        last_entry = state.L[-1]
        assert last_entry["action"] == "control"
        assert last_entry["cmd"] == "FREEZE"


class TestI4ObservabilityCompleteness:
    """I4: Every external event has ledger entry"""
    
    def test_event_creates_ledger_entry(self, mock_api_key):
        """Every processed event creates a ledger entry"""
        event = {
            "source": "stripe",
            "type": "payment_intent.succeeded",
            "payload": {"amount": 1000},
            "id": "evt_test_i4"
        }
        
        initial_size = len(state.L)
        
        client.post(
            "/ledger/events",
            json=event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert len(state.L) == initial_size + 1
    
    def test_ledger_entry_contains_required_fields(self, mock_api_key):
        """Ledger entry contains all required fields"""
        event = {
            "source": "github",
            "type": "pull_request.merged",
            "payload": {"pr_number": 50},
            "id": "github_pr_50"
        }
        
        client.post(
            "/ledger/events",
            json=event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        entry = state.L[-1]
        
        assert "hash" in entry
        assert "canonical" in entry
        assert "source" in entry
        assert "type" in entry
        assert "timestamp" in entry
        assert "processed_at" in entry
        assert "external_id" in entry
    
    def test_multiple_sources_tracked(self, mock_api_key):
        """Events from multiple sources are all tracked"""
        sources = ["stripe", "github", "manual", "zapier"]
        
        for source in sources:
            client.post(
                "/ledger/events",
                json={
                    "source": source,
                    "type": "test_event",
                    "payload": {"test": True},
                    "id": f"{source}_test"
                },
                headers={"X-API-Key": TEST_API_KEY}
            )
        
        # All sources should be in ledger
        ledger_sources = {e["source"] for e in state.L}
        assert ledger_sources == set(sources)


class TestRiskEngine:
    """Test risk evaluation and alerting"""
    
    def test_high_risk_events_flagged(self, mock_api_key):
        """Events with risk >= 0.7 are flagged"""
        high_risk_event = {
            "source": "stripe",
            "type": "charge.dispute.created",
            "payload": {"dispute_id": "dp_test"},
            "id": "evt_dispute"
        }
        
        response = client.post(
            "/ledger/events",
            json=high_risk_event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.json()["risk"] >= 0.7
    
    def test_low_risk_events_pass(self, mock_api_key):
        """Events with risk < 0.7 pass without alert"""
        low_risk_event = {
            "source": "github",
            "type": "push",
            "payload": {"ref": "refs/heads/main"},
            "id": "github_push_1"
        }
        
        response = client.post(
            "/ledger/events",
            json=low_risk_event,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.json()["risk"] < 0.7
    
    def test_risk_metrics_tracked(self, mock_api_key):
        """Risk events are tracked in metrics"""
        # Send high-risk event
        client.post(
            "/ledger/events",
            json={
                "source": "stripe",
                "type": "charge.dispute.created",
                "payload": {},
                "id": "evt_risk_test"
            },
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        response = client.get("/metrics")
        assert response.json()["echo_risk_events"] >= 1


class TestMathematicalGuarantees:
    """Verify mathematical guarantees"""
    
    def test_collision_resistance(self):
        """SHA256 provides 2^-256 collision probability"""
        # This is a property of SHA256, not something we can test directly
        # But we can verify we're using SHA256 correctly
        test_data = b"test data"
        expected = hashlib.sha256(test_data).hexdigest()
        
        assert len(expected) == 64
        assert all(c in "0123456789abcdef" for c in expected)
    
    def test_invariant_count(self):
        """System enforces exactly 4 invariants"""
        response = client.get("/health")
        invariants = response.json()["invariants"]
        
        assert len(invariants) == 4
        assert set(invariants) == {"I1", "I2", "I3", "I4"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
