"""
Test Suite for Echo Stripe Wrapper v2.0

Tests:
- State machine transitions and monotonicity
- Idempotency engine and canonicalization
- Deduplication layer
- Evidence ledger invariants (E1, E2, E3)
- Optimistic locking
- Governance gates
- Reconciliation job
- End-to-end payment flow

Run: python -m pytest tests/test_wrapper_v2.py -v
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/echo-production/src')

from stripe_wrapper_v2 import (
    WrapperConfig,
    PaymentState,
    LedgerEntry,
    IdempotencyEngine,
    DeduplicationLayer,
    EvidenceLedger,
    OptimisticLockingWrapper,
    GovernanceGates,
    ReconciliationJob,
    EchoStripeWrapperV2,
    ClinicPaymentProfile,
    MonotonicityViolation,
    InvalidTransition,
    DuplicatePaymentError,
    EvidenceRequiredError,
    OptimisticLockFailure,
    GovernanceBlockedError,
    is_valid_transition,
    is_final_state,
    VALID_TRANSITIONS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def config():
    return WrapperConfig(
        amount_threshold_cents=100000,
        refund_threshold_cents=50000,
        max_lock_retries=3
    )


@pytest.fixture
def idempotency_engine():
    return IdempotencyEngine()


@pytest.fixture
def dedupe_layer():
    return DeduplicationLayer()


@pytest.fixture
def ledger():
    return EvidenceLedger()


@pytest.fixture
def governance(config):
    return GovernanceGates(config)


@pytest.fixture
def wrapper(config):
    return EchoStripeWrapperV2(config)


# =============================================================================
# STATE MACHINE TESTS
# =============================================================================

class TestStateMachine:
    """Test state machine transitions and monotonicity."""
    
    def test_valid_transitions_from_initiated(self):
        """Test valid transitions from INITIATED state."""
        assert is_valid_transition(PaymentState.INITIATED, PaymentState.CREATED)
        assert is_valid_transition(PaymentState.INITIATED, PaymentState.FAILED)
        assert not is_valid_transition(PaymentState.INITIATED, PaymentState.SUCCEEDED)
    
    def test_valid_transitions_from_created(self):
        """Test valid transitions from CREATED state."""
        assert is_valid_transition(PaymentState.CREATED, PaymentState.REQUIRES_ACTION)
        assert is_valid_transition(PaymentState.CREATED, PaymentState.PROCESSING)
        assert is_valid_transition(PaymentState.CREATED, PaymentState.SUCCEEDED)
        assert is_valid_transition(PaymentState.CREATED, PaymentState.FAILED)
    
    def test_monotonicity_succeeded(self):
        """Test that SUCCEEDED can only go to RECONCILED."""
        assert is_valid_transition(PaymentState.SUCCEEDED, PaymentState.RECONCILED)
        assert not is_valid_transition(PaymentState.SUCCEEDED, PaymentState.FAILED)
        assert not is_valid_transition(PaymentState.SUCCEEDED, PaymentState.CREATED)
    
    def test_monotonicity_failed(self):
        """Test that FAILED can only go to RECONCILED."""
        assert is_valid_transition(PaymentState.FAILED, PaymentState.RECONCILED)
        assert not is_valid_transition(PaymentState.FAILED, PaymentState.SUCCEEDED)
        assert not is_valid_transition(PaymentState.FAILED, PaymentState.CREATED)
    
    def test_reconciled_is_terminal(self):
        """Test that RECONCILED is terminal state."""
        assert len(VALID_TRANSITIONS[PaymentState.RECONCILED]) == 0
    
    def test_is_final_state(self):
        """Test final state detection."""
        assert is_final_state(PaymentState.SUCCEEDED)
        assert is_final_state(PaymentState.FAILED)
        assert is_final_state(PaymentState.RECONCILED)
        assert not is_final_state(PaymentState.CREATED)
        assert not is_final_state(PaymentState.PROCESSING)


# =============================================================================
# IDEMPOTENCY ENGINE TESTS
# =============================================================================

class TestIdempotencyEngine:
    """Test idempotency key derivation and canonicalization."""
    
    def test_derive_key_deterministic(self, idempotency_engine):
        """Test that same params produce same key."""
        key1 = idempotency_engine.derive_key("order_123", 1000, "usd", "cus_abc")
        key2 = idempotency_engine.derive_key("order_123", 1000, "usd", "cus_abc")
        assert key1 == key2
    
    def test_derive_key_different_params(self, idempotency_engine):
        """Test that different params produce different keys."""
        key1 = idempotency_engine.derive_key("order_123", 1000, "usd", "cus_abc")
        key2 = idempotency_engine.derive_key("order_456", 1000, "usd", "cus_abc")
        assert key1 != key2
    
    def test_canonicalize_order_independence(self, idempotency_engine):
        """Test that param order doesn't affect canonical form."""
        params1 = {"a": "1", "b": "2", "c": "3"}
        params2 = {"c": "3", "a": "1", "b": "2"}
        
        canon1 = idempotency_engine.canonicalize(params1)
        canon2 = idempotency_engine.canonicalize(params2)
        
        assert canon1 == canon2
    
    def test_canonicalize_null_trimming(self, idempotency_engine):
        """Test that null values are trimmed."""
        params1 = {"a": "1", "b": None}
        params2 = {"a": "1"}
        
        canon1 = idempotency_engine.canonicalize(params1)
        canon2 = idempotency_engine.canonicalize(params2)
        
        assert canon1 == canon2
    
    def test_store_and_check_key(self, idempotency_engine):
        """Test key storage and retrieval."""
        key = "test_key_123"
        result_id = "pi_abc123"
        
        # Initially not found
        assert idempotency_engine.check_key(key) is None
        
        # Store key
        idempotency_engine.store_key(key, result_id)
        
        # Now found
        assert idempotency_engine.check_key(key) == result_id


