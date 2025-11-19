"""
ECHO ORGANISM v2.1 - VALIDATION & RECOVERY
Classification: PRODUCTION-READY

State validation and error recovery:
- Manifold constraint checking
- Automatic repair
- Graceful degradation
- Emergency fallback modes
"""

import numpy as np
import logging
from typing import Tuple, Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class RecoveryMode(Enum):
    """Recovery severity levels"""
    NONE = 0           # No recovery needed
    SOFT_REPAIR = 1    # Gentle correction
    HARD_RESET = 2     # Force to safe state
    EMERGENCY = 3      # Complete reinitialization


class StateValidator:
    """
    Validate organism state integrity.
    """

    def __init__(self):
        self.validation_count = 0
        self.failure_count = 0
        self.repair_count = 0

    def validate_creative_state(self, x) -> Tuple[bool, List[str]]:
        """
        Validate creative state constraints.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        x_flat = x.to_flat()

        # NaN/Inf check
        if not np.all(np.isfinite(x_flat)):
            nan_count = np.sum(~np.isfinite(x_flat))
            errors.append(f"Non-finite values: {nan_count}")

        # Dimension check
        if x.continuous.shape != (512,):
            errors.append(f"Wrong continuous shape: {x.continuous.shape}")
        if x.probabilistic.shape != (128,):
            errors.append(f"Wrong probabilistic shape: {x.probabilistic.shape}")
        if x.semantic.shape != (256,):
            errors.append(f"Wrong semantic shape: {x.semantic.shape}")

        # Simplex constraint
        prob_sum = np.sum(x.probabilistic)
        if abs(prob_sum - 1.0) > 1e-3:
            errors.append(f"Simplex sum: {prob_sum:.4f}")
        if np.any(x.probabilistic < -1e-6):
            errors.append("Negative probabilistic values")

        # Sphere constraint
        sem_norm = np.linalg.norm(x.semantic)
        if abs(sem_norm - 1.0) > 1e-3:
            errors.append(f"Semantic norm: {sem_norm:.4f}")

        # Bounds check
        if np.any(np.abs(x.continuous) > 15.0):
            errors.append("Continuous out of bounds")

        # Checksum
        if hasattr(x, 'verify_integrity') and not x.verify_integrity():
            errors.append("Checksum mismatch")

        self.validation_count += 1
        if errors:
            self.failure_count += 1

        return len(errors) == 0, errors

    def validate_homeostatic_state(self, h) -> Tuple[bool, List[str]]:
        """
        Validate homeostatic state bounds.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # NaN/Inf check
        all_vals = np.concatenate([h.resources, h.stress, h.gains])
        if not np.all(np.isfinite(all_vals)):
            errors.append("Non-finite values")

        # Shape checks
        if h.resources.shape != (3,):
            errors.append(f"Wrong resources shape: {h.resources.shape}")
        if h.stress.shape != (2,):
            errors.append(f"Wrong stress shape: {h.stress.shape}")
        if h.gains.shape != (3,):
            errors.append(f"Wrong gains shape: {h.gains.shape}")

        # Bounds checks
        if np.any(h.resources < 0) or np.any(h.resources > 1):
            errors.append(f"Resources out of bounds: {h.resources}")
        if np.any(h.stress < 0) or np.any(h.stress > 1):
            errors.append(f"Stress out of bounds: {h.stress}")
        if np.any(h.gains < h.KAPPA_MIN) or np.any(h.gains > h.KAPPA_MAX):
            errors.append(f"Gains out of bounds: {h.gains}")

        self.validation_count += 1
        if errors:
            self.failure_count += 1

        return len(errors) == 0, errors

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'total_validations': self.validation_count,
            'failures': self.failure_count,
            'repairs': self.repair_count,
            'failure_rate': self.failure_count / max(1, self.validation_count)
        }


