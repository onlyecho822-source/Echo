# ECP v2.0 "Pressure Engine" - Project Manager Decision Log

**Project Manager:** Manus AI
**Date:** December 14, 2025
**Objective:** Integrate Nexus Gate, Power Dynamics, and Pressure Engine concepts into ECP v1.1, making all necessary architectural decisions independently.

---

### Architectural & Strategic Decisions

| ID | Decision | Rationale |
| :--- | :--- | :--- |
| **D01** | **Upgrade to ECP v2.0 "Pressure Engine"** | The shift from ethics-based governance to physics-based stability enforcement is a fundamental architectural change, warranting a major version bump. |
| **D02** | **Establish Two-Stage Gated Execution Flow** | The new Power Gate will act as a mandatory, pre-execution membrane. The existing ECP v1.1 gate (renamed NexusGate) will run *after* it. Flow: `Intent -> PowerGate (Stability Check) -> NexusGate (Ethical Analysis) -> Execution`. |
| **D03** | **Power Gate is Blocking by Default** | To enforce stability, the Power Gate must reject actions that exceed collapse thresholds. Rejected actions will not proceed to ethical analysis. |
| **D04**| **Enforcement is Mandatory & Non-Bypassable** | The documents are explicit: "If it were optional, it would be bypassed." The new layer will be architecturally mandatory for all registered agentive actions. |
| **D05** | **Create New `power_dynamics` Sub-Package** | To keep the new, complex logic organized, a new package `src/ecp/power_dynamics/` will house `legitimacy.py`, `influence.py`, and `adversarial.py`. |
| **D06** | **Retain ECP v1.1 Flow for Ethical Analysis** | The Power Gate assesses *stability*; the existing ECP flow assesses *ethical disagreement*. They serve different purposes and will coexist. Actions must pass both gates. |
| **D07** | **Implement Rule-Based Adversarial Simulation** | The "Sun Tzu Red-Team" concept will be implemented as a rule-based simulation in `adversarial.py` to check for power concentration and second-order risks. |
| **D08** | **Legitimacy is a Quantifiable, Decaying Metric** | Legitimacy will be modeled as a numerical value (0.0-1.0) that decays over time and is impacted by violations and dissent, as per the document's physics-based model. |
| **D09** | **Influence is a First-Class Signal** | Influence methods (Framing, Praise, etc.) will be tracked as part of the decision context and will directly impact the legitimacy score, treating them as potential attack vectors. |
| **D10** | **Unify Enforcement Under a Single Interface** | An `ECPEnforcer` class will be created to manage the two-gate system, making the integration clean and explicit. |
| **D11** | **Rename Existing `gate.py` to `nexus_gate.py`** | To align with the new terminology in the provided documents and clearly distinguish the two gates. |
| **D12** | **Update All Documentation to Reflect v2.0** | All READMEs, architecture documents, and governance models will be updated to reflect the new two-gate, pressure-based system. |
| **D13** | **Create New `power_gate.py` as Primary Entry** | This new module will be the single entry point for all decisions, orchestrating the checks against the `power_dynamics` sub-package. |
| **D14** | **Human Rulings Can Restore Legitimacy** | A human-issued ruling on an escalated case will have the ability to partially or fully restore a decayed legitimacy score, reinforcing human sovereignty. |
| **D15** | **Reject Actions, Don't Just Flag** | The Pressure Engine's purpose is to prevent collapse. Therefore, it will hard-reject destabilizing actions rather than just escalating them, which is the role of the NexusGate. |

---

**Total Decisions Made:** 15
