"""
ECP v2.0 Enforcement Layer

Primary entry point for all decision enforcement, combining Power Dynamics
with the Nexus Gate for ethical analysis.
"""

from .power_gate import PowerGate
from .nexus_gate import NexusGate, NexusDecision, DecisionRejected

class ECPEnforcer:
    """Unified enforcement interface with Power Dynamics as default"""
    
    def __init__(self, policy_path, enable_power_dynamics: bool = True):
        self.nexus_gate = NexusGate()
        self.power_gate = PowerGate(self.nexus_gate, policy_path) if enable_power_dynamics else None
    
    def enforce(self, decision: NexusDecision) -> str:
        """Primary enforcement entry point with power dynamics"""
        if self.power_gate:
            return self.power_gate.enforce_with_power_check(decision)
        return self.nexus_gate.enforce_decision(decision)

__all__ = ["ECPEnforcer", "NexusDecision", "DecisionRejected"]