# =============================================================================
# DEDUPLICATION LAYER TESTS
# =============================================================================

class TestDeduplicationLayer:
    """Test webhook deduplication."""
    
    def test_is_duplicate_new_event(self, dedupe_layer):
        """Test that new events are not duplicates."""
        assert not dedupe_layer.is_duplicate("evt_new_123")
    
    def test_is_duplicate_processed_event(self, dedupe_layer):
        """Test that processed events are duplicates."""
        event_id = "evt_test_123"
        dedupe_layer.mark_processed(event_id, "payment_intent.succeeded", datetime.utcnow())
        
        assert dedupe_layer.is_duplicate(event_id)
    
    def test_watermark_update(self, dedupe_layer):
        """Test watermark tracking."""
        t1 = datetime.utcnow()
        t2 = t1 + timedelta(hours=1)
        
        dedupe_layer.mark_processed("evt_1", "payment_intent.succeeded", t1)
        assert dedupe_layer.get_watermark("payment_intent") == t1
        
        dedupe_layer.mark_processed("evt_2", "payment_intent.succeeded", t2)
        assert dedupe_layer.get_watermark("payment_intent") == t2
    
    def test_watermark_no_regression(self, dedupe_layer):
        """Test that watermark doesn't regress."""
        t1 = datetime.utcnow()
        t2 = t1 - timedelta(hours=1)  # Earlier time
        
        dedupe_layer.mark_processed("evt_1", "payment_intent.succeeded", t1)
        dedupe_layer.mark_processed("evt_2", "payment_intent.succeeded", t2)
        
        # Watermark should still be t1
        assert dedupe_layer.get_watermark("payment_intent") == t1


# =============================================================================
# EVIDENCE LEDGER TESTS
# =============================================================================

class TestEvidenceLedger:
    """Test evidence ledger and invariants."""
    
    def test_create_entry(self, ledger):
        """Test basic entry creation."""
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        assert entry.order_id == "order_123"
        assert entry.stripe_id == "pi_abc"
        assert entry.state == PaymentState.CREATED
    
    def test_e1_no_duplicate_payments(self, ledger):
        """Test E1: No duplicate payments invariant."""
        # Create first entry
        entry1 = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        # Mark as succeeded
        ledger.update_state("pi_abc", PaymentState.SUCCEEDED, "evt_success")
        
        # Attempt to create another payment for same order
        with pytest.raises(DuplicatePaymentError):
            ledger.create_entry(
                order_id="order_123",
                stripe_id="pi_def",
                amount=1000,
                currency="usd",
                idempotency_key="key_456"
            )
    
    def test_e2_evidence_required(self, ledger):
        """Test E2: No final state without evidence."""
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        # Attempt to mark succeeded without evidence
        with pytest.raises(EvidenceRequiredError):
            ledger.update_state("pi_abc", PaymentState.SUCCEEDED, "")
    
    def test_monotonicity_violation(self, ledger):
        """Test monotonicity enforcement."""
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        # Mark as succeeded
        ledger.update_state("pi_abc", PaymentState.SUCCEEDED, "evt_success")
        
        # Attempt to mark as failed
        with pytest.raises(MonotonicityViolation):
            ledger.update_state("pi_abc", PaymentState.FAILED, "evt_fail")
    
    def test_invalid_transition(self, ledger):
        """Test invalid transition rejection."""
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        # Attempt invalid transition: CREATED -> RECONCILED
        with pytest.raises(InvalidTransition):
            ledger.update_state("pi_abc", PaymentState.RECONCILED, "evt_recon")
    
    def test_is_paid(self, ledger):
        """Test is_paid helper."""
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        assert not ledger.is_paid("order_123")
        
        ledger.update_state("pi_abc", PaymentState.SUCCEEDED, "evt_success")
        
        assert ledger.is_paid("order_123")


