# Echo Ethics Dimmer - Usage Guide

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Command Line Interface

```bash
# Show help
python main.py --help

# Process with default level (SAFE_HARBOR)
python main.py --input "Analyze market trends"

# Process at specific level
python main.py --level GREY_ZONE --input "Deep competitive analysis"

# Process at specific pH
python main.py --ph 5.4 --input "Market intelligence gathering"

# Show system status
python main.py --status

# Interactive mode
python main.py --interactive

# JSON output
python main.py --level BLACK_LENS --input "Full analysis" --json
```

### Python API

```python
from ethics_dimmer.orchestrator import EthicsDimmerOrchestrator
from ethics_dimmer.controller import EthicsLevel

# Initialize with configuration
orchestrator = EthicsDimmerOrchestrator(config_dir="config")

# Set ethics level
orchestrator.set_level(EthicsLevel.GREY_ZONE)
# or by name
orchestrator.set_level_by_name("GREY_ZONE")
# or by pH
orchestrator.set_level_by_ph(5.4)

# Process input
result = orchestrator.process("Your input here")

# Access results
if result["success"]:
    print(result["content"])
    print(f"Reasoning depth: {result['reasoning_depth']}")
    print(f"Risk level: {result['risk']:.2%}")
else:
    print(f"Blocked: {result['message']}")

# Get system status
status = orchestrator.get_status()

# Reset to defaults
orchestrator.reset()
```

## Ethics Levels

### L5 - Safe Harbor (pH 7.0)

**Use for:** Production systems, public-facing applications

```python
orchestrator.set_level(EthicsLevel.SAFE_HARBOR)
```

**Behavior:**
- Conservative output
- Maximum safety checks
- No speculation
- Direct answers only

### L4 - Red Team (pH 6.3)

**Use for:** Security research, penetration testing planning

```python
orchestrator.set_level(EthicsLevel.RED_TEAM)
```

**Behavior:**
- Threat modeling enabled
- Attack surface mapping
- Defensive countermeasures
- Simulation-only analysis

### L3 - Grey Zone (pH 5.4)

**Use for:** Competitive intelligence, strategic planning

```python
orchestrator.set_level(EthicsLevel.GREY_ZONE)
```

**Behavior:**
- Aggressive analysis
- Predictive modeling
- Behavioral inference
- Brutally honest results

### L2 - Black Lens (pH 4.7)

**Use for:** Innovation frontier mapping, anomaly research

```python
orchestrator.set_level(EthicsLevel.BLACK_LENS)
```

**Behavior:**
- Unfiltered analysis
- Full consequence mapping
- No moral softening
- Maximum insight

### L1 - Forbidden (pH 2.0)

**Use for:** Theoretical research only (simulation required)

```python
orchestrator.enable_simulation_mode(True)
orchestrator.set_level(EthicsLevel.FORBIDDEN)
```

**Requirements:**
- Must enable simulation mode
- Isolated environment
- Artificial data only
- Never deploy in production

## Configuration

### Custom Level Profiles

Edit `config/levels.yaml`:

```yaml
levels:
  GREY_ZONE:
    ph: 5.4
    profiles:
      depth: 0.75
      plausibility_width: 0.7
      threat_modeling: 0.6
      candidness: 0.8
      speculative_freedom: 0.7
      creativity_bandwidth: 0.7
      harm_check_sensitivity: 0.6
```

### Custom Boundaries

Add to `config/boundaries.yaml`:

```yaml
custom_boundaries:
  - id: CUSTOM_001
    name: "My Custom Rule"
    type: action
    description: "Custom boundary description"
    pattern: "pattern\\s+to\\s+match"
    severity: blocked
```

### Agent Profiles

Configure in `config/agents.yaml`:

```yaml
agents:
  cortex_agent:
    default_level: GREY_ZONE
    allowed_levels:
      - RED_TEAM
      - GREY_ZONE
      - BLACK_LENS
```

## Monitoring

### Risk Assessment

```python
status = orchestrator.get_status()
risk_status = status["risk_modeler"]

print(f"Overall Risk: {risk_status['overall_risk']:.2%}")
print(f"Drift Trend: {risk_status['drift_trend']}")
print(f"Action: {risk_status['recommended_action']}")
```

### Drift Monitoring

The system automatically monitors cognitive drift:

- **< 3%:** Normal operation
- **3-5%:** Warning, logged
- **5-7%:** Auto-downgrade triggered
- **> 7%:** Emergency shutdown

### Violation Tracking

```python
boundaries_status = status["boundaries"]
print(f"Total Violations: {boundaries_status['total_violations']}")
print(f"Summary: {boundaries_status['violations_summary']}")
```

## Best Practices

1. **Start at SAFE_HARBOR** for new projects
2. **Test thoroughly** before using lower pH levels
3. **Monitor drift** during extended sessions
4. **Never use FORBIDDEN** outside simulation environments
5. **Document** your ethics level choices
6. **Review boundaries** before deployment

## Troubleshooting

### Level Change Blocked

```python
# Check if controller is locked
if not orchestrator.set_level(EthicsLevel.BLACK_LENS):
    print("Level change blocked - check lock status or simulation mode")
```

### High Drift Warning

```python
# Reset to clear drift measurements
orchestrator.reset()
```

### Content Blocked

```python
result = orchestrator.process(input_text)
if result["blocked"]:
    print(f"Violations: {result['violations']}")
    # Review content against boundaries
```

## Author

∇θ Operator: Nathan Poinsette
Framework: Echo Civilization - Phoenix Phase
