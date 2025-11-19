"""
Elasticity Matrix Core Implementation

Dynamic capability-context mapping with resonance weighting.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class MatrixConfig:
    """Configuration for Elasticity Matrix."""
    learning_rate: float = 0.1
    resonance_decay: float = 0.95
    default_weight: float = 0.5


class ElasticityMatrix:
    """
    LLM Capability Mapping and Adaptation Matrix.

    Models relationships between capabilities and contexts
    for dynamic behavior adaptation.

    Attributes:
        capabilities: List of capability names
        contexts: List of context names
        matrix: The elasticity matrix

    Example:
        >>> matrix = ElasticityMatrix(
        ...     capabilities=["reasoning", "coding"],
        ...     contexts=["technical", "creative"]
        ... )
        >>> matrix.set("reasoning", "technical", 0.95)
        >>> score = matrix.predict({"reasoning": 0.8, "coding": 0.2})
    """

    def __init__(
        self,
        capabilities: List[str],
        contexts: List[str],
        config: Optional[MatrixConfig] = None
    ):
        """Initialize the Elasticity Matrix."""
        self.capabilities = capabilities
        self.contexts = contexts
        self.config = config or MatrixConfig()

        # Create capability and context indices
        self._cap_idx = {cap: i for i, cap in enumerate(capabilities)}
        self._ctx_idx = {ctx: i for i, ctx in enumerate(contexts)}

        # Initialize matrix with default weights
        n_caps = len(capabilities)
        n_ctxs = len(contexts)
        self._matrix = np.full(
            (n_caps, n_ctxs),
            self.config.default_weight,
            dtype=np.float64
        )

        # Resonance factors
        self._resonance = np.ones((n_caps, n_ctxs), dtype=np.float64)

    def set(self, capability: str, context: str, weight: float):
        """
        Set capability-context weight.

        Args:
            capability: Capability name
            context: Context name
            weight: Weight value [0, 1]

        Raises:
            KeyError: If capability or context not found
        """
        i = self._cap_idx[capability]
        j = self._ctx_idx[context]
        self._matrix[i, j] = np.clip(weight, 0.0, 1.0)

    def get(self, capability: str, context: str) -> float:
        """
        Get capability-context weight.

        Args:
            capability: Capability name
            context: Context name

        Returns:
            Weight value
        """
        i = self._cap_idx[capability]
        j = self._ctx_idx[context]
        return float(self._matrix[i, j])

    def update(
        self,
        capability: str,
        context: str,
        delta: float,
        resonance: float = 1.0
    ):
        """
        Update weight with resonance factor.

        Implements: E'[i,j] = E[i,j] + α × delta × resonance

        Args:
            capability: Capability name
            context: Context name
            delta: Change amount
            resonance: Resonance factor [0, 1]
        """
        i = self._cap_idx[capability]
        j = self._ctx_idx[context]

        current = self._matrix[i, j]
        new_weight = current + self.config.learning_rate * delta * resonance
        self._matrix[i, j] = np.clip(new_weight, 0.0, 1.0)

        # Update resonance factor with decay
        self._resonance[i, j] *= self.config.resonance_decay

    def predict(self, task_vector: Dict[str, float]) -> float:
        """
        Predict performance for a task.

        Args:
            task_vector: Dict mapping capabilities to task weights

        Returns:
            Predicted performance score

        Example:
            >>> score = matrix.predict({
            ...     "reasoning": 0.8,
            ...     "coding": 0.2
            ... })
        """
        score = 0.0
        total_weight = 0.0

        for cap, task_weight in task_vector.items():
            if cap in self._cap_idx:
                i = self._cap_idx[cap]
                # Sum across all contexts
                cap_score = np.mean(self._matrix[i, :])
                score += cap_score * task_weight
                total_weight += task_weight

        if total_weight == 0:
            return 0.0

        return float(score / total_weight)

    def capability_profile(self, capability: str) -> Dict[str, float]:
        """
        Get profile for a capability across all contexts.

        Args:
            capability: Capability name

        Returns:
            Dict mapping contexts to weights
        """
        if capability not in self._cap_idx:
            raise KeyError(f"Unknown capability: {capability}")

        i = self._cap_idx[capability]
        return {
            ctx: float(self._matrix[i, j])
            for ctx, j in self._ctx_idx.items()
        }

    def context_requirements(self, context: str) -> Dict[str, float]:
        """
        Get capability requirements for a context.

        Args:
            context: Context name

        Returns:
            Dict mapping capabilities to weights
        """
        if context not in self._ctx_idx:
            raise KeyError(f"Unknown context: {context}")

        j = self._ctx_idx[context]
        return {
            cap: float(self._matrix[i, j])
            for cap, i in self._cap_idx.items()
        }

    def optimal_capability(self, context: str) -> str:
        """
        Find optimal capability for a context.

        Args:
            context: Context name

        Returns:
            Name of highest-weighted capability
        """
        requirements = self.context_requirements(context)
        return max(requirements, key=requirements.get)

    def to_dict(self) -> Dict[str, Any]:
        """Export matrix as dictionary."""
        return {
            "capabilities": self.capabilities,
            "contexts": self.contexts,
            "matrix": self._matrix.tolist(),
            "resonance": self._resonance.tolist()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElasticityMatrix':
        """Create matrix from dictionary."""
        matrix = cls(
            capabilities=data["capabilities"],
            contexts=data["contexts"]
        )
        matrix._matrix = np.array(data["matrix"])
        matrix._resonance = np.array(data["resonance"])
        return matrix

    @property
    def shape(self) -> tuple:
        """Get matrix shape (capabilities, contexts)."""
        return self._matrix.shape
