"""Storage layer connecting beliefs to immutable ledger.

This bridges the belief model (what) with the ledger (how).

Design principles:
- All belief operations append to ledger
- No direct mutation - only through ledger
- Founder constraints enforced here
- Shadow decision detection built-in
"""

from pathlib import Path
from typing import List, Optional

from .ledger import ImmutableLedger
from .models import Belief, BeliefStatus, Evidence


class BeliefStorage:
    """Storage layer for beliefs with immutable audit trail.

    All operations append to the ledger.
    Current state is reconstructed from ledger entries.
    """

    # Founder constraint: These emails have NO special privileges
    FOUNDER_EMAILS = [
        "nathan.odom@echo.universe",
        "nathan.odom@gmail.com",
        # Add more as needed
    ]

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        """Initialize storage with ledger.

        Args:
            ledger_path: Path to ledger file
        """
        self.ledger = ImmutableLedger(ledger_path)

    def create_belief(
        self,
        statement: str,
        falsification: str,
        tier: str = "hypothesis",
        confidence: float = 0.5,
        created_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> Belief:
        """Create a new belief.

        Args:
            statement: What you believe
            falsification: How you could be wrong (mandatory)
            tier: Verification Ladder tier
            confidence: How sure are you (0.0-1.0)
            created_by: Email of creator (no special privileges)
            tags: Optional tags for organization

        Returns:
            The created belief
        """
        # Create belief
        belief = Belief(
            statement=statement,
            falsification=falsification,
            tier=tier,
            confidence=confidence,
            created_by=created_by,
            tags=tags or [],
        )

        # Append to ledger
        self.ledger.append(
            entry_type="belief_created",
            data={
                "belief_id": belief.belief_id,
                "statement": belief.statement,
                "falsification": belief.falsification,
                "tier": belief.tier,
                "confidence": belief.confidence,
                "created_by": belief.created_by,
                "created_at": belief.created_at.isoformat(),
                "tags": belief.tags,
            },
        )

        # Log if founder created belief (for audit)
        if self._is_founder(created_by):
            self.ledger.append(
                entry_type="founder_action",
                data={
                    "action": "belief_created",
                    "belief_id": belief.belief_id,
                    "founder_email": created_by,
                    "note": "Founder has no special privileges - logged for transparency",
                },
            )

        return belief

    def add_evidence(
        self,
        belief_id: str,
        description: str,
        source: str,
        supports: bool,
        added_by: str = "",
    ) -> Evidence:
        """Add evidence to a belief.

        Args:
            belief_id: ID of belief
            description: What was observed
            source: Where did this come from
            supports: Does this support or refute the belief?
            added_by: Email of person adding evidence

        Returns:
            The created evidence
        """
        # Get current belief state
        belief = self.get_belief(belief_id)
        if belief is None:
            raise ValueError(f"Belief {belief_id} not found")

        # Add evidence
        evidence = belief.add_evidence(description, source, supports)

        # Append to ledger
        self.ledger.append(
            entry_type="evidence_added",
            data={
                "belief_id": belief_id,
                "evidence_id": evidence.evidence_id,
                "description": description,
                "source": source,
                "supports": supports,
                "added_by": added_by,
                "added_at": evidence.added_at.isoformat(),
            },
        )

        # Log if founder added evidence
        if self._is_founder(added_by):
            self.ledger.append(
                entry_type="founder_action",
                data={
                    "action": "evidence_added",
                    "belief_id": belief_id,
                    "evidence_id": evidence.evidence_id,
                    "founder_email": added_by,
                },
            )

        return evidence

    def mark_decision(
        self,
        belief_id: str,
        decision_description: str,
        decided_by: str = "",
    ) -> None:
        """Mark that a decision was made based on a belief.

        This is critical for shadow decision tracking.

        Args:
            belief_id: ID of belief
            decision_description: What decision was made
            decided_by: Email of person making decision
        """
        # Get current belief state
        belief = self.get_belief(belief_id)
        if belief is None:
            raise ValueError(f"Belief {belief_id} not found")

        # Mark decision
        belief.mark_decision_made()

        # Check if retroactive
        is_retroactive = belief.is_retroactive()

        # Append to ledger
        self.ledger.append(
            entry_type="decision_made",
            data={
                "belief_id": belief_id,
                "decision_description": decision_description,
                "decided_by": decided_by,
                "decision_at": belief.decision_at.isoformat() if belief.decision_at else None,
                "is_retroactive": is_retroactive,
                "warning": "RETROACTIVE JUSTIFICATION DETECTED" if is_retroactive else None,
            },
        )

        # Log if founder made decision
        if self._is_founder(decided_by):
            self.ledger.append(
                entry_type="founder_action",
                data={
                    "action": "decision_made",
                    "belief_id": belief_id,
                    "founder_email": decided_by,
                    "is_retroactive": is_retroactive,
                },
            )

    def falsify_belief(
        self,
        belief_id: str,
        reason: str,
        falsified_by: str = "",
    ) -> None:
        """Mark belief as falsified.

        Args:
            belief_id: ID of belief
            reason: Why falsification criteria were met
            falsified_by: Email of person marking as falsified
        """
        # Get current belief state
        belief = self.get_belief(belief_id)
        if belief is None:
            raise ValueError(f"Belief {belief_id} not found")

        # Falsify
        belief.falsify(reason)

        # Append to ledger
        self.ledger.append(
            entry_type="belief_falsified",
            data={
                "belief_id": belief_id,
                "reason": reason,
                "falsified_by": falsified_by,
                "falsified_at": belief.updated_at.isoformat(),
            },
        )

    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Reconstruct current state of a belief from ledger.

        Args:
            belief_id: ID of belief

        Returns:
            Current belief state, or None if not found
        """
        # Get all entries for this belief
        entries = self.ledger.get_entries_by_belief_id(belief_id)
        if not entries:
            return None

        # Reconstruct state from entries
        belief: Optional[Belief] = None

        for entry in entries:
            if entry.entry_type == "belief_created":
                belief = Belief(
                    belief_id=entry.data["belief_id"],
                    statement=entry.data["statement"],
                    falsification=entry.data["falsification"],
                    tier=entry.data["tier"],
                    confidence=entry.data["confidence"],
                    created_by=entry.data["created_by"],
                    tags=entry.data.get("tags", []),
                )

            elif entry.entry_type == "evidence_added" and belief:
                belief.add_evidence(
                    description=entry.data["description"],
                    source=entry.data["source"],
                    supports=entry.data["supports"],
                )

            elif entry.entry_type == "decision_made" and belief:
                belief.mark_decision_made()

            elif entry.entry_type == "belief_falsified" and belief:
                belief.falsify(entry.data["reason"])

        return belief

    def list_beliefs(
        self,
        status: Optional[BeliefStatus] = None,
        created_by: Optional[str] = None,
    ) -> List[Belief]:
        """List all beliefs, optionally filtered.

        Args:
            status: Filter by status
            created_by: Filter by creator

        Returns:
            List of beliefs
        """
        # Get all belief_created entries
        created_entries = self.ledger.get_entries_by_type("belief_created")

        # Reconstruct each belief
        beliefs = []
        for entry in created_entries:
            belief = self.get_belief(entry.data["belief_id"])
            if belief is None:
                continue

            # Apply filters
            if status and belief.status != status:
                continue
            if created_by and belief.created_by != created_by:
                continue

            beliefs.append(belief)

        return beliefs

    def audit_founder_actions(self) -> List[dict]:
        """Get all founder actions for audit.

        Returns:
            List of founder actions with timestamps
        """
        entries = self.ledger.get_entries_by_type("founder_action")
        return [
            {
                "timestamp": entry.timestamp,
                "action": entry.data["action"],
                "founder_email": entry.data["founder_email"],
                "details": entry.data,
            }
            for entry in entries
        ]

    def detect_shadow_decisions(self) -> List[dict]:
        """Detect potential shadow decisions (retroactive beliefs).

        Returns:
            List of suspicious decision patterns
        """
        decision_entries = self.ledger.get_entries_by_type("decision_made")
        shadow_decisions = []

        for entry in decision_entries:
            if entry.data.get("is_retroactive"):
                shadow_decisions.append({
                    "belief_id": entry.data["belief_id"],
                    "decision_description": entry.data["decision_description"],
                    "decided_by": entry.data["decided_by"],
                    "timestamp": entry.timestamp,
                    "warning": entry.data.get("warning"),
                })

        return shadow_decisions

    def _is_founder(self, email: str) -> bool:
        """Check if email belongs to founder.

        Args:
            email: Email to check

        Returns:
            True if founder email
        """
        return email.lower() in [e.lower() for e in self.FOUNDER_EMAILS]

    def verify_integrity(self) -> bool:
        """Verify ledger integrity.

        Returns:
            True if ledger is intact
        """
        return self.ledger.verify_integrity()

    def audit_report(self) -> dict:
        """Generate comprehensive audit report.

        Returns:
            Audit report with integrity, statistics, and warnings
        """
        return {
            "ledger": self.ledger.audit_report(),
            "beliefs": {
                "total": len(self.list_beliefs()),
                "active": len(self.list_beliefs(status=BeliefStatus.ACTIVE)),
                "falsified": len(self.list_beliefs(status=BeliefStatus.FALSIFIED)),
                "deprecated": len(self.list_beliefs(status=BeliefStatus.DEPRECATED)),
            },
            "founder_actions": len(self.audit_founder_actions()),
            "shadow_decisions": len(self.detect_shadow_decisions()),
        }
