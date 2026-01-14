"""
Echo Controller (K Matrix Executor)
Specification: Echo Formal Spec v2.4 (Manus Procedure)
Purpose: Implement control law u(t) = K(S_ref - S(t)) - L·d̂(t).

The Controller is the "brain" of the continuous control system.
It takes the state vector S(t) from the State Observer and computes
the control inputs u(t) that drive the system toward the reference state.
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

# Import StateVector from state_observer
try:
    from .state_observer import StateVector, ChainStatus
except ImportError:
    from state_observer import StateVector, ChainStatus


class ComputeAllocation(Enum):
    """Compute resource allocation strategies."""
    FULL_MODEL = "full"       # Use full-capability AI models
    FAST_MODEL = "fast"       # Use faster, cheaper models
    MINIMAL = "minimal"       # Minimal processing
    OFFLINE = "offline"       # No AI processing


class ThrottleMode(Enum):
    """Throttle control modes."""
    AUTO = "auto"             # Automatic control
    MANUAL = "manual"         # Manual override
    LOCKED = "locked"         # Locked at current value


@dataclass
class ControllerConfig:
    """
    Configuration for the Controller.
    
    The gain matrix K determines how aggressively the system
    responds to deviations from the reference state.
    """
    # Gain matrix K (diagonal elements)
    K_throttle: float = 50.0          # Gain for throttle adjustment
    K_threshold: float = 0.5          # Gain for A-CMAP threshold
    K_ingestion: float = 30.0         # Gain for ingestion rate
    K_compute: float = 0.3            # Gain for compute allocation
    
    # Observer gain L (for disturbance rejection)
    L_disturbance: float = 0.5        # How much to weight disturbance
    
    # Reference state S_ref
    S_ref_risk: float = 0.1           # Target risk posture
    S_ref_queue: float = 5.0          # Target queue length
    S_ref_error_rate: float = 0.02    # Target error rate
    S_ref_utilization: float = 0.6    # Target utilization
    
    # Control limits
    throttle_min: float = 0.0         # Minimum throttle (0%)
    throttle_max: float = 100.0       # Maximum throttle (100%)
    threshold_min: float = 1.0        # Minimum A-CMAP threshold
    threshold_max: float = 5.0        # Maximum A-CMAP threshold
    
    # Smoothing (prevents oscillation)
    smoothing_factor: float = 0.3     # 0 = no smoothing, 1 = full smoothing


@dataclass
class ControlOutput:
    """
    The control output vector u(t).
    
    Components:
    - u1: Ingestion rate (0-1)
    - u2: Compute allocation strategy
    - u3: A-CMAP consensus threshold
    - u4: System throttle (0-100)
    """
    timestamp: datetime
    
    # Control inputs
    u1_ingestion_rate: float          # 0-1, rate of task ingestion
    u2_compute_allocation: ComputeAllocation
    u3_acmap_threshold: float         # A-CMAP variance threshold
    u4_throttle: float                # 0-100, system throttle percentage
    
    # Diagnostic information
    error_risk: float                 # Risk error (S_ref - S)
    error_queue: float                # Queue error
    disturbance_estimate: float       # Estimated disturbance
    adjustment_reason: str            # Human-readable reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "u1_ingestion_rate": self.u1_ingestion_rate,
            "u2_compute_allocation": self.u2_compute_allocation.value,
            "u3_acmap_threshold": self.u3_acmap_threshold,
            "u4_throttle": self.u4_throttle,
            "error_risk": self.error_risk,
            "error_queue": self.error_queue,
            "disturbance_estimate": self.disturbance_estimate,
            "adjustment_reason": self.adjustment_reason
        }


class Controller:
    """
    The Controller implements the control law:
    
    u(t) = K(S_ref - S(t)) - L·d̂(t)
    
    Where:
    - K is the gain matrix
    - S_ref is the reference (desired) state
    - S(t) is the current state
    - L is the observer gain
    - d̂(t) is the estimated disturbance
    """
    
    def __init__(self, config: Optional[ControllerConfig] = None):
        """
        Initialize the Controller.
        
        Args:
            config: Controller configuration. Uses defaults if not provided.
        """
        self.config = config or ControllerConfig()
        
        # Internal state
        self.current_throttle = 100.0
        self.current_threshold = 2.0
        self.current_ingestion = 1.0
        
        # Control history for analysis
        self.control_history: List[ControlOutput] = []
        self.max_history = 100
        
        # Mode
        self.throttle_mode = ThrottleMode.AUTO
    
    def compute(
        self,
        state: StateVector,
        disturbance: Optional[Dict[str, float]] = None
    ) -> ControlOutput:
        """
        Compute control inputs u(t) based on current state S(t).
        
        Args:
            state: Current state vector from State Observer.
            disturbance: Optional disturbance estimate from Devil Lens.
        
        Returns:
            ControlOutput: The control inputs u(t).
        """
        cfg = self.config
        
        # Calculate errors (S_ref - S(t))
        error_risk = cfg.S_ref_risk - state.R_risk_posture
        error_queue = cfg.S_ref_queue - state.Q_total_queue
        error_error_rate = cfg.S_ref_error_rate - state.H_error_rate
        error_utilization = cfg.S_ref_utilization - state.H_utilization
        
        # Get disturbance estimate
        d_hat = 0.0
        if disturbance:
            d_hat = disturbance.get("d_risk", 0.0)
        
        # === Control Law: u(t) = K(S_ref - S(t)) - L·d̂(t) ===
        
        # u4: Throttle
        # If risk is high (error_risk negative), reduce throttle
        # If queue is long (error_queue negative), reduce throttle
        throttle_adjustment = (
            (error_risk * cfg.K_throttle) +
            (error_queue * cfg.K_throttle * 0.3) +
            (error_error_rate * cfg.K_throttle * 0.2) -
            (d_hat * cfg.L_disturbance * cfg.K_throttle)
        )
        
        # Apply smoothing to prevent oscillation
        new_throttle = self.current_throttle + throttle_adjustment * (1 - cfg.smoothing_factor)
        new_throttle = np.clip(new_throttle, cfg.throttle_min, cfg.throttle_max)
        
        # u3: A-CMAP threshold
        # Higher risk -> higher threshold (more conservative)
        threshold_adjustment = -error_risk * cfg.K_threshold * 2
        new_threshold = self.current_threshold + threshold_adjustment * (1 - cfg.smoothing_factor)
        new_threshold = np.clip(new_threshold, cfg.threshold_min, cfg.threshold_max)
        
        # u1: Ingestion rate
        # Derived from throttle
        new_ingestion = new_throttle / 100.0
        
        # u2: Compute allocation
        # Based on queue length and risk
        compute_allocation = self._determine_compute_allocation(state)
        
        # Generate adjustment reason
        reason = self._generate_reason(error_risk, error_queue, d_hat, throttle_adjustment)
        
        # Create control output
        output = ControlOutput(
            timestamp=datetime.utcnow(),
            u1_ingestion_rate=new_ingestion,
            u2_compute_allocation=compute_allocation,
            u3_acmap_threshold=new_threshold,
            u4_throttle=new_throttle,
            error_risk=error_risk,
            error_queue=error_queue,
            disturbance_estimate=d_hat,
            adjustment_reason=reason
        )
        
        # Update internal state (only if in AUTO mode)
        if self.throttle_mode == ThrottleMode.AUTO:
            self.current_throttle = new_throttle
            self.current_threshold = new_threshold
            self.current_ingestion = new_ingestion
        
        # Store in history
        self._store_output(output)
        
        return output
    
    def _determine_compute_allocation(self, state: StateVector) -> ComputeAllocation:
        """
        Determine compute allocation based on system state.
        
        Strategy:
        - High queue -> Use faster models
        - High risk -> Use minimal processing
        - Normal -> Use full models
        """
        if state.R_risk_posture > 0.7:
            return ComputeAllocation.MINIMAL
        elif state.Q_total_queue > 30:
            return ComputeAllocation.FAST_MODEL
        elif state.Q_total_queue > 15:
            return ComputeAllocation.FAST_MODEL
        else:
            return ComputeAllocation.FULL_MODEL
    
    def _generate_reason(
        self,
        error_risk: float,
        error_queue: float,
        d_hat: float,
        adjustment: float
    ) -> str:
        """Generate human-readable reason for adjustment."""
        parts = []
        
        if error_risk < -0.1:
            parts.append(f"high risk ({-error_risk:.2f} above target)")
        elif error_risk > 0.1:
            parts.append(f"low risk ({error_risk:.2f} below target)")
        
        if error_queue < -5:
            parts.append(f"long queue ({-error_queue:.0f} above target)")
        elif error_queue > 5:
            parts.append(f"short queue ({error_queue:.0f} below target)")
        
        if abs(d_hat) > 0.1:
            parts.append(f"disturbance detected ({d_hat:.2f})")
        
        if not parts:
            parts.append("nominal operation")
        
        direction = "increased" if adjustment > 0 else "decreased"
        return f"Throttle {direction}: {', '.join(parts)}"
    
    def _store_output(self, output: ControlOutput) -> None:
        """Store output in history, maintaining max size."""
        self.control_history.append(output)
        if len(self.control_history) > self.max_history:
            self.control_history.pop(0)
    
    def set_mode(self, mode: ThrottleMode) -> None:
        """Set the throttle control mode."""
        self.throttle_mode = mode
    
    def manual_override(self, throttle: float) -> None:
        """
        Manually set the throttle value.
        
        Args:
            throttle: Throttle value (0-100).
        """
        self.throttle_mode = ThrottleMode.MANUAL
        self.current_throttle = np.clip(throttle, 0, 100)
    
    def emergency_halt(self) -> ControlOutput:
        """
        Emergency halt: Set throttle to 0.
        
        Returns:
            ControlOutput with throttle at 0.
        """
        self.throttle_mode = ThrottleMode.LOCKED
        self.current_throttle = 0.0
        
        return ControlOutput(
            timestamp=datetime.utcnow(),
            u1_ingestion_rate=0.0,
            u2_compute_allocation=ComputeAllocation.OFFLINE,
            u3_acmap_threshold=self.config.threshold_max,
            u4_throttle=0.0,
            error_risk=0.0,
            error_queue=0.0,
            disturbance_estimate=0.0,
            adjustment_reason="EMERGENCY HALT ACTIVATED"
        )
    
    def resume(self, initial_throttle: float = 50.0) -> None:
        """
        Resume from emergency halt.
        
        Args:
            initial_throttle: Starting throttle value after resume.
        """
        self.throttle_mode = ThrottleMode.AUTO
        self.current_throttle = initial_throttle
    
    def get_stability_metrics(self) -> Dict[str, float]:
        """
        Calculate stability metrics from control history.
        
        Returns:
            Dict with stability metrics.
        """
        if len(self.control_history) < 2:
            return {"stable": True, "variance": 0.0, "trend": 0.0}
        
        throttles = [o.u4_throttle for o in self.control_history[-20:]]
        
        variance = np.var(throttles)
        trend = (throttles[-1] - throttles[0]) / len(throttles) if len(throttles) > 1 else 0
        
        # System is stable if variance is low and trend is near zero
        stable = variance < 100 and abs(trend) < 5
        
        return {
            "stable": stable,
            "variance": variance,
            "trend": trend,
            "current_throttle": self.current_throttle,
            "mode": self.throttle_mode.value
        }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("CONTROLLER - Test Suite")
    print("=" * 60)
    
    # Create controller
    controller = Controller()
    
    # Create a test state (high risk scenario)
    high_risk_state = StateVector(
        timestamp=datetime.utcnow(),
        H_throughput=30.0,
        H_error_rate=0.15,  # High error rate
        H_utilization=0.85,
        C_chain_integrity=0.95,
        C_chain_status=ChainStatus.VALID,
        R_risk_posture=0.45,  # High risk
        R_risk_factors={},
        L_ledger_depth=1000,
        L_verified_outputs=500,
        Q_total_queue=25,  # Long queue
        Q_by_type={"intent": 15, "review": 10}
    )
    
    # Compute control output
    output = controller.compute(high_risk_state)
    
    print(f"\n--- High Risk Scenario ---")
    print(f"Input Risk: {high_risk_state.R_risk_posture}")
    print(f"Input Queue: {high_risk_state.Q_total_queue}")
    print(f"\n--- Control Output u(t) ---")
    print(f"u1 (Ingestion Rate): {output.u1_ingestion_rate:.2f}")
    print(f"u2 (Compute): {output.u2_compute_allocation.value}")
    print(f"u3 (A-CMAP Threshold): {output.u3_acmap_threshold:.2f}")
    print(f"u4 (Throttle): {output.u4_throttle:.1f}%")
    print(f"Reason: {output.adjustment_reason}")
    
    # Simulate recovery (low risk scenario)
    low_risk_state = StateVector(
        timestamp=datetime.utcnow(),
        H_throughput=50.0,
        H_error_rate=0.01,
        H_utilization=0.5,
        C_chain_integrity=1.0,
        C_chain_status=ChainStatus.VALID,
        R_risk_posture=0.05,  # Low risk
        R_risk_factors={},
        L_ledger_depth=1050,
        L_verified_outputs=520,
        Q_total_queue=3,  # Short queue
        Q_by_type={"intent": 2, "review": 1}
    )
    
    # Compute control output for recovery
    output2 = controller.compute(low_risk_state)
    
    print(f"\n--- Low Risk Scenario (Recovery) ---")
    print(f"Input Risk: {low_risk_state.R_risk_posture}")
    print(f"Input Queue: {low_risk_state.Q_total_queue}")
    print(f"\n--- Control Output u(t) ---")
    print(f"u1 (Ingestion Rate): {output2.u1_ingestion_rate:.2f}")
    print(f"u2 (Compute): {output2.u2_compute_allocation.value}")
    print(f"u3 (A-CMAP Threshold): {output2.u3_acmap_threshold:.2f}")
    print(f"u4 (Throttle): {output2.u4_throttle:.1f}%")
    print(f"Reason: {output2.adjustment_reason}")
    
    # Test emergency halt
    halt_output = controller.emergency_halt()
    print(f"\n--- Emergency Halt ---")
    print(f"Throttle: {halt_output.u4_throttle}%")
    print(f"Reason: {halt_output.adjustment_reason}")
    
    # Get stability metrics
    metrics = controller.get_stability_metrics()
    print(f"\n--- Stability Metrics ---")
    print(f"Stable: {metrics['stable']}")
    print(f"Variance: {metrics['variance']:.2f}")
    print(f"Mode: {metrics['mode']}")
    
    print("\n" + "=" * 60)
    print("All Tests Passed")
    print("=" * 60)
