from .nexus_gate import NexusGate, NexusDecision, DecisionRejected
from ..power_dynamics.legitimacy import LegitimacyScorer
from ..power_dynamics.influence import InfluenceScorer
from ..power_dynamics.adversarial import AdversarialSimulator
from ..core.policy import load_policy
from pathlib import Path

class PowerGate:
    def __init__(self, nexus_gate: NexusGate, policy_path: Path):
        self.nexus_gate = nexus_gate
        self.policy = load_policy(policy_path)
        self.legitimacy_scorer = LegitimacyScorer(self.policy)
        self.influence_scorer = InfluenceScorer(self.policy)
        self.adversarial_simulator = AdversarialSimulator(self.policy)

    def enforce_with_power_check(self, decision: NexusDecision) -> str:
        # 1. Adversarial Simulation
        risks = self.adversarial_simulator.run_simulation(decision.context)
        if risks:
            # For now, just log risks. In a future version, this could be a blocking factor.
            print(f"Adversarial risks identified: {risks}")

        # 2. Legitimacy & Influence Scoring
        # These would be retrieved from a persistent state store in a real application
        current_legitimacy = 0.8 
        last_validated = self.nexus_gate.get_last_validation_time()
        decayed_legitimacy = self.legitimacy_scorer.calculate_decay(current_legitimacy, last_validated)

        influence_modifier = self.influence_scorer.calculate_influence_modifier(decision.context.get("influence_methods", []))
        final_legitimacy = decayed_legitimacy * influence_modifier

        # 3. Collapse Threshold Check
        collapse_threshold = self.legitimacy_scorer.get_collapse_threshold(365, 2) # Example values
        if final_legitimacy < collapse_threshold:
            raise DecisionRejected(f"Decision rejected: Legitimacy ({final_legitimacy:.2f}) is below collapse threshold ({collapse_threshold:.2f}).")

        # 4. If all checks pass, proceed to Nexus Gate for ethical analysis
        return self.nexus_gate.enforce_decision(decision)
