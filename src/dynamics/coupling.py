"""
ECHO ORGANISM v2.1 - COUPLING FUNCTIONS
Classification: CRITICAL FIX #3

Implements the coupling between creative and homeostatic subsystems:
- Φ: M_c → R^5 (Creative → Homeostatic influence)
- Ψ: M_h → R^3 (Homeostatic → Creative constraints)
- g: R^3 → R^3 (Chronic gain adaptation)

CRITICAL FIX #3: Nonlinear homeostasis
- Replace linear dynamics with proper regulation
- Stress uses nonlinear bounded response
- Resources have saturation dynamics
"""

import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def phi(x_flat: np.ndarray,
        x_prev_flat: Optional[np.ndarray],
        memory: List[np.ndarray]) -> np.ndarray:
    """
    Φ: Creative → Homeostatic influence (M_c → R^5)

    Returns: [novelty, coherence, utility, metabolic_cost, velocity]
    All outputs bounded ∈ [0, 1]

    Args:
        x_flat: Current 896D flattened state
        x_prev_flat: Previous 896D flattened state
        memory: List of past 896D states

    Returns:
        5D influence vector
    """
    try:
        # 1. NOVELTY: n(x) = 1 - exp(-d_min)
        if len(memory) == 0:
            novelty = 0.5
        else:
            distances = [np.linalg.norm(x_flat - m) for m in memory]
            min_dist = np.min(distances)
            novelty = 1.0 - np.exp(-min_dist)

        # 2. COHERENCE: c(x) = 1 - H(p)/H_max
        p = x_flat[512:640]
        p = np.clip(p, 1e-10, 1.0)
        p = p / np.sum(p)
        entropy = -np.sum(p * np.log(p))
        max_entropy = np.log(128.0)
        coherence = 1.0 - entropy / max_entropy

        # 3. UTILITY: Weighted combination
        utility = 0.5 * novelty + 0.5 * coherence

        # 4. METABOLIC COST: Computational load
        continuous = x_flat[:512]
        semantic = x_flat[640:]

        cost_cont = 0.002 * np.linalg.norm(continuous) ** 2
        cost_prob = 0.010 * entropy
        cost_sem = 0.004 * np.linalg.norm(semantic) ** 2
        raw_cost = cost_cont + cost_prob + cost_sem
        metabolic_cost = np.tanh(raw_cost)  # Bounded to [0, 1)

        # 5. CREATIVE VELOCITY: State change magnitude
        if x_prev_flat is not None:
            velocity_raw = np.linalg.norm(x_flat - x_prev_flat)
            velocity = velocity_raw / (1.0 + velocity_raw)  # Bounded
        else:
            velocity = 0.0

        influence = np.array([novelty, coherence, utility, metabolic_cost, velocity])
        influence = np.clip(np.nan_to_num(influence, nan=0.5), 0.0, 1.0)

        return influence

    except Exception as e:
        logger.error(f"Phi computation failed: {e}")
        return np.array([0.5, 0.5, 0.5, 0.3, 0.1])


def psi(h_resources: np.ndarray,
        h_stress: np.ndarray,
        h_gains: np.ndarray) -> Tuple[float, float, float]:
    """
    Ψ: Homeostatic → Creative constraints (M_h → R^3)

    Returns: (b_explore, λ_risk, α_coherence)

    Args:
        h_resources: (3,) resource levels
        h_stress: (2,) stress levels
        h_gains: (3,) gain parameters

    Returns:
        3-tuple of constraint parameters
    """
    try:
        # Aggregate stress
        sigma = 0.6 * h_stress[0] + 0.4 * h_stress[1]
        sigma = np.clip(sigma, 0.0, 1.0)

        # Resource capacity
        capacity = np.min(h_resources)

        # 1. EXPLORATION BUDGET
        # Higher when low stress, high resources, high explore gain
        # BOOSTED to prevent novelty collapse
        b_explore = 1.5 * h_gains[0] * capacity * (1.0 - sigma)
        b_explore = np.clip(b_explore, 0.1, 1.5)  # Minimum 0.1 for exploration

        # 2. RISK PENALTY
        # Reduced to allow more exploration
        lambda_risk = 0.3 * h_gains[1] * (1.0 - sigma)  # Reduced from 1.0x
        lambda_risk = np.clip(lambda_risk, 0.0, 2.0)

        # 3. COHERENCE WEIGHT
        # Moderate to maintain structure
        alpha_coherence = 0.5 * h_gains[2] * (1.0 + sigma)  # Reduced from 1.0x
        alpha_coherence = np.clip(alpha_coherence, 0.1, 1.5)

        return (b_explore, lambda_risk, alpha_coherence)

    except Exception as e:
        logger.error(f"Psi computation failed: {e}")
        return (0.5, 1.0, 1.0)


