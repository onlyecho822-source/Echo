"""
ECHO ORGANISM v2.1 - MANIFOLD PROJECTION OPERATIONS
Classification: PRODUCTION-READY

Projection functions to ensure states remain on their respective manifolds:
- Probability simplex (Δ^128)
- Unit sphere (S^256)
- Bounded intervals
"""

import numpy as np
from typing import Optional


def project_to_simplex(v: np.ndarray, method: str = "sorting") -> np.ndarray:
    """
    Project vector to probability simplex {p | p_i >= 0, Σp_i = 1}.

    Args:
        v: Input vector
        method: "sorting" (default, more stable) or "softmax"

    Returns:
        Projected vector on simplex
    """
    # Handle non-finite values
    v = np.nan_to_num(v, nan=0.0, posinf=1.0, neginf=0.0)

    if method == "softmax":
        return _project_simplex_softmax(v)
    else:
        return _project_simplex_sorting(v)


def _project_simplex_sorting(v: np.ndarray) -> np.ndarray:
    """
    Euclidean projection to simplex using sorting method.
    More numerically stable for extreme values.

    Algorithm: Duchi et al., 2008
    """
    n = len(v)

    # Handle edge cases
    if n == 0:
        return np.array([])
    if np.all(v == 0):
        return np.ones(n) / n

    # Sort descending
    u = np.sort(v)[::-1]

    # Find threshold
    cssv = np.cumsum(u) - 1.0
    ind = np.arange(1, n + 1)
    cond = u - cssv / ind > 0

    if np.any(cond):
        rho = ind[cond][-1]
        theta = cssv[cond][-1] / float(rho)
    else:
        # Fallback
        rho = n
        theta = (np.sum(u) - 1.0) / n

    # Project
    w = np.maximum(v - theta, 0.0)

    # Ensure proper normalization
    w_sum = np.sum(w)
    if w_sum > 0:
        return w / w_sum
    else:
        return np.ones(n) / n


def _project_simplex_softmax(v: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """
    Project to simplex using softmax.
    Good for probabilistic interpretations but less numerically stable.
    """
    # Shift for numerical stability
    v_shift = v - np.max(v)

    # Softmax
    exp_v = np.exp(v_shift / temperature)
    total = np.sum(exp_v)

    if total > 0:
        return exp_v / total
    else:
        return np.ones(len(v)) / len(v)


def project_to_sphere(v: np.ndarray, radius: float = 1.0) -> np.ndarray:
    """
    Project vector to sphere {x | ||x|| = radius}.

    Args:
        v: Input vector
        radius: Sphere radius (default 1.0)

    Returns:
        Projected vector on sphere
    """
    # Handle non-finite values
    v = np.nan_to_num(v, nan=0.0, posinf=1.0, neginf=-1.0)

    norm = np.linalg.norm(v)

    if norm < 1e-10:
        # Zero vector: project to random direction
        result = np.zeros(len(v))
        if len(v) > 0:
            result[0] = radius  # Default to e_1
        return result

    return (v / norm) * radius


def project_to_interval(v: np.ndarray, low: float = 0.0, high: float = 1.0) -> np.ndarray:
    """
    Project vector elements to bounded interval [low, high].

    Args:
        v: Input vector
        low: Lower bound
        high: Upper bound

    Returns:
        Clipped vector
    """
    return np.clip(v, low, high)


def project_creative_flat(x_flat: np.ndarray) -> np.ndarray:
    """
    Project flattened 896D creative state back to manifold M_c.

    Args:
        x_flat: 896D flattened state

    Returns:
        Projected 896D state on manifold
    """
    if len(x_flat) != 896:
        raise ValueError(f"Expected 896D vector, got {len(x_flat)}D")

    # Split components
    continuous = x_flat[:512].copy()
    probabilistic = x_flat[512:640].copy()
    semantic = x_flat[640:896].copy()

    # Project each component
    # Continuous: soft bounds
    continuous = np.clip(continuous, -10.0, 10.0)

    # Probabilistic: simplex
    probabilistic = project_to_simplex(probabilistic)

    # Semantic: sphere
    semantic = project_to_sphere(semantic)

    return np.concatenate([continuous, probabilistic, semantic])


def project_homeostatic_flat(h_flat: np.ndarray,
                             kappa_min: np.ndarray = None,
                             kappa_max: np.ndarray = None) -> np.ndarray:
    """
    Project flattened 8D homeostatic state back to manifold M_h.

    Args:
        h_flat: 8D flattened state
        kappa_min: Gain lower bounds (default [0.1, 0.1, 0.1])
        kappa_max: Gain upper bounds (default [1.0, 5.0, 2.0])

    Returns:
        Projected 8D state on manifold
    """
    if len(h_flat) != 8:
        raise ValueError(f"Expected 8D vector, got {len(h_flat)}D")

    if kappa_min is None:
        kappa_min = np.array([0.1, 0.1, 0.1])
    if kappa_max is None:
        kappa_max = np.array([1.0, 5.0, 2.0])

    resources = np.clip(h_flat[:3], 0.0, 1.0)
    stress = np.clip(h_flat[3:5], 0.0, 1.0)
    gains = np.clip(h_flat[5:8], kappa_min, kappa_max)

    return np.concatenate([resources, stress, gains])


def validate_simplex(p: np.ndarray, tol: float = 1e-4) -> bool:
    """Check if vector is on probability simplex"""
    if len(p) == 0:
        return False
    if np.any(p < -tol):
        return False
    if abs(np.sum(p) - 1.0) > tol:
        return False
    return True


def validate_sphere(s: np.ndarray, radius: float = 1.0, tol: float = 1e-4) -> bool:
    """Check if vector is on sphere"""
    if len(s) == 0:
        return False
    norm = np.linalg.norm(s)
    return abs(norm - radius) < tol


def compute_simplex_distance(p: np.ndarray, q: np.ndarray) -> float:
    """
    Compute distance between two probability distributions.
    Uses total variation distance (L1 / 2).
    """
    return np.sum(np.abs(p - q)) / 2.0


def compute_sphere_distance(s1: np.ndarray, s2: np.ndarray) -> float:
    """
    Compute angular distance between two points on sphere.
    Returns value in [0, 2].
    """
    cos_sim = np.dot(s1, s2) / (np.linalg.norm(s1) * np.linalg.norm(s2) + 1e-10)
    return 1.0 - np.clip(cos_sim, -1.0, 1.0)


def geodesic_interpolation_sphere(s1: np.ndarray, s2: np.ndarray, t: float) -> np.ndarray:
    """
    Geodesic interpolation on sphere (SLERP).

    Args:
        s1: Start point on sphere
        s2: End point on sphere
        t: Interpolation parameter in [0, 1]

    Returns:
        Interpolated point on sphere
    """
    # Ensure unit vectors
    s1 = s1 / (np.linalg.norm(s1) + 1e-10)
    s2 = s2 / (np.linalg.norm(s2) + 1e-10)

    # Compute angle
    cos_theta = np.clip(np.dot(s1, s2), -1.0, 1.0)
    theta = np.arccos(cos_theta)

    if theta < 1e-6:
        # Points are nearly identical
        return s1

    # SLERP formula
    sin_theta = np.sin(theta)
    result = (np.sin((1 - t) * theta) * s1 + np.sin(t * theta) * s2) / sin_theta

    return result / (np.linalg.norm(result) + 1e-10)
