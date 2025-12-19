># Echo Coordination System v1.0

## Physics-First AI Coordination with Emergent Ethics

**Core Principles:**
1. Events (physics) are immutable
2. Ethics require agency
3. Disagreement is information, not error
4. Humans create precedent, systems enforce
5. No hidden authority, no black boxes

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo
chmod +x setup.sh test.sh
./setup.sh

# 2. Run the forced disagreement test
./test.sh

# 3. View results
cat ai-coordination/consensus/*.json

# 4. Create a human ruling
python3 ai-coordination/scripts/create_human_ruling.py
```

## Architecture

- **Events/**: What happened (immutable reality)
- **Classifications/**: What it means (plural interpretations)
- **Consensus/**: How much disagreement (quantitative)
- **Rulings/**: Human precedent (authoritative)
- **Ethics/**: Baseline rules (minimal, immutable)

## Core Concepts

### Agency Gating
Only events with `agency_present: true` become cases for ethical review.
Natural disasters, accidents, and non-agentive phenomena are logged but not moralized.

### Plural Ethics
Multiple AIs can classify the same event differently. The system preserves all perspectives.

### Divergence Scoring
Quantitative measurement of disagreement across three axes:
1. Ethical status distance (40% weight)
2. Confidence difference (30% weight)
3. Risk assessment delta (30% weight)

### Human-in-the-Loop
When divergence > 0.4 or any AI flags "unethical", the system:
1. Creates a GitHub Issue
2. Logs the case
3. Waits for human ruling
4. Creates precedent for future events

## API

```python
from ai_coordination.scripts.ethical_ai_coordinator import EthicalAICoordinator

coord = EthicalAICoordinator(".", "your_ai_name")
event_id = coord.record_event(
    event_type="analysis",
    payload={"query": "Is this ethical?"},
    context={
        "causation": "ai",
        "agency_present": True,
        "duty_of_care": "medium",
        "knowledge_level": "full",
        "control_level": "direct"
    }
)

coord.classify_event(event_id, {
    "ethical_status": "permissible",
    "confidence": 0.85,
    "risk_estimate": "low",
    "reasoning": "Analysis shows no harm potential"
})
```

## Security Properties

✅ **Immutable Logs**: SHA-256 hash chain prevents tampering
✅ **Agency Gating**: No moralizing natural phenomena
✅ **Transparent Scoring**: Divergence formula is explicit
✅ **Plural Interpretation**: No single AI dominates truth
✅ **Human Sovereignty**: Final authority remains human

## Status

**System**: Production-ready v1.0
**Auto-Nate**: Active
**Test Coverage**: Forced disagreement scenario included
**Deployment**: Git + GitHub Actions ready

---

*"Truth precedes ethics. Agency gates responsibility. Disagreement is signal."*
