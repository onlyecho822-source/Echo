"""Tests for storage layer."""

import tempfile
from pathlib import Path

import pytest

from echo_core.models import BeliefStatus
from echo_core.storage import BeliefStorage


class TestBeliefStorage:
    """Test BeliefStorage functionality."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_ledger.jsonl"
            yield BeliefStorage(ledger_path)

    def test_create_belief(self, temp_storage):
        """Test creating a belief."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification criteria",
            tier="hypothesis",
            confidence=0.7,
            created_by="test@example.com",
        )

        assert belief.statement == "Test statement"
        assert belief.falsification == "Test falsification criteria"
        assert belief.tier == "hypothesis"
        assert belief.confidence == 0.7
        assert belief.created_by == "test@example.com"

    def test_create_belief_logs_to_ledger(self, temp_storage):
        """Test that creating belief logs to ledger."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        # Check ledger has entry
        entries = temp_storage.ledger.get_entries_by_type("belief_created")
        assert len(entries) == 1
        assert entries[0].data["belief_id"] == belief.belief_id

    def test_founder_action_logged(self, temp_storage):
        """Test that founder actions are logged."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
            created_by="nathan.odom@echo.universe",
        )

        # Check founder action logged
        founder_actions = temp_storage.audit_founder_actions()
        assert len(founder_actions) == 1
        assert founder_actions[0]["founder_email"] == "nathan.odom@echo.universe"

    def test_add_evidence(self, temp_storage):
        """Test adding evidence to belief."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        evidence = temp_storage.add_evidence(
            belief_id=belief.belief_id,
            description="Test observation",
            source="Test source",
            supports=True,
        )

        assert evidence.description == "Test observation"
        assert evidence.source == "Test source"

    def test_add_evidence_logs_to_ledger(self, temp_storage):
        """Test that adding evidence logs to ledger."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        temp_storage.add_evidence(
            belief_id=belief.belief_id,
            description="Test observation",
            source="Test source",
            supports=True,
        )

        # Check ledger has entry
        entries = temp_storage.ledger.get_entries_by_type("evidence_added")
        assert len(entries) == 1
        assert entries[0].data["belief_id"] == belief.belief_id

    def test_mark_decision(self, temp_storage):
        """Test marking decision made."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        temp_storage.mark_decision(
            belief_id=belief.belief_id,
            decision_description="Test decision",
            decided_by="test@example.com",
        )

        # Check ledger has entry
        entries = temp_storage.ledger.get_entries_by_type("decision_made")
        assert len(entries) == 1
        assert entries[0].data["belief_id"] == belief.belief_id

    def test_falsify_belief(self, temp_storage):
        """Test falsifying a belief."""
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        temp_storage.falsify_belief(
            belief_id=belief.belief_id,
            reason="Falsification criteria met",
            falsified_by="test@example.com",
        )

        # Check ledger has entry
        entries = temp_storage.ledger.get_entries_by_type("belief_falsified")
        assert len(entries) == 1
        assert entries[0].data["belief_id"] == belief.belief_id

    def test_get_belief(self, temp_storage):
        """Test retrieving a belief."""
        created_belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        retrieved_belief = temp_storage.get_belief(created_belief.belief_id)

        assert retrieved_belief is not None
        assert retrieved_belief.belief_id == created_belief.belief_id
        assert retrieved_belief.statement == created_belief.statement

    def test_get_nonexistent_belief(self, temp_storage):
        """Test retrieving nonexistent belief returns None."""
        belief = temp_storage.get_belief("nonexistent-id")
        assert belief is None

    def test_list_beliefs(self, temp_storage):
        """Test listing all beliefs."""
        temp_storage.create_belief(
            statement="Belief 1",
            falsification="Falsification 1",
        )
        temp_storage.create_belief(
            statement="Belief 2",
            falsification="Falsification 2",
        )

        beliefs = temp_storage.list_beliefs()
        assert len(beliefs) == 2

    def test_list_beliefs_by_status(self, temp_storage):
        """Test filtering beliefs by status."""
        belief1 = temp_storage.create_belief(
            statement="Belief 1",
            falsification="Falsification 1",
        )
        belief2 = temp_storage.create_belief(
            statement="Belief 2",
            falsification="Falsification 2",
        )

        # Falsify one belief
        temp_storage.falsify_belief(
            belief_id=belief1.belief_id,
            reason="Test",
        )

        # List active beliefs
        active_beliefs = temp_storage.list_beliefs(status=BeliefStatus.ACTIVE)
        assert len(active_beliefs) == 1
        assert active_beliefs[0].belief_id == belief2.belief_id

        # List falsified beliefs
        falsified_beliefs = temp_storage.list_beliefs(status=BeliefStatus.FALSIFIED)
        assert len(falsified_beliefs) == 1
        assert falsified_beliefs[0].belief_id == belief1.belief_id

    def test_list_beliefs_by_creator(self, temp_storage):
        """Test filtering beliefs by creator."""
        temp_storage.create_belief(
            statement="Belief 1",
            falsification="Falsification 1",
            created_by="user1@example.com",
        )
        temp_storage.create_belief(
            statement="Belief 2",
            falsification="Falsification 2",
            created_by="user2@example.com",
        )

        user1_beliefs = temp_storage.list_beliefs(created_by="user1@example.com")
        assert len(user1_beliefs) == 1
        assert user1_beliefs[0].created_by == "user1@example.com"

    def test_detect_shadow_decisions(self, temp_storage):
        """Test detecting shadow decisions."""
        from datetime import datetime, timezone, timedelta
        
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        # Simulate retroactive decision by manually creating ledger entry
        # with old created_at timestamp
        old_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Create a decision entry that appears retroactive
        temp_storage.ledger.append(
            entry_type="decision_made",
            data={
                "belief_id": belief.belief_id,
                "decision_description": "Test retroactive decision",
                "decided_by": "test@example.com",
                "decision_at": datetime.now(timezone.utc).isoformat(),
                "is_retroactive": True,
                "warning": "RETROACTIVE JUSTIFICATION DETECTED",
            },
        )

        # Should detect shadow decision
        shadow_decisions = temp_storage.detect_shadow_decisions()
        assert len(shadow_decisions) == 1
        assert shadow_decisions[0]["belief_id"] == belief.belief_id

    def test_verify_integrity(self, temp_storage):
        """Test verifying storage integrity."""
        temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        assert temp_storage.verify_integrity()

    def test_audit_report(self, temp_storage):
        """Test generating audit report."""
        temp_storage.create_belief(
            statement="Belief 1",
            falsification="Falsification 1",
            created_by="nathan.odom@echo.universe",
        )
        belief2 = temp_storage.create_belief(
            statement="Belief 2",
            falsification="Falsification 2",
        )

        # Falsify one belief
        temp_storage.falsify_belief(
            belief_id=belief2.belief_id,
            reason="Test",
        )

        report = temp_storage.audit_report()

        assert report["beliefs"]["total"] == 2
        assert report["beliefs"]["active"] == 1
        assert report["beliefs"]["falsified"] == 1
        assert report["founder_actions"] == 1
        assert report["ledger"]["integrity_verified"] is True

    def test_belief_reconstruction_from_ledger(self, temp_storage):
        """Test that belief state is correctly reconstructed from ledger."""
        # Create belief
        belief = temp_storage.create_belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        # Add evidence
        temp_storage.add_evidence(
            belief_id=belief.belief_id,
            description="Evidence 1",
            source="Source 1",
            supports=True,
        )
        temp_storage.add_evidence(
            belief_id=belief.belief_id,
            description="Evidence 2",
            source="Source 2",
            supports=False,
        )

        # Retrieve belief
        retrieved = temp_storage.get_belief(belief.belief_id)

        assert retrieved is not None
        assert len(retrieved.evidence) == 2
        assert retrieved.evidence[0].description == "Evidence 1"
        assert retrieved.evidence[1].description == "Evidence 2"

    def test_is_founder(self, temp_storage):
        """Test founder detection."""
        assert temp_storage._is_founder("nathan.odom@echo.universe")
        assert temp_storage._is_founder("NATHAN.ODOM@ECHO.UNIVERSE")  # Case insensitive
        assert not temp_storage._is_founder("other@example.com")