class StateRecovery:
    """
    Recovery system for failed states.
    """

    def __init__(self):
        self.recovery_count = 0
        self.emergency_count = 0

    def determine_recovery_mode(self, x_errors: List[str], h_errors: List[str]) -> RecoveryMode:
        """
        Determine appropriate recovery mode based on errors.
        """
        total_errors = len(x_errors) + len(h_errors)

        if total_errors == 0:
            return RecoveryMode.NONE

        # Critical errors requiring hard reset
        critical_keywords = ['Non-finite', 'shape', 'Checksum']
        critical_count = sum(1 for e in x_errors + h_errors
                             if any(kw in e for kw in critical_keywords))

        if critical_count >= 2:
            return RecoveryMode.EMERGENCY
        elif critical_count >= 1:
            return RecoveryMode.HARD_RESET
        else:
            return RecoveryMode.SOFT_REPAIR

    def recover_creative_state(self, x, mode: RecoveryMode, rng: np.random.Generator = None):
        """
        Recover creative state based on mode.

        Args:
            x: Current (possibly invalid) state
            mode: Recovery mode
            rng: Random number generator

        Returns:
            Recovered state
        """
        if rng is None:
            rng = np.random.default_rng()

        self.recovery_count += 1

        if mode == RecoveryMode.NONE:
            return x

        elif mode == RecoveryMode.SOFT_REPAIR:
            # Just re-project to manifold
            from ..core.states import CreativeState
            return CreativeState.from_flat(x.to_flat())

        elif mode == RecoveryMode.HARD_RESET:
            # Reset to default + small perturbation
            from ..core.states import CreativeState

            # Keep some memory of current state
            current = x.to_flat()
            current = np.nan_to_num(current, nan=0.0, posinf=1.0, neginf=-1.0)

            # Mix with default
            default = CreativeState.random(rng).to_flat()
            recovered = 0.7 * default + 0.3 * np.clip(current, -5, 5)

            return CreativeState.from_flat(recovered)

        elif mode == RecoveryMode.EMERGENCY:
            # Complete reinitialization
            self.emergency_count += 1
            from ..core.states import CreativeState
            logger.warning("EMERGENCY: Full creative state reinitialization")
            return CreativeState.random(rng)

    def recover_homeostatic_state(self, h, mode: RecoveryMode, rng: np.random.Generator = None):
        """
        Recover homeostatic state based on mode.
        """
        if rng is None:
            rng = np.random.default_rng()

        self.recovery_count += 1

        if mode == RecoveryMode.NONE:
            return h

        elif mode == RecoveryMode.SOFT_REPAIR:
            # Just clip to bounds
            from ..core.states import HomeostaticState
            return HomeostaticState(
                np.clip(h.resources, 0.0, 1.0),
                np.clip(h.stress, 0.0, 1.0),
                np.clip(h.gains, h.KAPPA_MIN, h.KAPPA_MAX)
            )

        elif mode == RecoveryMode.HARD_RESET:
            # Reset to healthy operating point
            from ..core.states import HomeostaticState
            return HomeostaticState.initial()

        elif mode == RecoveryMode.EMERGENCY:
            # Complete reinitialization
            self.emergency_count += 1
            from ..core.states import HomeostaticState
            logger.warning("EMERGENCY: Full homeostatic state reinitialization")
            return HomeostaticState.initial()

    def get_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        return {
            'total_recoveries': self.recovery_count,
            'emergency_recoveries': self.emergency_count,
            'emergency_rate': self.emergency_count / max(1, self.recovery_count)
        }


class GracefulDegradation:
    """
    Manages graceful degradation under stress.
    """

    def __init__(self):
        self.current_mode = "FULL_CAPABILITY"
        self.degradation_history = []

        self.capability_levels = {
            'FULL_CAPABILITY': 1.0,
            'REDUCED_PRECISION': 0.8,
            'SAFE_MODE': 0.6,
            'MINIMAL_OPERATIONS': 0.4,
            'EMERGENCY_PRESERVATION': 0.2
        }

    def assess_degradation_needed(self, health_score: float, alert_count: int) -> str:
        """
        Determine appropriate operational mode.
        """
        if health_score < 0.2 or alert_count >= 3:
            return 'EMERGENCY_PRESERVATION'
        elif health_score < 0.4 or alert_count >= 2:
            return 'MINIMAL_OPERATIONS'
        elif health_score < 0.6 or alert_count >= 1:
            return 'SAFE_MODE'
        elif health_score < 0.8:
            return 'REDUCED_PRECISION'
        else:
            return 'FULL_CAPABILITY'

    def apply_degradation(self, organism, mode: str) -> Dict[str, Any]:
        """
        Apply degradation settings to organism.

        Returns parameter adjustments made.
        """
        old_mode = self.current_mode
        self.current_mode = mode

        adjustments = {}

        if mode == 'REDUCED_PRECISION':
            adjustments['step_size_factor'] = 0.8
            adjustments['noise_factor'] = 0.5

        elif mode == 'SAFE_MODE':
            adjustments['step_size_factor'] = 0.5
            adjustments['exploration_budget'] = 0.3

        elif mode == 'MINIMAL_OPERATIONS':
            adjustments['step_size_factor'] = 0.3
            adjustments['exploration_budget'] = 0.1

        elif mode == 'EMERGENCY_PRESERVATION':
            adjustments['step_size_factor'] = 0.1
            adjustments['exploration_budget'] = 0.0

        # Apply adjustments
        if 'step_size_factor' in adjustments and hasattr(organism, 'params'):
            original = organism.params.get('step_size', 0.5)
            organism.params['step_size'] = original * adjustments['step_size_factor']

        if mode != old_mode:
            self.degradation_history.append({
                'from': old_mode,
                'to': mode,
                'timestamp': np.datetime64('now')
            })
            logger.info(f"Degradation: {old_mode} -> {mode}")

        return adjustments

    def get_capability_factor(self) -> float:
        """Get current capability factor"""
        return self.capability_levels.get(self.current_mode, 1.0)