# =============================================================================
# GOVERNANCE GATES TESTS
# =============================================================================

class TestGovernanceGates:
    """Test governance gates and PHI detection."""
    
    def test_amount_threshold(self, governance):
        """Test amount threshold check."""
        # Under threshold
        allowed, reason, action = governance.check_create_payment(
            amount=50000, currency="usd", metadata={}
        )
        assert allowed
        
        # Over threshold
        allowed, reason, action = governance.check_create_payment(
            amount=150000, currency="usd", metadata={}
        )
        assert not allowed
        assert reason == "amount_exceeds_threshold"
    
    def test_phi_detection_ssn(self, governance):
        """Test PHI detection for SSN."""
        allowed, reason, action = governance.check_create_payment(
            amount=1000,
            currency="usd",
            metadata={"patient_ssn": "123-45-6789"}
        )
        assert not allowed
        assert reason == "phi_detected_in_metadata"
    
    def test_phi_detection_patient_name(self, governance):
        """Test PHI detection for patient name."""
        allowed, reason, action = governance.check_create_payment(
            amount=1000,
            currency="usd",
            metadata={"patient_name": "John Doe"}
        )
        assert not allowed
        assert reason == "phi_detected_in_metadata"
    
    def test_phi_safe_metadata(self, governance):
        """Test that PHI-safe metadata passes."""
        allowed, reason, action = governance.check_create_payment(
            amount=1000,
            currency="usd",
            metadata={
                "appointment_id": "apt_123",
                "patient_ref": "abc123hash"
            }
        )
        assert allowed
    
    def test_refund_threshold(self, governance):
        """Test refund threshold check."""
        # Under threshold
        allowed, reason, action = governance.check_refund(
            amount=30000, original_amount=30000
        )
        assert allowed
        
        # Over threshold
        allowed, reason, action = governance.check_refund(
            amount=60000, original_amount=60000
        )
        assert not allowed
        assert reason == "full_refund_exceeds_threshold"
    
    def test_hash_patient_ref(self):
        """Test patient reference hashing."""
        ref1 = GovernanceGates.hash_patient_ref("patient_123", "practice_key")
        ref2 = GovernanceGates.hash_patient_ref("patient_123", "practice_key")
        ref3 = GovernanceGates.hash_patient_ref("patient_456", "practice_key")
        
        assert ref1 == ref2  # Same inputs -> same hash
        assert ref1 != ref3  # Different inputs -> different hash
        assert len(ref1) == 16  # Fixed length


# =============================================================================
# RECONCILIATION JOB TESTS
# =============================================================================

class TestReconciliationJob:
    """Test reconciliation job."""
    
    @pytest.mark.asyncio
    async def test_reconciliation_healthy(self, config):
        """Test reconciliation with no discrepancies."""
        ledger = EvidenceLedger()
        dedupe = DeduplicationLayer()
        recon = ReconciliationJob(ledger, dedupe, config)
        
        # Create entry and mark succeeded
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        ledger.update_state("pi_abc", PaymentState.SUCCEEDED, "evt_success")
        
        result = await recon.run()
        
        assert result.status == "healthy"
        assert len(result.discrepancies) == 0
    
    @pytest.mark.asyncio
    async def test_reconciliation_state_drift(self, config):
        """Test reconciliation detects state drift."""
        ledger = EvidenceLedger()
        dedupe = DeduplicationLayer()
        recon = ReconciliationJob(ledger, dedupe, config)
        
        # Create entry but don't update state
        entry = ledger.create_entry(
            order_id="order_123",
            stripe_id="pi_abc",
            amount=1000,
            currency="usd",
            idempotency_key="key_123"
        )
        
        # Mock Stripe returning succeeded status
        def mock_fetcher(hours):
            return [{
                "id": "pi_abc",
                "status": "succeeded",
                "amount": 1000,
                "currency": "usd"
            }]
        
        recon.set_stripe_fetcher(mock_fetcher)
        result = await recon.run()
        
        assert result.status == "needs_repair"
        assert len(result.discrepancies) > 0
        assert result.discrepancies[0]["type"] == "state_drift"


# =============================================================================
# WRAPPER INTEGRATION TESTS
# =============================================================================

