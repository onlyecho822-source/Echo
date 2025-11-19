"""
ECHO ORGANISM v2.1 - GLOBAL ENERGY FUNCTION
Classification: CRITICAL FIX #2

The global energy function E(x, h) provides:
1. Proper energy landscape for gradient descent
2. Analytical gradients (no finite differences needed)
3. Stability guarantees through bounded energy
4. Clear interpretability of organism behavior

E(x, h) = -U(x) + λ_risk * R(x) - α * C(x) + E_boundary(x)

Where:
- U(x): Utility (novelty-based reward)
- R(x): Risk penalty (velocity damping)
- C(x): Coherence reward
- E_boundary: Soft boundary enforcement
"""

import numpy as np
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class GlobalEnergyFunction:
    """
    Global energy function for Echo Organism.

    This function defines the energy landscape that the organism
    explores through gradient descent. Lower energy = better states.
    """

    def __init__(self):
        # Energy component weights (can be modulated)
        self.novelty_weight = 1.0
        self.risk_weight = 1.0
        self.coherence_weight = 1.0
        self.boundary_weight = 2.0

        # Thermal floor (Critical Fix #5)
        self.thermal_floor = 0.01  # Minimum noise for exploration

    def compute_energy(self,
                       x_flat: np.ndarray,
                       x_prev_flat: Optional[np.ndarray],
                       memory: List[np.ndarray],
                       constraints: Tuple[float, float, float]) -> float:
        """
        Compute global energy E(x, h).

        Args:
            x_flat: Current 896D state
            x_prev_flat: Previous 896D state (for velocity)
            memory: List of past 896D states
            constraints: (b_explore, lambda_risk, alpha_coherence) from Ψ(h)

        Returns:
            Energy scalar (lower = better)
        """
        b, lam, alpha = constraints

        # Component energies
        E_novelty = self._novelty_energy(x_flat, memory, b)
        E_risk = self._risk_energy(x_flat, x_prev_flat, lam)
        E_coherence = self._coherence_energy(x_flat, alpha)
        E_boundary = self._boundary_energy(x_flat)

        # Total energy
        E_total = -E_novelty + E_risk - E_coherence + E_boundary

        return E_total

    def compute_energy_gradient(self,
                                x_flat: np.ndarray,
                                x_prev_flat: Optional[np.ndarray],
                                memory: List[np.ndarray],
                                constraints: Tuple[float, float, float]) -> np.ndarray:
        """
        Compute analytical gradient of energy function.
        CRITICAL FIX #1: Proper 896D gradient alignment.

        Returns:
            896D gradient vector ∇_x E(x, h)
        """
        b, lam, alpha = constraints

        # Component gradients (all 896D)
        grad_novelty = self._novelty_gradient(x_flat, memory, b)      # 896D
        grad_risk = self._risk_gradient(x_flat, x_prev_flat, lam)     # 896D
        grad_coherence = self._coherence_gradient(x_flat, alpha)      # 896D
        grad_boundary = self._boundary_gradient(x_flat)               # 896D

        # Total gradient: ∇E = -∇U + λ∇R - α∇C + ∇E_boundary
        grad_total = -grad_novelty + grad_risk - grad_coherence + grad_boundary

        # Numerical stability
        grad_total = np.nan_to_num(grad_total, nan=0.0, posinf=1.0, neginf=-1.0)

        return grad_total

    def _novelty_energy(self, x_flat: np.ndarray, memory: List[np.ndarray], b: float) -> float:
        """
        Novelty-based utility energy (negative because we want to maximize).
        U(x) = b * n(x) where n(x) = 1 - exp(-d_min)
        """
        if len(memory) == 0:
            return b * 0.5  # Default novelty

        # Find minimum distance to memory
        distances = [np.linalg.norm(x_flat - m) for m in memory]
        min_dist = np.min(distances)

        # Novelty: 1 - exp(-d)
        novelty = 1.0 - np.exp(-min_dist)

        return b * novelty

    def _novelty_gradient(self, x_flat: np.ndarray, memory: List[np.ndarray], b: float) -> np.ndarray:
        """
        Analytical gradient of novelty energy.
        ∇n(x) = exp(-d_min) * (x - x_nearest) / d_min
        """
        if len(memory) == 0:
            return np.zeros(896)

        # Find nearest memory and distance
        distances = [np.linalg.norm(x_flat - m) for m in memory]
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]
        nearest = memory[min_idx]

        if min_dist < 1e-10:
            # At memory point: return small random direction
            return np.random.standard_normal(896) * 0.01

        # Gradient: points away from nearest memory
        direction = (x_flat - nearest) / min_dist
        magnitude = b * np.exp(-min_dist)

        return magnitude * direction

    def _risk_energy(self, x_flat: np.ndarray, x_prev_flat: Optional[np.ndarray], lam: float) -> float:
        """
        Risk/velocity energy (quadratic damping).
        R(x) = λ * ||x - x_prev||^2 / 2
        """
        if x_prev_flat is None:
            return 0.0

        velocity = x_flat - x_prev_flat
        return 0.5 * lam * np.dot(velocity, velocity)

    def _risk_gradient(self, x_flat: np.ndarray, x_prev_flat: Optional[np.ndarray], lam: float) -> np.ndarray:
        """
        Gradient of risk energy.
        ∇R = λ * (x - x_prev)
        """
        if x_prev_flat is None:
            return np.zeros(896)

        return lam * (x_flat - x_prev_flat)

    def _coherence_energy(self, x_flat: np.ndarray, alpha: float) -> float:
        """
        Coherence energy based on entropy of probabilistic component.
        C(x) = α * (1 - H(p)/H_max)
        """
        # Extract probabilistic component
        p = x_flat[512:640]
        p = np.clip(p, 1e-10, 1.0)
        p = p / np.sum(p)  # Normalize

        # Entropy
        entropy = -np.sum(p * np.log(p))
        max_entropy = np.log(128.0)

        # Coherence (higher when low entropy)
        coherence = 1.0 - entropy / max_entropy

        return alpha * coherence

    def _coherence_gradient(self, x_flat: np.ndarray, alpha: float) -> np.ndarray:
        """
        Gradient of coherence energy.
        Only affects probabilistic component (indices 512-640).
        """
        grad = np.zeros(896)

        # Extract probabilistic component
        p = x_flat[512:640]
        p = np.clip(p, 1e-10, 1.0)
        p_sum = np.sum(p)
        if p_sum > 0:
            p = p / p_sum

        # Gradient of entropy w.r.t. p
        # ∂H/∂p_i = -(1 + log(p_i))
        # ∂C/∂p_i = -α/H_max * ∂H/∂p_i = α/H_max * (1 + log(p_i))
        max_entropy = np.log(128.0)

        grad_p = (alpha / max_entropy) * (1 + np.log(p + 1e-10))

        # Apply to correct indices
        grad[512:640] = grad_p

        return grad

    def _boundary_energy(self, x_flat: np.ndarray) -> float:
        """
        Soft boundary energy to keep states bounded.
        Penalizes states far from origin in continuous space.
        """
        # Continuous component only (first 512 dims)
        continuous = x_flat[:512]

        # Soft L2 penalty beyond radius
        radius = 5.0
        excess = np.maximum(np.abs(continuous) - radius, 0.0)

        return self.boundary_weight * np.sum(excess ** 2)

    def _boundary_gradient(self, x_flat: np.ndarray) -> np.ndarray:
        """
        Gradient of boundary energy.
        """
        grad = np.zeros(896)

        # Continuous component only
        continuous = x_flat[:512]
        radius = 5.0

        # Gradient: 2 * excess * sign
        excess = np.maximum(np.abs(continuous) - radius, 0.0)
        signs = np.sign(continuous)

        grad[:512] = 2.0 * self.boundary_weight * excess * signs

        return grad

    def compute_detailed_energy(self,
                                x_flat: np.ndarray,
                                x_prev_flat: Optional[np.ndarray],
                                memory: List[np.ndarray],
                                constraints: Tuple[float, float, float]) -> dict:
        """
        Compute detailed energy breakdown for monitoring.
        """
        b, lam, alpha = constraints

        E_novelty = self._novelty_energy(x_flat, memory, b)
        E_risk = self._risk_energy(x_flat, x_prev_flat, lam)
        E_coherence = self._coherence_energy(x_flat, alpha)
        E_boundary = self._boundary_energy(x_flat)
        E_total = -E_novelty + E_risk - E_coherence + E_boundary

        return {
            'total': E_total,
            'novelty': E_novelty,
            'risk': E_risk,
            'coherence': E_coherence,
            'boundary': E_boundary,
            'components_sum': -E_novelty + E_risk - E_coherence + E_boundary
        }


def create_energy_function() -> GlobalEnergyFunction:
    """Factory function for energy system"""
    return GlobalEnergyFunction()
