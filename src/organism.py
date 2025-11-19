"""
ECHO ORGANISM v2.1 - MAIN ORGANISM CLASS
Classification: MILITARY-GRADE PRODUCTION-READY

The complete Echo Organism with:
- All 6 critical fixes implemented
- Military monitoring and validation
- Graceful degradation
- Comprehensive metrics

This is the main interface for running the Echo Organism.
"""

import numpy as np
import time
import logging
from typing import Tuple, List, Optional, Dict, Any
from collections import deque

# Core components
from .core.states import CreativeState, HomeostaticState
from .core.manifolds import project_creative_flat
from .core.energy import GlobalEnergyFunction

# Dynamics
from .dynamics.coupling import phi, psi, g_gain_adaptation, f_homeostatic
from .dynamics.gradients import GradientComputer

# Memory
from .memory.memory_system import MemorySystem

# Military systems
from .military.monitoring import MonitoringSystem, AlertLevel
from .military.validation import StateValidator, StateRecovery, GracefulDegradation, RecoveryMode

logger = logging.getLogger(__name__)


class EchoOrganism:
    """
    Military-Grade Echo Organism v2.1

    Features:
    - 896D creative state on product manifold
    - 8D homeostatic state with nonlinear dynamics
    - Global energy function with analytical gradients
    - Entropy-weighted memory system
    - Real-time monitoring and validation
    - Graceful degradation under stress

    Critical Fixes Implemented:
    1. Gradient alignment (896D)
    2. Global energy function
    3. Nonlinear homeostasis
    4. Memory unpredictability
    5. Thermal floor
    6. Safety fallback modes
    """

    def __init__(self,
                 seed: Optional[int] = None,
                 memory_capacity: int = 1000,
                 monitoring: bool = True):
        """
        Initialize Echo Organism.

        Args:
            seed: Random seed for reproducibility
            memory_capacity: Size of memory bank
            monitoring: Enable military monitoring
        """
        # Random number generator
        self.rng = np.random.default_rng(seed)

        # States
        self.x = CreativeState.random(self.rng)
        self.h = HomeostaticState.initial()
        self.x_prev = None

        # Energy function (Critical Fix #2)
        self.energy_fn = GlobalEnergyFunction()

        # Gradient computer (Critical Fix #1)
        self.gradient_computer = GradientComputer(method="analytical")

        # Memory system (Critical Fix #4)
        self.memory = MemorySystem(capacity=memory_capacity)

        # Timescale-separated averages
        self.novelty_short = deque(maxlen=10)   # Fast response
        self.novelty_long = deque(maxlen=100)   # Chronic adaptation
        self.coherence_long = deque(maxlen=100)
        self.stress_long = deque(maxlen=100)

        # Military systems
        self.monitoring_enabled = monitoring
        if monitoring:
            self.monitor = MonitoringSystem()
            self.validator = StateValidator()
            self.recovery = StateRecovery()
            self.degradation = GracefulDegradation()
        else:
            self.monitor = None
            self.validator = None
            self.recovery = None
            self.degradation = None

        # Parameters - TUNED FOR STABLE EXPLORATION
        self.params = {
            'inflow': np.array([0.1, 0.08, 0.12]),
            'cost_scaling': 0.05,  # Reduced to preserve resources
            'stress_drivers': (0.03, 0.02, 0.01),  # Lower stress accumulation
            'stress_relaxation': 0.15,  # Faster stress recovery
            'gain_learning_rate': 0.005,  # Slower gain adaptation
            'step_size': 0.4,  # Balanced step size
            'thermal_floor': 0.15,  # Balanced thermal noise
            'memory_store_interval': 3,  # Store memory every N steps
            'novelty_maintenance_threshold': 0.08,  # Inject noise below this
            'dt': 1.0
        }

        # Metrics tracking
        self.step_count = 0
        self.trajectory: List[Tuple[CreativeState, HomeostaticState]] = []
        self.metrics_history = {
            'novelty': [],
            'coherence': [],
            'stress': [],
            'resources': [],
            'gains': [],
            'global_energy': [],
            'gradient_norms': [],
            'constraints': []
        }

        logger.info(f"EchoOrganism v2.1 initialized (seed={seed})")

    def step(self) -> Tuple[CreativeState, HomeostaticState]:
        """
        Execute one step of organism dynamics.

        Returns:
            (new_creative_state, new_homeostatic_state)
        """
        step_start = time.time()

        try:
            # 1. Compute influence Φ(x)
            x_flat = self.x.to_flat()
            x_prev_flat = self.x_prev.to_flat() if self.x_prev else None
            memory_list = self.memory.get_all()

            influence = phi(x_flat, x_prev_flat, memory_list)
            n, c, u, rho, v = influence

            # 2. Update timescale-separated averages
            self._update_averages(n, c, np.mean(self.h.stress))

            # 3. Compute constraints Ψ(h)
            constraints = psi(self.h.resources, self.h.stress, self.h.gains)
            b, lam, alpha = constraints

            # 4. Homeostatic update (Critical Fix #3: Nonlinear)
            r_new, sigma_new, kappa_new = f_homeostatic(
                self.h.resources, self.h.stress, self.h.gains,
                influence, self.params, self.rng
            )

            # 5. Chronic gain adaptation (if enough history)
            if len(self.novelty_long) >= 20:
                n_bar = np.mean(self.novelty_long)
                c_bar = np.mean(self.coherence_long)
                sigma_bar = np.mean(self.stress_long)

                delta_kappa = g_gain_adaptation(n_bar, c_bar, sigma_bar)
                kappa_new = kappa_new + self.params['gain_learning_rate'] * delta_kappa
                kappa_new = np.clip(kappa_new, HomeostaticState.KAPPA_MIN, HomeostaticState.KAPPA_MAX)

            h_new = HomeostaticState(r_new, sigma_new, kappa_new)

            # 6. Compute gradient (Critical Fix #1: 896D aligned)
            grad = self.gradient_computer.compute_creative_gradient(
                x_flat, x_prev_flat, memory_list, constraints, self.energy_fn
            )

            # 7. Creative state update
            # Add thermal noise (Critical Fix #5)
            base_noise = self.params['thermal_floor']

            # NOVELTY MAINTENANCE: Boost noise when novelty is low
            if n < self.params.get('novelty_maintenance_threshold', 0.1):
                # Inject extra noise to escape local minima
                base_noise = base_noise * 3.0  # Triple the noise

            noise = self.rng.standard_normal(896) * base_noise
            dx = self.params['step_size'] * grad + noise

            x_new_flat = x_flat + dx
            x_new_flat = project_creative_flat(x_new_flat)  # Project to manifold
            x_new = CreativeState.from_flat(x_new_flat)

            # 8. Validation and recovery (Critical Fix #6)
            if self.validator:
                x_valid, x_errors = self.validator.validate_creative_state(x_new)
                h_valid, h_errors = self.validator.validate_homeostatic_state(h_new)

                if not x_valid or not h_valid:
                    mode = self.recovery.determine_recovery_mode(x_errors, h_errors)
                    if mode != RecoveryMode.NONE:
                        x_new = self.recovery.recover_creative_state(x_new, mode, self.rng)
                        h_new = self.recovery.recover_homeostatic_state(h_new, mode, self.rng)
                        logger.debug(f"Recovery mode {mode}: x_errors={x_errors}, h_errors={h_errors}")

            # 9. Update memory (only every N steps to maintain novelty)
            memory_interval = self.params.get('memory_store_interval', 5)
            if self.step_count % memory_interval == 0:
                self.memory.store(x_new.to_flat(), self.step_count, influence)

            # 10. Compute and record energy
            energy = self.energy_fn.compute_energy(x_new.to_flat(), x_flat, memory_list, constraints)

            # 11. Update metrics
            self._update_metrics(influence, constraints, energy, np.linalg.norm(grad))

            # 12. State transition
            self.x_prev = self.x
            self.x = x_new
            self.h = h_new
            self.step_count += 1

            # 13. Record trajectory
            self.trajectory.append((x_new, h_new))

            # 14. Monitoring
            if self.monitor:
                report = self.monitor.monitor_step(self, step_start)

                # Check for degradation
                if self.degradation:
                    health = self.monitor.get_health_score()
                    alerts = report.get('alerts', [])
                    mode = self.degradation.assess_degradation_needed(health, len(alerts))
                    self.degradation.apply_degradation(self, mode)

            return x_new, h_new

        except Exception as e:
            logger.error(f"Step failed at step {self.step_count}: {e}")

            # Emergency recovery
            if self.recovery:
                self.x = self.recovery.recover_creative_state(
                    self.x, RecoveryMode.HARD_RESET, self.rng
                )
                self.h = self.recovery.recover_homeostatic_state(
                    self.h, RecoveryMode.HARD_RESET, self.rng
                )

            return self.x, self.h

    def _update_averages(self, n: float, c: float, sigma: float):
        """Update timescale-separated signal averages"""
        self.novelty_short.append(n)
        self.novelty_long.append(n)
        self.coherence_long.append(c)
        self.stress_long.append(sigma)

    def _update_metrics(self, influence: np.ndarray, constraints: Tuple, energy: float, grad_norm: float):
        """Record metrics for monitoring"""
        n, c, u, rho, v = influence
        b, lam, alpha = constraints

        self.metrics_history['novelty'].append(float(n))
        self.metrics_history['coherence'].append(float(c))
        self.metrics_history['stress'].append(float(np.mean(self.h.stress)))
        self.metrics_history['resources'].append(float(np.mean(self.h.resources)))
        self.metrics_history['gains'].append(float(np.mean(self.h.gains)))
        self.metrics_history['global_energy'].append(float(energy))
        self.metrics_history['gradient_norms'].append(float(grad_norm))
        self.metrics_history['constraints'].append((float(b), float(lam), float(alpha)))

    def run(self, n_steps: int, verbose: bool = False) -> List[Tuple[CreativeState, HomeostaticState]]:
        """
        Run organism for multiple steps.

        Args:
            n_steps: Number of steps to run
            verbose: Print progress

        Returns:
            Trajectory list
        """
        for i in range(n_steps):
            self.step()

            if verbose and (i + 1) % 100 == 0:
                health = self.monitor.get_health_score() if self.monitor else 1.0
                novelty = np.mean(self.metrics_history['novelty'][-100:]) if self.metrics_history['novelty'] else 0.5
                stress = np.mean(self.metrics_history['stress'][-100:]) if self.metrics_history['stress'] else 0.3

                alert = ""
                if self.monitor:
                    alert = f" [{self.monitor.current_alert_level.value}]"

                print(f"Step {i+1}/{n_steps}: health={health:.2f}, novelty={novelty:.2f}, stress={stress:.2f}{alert}")

        return self.trajectory

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        if not self.metrics_history['novelty']:
            return {}

        metrics = {
            'basic': {
                'novelty_mean': np.mean(self.metrics_history['novelty']),
                'novelty_std': np.std(self.metrics_history['novelty']),
                'coherence_mean': np.mean(self.metrics_history['coherence']),
                'coherence_std': np.std(self.metrics_history['coherence']),
                'stress_mean': np.mean(self.metrics_history['stress']),
                'energy_mean': np.mean(self.metrics_history['global_energy']),
                'gradient_mean': np.mean(self.metrics_history['gradient_norms'])
            },
            'stability': {
                'novelty_min': np.min(self.metrics_history['novelty']),
                'novelty_max': np.max(self.metrics_history['novelty']),
                'energy_variance': np.var(self.metrics_history['global_energy']),
                'gradient_max': np.max(self.metrics_history['gradient_norms']),
                'bounded': (np.min(self.metrics_history['novelty']) > 0.01 and
                           np.max(self.metrics_history['stress']) < 0.99)
            },
            'system': {
                'steps_completed': self.step_count,
                'memory_size': len(self.memory),
                'memory_health': self.memory.health_metric()
            }
        }

        if self.monitor:
            metrics['monitoring'] = self.monitor.get_summary()

        if self.validator:
            metrics['validation'] = self.validator.get_stats()

        if self.recovery:
            metrics['recovery'] = self.recovery.get_stats()

        return metrics

    def validate_safety_properties(self) -> Dict[str, bool]:
        """
        Validate mathematical safety properties.

        Returns:
            Dictionary of property checks
        """
        if not self.metrics_history['novelty']:
            return {'error': 'No data to validate'}

        return {
            'bounded_exploration': np.all(np.array(self.metrics_history['novelty']) >= 0),
            'no_collapse': np.min(self.metrics_history['novelty']) > 0.01,
            'stress_bounded': np.all(np.array(self.metrics_history['stress']) <= 1.0),
            'resources_positive': np.all(np.array(self.metrics_history['resources']) >= 0),
            'energy_finite': np.all(np.isfinite(self.metrics_history['global_energy'])),
            'gradients_bounded': np.max(self.metrics_history['gradient_norms']) < 10.0
        }


def create_organism(seed: int = None, **kwargs) -> EchoOrganism:
    """Factory function for creating organisms"""
    return EchoOrganism(seed=seed, **kwargs)
