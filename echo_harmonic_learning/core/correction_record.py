"""
CorrectionRecord - Append-only record of corrections

Every correction is a step in the harmonic learning dance.
We don't just fix errors; we tune them into rhythm.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Intervention:
    """Description of the corrective action taken."""
    type: str  # prompt_patch, retrieval_fix, tool_addition, policy_update
    diff: str  # Human-readable description of change
    hypothesis_tag: str = ""  # H# for tracking experiments


@dataclass
class EvalResults:
    """Before/after evaluation metrics."""
    pre_score: float
    post_score: float
    test_suite: str
    metrics: dict[str, float] = field(default_factory=dict)

    @property
    def improvement(self) -> float:
        """Calculate the improvement delta."""
        return self.post_score - self.pre_score

    @property
    def improved(self) -> bool:
        """Check if the correction improved performance."""
        return self.improvement > 0


@dataclass
class Rollout:
    """Configuration for gradual rollout of correction."""
    feature_flag: str
    ramp_stages: list[str]  # e.g., ["10%", "50%", "100%"]
    current_stage: int = 0

    @property
    def current_percentage(self) -> str:
        """Get current rollout percentage."""
        if self.current_stage < len(self.ramp_stages):
            return self.ramp_stages[self.current_stage]
        return "100%"

    def advance(self) -> bool:
        """Advance to next rollout stage. Returns True if advanced."""
        if self.current_stage < len(self.ramp_stages) - 1:
            self.current_stage += 1
            return True
        return False


@dataclass
class RegressionWatch:
    """Configuration for monitoring regressions after rollout."""
    window_days: int = 14
    abort_threshold: float = -0.05  # Rollback if delta < this
    metrics_to_watch: list[str] = field(default_factory=lambda: ["accuracy", "harmony_score"])

    def should_abort(self, current_delta: float) -> bool:
        """Check if regression requires rollback."""
        return current_delta < self.abort_threshold


@dataclass
class CorrectionRecord:
    """
    Append-only record of a correction applied to the system.

    This is where learning crystallizes into change - where the
    friction of error becomes the structure of knowledge.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    # Link to trigger
    event_id: str = ""  # Links to LearningEvent

    # The correction
    intervention: Intervention | None = None

    # Validation
    eval_results: EvalResults | None = None

    # Approvals (for safety/policy changes)
    approvals: list[str] = field(default_factory=list)

    # Deployment
    rollout: Rollout | None = None
    regression_watch: RegressionWatch | None = None

    # Status tracking
    status: str = "pending"  # pending, approved, deployed, rolled_back, completed

    @property
    def is_safe_to_deploy(self) -> bool:
        """Check if correction has passed all gates."""
        if not self.eval_results:
            return False
        if not self.eval_results.improved:
            return False
        return True

    @property
    def requires_approval(self) -> bool:
        """Check if correction requires human approval."""
        if self.intervention:
            return self.intervention.type in ["policy_update", "safety_fix"]
        return False

    def approve(self, approver: str) -> None:
        """Add approval to the record."""
        if approver not in self.approvals:
            self.approvals.append(approver)

    def is_fully_approved(self, required_approvers: int = 2) -> bool:
        """Check if all required approvals are present."""
        return len(self.approvals) >= required_approvers

    def can_amend(self, is_same_author: bool, is_pushed: bool) -> bool:
        """
        Check if this correction can be amended.

        Following the philosophy: ONLY amend when either
        (1) it's the original author OR (2) adding edits from pre-commit hook
        """
        if is_pushed:
            return False
        return is_same_author

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "intervention": {
                "type": self.intervention.type,
                "diff": self.intervention.diff,
                "hypothesis_tag": self.intervention.hypothesis_tag
            } if self.intervention else None,
            "eval_results": {
                "pre_score": self.eval_results.pre_score,
                "post_score": self.eval_results.post_score,
                "test_suite": self.eval_results.test_suite,
                "metrics": self.eval_results.metrics
            } if self.eval_results else None,
            "approvals": self.approvals,
            "rollout": {
                "feature_flag": self.rollout.feature_flag,
                "ramp_stages": self.rollout.ramp_stages,
                "current_stage": self.rollout.current_stage
            } if self.rollout else None,
            "regression_watch": {
                "window_days": self.regression_watch.window_days,
                "abort_threshold": self.regression_watch.abort_threshold,
                "metrics_to_watch": self.regression_watch.metrics_to_watch
            } if self.regression_watch else None,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CorrectionRecord':
        """Create CorrectionRecord from dictionary."""
        record = cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            event_id=data.get("event_id", ""),
            approvals=data.get("approvals", []),
            status=data.get("status", "pending")
        )

        if data.get("intervention"):
            record.intervention = Intervention(**data["intervention"])

        if data.get("eval_results"):
            record.eval_results = EvalResults(**data["eval_results"])

        if data.get("rollout"):
            record.rollout = Rollout(**data["rollout"])

        if data.get("regression_watch"):
            record.regression_watch = RegressionWatch(**data["regression_watch"])

        return record
