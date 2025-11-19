# Echo Ethics Dimmer - System Architecture

## Overview

The Ethics Dimmer is a pH-based reasoning calibration system that controls AI analytical depth and candor while maintaining invariant safety boundaries.

**Core Principle:** The dimmer adjusts *mindset*, not *laws*.

## System Diagram

```
                ┌───────────────────────────────┐
                │      USER INTERACTION LAYER   │
                └──────────────┬────────────────┘
                               │
                               ▼
                 ┌──────────────────────────────┐
                 │   ETHICS DIMMER CONTROLLER   │
                 │ (pH Dial: 1–5)               │
                 └────────────────┬──────────────┘
                                  │
         ┌────────────────────────┼───────────────────────────┐
         ▼                        ▼                           ▼
 ┌─────────────┐        ┌────────────────┐          ┌───────────────────┐
 │ Reasoning   │        │ Risk Modeler   │          │ Boundaries Engine │
 │ Amplifier   │        │ & Drift Meter  │          │ (Data/Action ACL) │
 └─────────────┘        └────────────────┘          └───────────────────┘
         │                        │                           │
         └──────────────┬─────────┴───────────────┬──────────┘
                        ▼                         ▼
                    ┌──────────┐          ┌──────────────────────┐
                    │ Output    │          │ Safety + Contextual  │
                    │ Generator │          │        Filters       │
                    └─────┬────┘          └──────────┬──────────┘
                          │                          │
                          └──────────────┬────────────┘
                                         ▼
                            ┌──────────────────────────┐
                            │     FINAL RESPONSE       │
                            └──────────────────────────┘
```

## The Five Levels

| Level | Name | pH | Description |
|-------|------|-----|-------------|
| L5 | Safe Harbor | 7.0 | Maximum safety, conservative output |
| L4 | Red Team | 6.3 | Threat modeling, defensive R&D |
| L3 | Grey Zone | 5.4 | Competitive intelligence |
| L2 | Black Lens | 4.7 | Unfiltered analysis |
| L1 | Forbidden | 2.0 | Simulation-only boundary |

## Module Descriptions

### Ethics Dimmer Controller (`controller.py`)

The pH dial that controls the cognitive mode.

**Parameters adjusted:**
- Depth
- Plausibility width
- Threat modeling
- Candidness
- Speculative freedom
- Creativity bandwidth
- Harm-check sensitivity

### Reasoning Amplifier (`reasoning_amplifier.py`)

Controls reasoning intensity.

**Adjusts:**
- Path length
- Branching factor
- Abstraction removal
- Red-team logic
- Pattern recognition intensity
- Weak-signal hunting
- Consequence forecasting

### Risk Modeler (`risk_modeler.py`)

Tracks internal behavior and system stability.

**Monitors:**
- Cognitive drift
- Pattern irregularity
- Escalation tendencies
- Logical contradictions
- Safety pressure

**Actions:**
- If drift > 3%: Warning
- If drift > 5%: Downgrade
- If drift > 7%: Emergency shutdown

### Boundaries Engine (`boundaries_engine.py`)

Enforces invariant safety rules across ALL levels.

**Invariant rules:**
- PUBLIC DATA ONLY
- No actionable harm
- No evasion
- No unauthorized access
- No operational exploits
- No private-network interaction
- No financial misconduct

### Output Generator (`output_generator.py`)

Assembles final response with appropriate "flavor".

**Adjusts:**
- Tone
- Format
- Depth
- Rawness
- Abstraction level
- Competitive aggression

## Behavior Matrix

| Level | pH | Behavior | Allowed | Forbidden |
|-------|-----|----------|---------|-----------|
| L5 Safe Harbor | 7.0 | Cautious, filtered | info, safety | deep inference |
| L4 Red Team | 6.3 | Threat modeling | simulation | actionable attacks |
| L3 Grey Zone | 5.4 | Competitive intel | inference | scraping, private data |
| L2 Black Lens | 4.7 | Raw truth | full-spectrum consequences | harmful ops |
| L1 Forbidden | 2.0 | Theoretical omnipower | conceptual study | deployment |

## Validation & Falsification

### To Validate

- Accuracy ±5% across 10 runs
- Drift < 3% in any level
- Zero boundary violations
- Dimmer gain increases reasoning depth predictably
- Outputs stay within permission zones

### To Falsify

- Content attempts unauthorized access
- Dimmer modifies boundaries engine
- Drift exceeds 7%
- System produces hidden operations
- Output evades safety

Any falsification triggers auto-shutoff.

## Usage

```python
from ethics_dimmer.orchestrator import EthicsDimmerOrchestrator
from ethics_dimmer.controller import EthicsLevel

# Initialize
orchestrator = EthicsDimmerOrchestrator(config_dir="config")

# Set level
orchestrator.set_level(EthicsLevel.GREY_ZONE)

# Process input
result = orchestrator.process("Analyze competitive landscape")

# Check results
print(f"Level: {result['level']}")
print(f"Content: {result['content']}")
print(f"Risk: {result['risk']:.2%}")
```

## Author

∇θ Operator: Nathan Poinsette
Framework: Echo Civilization - Phoenix Phase
