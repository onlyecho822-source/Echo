"""
LearningEvent - Immutable record of error-driven learning

Every mismatch between Echo's prediction and reality is a first-class artifact.
That artifact fuels updates to models, prompts, policies, and UX.
No error → no learning.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Uncertainty:
    """Uncertainty metrics for a prediction."""
    aleatoric: float  # Irreducible uncertainty (data noise)
    epistemic: float  # Model uncertainty (lack of knowledge)

    def total(self) -> float:
        """Combined uncertainty score."""
        return min(1.0, self.aleatoric + self.epistemic)

    def confidence(self) -> float:
        """Inverse of uncertainty - how confident the model is."""
        return 1.0 - self.total()


@dataclass
class Comparison:
    """Result of comparing prediction to ground truth."""
    delta_score: float  # Error magnitude [0, 1]
    classes: list[str]  # Error taxonomy classes
    severity: str = "S2"  # Default to material

    def is_critical(self) -> bool:
        """Check if error requires immediate attention."""
        return self.severity in ["S0", "S1"]


@dataclass
class Trace:
    """Execution trace for provenance."""
    tools: list[str]
    rationale: str
    model_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningEvent:
    """
    Immutable record of a learning opportunity.

    Each LearningEvent represents the friction between what Echo thought
    and what reality revealed. This friction is the heat that forges understanding.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    # Context
    tenant: str = ""
    task: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    # Input/Output
    input_data: Any = None
    input_fingerprint: str = ""
    prediction: dict[str, Any] = field(default_factory=dict)
    ground_truth: dict[str, Any] = field(default_factory=dict)

    # Analysis
    comparison: Comparison | None = None
    uncertainty: Uncertainty | None = None
    trace: Trace | None = None

    # Routing
    owner_queue: str = ""
    signatures: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Generate fingerprints and signatures after initialization."""
        if self.input_data and not self.input_fingerprint:
            self.input_fingerprint = self._hash_data(self.input_data)

        # Sign the event
        self.signatures["system"] = self._generate_signature()

    def _hash_data(self, data: Any) -> str:
        """Generate SHA-256 hash of data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(serialized.encode()).hexdigest()}"

    def _generate_signature(self) -> str:
        """Generate signature for the event."""
        content = {
            "id": self.id,
            "timestamp": self.timestamp,
            "input_fingerprint": self.input_fingerprint,
            "prediction": self.prediction,
            "ground_truth": self.ground_truth
        }
        return self._hash_data(content)

    @property
    def error_score(self) -> float:
        """Get the error magnitude."""
        if self.comparison:
            return self.comparison.delta_score
        return 0.0

    @property
    def error_classes(self) -> list[str]:
        """Get the error classification."""
        if self.comparison:
            return self.comparison.classes
        return []

    def requires_intervention(self, threshold: float = 0.3) -> bool:
        """
        Determine if this error requires intervention.

        The anomaly is the signal - errors above threshold
        trigger the learning loop.
        """
        if self.comparison and self.comparison.is_critical():
            return True
        return self.error_score > threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "tenant": self.tenant,
            "task": self.task,
            "context": self.context,
            "input_fingerprint": self.input_fingerprint,
            "prediction": self.prediction,
            "ground_truth": self.ground_truth,
            "comparison": {
                "delta_score": self.comparison.delta_score,
                "classes": self.comparison.classes,
                "severity": self.comparison.severity
            } if self.comparison else None,
            "uncertainty": {
                "aleatoric": self.uncertainty.aleatoric,
                "epistemic": self.uncertainty.epistemic
            } if self.uncertainty else None,
            "trace": {
                "tools": self.trace.tools,
                "rationale": self.trace.rationale,
                "model_config": self.trace.model_config
            } if self.trace else None,
            "owner_queue": self.owner_queue,
            "signatures": self.signatures
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LearningEvent':
        """Create LearningEvent from dictionary."""
        event = cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            tenant=data.get("tenant", ""),
            task=data.get("task", ""),
            context=data.get("context", {}),
            input_fingerprint=data.get("input_fingerprint", ""),
            prediction=data.get("prediction", {}),
            ground_truth=data.get("ground_truth", {}),
            owner_queue=data.get("owner_queue", ""),
            signatures=data.get("signatures", {})
        )

        if data.get("comparison"):
            event.comparison = Comparison(**data["comparison"])

        if data.get("uncertainty"):
            event.uncertainty = Uncertainty(**data["uncertainty"])

        if data.get("trace"):
            event.trace = Trace(**data["trace"])

        return event
