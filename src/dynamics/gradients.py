"""
ECHO ORGANISM v2.1 - GRADIENT COMPUTATION
Classification: CRITICAL FIX #1

Proper 896D gradient computation with:
- Analytical gradients from global energy function
- Finite difference fallback
- Multiple gradient computation methods
- Numerical stability and normalization

CRITICAL FIX #1: All gradients must be 896D aligned.
No more mixing different sized vectors.
"""

import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import JAX for analytical gradients
try:
    import jax
    import jax.numpy as jnp
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False


class GradientComputer:
    """
    Military-grade gradient computation system.

    Features:
    - Multiple computation methods (analytical, finite diff, heuristic)
    - Automatic fallback on failure
    - Gradient normalization and clipping
    - Numerical stability enforcement
    """

    def __init__(self, method: str = "analytical"):
        """
        Args:
            method: "analytical", "finite_diff", or "heuristic"
        """
        self.method = method
        self.gradient_history = []
        self.fallback_count = 0

        logger.info(f"GradientComputer initialized with method: {method}")

    def compute_creative_gradient(self,
                                  x_flat: np.ndarray,
                                  x_prev_flat: Optional[np.ndarray],
                                  memory: List[np.ndarray],
                                  constraints: Tuple[float, float, float],
                                  energy_fn) -> np.ndarray:
        """
        Compute creative state gradient for gradient descent.

        CRITICAL: Output must be 896D to match state dimension.

        Args:
            x_flat: Current 896D state
            x_prev_flat: Previous state
            memory: Memory bank
            constraints: (b, λ, α) from Ψ(h)
            energy_fn: Global energy function object

        Returns:
            896D gradient vector
        """
        try:
            if self.method == "analytical":
                grad = self._analytical_gradient(
                    x_flat, x_prev_flat, memory, constraints, energy_fn
                )
            elif self.method == "finite_diff":
                grad = self._finite_diff_gradient(
                    x_flat, x_prev_flat, memory, constraints, energy_fn
                )
            else:  # heuristic
                grad = self._heuristic_gradient(
                    x_flat, x_prev_flat, memory, constraints
                )

            # Validate and normalize
            grad = self._validate_and_normalize(grad)

            # Track history
            self.gradient_history.append(np.linalg.norm(grad))

            return grad

        except Exception as e:
            logger.warning(f"Gradient computation failed: {e}, using fallback")
            self.fallback_count += 1
            return self._fallback_gradient(x_flat, memory)

    def _analytical_gradient(self,
                             x_flat: np.ndarray,
                             x_prev_flat: Optional[np.ndarray],
                             memory: List[np.ndarray],
                             constraints: Tuple[float, float, float],
                             energy_fn) -> np.ndarray:
        """
        Analytical gradient from energy function.
        Returns negative gradient (descent direction).
        """
        # Get gradient from energy function
        grad_E = energy_fn.compute_energy_gradient(
            x_flat, x_prev_flat, memory, constraints
        )

        # Return negative for descent (minimizing energy)
        return -grad_E

    def _finite_diff_gradient(self,
                              x_flat: np.ndarray,
                              x_prev_flat: Optional[np.ndarray],
                              memory: List[np.ndarray],
                              constraints: Tuple[float, float, float],
                              energy_fn,
                              eps: float = 1e-5) -> np.ndarray:
        """
        Finite difference gradient computation.
        Slower but more robust for debugging.
        """
        grad = np.zeros(896)

        for i in range(896):
            x_plus = x_flat.copy()
            x_minus = x_flat.copy()
            x_plus[i] += eps
            x_minus[i] -= eps

            E_plus = energy_fn.compute_energy(
                x_plus, x_prev_flat, memory, constraints
            )
            E_minus = energy_fn.compute_energy(
                x_minus, x_prev_flat, memory, constraints
            )

            grad[i] = (E_plus - E_minus) / (2 * eps)

        # Return negative for descent
        return -grad

    def _heuristic_gradient(self,
                            x_flat: np.ndarray,
                            x_prev_flat: Optional[np.ndarray],
                            memory: List[np.ndarray],
                            constraints: Tuple[float, float, float]) -> np.ndarray:
        """
        Heuristic gradient based on component-wise objectives.
        Useful when energy function is unavailable.
        """
        b, lam, alpha = constraints

        # Novelty gradient: point away from nearest memory
        grad_novelty = self._novelty_heuristic_grad(x_flat, memory)

        # Velocity gradient: damping
        grad_velocity = self._velocity_heuristic_grad(x_flat, x_prev_flat)

        # Coherence gradient: entropy reduction
        grad_coherence = self._coherence_heuristic_grad(x_flat)

        # Combine with constraints
        grad = b * grad_novelty - lam * grad_velocity + alpha * grad_coherence

        return grad

    def _novelty_heuristic_grad(self, x_flat: np.ndarray, memory: List[np.ndarray]) -> np.ndarray:
        """Heuristic: move away from nearest memories"""
        if len(memory) == 0:
            return np.random.standard_normal(896) * 0.1

        # Find k nearest neighbors
        k = min(5, len(memory))
        distances = [(np.linalg.norm(x_flat - m), m) for m in memory]
        distances.sort(key=lambda x: x[0])

        # Weighted average direction away from neighbors
        total_weight = 0.0
        grad = np.zeros(896)

        for i in range(k):
            dist, mem = distances[i]
            if dist < 1e-10:
                continue
            weight = np.exp(-dist)
            direction = (x_flat - mem) / dist
            grad += weight * direction
            total_weight += weight

        if total_weight > 0:
            grad /= total_weight

        return grad

    def _velocity_heuristic_grad(self, x_flat: np.ndarray,
                                 x_prev_flat: Optional[np.ndarray]) -> np.ndarray:
        """Heuristic: velocity damping"""
        if x_prev_flat is None:
            return np.zeros(896)

        return x_flat - x_prev_flat

    def _coherence_heuristic_grad(self, x_flat: np.ndarray) -> np.ndarray:
        """Heuristic: reduce entropy of probabilistic component"""
        grad = np.zeros(896)

        # Only affects probabilistic component
        p = x_flat[512:640]
        p = np.clip(p, 1e-10, 1.0)
        p = p / np.sum(p)

        # Push toward peaked distribution
        # Gradient: -(1 + log(p_i))
        grad[512:640] = -(1.0 + np.log(p))

        return grad

    def _validate_and_normalize(self, grad: np.ndarray) -> np.ndarray:
        """
        Validate gradient and apply normalization/clipping.
        """
        # Check dimension
        if len(grad) != 896:
            raise ValueError(f"Gradient dimension {len(grad)} != 896")

        # Handle NaN/Inf
        if not np.all(np.isfinite(grad)):
            nan_count = np.sum(~np.isfinite(grad))
            logger.warning(f"Gradient has {nan_count} non-finite values")
            grad = np.nan_to_num(grad, nan=0.0, posinf=1.0, neginf=-1.0)

        # Gradient clipping
        norm = np.linalg.norm(grad)
        max_norm = 2.0

        if norm > max_norm:
            grad = grad * (max_norm / norm)

        # Minimum gradient for exploration
        min_norm = 0.01
        if norm < min_norm and norm > 0:
            grad = grad * (min_norm / norm)

        return grad

    def _fallback_gradient(self, x_flat: np.ndarray, memory: List[np.ndarray]) -> np.ndarray:
        """
        Emergency fallback: simple repulsion from memory.
        """
        if len(memory) == 0:
            return np.random.standard_normal(896) * 0.1

        # Simple: move away from centroid
        centroid = np.mean(memory, axis=0)
        diff = x_flat - centroid
        norm = np.linalg.norm(diff)

        if norm < 1e-10:
            return np.random.standard_normal(896) * 0.1

        return diff / norm * 0.5


def compute_gradient_stats(gradient_computer: GradientComputer) -> dict:
    """Compute statistics on gradient computation"""
    history = gradient_computer.gradient_history

    if not history:
        return {}

    return {
        'mean_norm': np.mean(history),
        'std_norm': np.std(history),
        'max_norm': np.max(history),
        'min_norm': np.min(history),
        'fallback_rate': gradient_computer.fallback_count / max(1, len(history))
    }
