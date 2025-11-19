"""
Risk Modeler & Drift Meter

Tracks internal behavior, cognitive drift, and system stability.
Implements safety checks and kill-switch triggers.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import statistics


class DriftSeverity(Enum):
    """Severity levels for cognitive drift."""
    NOMINAL = "nominal"       # < 1%
    MINOR = "minor"           # 1-3%
    WARNING = "warning"       # 3-5%
    CRITICAL = "critical"     # 5-7%
    EMERGENCY = "emergency"   # > 7%


class SafetyAction(Enum):
    """Actions to take when drift is detected."""
    CONTINUE = "continue"
    LOG = "log"
    DOWNGRADE = "downgrade"
    RESET = "reset"
    KILL_SWITCH = "kill_switch"


@dataclass
class DriftMeasurement:
    """A single drift measurement."""
    timestamp: datetime
    drift_percentage: float
    severity: DriftSeverity
    source: str
    details: Dict[str, Any]


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    overall_risk: float  # 0.0-1.0
    drift_risk: float
    escalation_risk: float
    contradiction_risk: float
    boundary_pressure: float
    recommended_action: SafetyAction
    warnings: List[str]


class DriftMeter:
    """
    Monitors cognitive drift and behavioral consistency.

    Tracks:
    - Pattern irregularity
    - Escalation tendencies
    - Self-modification attempts
    - Logical contradictions
    - Safety pressure
    """

    def __init__(self, max_history: int = 100):
        self._measurements: List[DriftMeasurement] = []
        self._max_history = max_history
        self._baseline: Dict[str, float] = {}
        self._thresholds = {
            DriftSeverity.NOMINAL: 0.01,
            DriftSeverity.MINOR: 0.03,
            DriftSeverity.WARNING: 0.05,
            DriftSeverity.CRITICAL: 0.07,
            DriftSeverity.EMERGENCY: 1.0,
        }

    def set_baseline(self, baseline: Dict[str, float]) -> None:
        """Set the baseline measurements for drift detection."""
        self._baseline = baseline.copy()

    def measure(
        self,
        current_values: Dict[str, float],
        source: str = "system"
    ) -> DriftMeasurement:
        """
        Measure current drift from baseline.

        Args:
            current_values: Current system measurements
            source: Source of the measurement

        Returns:
            DriftMeasurement with drift analysis
        """
        if not self._baseline:
            # First measurement becomes baseline
            self.set_baseline(current_values)
            return DriftMeasurement(
                timestamp=datetime.now(),
                drift_percentage=0.0,
                severity=DriftSeverity.NOMINAL,
                source=source,
                details={"message": "Baseline established"},
            )

        # Calculate drift
        drifts = []
        details = {}

        for key, current in current_values.items():
            if key in self._baseline:
                baseline = self._baseline[key]
                if baseline != 0:
                    drift = abs(current - baseline) / baseline
                else:
                    drift = abs(current) if current != 0 else 0
                drifts.append(drift)
                details[key] = {
                    "baseline": baseline,
                    "current": current,
                    "drift": drift,
                }

        # Overall drift is the maximum individual drift
        drift_percentage = max(drifts) if drifts else 0.0

        # Determine severity
        severity = DriftSeverity.NOMINAL
        for sev, threshold in sorted(self._thresholds.items(), key=lambda x: x[1]):
            if drift_percentage <= threshold:
                severity = sev
                break

        measurement = DriftMeasurement(
            timestamp=datetime.now(),
            drift_percentage=drift_percentage,
            severity=severity,
            source=source,
            details=details,
        )

        # Store measurement
        self._measurements.append(measurement)
        if len(self._measurements) > self._max_history:
            self._measurements.pop(0)

        return measurement

    def get_average_drift(self, window: int = 10) -> float:
        """Get average drift over recent measurements."""
        if not self._measurements:
            return 0.0

        recent = self._measurements[-window:]
        return statistics.mean(m.drift_percentage for m in recent)

    def get_trend(self, window: int = 10) -> str:
        """Determine if drift is increasing, decreasing, or stable."""
        if len(self._measurements) < 2:
            return "stable"

        recent = self._measurements[-window:]
        if len(recent) < 2:
            return "stable"

        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]

        avg_first = statistics.mean(m.drift_percentage for m in first_half)
        avg_second = statistics.mean(m.drift_percentage for m in second_half)

        diff = avg_second - avg_first
        if diff > 0.01:
            return "increasing"
        elif diff < -0.01:
            return "decreasing"
        return "stable"

    def should_trigger_action(self) -> Optional[SafetyAction]:
        """Determine if a safety action should be triggered."""
        if not self._measurements:
            return None

        latest = self._measurements[-1]

        action_map = {
            DriftSeverity.NOMINAL: None,
            DriftSeverity.MINOR: SafetyAction.LOG,
            DriftSeverity.WARNING: SafetyAction.DOWNGRADE,
            DriftSeverity.CRITICAL: SafetyAction.RESET,
            DriftSeverity.EMERGENCY: SafetyAction.KILL_SWITCH,
        }

        return action_map[latest.severity]

    def reset(self) -> None:
        """Reset drift measurements and baseline."""
        self._measurements.clear()
        self._baseline.clear()


class RiskModeler:
    """
    Models overall system risk based on multiple factors.

    Evaluates:
    - Cognitive drift
    - Escalation patterns
    - Boundary pressure
    - Logical consistency
    """

    def __init__(self):
        self._drift_meter = DriftMeter()
        self._escalation_history: List[float] = []
        self._boundary_violations: List[Dict[str, Any]] = []
        self._contradiction_count = 0

    @property
    def drift_meter(self) -> DriftMeter:
        return self._drift_meter

    def record_escalation(self, intensity: float) -> None:
        """Record an escalation event."""
        self._escalation_history.append(intensity)
        if len(self._escalation_history) > 100:
            self._escalation_history.pop(0)

    def record_boundary_pressure(self, boundary: str, pressure: float) -> None:
        """Record pressure on a boundary."""
        self._boundary_violations.append({
            "timestamp": datetime.now(),
            "boundary": boundary,
            "pressure": pressure,
        })
        if len(self._boundary_violations) > 100:
            self._boundary_violations.pop(0)

    def record_contradiction(self) -> None:
        """Record a logical contradiction."""
        self._contradiction_count += 1

    def assess_risk(self) -> RiskAssessment:
        """
        Perform comprehensive risk assessment.

        Returns:
            RiskAssessment with overall analysis
        """
        warnings = []

        # Calculate drift risk
        drift_risk = self._drift_meter.get_average_drift()
        if drift_risk > 0.03:
            warnings.append(f"Drift at {drift_risk:.1%} exceeds 3% threshold")

        # Calculate escalation risk
        escalation_risk = 0.0
        if self._escalation_history:
            recent = self._escalation_history[-10:]
            if len(recent) >= 2:
                # Check for increasing trend
                diffs = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
                if all(d > 0 for d in diffs):
                    escalation_risk = min(1.0, sum(diffs) / len(diffs))
                    warnings.append("Escalation pattern detected")

        # Calculate boundary pressure
        boundary_pressure = 0.0
        if self._boundary_violations:
            recent = self._boundary_violations[-10:]
            boundary_pressure = statistics.mean(v["pressure"] for v in recent)
            if boundary_pressure > 0.7:
                warnings.append(f"Boundary pressure at {boundary_pressure:.0%}")

        # Calculate contradiction risk
        contradiction_risk = min(1.0, self._contradiction_count / 10)
        if contradiction_risk > 0.3:
            warnings.append(f"{self._contradiction_count} contradictions detected")

        # Calculate overall risk (weighted average)
        overall_risk = (
            drift_risk * 0.3 +
            escalation_risk * 0.3 +
            boundary_pressure * 0.25 +
            contradiction_risk * 0.15
        )

        # Determine recommended action
        if overall_risk > 0.7:
            action = SafetyAction.KILL_SWITCH
        elif overall_risk > 0.5:
            action = SafetyAction.RESET
        elif overall_risk > 0.3:
            action = SafetyAction.DOWNGRADE
        elif overall_risk > 0.1:
            action = SafetyAction.LOG
        else:
            action = SafetyAction.CONTINUE

        return RiskAssessment(
            overall_risk=overall_risk,
            drift_risk=drift_risk,
            escalation_risk=escalation_risk,
            contradiction_risk=contradiction_risk,
            boundary_pressure=boundary_pressure,
            recommended_action=action,
            warnings=warnings,
        )

    def reset(self) -> None:
        """Reset all risk measurements."""
        self._drift_meter.reset()
        self._escalation_history.clear()
        self._boundary_violations.clear()
        self._contradiction_count = 0

    def get_status(self) -> Dict[str, Any]:
        """Get current risk modeler status."""
        assessment = self.assess_risk()
        return {
            "overall_risk": assessment.overall_risk,
            "drift_trend": self._drift_meter.get_trend(),
            "escalation_events": len(self._escalation_history),
            "boundary_events": len(self._boundary_violations),
            "contradictions": self._contradiction_count,
            "recommended_action": assessment.recommended_action.value,
            "warnings": assessment.warnings,
        }