def g_gain_adaptation(n_bar: float, c_bar: float, sigma_bar: float) -> np.ndarray:
    """
    g: Chronic gain adaptation (R^3 → R^3)

    Long-term calibration based on moving averages.
    No immediate stress response (that's Ψ's job).

    Args:
        n_bar: Average novelty (50-100 step window)
        c_bar: Average coherence
        sigma_bar: Average stress

    Returns:
        Gain adjustments Δκ ∈ [-0.03, 0.03]^3
    """
    try:
        # Target setpoints
        n_target = 0.7
        c_target = 0.8
        sigma_target = 0.3

        # Errors
        n_err = np.clip(n_bar, 0.0, 1.0) - n_target
        c_err = np.clip(c_bar, 0.0, 1.0) - c_target
        sigma_err = np.clip(sigma_bar, 0.0, 1.0) - sigma_target

        # Gain adjustments
        # 1. Explore: ONLY novelty feedback
        g_explore = -0.4 * n_err

        # 2. Risk: stress + coherence
        g_risk = 0.3 * sigma_err - 0.2 * c_err

        # 3. Coherence: coherence + stress
        g_coherence = -0.3 * c_err + 0.1 * sigma_err

        adjustments = np.array([g_explore, g_risk, g_coherence])
        adjustments = np.clip(adjustments, -0.03, 0.03)

        return adjustments

    except Exception as e:
        logger.error(f"Gain adaptation failed: {e}")
        return np.zeros(3)


def f_homeostatic(h_resources: np.ndarray,
                  h_stress: np.ndarray,
                  h_gains: np.ndarray,
                  influence: np.ndarray,
                  params: dict,
                  rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    CRITICAL FIX #3: Nonlinear homeostatic dynamics.

    f_h: Homeostatic state evolution with proper regulation.

    Args:
        h_resources: Current resources (3,)
        h_stress: Current stress (2,)
        h_gains: Current gains (3,)
        influence: Φ(x) output (5,)
        params: Dynamics parameters
        rng: Random number generator

    Returns:
        Updated (resources, stress, gains)
    """
    n, c, u, rho, v = influence

    # Parameters
    inflow = params.get('inflow', np.array([0.1, 0.08, 0.12]))
    cost_scaling = params.get('cost_scaling', 0.1)
    stress_drivers = params.get('stress_drivers', (0.05, 0.03, 0.02))
    stress_relaxation = params.get('stress_relaxation', 0.10)
    dt = params.get('dt', 1.0)

    # ========== RESOURCE DYNAMICS (Nonlinear) ==========
    # dr/dt = inflow * (1 - r) - cost_scaling * ρ * r
    # Saturation dynamics: regeneration slows as r approaches 1

    r = h_resources.copy()
    regeneration = inflow * (1.0 - r)  # Slows near 1
    consumption = cost_scaling * rho * r  # Proportional to current level
    dr = regeneration - consumption

    r_new = r + dt * dr
    r_new = np.clip(r_new, 0.0, 1.0)

    # ========== STRESS DYNAMICS (Nonlinear) ==========
    # dσ/dt = drivers * (1 - σ) - relaxation * σ
    # Bounded response: stress saturates, can't exceed 1

    sigma = h_stress.copy()

    # Load stress: driven by novelty-seeking and metabolic cost
    load_driver = stress_drivers[0] * (1 - n) + stress_drivers[1] * rho
    load_relaxation = stress_relaxation * sigma[0]
    d_load = load_driver * (1.0 - sigma[0]) - load_relaxation

    # Variance stress: driven by velocity/instability
    var_driver = stress_drivers[2] * v
    var_relaxation = stress_relaxation * sigma[1]
    d_var = var_driver * (1.0 - sigma[1]) - var_relaxation

    sigma_new = sigma + dt * np.array([d_load, d_var])
    sigma_new = np.clip(sigma_new, 0.0, 1.0)

    # ========== GAIN STABILITY (No change here) ==========
    # Gains are updated through chronic adaptation (g function)
    # Not in fast dynamics

    kappa_new = h_gains.copy()

    return r_new, sigma_new, kappa_new


def compute_influence_summary(influences: List[np.ndarray]) -> dict:
    """Compute summary statistics on influence history"""
    if not influences:
        return {}

    arr = np.array(influences)
    return {
        'novelty_mean': np.mean(arr[:, 0]),
        'novelty_std': np.std(arr[:, 0]),
        'coherence_mean': np.mean(arr[:, 1]),
        'coherence_std': np.std(arr[:, 1]),
        'utility_mean': np.mean(arr[:, 2]),
        'metabolic_mean': np.mean(arr[:, 3]),
        'velocity_mean': np.mean(arr[:, 4])
    }
