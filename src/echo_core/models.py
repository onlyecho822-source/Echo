"""Belief models with mandatory falsification and causality tracking.

This is Echo's decision hygiene system.

Design principles:
- Falsification is mandatory, not optional
- Causality matters (when was belief formed vs. when was decision made)
- Evidence must be external and verifiable
- Beliefs can be deprecated but never deleted
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class VerificationTier(str, Enum):
    """Verification Ladder tiers.

    From weakest to strongest:
    - SPECULATION: Unverified ideas
    - HYPOTHESIS: Testable claims with falsification criteria
    - EVIDENCE: Observations that support or refute
    - CONCLUSION: Beliefs derived from evidence
    - TRUTH: Conclusions that survived repeated testing
    """

    SPECULATION = "speculation"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    CONCLUSION = "conclusion"
    TRUTH = "truth"


class BeliefStatus(str, Enum):
    """Belief lifecycle status."""

    ACTIVE = "active"  # Currently held
    FALSIFIED = "falsified"  # Falsification criteria met
    DEPRECATED = "deprecated"  # No longer relevant
    SUPERSEDED = "superseded"  # Replaced by better belief


class Evidence(BaseModel):
    """Evidence supporting or refuting a belief."""

    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)  # Where did this come from?
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    supports: bool  # True if supports belief, False if refutes


class Belief(BaseModel):
    """A belief with mandatory falsification criteria.

    This is the core unit of Echo's memory prosthetic.

    Required fields:
    - statement: What you believe
    - falsification: How you could be wrong (mandatory)
    - tier: Where on the Verification Ladder

    Optional fields:
    - confidence: How sure are you (0.0-1.0)
    - evidence: Supporting or refuting observations
    - tags: For organization
    """

    belief_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = Field(min_length=1)
    falsification: str = Field(min_length=1)  # Mandatory - how could you be wrong?
    tier: VerificationTier = VerificationTier.HYPOTHESIS
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: BeliefStatus = BeliefStatus.ACTIVE

    # Causality tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decision_at: Optional[datetime] = None  # When was decision made based on this?

    # Evidence and metadata
    evidence: List[Evidence] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    notes: str = ""

    # Founder constraint enforcement
    created_by: str = ""  # Email address - no special privileges

    @field_validator("falsification")
    @classmethod
    def falsification_must_be_specific(cls, v: str) -> str:
        """Validate that falsification criteria is specific enough.

        Rejects vague criteria like:
        - "If I'm wrong"
        - "If it doesn't work"
        - "If evidence shows otherwise"

        Requires specific, testable criteria.
        """
        vague_patterns = [
            "if i'm wrong",
            "if it doesn't work",
            "if evidence shows",
            "if proven wrong",
            "if incorrect",
        ]

        v_lower = v.lower()
        for pattern in vague_patterns:
            if pattern in v_lower and len(v) < 50:
                raise ValueError(
                    f"Falsification criteria too vague: '{v}'. "
                    "Specify concrete, measurable conditions."
                )

        return v

    def add_evidence(
        self,
        description: str,
        source: str,
        supports: bool,
    ) -> Evidence:
        """Add evidence to belief.

        Args:
            description: What was observed
            source: Where did this come from
            supports: Does this support or refute the belief?

        Returns:
            The created evidence
        """
        evidence = Evidence(
            description=description,
            source=source,
            supports=supports,
        )
        self.evidence.append(evidence)
        self.updated_at = datetime.now(timezone.utc)
        return evidence

    def mark_decision_made(self) -> None:
        """Mark that a decision was made based on this belief.

        This is critical for shadow decision tracking.
        If decision_at is set AFTER created_at by more than a threshold,
        it indicates retroactive justification.
        """
        self.decision_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def is_retroactive(self, threshold_seconds: int = 300) -> bool:
        """Check if belief was created retroactively (after decision).

        Args:
            threshold_seconds: Grace period for recording (default 5 minutes)

        Returns:
            True if belief appears to be retroactive justification
        """
        if self.decision_at is None:
            return False

        # If decision was marked more than threshold after creation,
        # it's suspicious (but not necessarily wrong - could be legitimate delay)
        delta = (self.decision_at - self.created_at).total_seconds()
        return delta > threshold_seconds

    def falsify(self, reason: str) -> None:
        """Mark belief as falsified.

        Args:
            reason: Why falsification criteria were met
        """
        self.status = BeliefStatus.FALSIFIED
        self.notes += f"\n\nFalsified: {reason}"
        self.updated_at = datetime.now(timezone.utc)

    def deprecate(self, reason: str) -> None:
        """Mark belief as deprecated (no longer relevant).

        Args:
            reason: Why belief is no longer relevant
        """
        self.status = BeliefStatus.DEPRECATED
        self.notes += f"\n\nDeprecated: {reason}"
        self.updated_at = datetime.now(timezone.utc)

    def supersede(self, new_belief_id: str, reason: str) -> None:
        """Mark belief as superseded by a better belief.

        Args:
            new_belief_id: ID of belief that replaces this one
            reason: Why new belief is better
        """
        self.status = BeliefStatus.SUPERSEDED
        self.notes += f"\n\nSuperseded by {new_belief_id}: {reason}"
        self.updated_at = datetime.now(timezone.utc)
