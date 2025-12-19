"""Tests for belief models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from echo_core.models import Belief, BeliefStatus, Evidence, VerificationTier


class TestEvidence:
    """Test Evidence model."""

    def test_evidence_creation(self):
        """Test creating evidence."""
        evidence = Evidence(
            description="Test observation",
            source="Test source",
            supports=True,
        )

        assert evidence.description == "Test observation"
        assert evidence.source == "Test source"
        assert evidence.supports is True
        assert evidence.evidence_id is not None
        assert evidence.added_at is not None

    def test_evidence_requires_description(self):
        """Test that evidence requires description."""
        with pytest.raises(ValidationError):
            Evidence(
                description="",
                source="Test source",
                supports=True,
            )

    def test_evidence_requires_source(self):
        """Test that evidence requires source."""
        with pytest.raises(ValidationError):
            Evidence(
                description="Test observation",
                source="",
                supports=True,
            )


class TestBelief:
    """Test Belief model."""

    def test_belief_creation(self):
        """Test creating a belief."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification criteria",
        )

        assert belief.statement == "Test statement"
        assert belief.falsification == "Test falsification criteria"
        assert belief.tier == VerificationTier.HYPOTHESIS
        assert belief.confidence == 0.5
        assert belief.status == BeliefStatus.ACTIVE
        assert belief.belief_id is not None

    def test_belief_requires_statement(self):
        """Test that belief requires statement."""
        with pytest.raises(ValidationError):
            Belief(
                statement="",
                falsification="Test falsification",
            )

    def test_belief_requires_falsification(self):
        """Test that belief requires falsification."""
        with pytest.raises(ValidationError):
            Belief(
                statement="Test statement",
                falsification="",
            )

    def test_belief_rejects_vague_falsification(self):
        """Test that vague falsification is rejected."""
        vague_criteria = [
            "If I'm wrong",
            "If it doesn't work",
            "If evidence shows otherwise",
            "If proven wrong",
        ]

        for criteria in vague_criteria:
            with pytest.raises(ValidationError, match="too vague"):
                Belief(
                    statement="Test statement",
                    falsification=criteria,
                )

    def test_belief_accepts_specific_falsification(self):
        """Test that specific falsification is accepted."""
        belief = Belief(
            statement="Conversion rate is >5%",
            falsification="If conversion rate <3% after 1000 visitors, belief is false",
        )

        assert belief.falsification is not None

    def test_belief_confidence_validation(self):
        """Test that confidence is validated."""
        # Valid confidence
        belief = Belief(
            statement="Test",
            falsification="Test criteria",
            confidence=0.7,
        )
        assert belief.confidence == 0.7

        # Invalid confidence (too low)
        with pytest.raises(ValidationError):
            Belief(
                statement="Test",
                falsification="Test criteria",
                confidence=-0.1,
            )

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            Belief(
                statement="Test",
                falsification="Test criteria",
                confidence=1.1,
            )

    def test_add_evidence(self):
        """Test adding evidence to belief."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        evidence = belief.add_evidence(
            description="Test observation",
            source="Test source",
            supports=True,
        )

        assert len(belief.evidence) == 1
        assert belief.evidence[0] == evidence
        assert evidence.description == "Test observation"

    def test_mark_decision_made(self):
        """Test marking decision made."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        assert belief.decision_at is None

        belief.mark_decision_made()

        assert belief.decision_at is not None

    def test_is_retroactive(self):
        """Test retroactive belief detection."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        # No decision yet
        assert not belief.is_retroactive()

        # Decision made immediately
        belief.mark_decision_made()
        assert not belief.is_retroactive(threshold_seconds=300)

        # Simulate retroactive decision (manually set old created_at)
        belief.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        belief.decision_at = datetime(2020, 1, 1, 0, 10, 0, tzinfo=timezone.utc)
        
        assert belief.is_retroactive(threshold_seconds=300)

    def test_falsify(self):
        """Test falsifying a belief."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        assert belief.status == BeliefStatus.ACTIVE

        belief.falsify("Falsification criteria met")

        assert belief.status == BeliefStatus.FALSIFIED
        assert "Falsified" in belief.notes

    def test_deprecate(self):
        """Test deprecating a belief."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        belief.deprecate("No longer relevant")

        assert belief.status == BeliefStatus.DEPRECATED
        assert "Deprecated" in belief.notes

    def test_supersede(self):
        """Test superseding a belief."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        belief.supersede("new-belief-id", "Better belief available")

        assert belief.status == BeliefStatus.SUPERSEDED
        assert "Superseded" in belief.notes
        assert "new-belief-id" in belief.notes

    def test_verification_tiers(self):
        """Test all verification tiers."""
        tiers = [
            VerificationTier.SPECULATION,
            VerificationTier.HYPOTHESIS,
            VerificationTier.EVIDENCE,
            VerificationTier.CONCLUSION,
            VerificationTier.TRUTH,
        ]

        for tier in tiers:
            belief = Belief(
                statement="Test statement",
                falsification="Test falsification",
                tier=tier,
            )
            assert belief.tier == tier

    def test_belief_statuses(self):
        """Test all belief statuses."""
        belief = Belief(
            statement="Test statement",
            falsification="Test falsification",
        )

        # Active by default
        assert belief.status == BeliefStatus.ACTIVE

        # Falsified
        belief.falsify("Test")
        assert belief.status == BeliefStatus.FALSIFIED

        # Deprecated
        belief.status = BeliefStatus.ACTIVE
        belief.deprecate("Test")
        assert belief.status == BeliefStatus.DEPRECATED

        # Superseded
        belief.status = BeliefStatus.ACTIVE
        belief.supersede("new-id", "Test")
        assert belief.status == BeliefStatus.SUPERSEDED
