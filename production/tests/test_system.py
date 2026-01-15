"""
Echo Phoenix Control Service - Verification Test Suite

Tests all critical functionality:
1. API endpoints (using TestClient)
2. State management
3. Control loop
4. Kill switch
5. Stripe integration
6. Deduplication
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

# Import modules under test
import sys
sys.path.insert(0, '/home/ubuntu/echo-production')

from src.api import app, state_manager, SystemState, ControlAction
from src.stripe_wrapper import (
    EchoStripeWrapper, 
    IdempotencyEngine, 
    DeduplicationLayer,
    EvidenceLedger,
    PaymentState,
    ClinicPaymentProfile
)

# Create test client
client = TestClient(app)


# =============================================================================
# API TESTS
# =============================================================================

class TestHealthEndpoint:
    """Test /health endpoint."""
    
    def test_health_returns_200(self):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert data["version"] == "2.4.0"
    
    def test_health_shows_kill_status(self):
        """Health should reflect kill switch status."""
        state_manager.kill_active = True
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "killed"
        state_manager.kill_active = False


class TestObserveEndpoint:
    """Test /observe endpoint."""
    
    def test_observe_returns_state(self):
        """Observe should return current system state."""
        response = client.post("/observe", json={"source": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "state" in data
        assert "health" in data
        assert "recommendations" in data
    
    def test_observe_includes_viability_metrics(self):
        """Observe should include phi_static and phi_dynamic."""
        response = client.post("/observe", json={})
        data = response.json()
        state = data["state"]
        assert "phi_static" in state
        assert "phi_dynamic" in state
        assert "temperature" in state


class TestControlEndpoint:
    """Test /control endpoint."""
    
    def test_control_computes_action(self):
        """Control should compute and return action."""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "throttle_pct": 0.0,
            "error_rate": 0.05,
            "latency_p99_ms": 100.0,
            "requests_per_minute": 100.0,
            "phi_static": 0.5,
            "phi_dynamic": 0.45,
            "temperature": 0.85,
            "susceptibility": 2.0
        }
        
        response = client.post("/control", json={"current_state": state})
        assert response.status_code == 200
        data = response.json()
        assert "action" in data
        assert "applied" in data
        assert data["applied"] == True
    
    def test_control_increases_throttle_on_high_error(self):
        """Control should increase throttle when error rate is high."""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "throttle_pct": 0.0,
            "error_rate": 0.6,  # High error rate
            "latency_p99_ms": 100.0,
            "requests_per_minute": 100.0,
            "phi_static": 0.5,
            "phi_dynamic": 0.45,
            "temperature": 0.85,
            "susceptibility": 2.0
        }
        
        response = client.post("/control", json={"current_state": state})
        data = response.json()
        assert data["action"]["new_throttle"] == 1.0
        assert data["action"]["urgency"] == "critical"


class TestKillEndpoint:
    """Test /kill endpoint."""
    
    def test_kill_requires_confirmation(self):
        """Kill should require correct confirmation."""
        response = client.post("/kill", json={
            "reason": "test",
            "operator": "test",
            "confirmation": "wrong"
        })
        assert response.status_code == 400
    
    def test_kill_activates_with_confirmation(self):
        """Kill should activate with correct confirmation."""
        response = client.post("/kill", json={
            "reason": "test",
            "operator": "test",
            "confirmation": "CONFIRM_KILL"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "killed"
        assert state_manager.kill_active == True
        
        # Revive for other tests
        client.post("/revive")
        state_manager.kill_active = False


# =============================================================================
# IDEMPOTENCY TESTS
# =============================================================================

class TestIdempotencyEngine:
    """Test idempotency key derivation and management."""
    
    def test_canonicalize_sorts_metadata(self):
        """Canonicalization should sort metadata keys."""
        engine = IdempotencyEngine()
        
        params1 = {"metadata": {"b": 2, "a": 1}}
        params2 = {"metadata": {"a": 1, "b": 2}}
        
        assert engine.canonicalize(params1) == engine.canonicalize(params2)
    
    def test_derive_key_is_deterministic(self):
        """Key derivation should be deterministic."""
        engine = IdempotencyEngine()
        
        key1 = engine.derive_key("order_1", 1000, "usd", "cus_1")
        key2 = engine.derive_key("order_1", 1000, "usd", "cus_1")
        
        assert key1 == key2
    
    def test_derive_key_differs_for_different_orders(self):
        """Different orders should have different keys."""
        engine = IdempotencyEngine()
        
        key1 = engine.derive_key("order_1", 1000, "usd", "cus_1")
        key2 = engine.derive_key("order_2", 1000, "usd", "cus_1")
        
        assert key1 != key2
    
    def test_key_storage_and_retrieval(self):
        """Keys should be stored and retrievable within window."""
        engine = IdempotencyEngine()
        
        key = "test_key_123"
        result_id = "pi_123"
        
        engine.store_key(key, result_id)
        
        assert engine.check_key(key) == result_id
        assert engine.check_key("nonexistent") is None


# =============================================================================
# DEDUPLICATION TESTS
# =============================================================================

class TestDeduplicationLayer:
    """Test webhook deduplication."""
    
    def test_duplicate_detection(self):
        """Should detect duplicate events."""
        dedup = DeduplicationLayer()
        
        event_id = "evt_123"
        
        assert dedup.is_duplicate(event_id) == False
        dedup.mark_processed(event_id, "payment_intent", datetime.utcnow())
        assert dedup.is_duplicate(event_id) == True
    
    def test_watermark_tracking(self):
        """Should track watermarks per object type."""
        dedup = DeduplicationLayer()
        
        t1 = datetime.utcnow()
        t2 = t1 + timedelta(hours=1)
        
        dedup.mark_processed("evt_1", "payment_intent", t1)
        dedup.mark_processed("evt_2", "payment_intent", t2)
        
        watermark = dedup.get_watermark("payment_intent")
        assert watermark == t2
    
    def test_gap_detection(self):
        """Should detect gaps in event sequence."""
        dedup = DeduplicationLayer()
        
        # Process some events
        t1 = datetime.utcnow()
        dedup.mark_processed("evt_1", "payment_intent", t1)
        dedup.mark_processed("evt_3", "payment_intent", t1 + timedelta(hours=2))
        
        # Check for gaps
        events = [
            {"id": "evt_1", "created": int(t1.timestamp())},
            {"id": "evt_2", "created": int((t1 + timedelta(hours=1)).timestamp())},
            {"id": "evt_3", "created": int((t1 + timedelta(hours=2)).timestamp())},
        ]
        
        gaps = dedup.detect_gaps("payment_intent", events)
        assert "evt_2" in gaps


# =============================================================================
# LEDGER TESTS
# =============================================================================

class TestEvidenceLedger:
    """Test Evidence & Integrity Ledger."""
    
    def test_create_entry(self):
        """Should create ledger entry."""
        ledger = EvidenceLedger()
        
        entry = ledger.create_entry(
            stripe_id="pi_123",
            order_id="order_456",
            amount=5000,
            currency="usd",
            idempotency_key="key_789"
        )
        
        assert entry.stripe_id == "pi_123"
        assert entry.order_id == "order_456"
        assert entry.state == PaymentState.CREATED
    
    def test_state_update(self):
        """Should update entry state."""
        ledger = EvidenceLedger()
        
        ledger.create_entry(
            stripe_id="pi_123",
            order_id="order_456",
            amount=5000,
            currency="usd",
            idempotency_key="key_789"
        )
        
        entry = ledger.update_state("pi_123", PaymentState.SUCCEEDED, "evt_1")
        
        assert entry.state == PaymentState.SUCCEEDED
        assert "evt_1" in entry.events
    
    def test_succeeded_is_monotonic(self):
        """SUCCEEDED state should be monotonic (can't go back)."""
        ledger = EvidenceLedger()
        
        ledger.create_entry(
            stripe_id="pi_123",
            order_id="order_456",
            amount=5000,
            currency="usd",
            idempotency_key="key_789"
        )
        
        ledger.update_state("pi_123", PaymentState.SUCCEEDED, "evt_1")
        entry = ledger.update_state("pi_123", PaymentState.FAILED, "evt_2")
        
        # Should still be SUCCEEDED
        assert entry.state == PaymentState.SUCCEEDED
    
    def test_is_paid(self):
        """Should correctly report paid status."""
        ledger = EvidenceLedger()
        
        ledger.create_entry(
            stripe_id="pi_123",
            order_id="order_456",
            amount=5000,
            currency="usd",
            idempotency_key="key_789"
        )
        
        assert ledger.is_paid("order_456") == False
        
        ledger.update_state("pi_123", PaymentState.SUCCEEDED, "evt_1")
        
        assert ledger.is_paid("order_456") == True


# =============================================================================
# CLINIC PROFILE TESTS
# =============================================================================

class TestClinicPaymentProfile:
    """Test clinic-specific payment profile."""
    
    def test_patient_ref_hashing(self):
        """Should hash patient reference correctly."""
        ref1 = ClinicPaymentProfile.hash_patient_ref("patient_123", "practice_key")
        ref2 = ClinicPaymentProfile.hash_patient_ref("patient_123", "practice_key")
        ref3 = ClinicPaymentProfile.hash_patient_ref("patient_456", "practice_key")
        
        assert ref1 == ref2  # Same input = same output
        assert ref1 != ref3  # Different patient = different output
        assert len(ref1) == 16  # Correct length
    
    def test_phi_detection(self):
        """Should detect potential PHI in metadata."""
        valid, errors = ClinicPaymentProfile.validate_metadata(
            {"appointment_id": "apt_1", "patient_ssn": "123-45-6789"},
            ClinicPaymentProfile.MINIMAL_PROFILE["metadata_template"]
        )
        
        assert valid == False
        assert any("PHI" in e for e in errors)
    
    def test_safe_metadata_creation(self):
        """Should create PHI-safe metadata."""
        metadata = ClinicPaymentProfile.create_safe_metadata(
            appointment_id="apt_123",
            service_date="2024-01-15",
            patient_id="patient_456",
            practice_key="secret_key"
        )
        
        assert "appointment_id" in metadata
        assert "patient_ref" in metadata
        assert "patient_id" not in metadata  # Raw ID should not be present
        assert len(metadata["patient_ref"]) == 16


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestEchoStripeWrapper:
    """Integration tests for the complete wrapper."""
    
    @pytest.mark.asyncio
    async def test_create_payment_idempotent(self):
        """Creating same payment twice should return same entry."""
        wrapper = EchoStripeWrapper()
        
        # Mock the Stripe client
        with patch.object(wrapper.client, 'create_payment_intent') as mock:
            mock.return_value = {"id": "pi_test_123"}
            
            entry1 = await wrapper.create_payment(
                order_id="order_1",
                amount=5000,
                currency="usd",
                customer_id="cus_1"
            )
            
            entry2 = await wrapper.create_payment(
                order_id="order_1",
                amount=5000,
                currency="usd",
                customer_id="cus_1"
            )
            
            # Should return same entry
            assert entry1.stripe_id == entry2.stripe_id
            
            # Stripe should only be called once
            assert mock.call_count == 1
    
    @pytest.mark.asyncio
    async def test_webhook_deduplication(self):
        """Processing same webhook twice should only apply once."""
        wrapper = EchoStripeWrapper()
        
        # Create a payment first
        wrapper.ledger.create_entry(
            stripe_id="pi_123",
            order_id="order_1",
            amount=5000,
            currency="usd",
            idempotency_key="key_1"
        )
        
        # Process webhook
        result1 = await wrapper.process_webhook(
            event_id="evt_1",
            event_type="payment_intent.succeeded",
            data={"object": {"id": "pi_123"}, "created": 1234567890}
        )
        
        result2 = await wrapper.process_webhook(
            event_id="evt_1",
            event_type="payment_intent.succeeded",
            data={"object": {"id": "pi_123"}, "created": 1234567890}
        )
        
        assert result1 == True  # First time processed
        assert result2 == False  # Duplicate


# =============================================================================
# METRICS TESTS
# =============================================================================

class TestMetricsEndpoint:
    """Test /metrics endpoint."""
    
    def test_metrics_returns_prometheus_format(self):
        """Metrics should return Prometheus-compatible format."""
        response = client.get("/metrics")
        assert response.status_code == 200
        text = response.text
        assert "echo_throttle_pct" in text
        assert "echo_error_rate" in text
        assert "echo_phi_static" in text
        assert "echo_phi_dynamic" in text
        assert "echo_temperature" in text


# =============================================================================
# REVIVE TESTS
# =============================================================================

class TestReviveEndpoint:
    """Test /revive endpoint."""
    
    def test_revive_deactivates_kill(self):
        """Revive should deactivate kill switch."""
        # First activate kill
        state_manager.kill_active = True
        
        # Then revive
        response = client.post("/revive?operator=test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "revived"
        assert state_manager.kill_active == False


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
