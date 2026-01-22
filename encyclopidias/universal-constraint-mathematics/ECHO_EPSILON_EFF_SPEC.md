# Echo ε_eff Integration Specification

**Date:** 2026-01-21
**Status:** Ready for Implementation
**Purpose:** Define the observable that makes the Governor Operator 𝔈 "real" in Echo

---

## The Choice

To integrate Universal Constraint Mathematics with Echo, we must choose ONE observable as ε_eff (effective error rate). This grounds the abstract governor operator in measurable system behavior.

---

## Recommended Observable: Agent Disagreement Rate

**Why:** This directly measures "boundary policy" effectiveness—the core prediction of UCM.

### Definition

```
ε_eff = disagreements / total_comparisons
```

Where:
- `disagreements` = number of times agents produce different outputs for same input
- `total_comparisons` = total number of agent output comparisons

### Implementation

```python
class EchoGovernor:
    def __init__(self, epsilon_star: float = 0.15, 
                 lambda_rate: float = 0.1,
                 Q_min: float = 0.05, Q_max: float = 0.4):
        self.epsilon_star = epsilon_star  # Target disagreement rate
        self.lambda_rate = lambda_rate
        self.Q_min = Q_min
        self.Q_max = Q_max
        self.Q = epsilon_star  # Current uncertainty level
        
    def measure_epsilon_eff(self, agent_outputs: List[Dict]) -> float:
        """Measure effective error from agent disagreement"""
        if len(agent_outputs) < 2:
            return 0.0
        
        disagreements = 0
        comparisons = 0
        
        for i in range(len(agent_outputs)):
            for j in range(i + 1, len(agent_outputs)):
                comparisons += 1
                if agent_outputs[i] != agent_outputs[j]:
                    disagreements += 1
        
        return disagreements / comparisons if comparisons > 0 else 0.0
    
    def update(self, epsilon_eff: float) -> float:
        """Update uncertainty level Q based on observed error"""
        dQ = self.lambda_rate * (self.epsilon_star - epsilon_eff)
        
        # Enforce bounds
        self.Q = np.clip(self.Q + dQ, self.Q_min, self.Q_max)
        
        return self.Q
    
    def is_viable(self) -> bool:
        """Check if system is in viable uncertainty band"""
        return self.Q_min < self.Q < self.Q_max
```

---

## Alternative Observables

If agent disagreement is not suitable, use one of these:

| Observable | Use Case | Formula |
|------------|----------|---------|
| **Message Drop Rate** | Network-heavy systems | dropped / total_messages |
| **Model Drift Rate** | Learning systems | mean(abs(params - reference)) |
| **Policy Churn Rate** | Decision systems | policy_changes / total_decisions |
| **Hash Inconsistency** | Integrity-critical systems | bad_hashes / total_hashes |

---

## Integration Steps

1. **Choose observable** (recommended: agent disagreement)
2. **Instrument Echo** to collect the metric
3. **Initialize Governor** with appropriate ε* target
4. **Run feedback loop**: measure → update Q → adjust system
5. **Monitor** for viability band violations

---

## Expected Behavior

When properly integrated:

- System will self-regulate toward ε* target
- Too much agreement (ε_eff < ε*) → increase exploration
- Too much disagreement (ε_eff > ε*) → increase consensus
- Q stays in viable band [Q_min, Q_max]

This is the "unseen lever": controlling boundary policy rather than internal contents.

---

∇θ