class TestEchoStripeWrapperV2:
    """Test full wrapper integration."""
    
    @pytest.mark.asyncio
    async def test_create_payment(self, wrapper):
        """Test basic payment creation."""
        entry = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,
            currency="usd"
        )
        
        assert entry.order_id == "order_123"
        assert entry.amount == 5000
        assert entry.state == PaymentState.CREATED
    
    @pytest.mark.asyncio
    async def test_idempotent_payment(self, wrapper):
        """Test idempotent payment creation."""
        entry1 = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,
            currency="usd"
        )
        
        entry2 = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,
            currency="usd"
        )
        
        # Should return same entry
        assert entry1.stripe_id == entry2.stripe_id
    
    @pytest.mark.asyncio
    async def test_governance_blocks_high_amount(self, wrapper):
        """Test governance blocks high amount."""
        with pytest.raises(GovernanceBlockedError):
            await wrapper.create_payment(
                order_id="order_123",
                amount=150000,  # Over threshold
                currency="usd"
            )
    
    @pytest.mark.asyncio
    async def test_governance_blocks_phi(self, wrapper):
        """Test governance blocks PHI in metadata."""
        with pytest.raises(GovernanceBlockedError):
            await wrapper.create_payment(
                order_id="order_123",
                amount=5000,
                currency="usd",
                metadata={"patient_name": "John Doe"}
            )
    
    @pytest.mark.asyncio
    async def test_process_webhook(self, wrapper):
        """Test webhook processing."""
        # Create payment first
        entry = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,
            currency="usd"
        )
        
        # Process webhook
        processed = await wrapper.process_webhook(
            event_id="evt_test_123",
            event_type="payment_intent.succeeded",
            data={
                "object": {"id": entry.stripe_id},
                "created": int(datetime.utcnow().timestamp())
            }
        )
        
        assert processed
        
        # Check state updated
        updated_entry = wrapper.ledger.get_entry(entry.stripe_id)
        assert updated_entry.state == PaymentState.SUCCEEDED
    
    @pytest.mark.asyncio
    async def test_duplicate_webhook_rejected(self, wrapper):
        """Test duplicate webhook is rejected."""
        entry = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,
            currency="usd"
        )
        
        # First webhook
        processed1 = await wrapper.process_webhook(
            event_id="evt_test_123",
            event_type="payment_intent.succeeded",
            data={
                "object": {"id": entry.stripe_id},
                "created": int(datetime.utcnow().timestamp())
            }
        )
        
        # Duplicate webhook
        processed2 = await wrapper.process_webhook(
            event_id="evt_test_123",
            event_type="payment_intent.succeeded",
            data={
                "object": {"id": entry.stripe_id},
                "created": int(datetime.utcnow().timestamp())
            }
        )
        
        assert processed1 == True
        assert processed2 == False  # Duplicate rejected
    
    @pytest.mark.asyncio
    async def test_get_payment_status(self, wrapper):
        """Test payment status retrieval."""
        entry = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,
            currency="usd"
        )
        
        status = wrapper.get_payment_status("order_123")
        
        assert status["order_id"] == "order_123"
        assert status["amount"] == 5000
        assert status["is_paid"] == False
        
        # Mark as succeeded
        await wrapper.process_webhook(
            event_id="evt_success",
            event_type="payment_intent.succeeded",
            data={
                "object": {"id": entry.stripe_id},
                "created": int(datetime.utcnow().timestamp())
            }
        )
        
        status = wrapper.get_payment_status("order_123")
        assert status["is_paid"] == True


# =============================================================================
# CLINIC PAYMENT PROFILE TESTS
# =============================================================================

class TestClinicPaymentProfile:
    """Test clinic-specific payment profile."""
    
    def test_hash_patient_ref(self):
        """Test patient reference hashing."""
        ref = ClinicPaymentProfile.hash_patient_ref("patient_123", "practice_key")
        assert len(ref) == 16
        assert ref.isalnum()
    
    def test_validate_metadata_valid(self):
        """Test valid metadata validation."""
        metadata = {
            "appointment_id": "apt_123",
            "service_date": "2026-01-14",
            "patient_ref": "abc123hash"
        }
        
        valid, errors = ClinicPaymentProfile.validate_metadata(
            metadata, ClinicPaymentProfile.MINIMAL_PROFILE["metadata_template"]
        )
        
        assert valid
        assert len(errors) == 0
    
    def test_validate_metadata_missing_field(self):
        """Test metadata validation with missing field."""
        metadata = {
            "appointment_id": "apt_123"
            # Missing service_date and patient_ref
        }
        
        valid, errors = ClinicPaymentProfile.validate_metadata(
            metadata, ClinicPaymentProfile.MINIMAL_PROFILE["metadata_template"]
        )
        
        assert not valid
        assert len(errors) > 0
    
    def test_create_safe_metadata(self):
        """Test safe metadata creation."""
        metadata = ClinicPaymentProfile.create_safe_metadata(
            appointment_id="apt_123",
            service_date="2026-01-14",
            patient_id="patient_456",
            practice_key="practice_key"
        )
        
        assert "appointment_id" in metadata
        assert "service_date" in metadata
        assert "patient_ref" in metadata
        assert "patient_id" not in metadata  # Raw ID not included
        assert len(metadata["patient_ref"]) == 16


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
