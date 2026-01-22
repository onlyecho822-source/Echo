#!/usr/bin/env python3
"""
UNIVERSAL CONSTRAINT MATHEMATICS: Clean Implementation
======================================================

A minimal, correct implementation of the Universal Constraint Mathematics framework.
No placeholders. No ellipsis. Production-ready code.

This provides:
1. BoundarySystem - ODE for boundary dynamics x(t)
2. info_capacity - Shannon capacity with filter efficiency
3. selective_exchange_matrix - Decision function π(z)
4. foam_cost_gain - Scaling laws for intermediate chaos
5. measure_u_vector - Extract u⃗ from empirical data
6. optimize_u_vector - Find optimal parameters
7. viability_score - Objective function J(u⃗)

Author: Echo System
Date: 2026-01-21
Status: Production Ready
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize, differential_evolution
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Callable
import warnings


# =============================================================================
# CONSTANTS AND TYPES
# =============================================================================

@dataclass
class UniversalityVector:
    """
    The 6D universality vector u⃗ = (κ, φ, ε*, μ, γ, Θ)
    
    Characterizes any system implementing universal constraints.
    """
    kappa: float      # Permeability (0, 1)
    phi: float        # Filter efficiency (0, 1)
    epsilon_star: float  # Target error rate (0, 1)
    mu: float         # Memory ratio (1, ∞)
    gamma: float      # Damping ratio (0, ∞)
    theta: float      # Foam intensity (0, ∞)
    
    def to_array(self) -> np.ndarray:
        return np.array([self.kappa, self.phi, self.epsilon_star, 
                        self.mu, self.gamma, self.theta])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'UniversalityVector':
        return cls(kappa=arr[0], phi=arr[1], epsilon_star=arr[2],
                  mu=arr[3], gamma=arr[4], theta=arr[5])
    
    def in_stable_region(self) -> bool:
        """Check if vector lies in stable_operation attractor"""
        return (0.3 < self.kappa < 0.8 and
                0.6 < self.phi < 0.95 and
                0.05 < self.epsilon_star < 0.4 and
                5 < self.mu < 200 and
                0.5 < self.gamma < 2.0 and
                0.1 < self.theta < 5.0)


@dataclass
class StableOperationRegion:
    """Defines the stable operation attractor region Ω"""
    kappa_range: Tuple[float, float] = (0.3, 0.8)
    phi_range: Tuple[float, float] = (0.6, 0.95)
    epsilon_range: Tuple[float, float] = (0.05, 0.4)
    mu_range: Tuple[float, float] = (5, 200)
    gamma_range: Tuple[float, float] = (0.5, 2.0)
    theta_range: Tuple[float, float] = (0.1, 5.0)


# =============================================================================
# BOUNDARY SYSTEM DYNAMICS
# =============================================================================

class BoundarySystem:
    """
    ODE system for boundary dynamics x(t)
    
    Implements the Euler-Lagrange equation derived from the universal Lagrangian:
    ẍ + 2γω₀ẋ + ω₀²x = κ·ΔP(t)
    
    where:
    - x: boundary displacement/state
    - γ: damping ratio
    - ω₀: natural frequency
    - κ: permeability
    - ΔP: pressure differential
    """
    
    def __init__(self, omega_0: float = 1.0, gamma: float = 1.0, kappa: float = 0.5):
        self.omega_0 = omega_0
        self.gamma = gamma
        self.kappa = kappa
    
    def pressure_differential(self, t: float, P_in: float = 1.0, P_out: float = 0.0) -> float:
        """Calculate pressure differential at time t"""
        return P_in - P_out
    
    def dynamics(self, t: float, state: np.ndarray, 
                 P_in: float = 1.0, P_out: float = 0.0) -> np.ndarray:
        """
        System dynamics: [ẋ, ẍ]
        
        state = [x, ẋ]
        """
        x, x_dot = state
        delta_P = self.pressure_differential(t, P_in, P_out)
        
        x_ddot = (-2 * self.gamma * self.omega_0 * x_dot 
                  - self.omega_0**2 * x 
                  + self.kappa * delta_P)
        
        return np.array([x_dot, x_ddot])
    
    def solve(self, t_span: Tuple[float, float], x0: float = 0.0, 
              x_dot0: float = 0.0, P_in: float = 1.0, P_out: float = 0.0,
              t_eval: Optional[np.ndarray] = None) -> dict:
        """
        Solve the boundary dynamics ODE
        
        Returns solution dictionary with 't', 'x', 'x_dot'
        """
        initial_state = np.array([x0, x_dot0])
        
        sol = solve_ivp(
            lambda t, y: self.dynamics(t, y, P_in, P_out),
            t_span,
            initial_state,
            t_eval=t_eval,
            method='RK45'
        )
        
        return {
            't': sol.t,
            'x': sol.y[0],
            'x_dot': sol.y[1],
            'success': sol.success
        }
    
    def measure_damping(self, response_data: np.ndarray, 
                        time_data: np.ndarray) -> float:
        """
        Measure damping ratio from step response data
        
        Uses logarithmic decrement method
        """
        # Find peaks in response
        peaks = []
        for i in range(1, len(response_data) - 1):
            if response_data[i] > response_data[i-1] and response_data[i] > response_data[i+1]:
                peaks.append((time_data[i], response_data[i]))
        
        if len(peaks) < 2:
            return 1.0  # Critically damped or overdamped
        
        # Calculate logarithmic decrement
        delta = np.log(peaks[0][1] / peaks[1][1])
        
        # Calculate damping ratio
        gamma = delta / np.sqrt(4 * np.pi**2 + delta**2)
        
        return gamma


# =============================================================================
# INFORMATION FLOW OPERATORS
# =============================================================================

def info_capacity(S: float, N: float, phi: float) -> float:
    """
    Shannon capacity with filter efficiency
    
    C = log₂(1 + S_eff / N_eff)
    
    where:
    - S_eff = φ·S (filtered signal)
    - N_eff = N·(1-φ) + S·(1-φ) (remaining noise + leaked signal)
    
    Args:
        S: Signal power
        N: Noise power
        phi: Filter efficiency (0 to 1)
    
    Returns:
        Channel capacity in bits
    """
    if phi <= 0 or phi >= 1:
        warnings.warn("Filter efficiency should be in (0, 1)")
        phi = np.clip(phi, 0.001, 0.999)
    
    S_eff = phi * S
    N_eff = N * (1 - phi) + S * (1 - phi)
    
    if N_eff <= 0:
        N_eff = 1e-10  # Prevent division by zero
    
    return np.log2(1 + S_eff / N_eff)


def optimal_filter_efficiency(S: float, N: float) -> float:
    """
    Find optimal filter efficiency that maximizes capacity
    
    Args:
        S: Signal power
        N: Noise power
    
    Returns:
        Optimal φ value
    """
    def neg_capacity(phi):
        return -info_capacity(S, N, phi[0])
    
    result = minimize(neg_capacity, x0=[0.5], bounds=[(0.01, 0.99)], method='L-BFGS-B')
    return result.x[0]


# =============================================================================
# SELECTIVE EXCHANGE MATRIX
# =============================================================================

def selective_exchange_matrix(benefit: np.ndarray, risk: np.ndarray, 
                              cost: np.ndarray, 
                              alpha: float = 1.0, beta: float = 1.0, 
                              gamma: float = 0.5) -> np.ndarray:
    """
    Compute selective permeability as a decision function
    
    π(z) = σ(α·B(z) - β·R(z) - γ·Cost(z))
    
    where σ is the sigmoid function
    
    Args:
        benefit: Array of benefit values for each input type
        risk: Array of risk values for each input type
        cost: Array of cost values for each input type
        alpha: Weight for benefit
        beta: Weight for risk
        gamma: Weight for cost
    
    Returns:
        Array of permeability values (0 to 1)
    """
    decision_value = alpha * benefit - beta * risk - gamma * cost
    permeability = 1 / (1 + np.exp(-decision_value))
    return permeability


def create_exchange_matrix(n_types: int = 4) -> Dict[str, np.ndarray]:
    """
    Create a standard exchange matrix for common input types
    
    Types: beneficial_small, beneficial_large, harmful_small, harmful_large
    """
    # Define characteristics for each type
    types = ['beneficial_small', 'beneficial_large', 'harmful_small', 'harmful_large']
    
    benefit = np.array([1.0, 0.8, 0.0, 0.0])
    risk = np.array([0.0, 0.1, 0.5, 1.0])
    cost = np.array([0.1, 0.5, 0.1, 0.5])
    
    permeability = selective_exchange_matrix(benefit, risk, cost)
    
    return {
        'types': types,
        'benefit': benefit,
        'risk': risk,
        'cost': cost,
        'permeability': permeability
    }


# =============================================================================
# FOAM ZONE SCALING
# =============================================================================

def foam_cost_gain(theta: float, a: float = 0.5, b: float = 1.5) -> Dict[str, float]:
    """
    Scaling laws for intermediate chaos (foam zone)
    
    Processing: I ∝ Θ^a (sublinear, a < 1)
    Dissipation: E ∝ Θ^b (superlinear, b > 1)
    
    Key insight: a < 1 < b
    Information gains diminish while energy costs grow faster.
    
    Args:
        theta: Foam intensity (turbulence × complexity)
        a: Processing exponent (default 0.5)
        b: Dissipation exponent (default 1.5)
    
    Returns:
        Dictionary with processing gain and energy cost
    """
    if theta < 0:
        raise ValueError("Theta must be non-negative")
    
    processing = theta ** a
    dissipation = theta ** b
    
    # Net gain (processing - cost)
    net_gain = processing - dissipation
    
    # Efficiency (processing / cost)
    efficiency = processing / dissipation if dissipation > 0 else float('inf')
    
    return {
        'theta': theta,
        'processing': processing,
        'dissipation': dissipation,
        'net_gain': net_gain,
        'efficiency': efficiency,
        'exponents': {'a': a, 'b': b}
    }


def optimal_foam_intensity(a: float = 0.5, b: float = 1.5) -> float:
    """
    Find optimal foam intensity that maximizes net gain
    
    d/dΘ (Θ^a - Θ^b) = 0
    aΘ^(a-1) = bΘ^(b-1)
    Θ* = (a/b)^(1/(b-a))
    """
    if b <= a:
        raise ValueError("b must be greater than a for meaningful optimization")
    
    return (a / b) ** (1 / (b - a))


# =============================================================================
# MEASUREMENT PROTOCOL
# =============================================================================

def measure_u_vector(data: Dict) -> UniversalityVector:
    """
    Extract universality vector u⃗ from empirical data
    
    Args:
        data: Dictionary containing:
            - 'exchange_flux': Measured exchange rate
            - 'max_flux': Maximum possible exchange rate
            - 'signal_passed': Signal that passed filter
            - 'noise_passed': Noise that passed filter
            - 'error_rate': Observed error rate
            - 'max_error': Maximum viable error rate
            - 'memory_time': Memory persistence time
            - 'system_time': System cycle time
            - 'damping_ratio': Measured damping ratio
            - 'turbulence': Turbulence measure
            - 'complexity': Complexity measure
    
    Returns:
        UniversalityVector with measured parameters
    """
    # κ: Permeability
    kappa = data.get('exchange_flux', 0.5) / data.get('max_flux', 1.0)
    kappa = np.clip(kappa, 0.01, 0.99)
    
    # φ: Filter efficiency
    S_passed = data.get('signal_passed', 0.8)
    N_passed = data.get('noise_passed', 0.2)
    phi = S_passed / (S_passed + N_passed) if (S_passed + N_passed) > 0 else 0.5
    phi = np.clip(phi, 0.01, 0.99)
    
    # ε*: Target error rate
    epsilon_star = data.get('error_rate', 0.1) / data.get('max_error', 1.0)
    epsilon_star = np.clip(epsilon_star, 0.001, 0.99)
    
    # μ: Memory ratio
    mu = data.get('memory_time', 100) / data.get('system_time', 1.0)
    mu = max(mu, 1.0)
    
    # γ: Damping ratio
    gamma = data.get('damping_ratio', 1.0)
    gamma = max(gamma, 0.01)
    
    # Θ: Foam intensity
    theta = data.get('turbulence', 1.0) * data.get('complexity', 1.0)
    theta = max(theta, 0.01)
    
    return UniversalityVector(
        kappa=kappa,
        phi=phi,
        epsilon_star=epsilon_star,
        mu=mu,
        gamma=gamma,
        theta=theta
    )


# =============================================================================
# VIABILITY SCORE AND OPTIMIZATION
# =============================================================================

def viability_score(u: UniversalityVector, 
                    S: float = 1.0, N: float = 0.5,
                    lambda_B: float = 1.0, lambda_E: float = 1.0,
                    Q_target: float = 0.2) -> float:
    """
    Compute viability score J(u⃗)
    
    J = I(usable info) - C_energy(Θ) - λ_B·Var(x) - λ_E·(Q-Q*)²
    
    Args:
        u: Universality vector
        S: Signal power
        N: Noise power
        lambda_B: Weight for boundary instability
        lambda_E: Weight for uncertainty drift
        Q_target: Target uncertainty level
    
    Returns:
        Viability score (higher is better)
    """
    # Information gain
    I = info_capacity(S, N, u.phi)
    
    # Energy cost from foam zone
    foam = foam_cost_gain(u.theta)
    C_energy = foam['dissipation']
    
    # Boundary instability (approximated by deviation from critical damping)
    boundary_instability = (u.gamma - 1.0) ** 2
    
    # Uncertainty drift (error rate deviation from target)
    uncertainty_drift = (u.epsilon_star - Q_target) ** 2
    
    # Total score
    J = I - C_energy - lambda_B * boundary_instability - lambda_E * uncertainty_drift
    
    return J


def optimize_u_vector(objective: Callable[[UniversalityVector], float],
                      region: StableOperationRegion = StableOperationRegion(),
                      method: str = 'differential_evolution') -> UniversalityVector:
    """
    Find optimal universality vector within stable operation region
    
    Args:
        objective: Function to maximize (takes UniversalityVector, returns float)
        region: Stable operation region constraints
        method: Optimization method ('differential_evolution' or 'minimize')
    
    Returns:
        Optimal UniversalityVector
    """
    bounds = [
        region.kappa_range,
        region.phi_range,
        region.epsilon_range,
        region.mu_range,
        region.gamma_range,
        region.theta_range
    ]
    
    def neg_objective(x):
        u = UniversalityVector.from_array(x)
        return -objective(u)
    
    if method == 'differential_evolution':
        result = differential_evolution(neg_objective, bounds, seed=42, maxiter=1000)
    else:
        x0 = np.array([np.mean(b) for b in bounds])
        result = minimize(neg_objective, x0, bounds=bounds, method='L-BFGS-B')
    
    return UniversalityVector.from_array(result.x)


# =============================================================================
# GOVERNOR OPERATOR (ERROR MODULATION)
# =============================================================================

class GovernorOperator:
    """
    The Governor Operator 𝔈 for controlled error/uncertainty
    
    Enforces: Q_min < Q(t) < Q_max
    Control law: dQ/dt = λ(ε* - ε_eff(t))
    """
    
    def __init__(self, Q_min: float = 0.05, Q_max: float = 0.4, 
                 epsilon_star: float = 0.15, lambda_rate: float = 0.1):
        self.Q_min = Q_min
        self.Q_max = Q_max
        self.epsilon_star = epsilon_star
        self.lambda_rate = lambda_rate
    
    def dynamics(self, Q: float, epsilon_eff: float) -> float:
        """
        Compute dQ/dt
        
        Args:
            Q: Current uncertainty level
            epsilon_eff: Effective error rate (measured)
        
        Returns:
            Rate of change of uncertainty
        """
        dQ_dt = self.lambda_rate * (self.epsilon_star - epsilon_eff)
        
        # Enforce bounds
        if Q <= self.Q_min and dQ_dt < 0:
            dQ_dt = 0
        if Q >= self.Q_max and dQ_dt > 0:
            dQ_dt = 0
        
        return dQ_dt
    
    def is_viable(self, Q: float) -> bool:
        """Check if uncertainty is within viable band"""
        return self.Q_min < Q < self.Q_max


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main():
    """Demonstrate the Universal Constraint Mathematics framework"""
    
    print("=" * 60)
    print("UNIVERSAL CONSTRAINT MATHEMATICS: Demonstration")
    print("=" * 60)
    
    # 1. Create a boundary system
    print("\n1. BOUNDARY SYSTEM DYNAMICS")
    print("-" * 40)
    boundary = BoundarySystem(omega_0=1.0, gamma=0.7, kappa=0.6)
    solution = boundary.solve(t_span=(0, 20), x0=0, x_dot0=0, P_in=1.0)
    print(f"   Solved boundary dynamics: {len(solution['t'])} time points")
    print(f"   Final state: x = {solution['x'][-1]:.4f}")
    
    # 2. Information capacity
    print("\n2. INFORMATION FLOW")
    print("-" * 40)
    S, N = 1.0, 0.5
    phi_opt = optimal_filter_efficiency(S, N)
    C_opt = info_capacity(S, N, phi_opt)
    print(f"   Signal: {S}, Noise: {N}")
    print(f"   Optimal filter efficiency: φ* = {phi_opt:.4f}")
    print(f"   Maximum capacity: C = {C_opt:.4f} bits")
    
    # 3. Selective exchange
    print("\n3. SELECTIVE EXCHANGE MATRIX")
    print("-" * 40)
    exchange = create_exchange_matrix()
    for i, t in enumerate(exchange['types']):
        print(f"   {t}: π = {exchange['permeability'][i]:.4f}")
    
    # 4. Foam zone scaling
    print("\n4. FOAM ZONE SCALING")
    print("-" * 40)
    theta_opt = optimal_foam_intensity()
    foam = foam_cost_gain(theta_opt)
    print(f"   Optimal foam intensity: Θ* = {theta_opt:.4f}")
    print(f"   Processing gain: {foam['processing']:.4f}")
    print(f"   Energy cost: {foam['dissipation']:.4f}")
    print(f"   Net gain: {foam['net_gain']:.4f}")
    
    # 5. Measure u-vector from sample data
    print("\n5. UNIVERSALITY VECTOR MEASUREMENT")
    print("-" * 40)
    sample_data = {
        'exchange_flux': 0.6,
        'max_flux': 1.0,
        'signal_passed': 0.82,
        'noise_passed': 0.18,
        'error_rate': 0.0001,
        'max_error': 0.1,
        'memory_time': 1000,
        'system_time': 1,
        'damping_ratio': 1.1,
        'turbulence': 1.2,
        'complexity': 1.5
    }
    u = measure_u_vector(sample_data)
    print(f"   κ (permeability): {u.kappa:.4f}")
    print(f"   φ (filter): {u.phi:.4f}")
    print(f"   ε* (error): {u.epsilon_star:.6f}")
    print(f"   μ (memory): {u.mu:.1f}")
    print(f"   γ (damping): {u.gamma:.4f}")
    print(f"   Θ (foam): {u.theta:.4f}")
    print(f"   In stable region: {u.in_stable_region()}")
    
    # 6. Viability score
    print("\n6. VIABILITY SCORE")
    print("-" * 40)
    J = viability_score(u)
    print(f"   J(u⃗) = {J:.4f}")
    
    # 7. Optimize u-vector
    print("\n7. OPTIMAL UNIVERSALITY VECTOR")
    print("-" * 40)
    u_opt = optimize_u_vector(viability_score)
    J_opt = viability_score(u_opt)
    print(f"   κ* = {u_opt.kappa:.4f}")
    print(f"   φ* = {u_opt.phi:.4f}")
    print(f"   ε** = {u_opt.epsilon_star:.4f}")
    print(f"   μ* = {u_opt.mu:.1f}")
    print(f"   γ* = {u_opt.gamma:.4f}")
    print(f"   Θ* = {u_opt.theta:.4f}")
    print(f"   J(u⃗*) = {J_opt:.4f}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nThe mathematics is complete. The next step is DATA.")
    print("∇θ")


if __name__ == "__main__":
    main()
