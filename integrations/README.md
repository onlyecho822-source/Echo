# Echo ↔ Agent-Zero Integration

This directory contains the integration layer between Echo and Agent-Zero.

## Overview

Agent-Zero is integrated as a Git submodule, providing autonomous validation, truth enforcement, and cross-domain analysis capabilities to the Echo platform.

## Components

- `agent_zero_bridge.py` - Main integration bridge
- `test_bridge.py` - Comprehensive integration tests

## Architecture

```
Echo (Public Repository)
    ↓
integrations/agent_zero_bridge.py (Integration Layer)
    ↓
agent-zero/ (Git Submodule - Private Repository)
    ├── src/autonomous/
    │   ├── dual_system.py (Uncontrolled/Controlled oscillation)
    │   └── kraken_agent_zero.py (Continuous monitoring)
    └── src/core/
        ├── zero_operator.py (Zero reference calculation)
        ├── consensus_protocol.py (Multi-agent consensus)
        └── temporal_sync.py (Multi-calendar alignment)
```

## Installation

### Clone with Submodules

```bash
# Clone Echo with Agent-Zero submodule
git clone --recurse-submodules https://github.com/onlyecho822-source/Echo.git

# Or if already cloned
git submodule init
git submodule update
```

### Install Dependencies

```bash
cd Echo
pip install -r requirements.txt
pip install -r agent-zero/requirements.txt
```

## Usage

### Initialize Bridge

```python
from integrations.agent_zero_bridge import EchoAgentZeroBridge

bridge = EchoAgentZeroBridge()

# Check if Agent-Zero is available
if bridge.is_available():
    print("Agent-Zero integration active")
else:
    print("Agent-Zero not available - integration features disabled")
```

### Validate Claims

```python
from integrations.agent_zero_bridge import validate_claim

# Validate a single claim
result = validate_claim("Climate temperature is +0.8K above baseline")

print(f"Tension: {result['tension']}")
print(f"Optimal: {result['optimal']}")
print(f"Controlled: {result['controlled']}")
print(f"Decision: {result['decision']}")
print(f"Decision Maker: {result['decision_maker']}")
```

### Analyze News Articles

```python
from integrations.agent_zero_bridge import analyze_article

article = {
    "title": "Breaking News: Major Discovery",
    "content": "Scientists announce groundbreaking findings...",
    "source": "Science Daily"
}

analysis = analyze_article(article)

print(f"Truth Score: {analysis['truth_score']}")
print(f"Bias Detected: {analysis['bias_detected']}")
print(f"Narrative Contamination: {analysis['narrative_contamination']}")
print(f"Final Assessment: {analysis['final_assessment']}")
```

### Calculate Zero References

```python
bridge = EchoAgentZeroBridge()

# Climate domain
climate_data = {
    "temperature": 15.0,
    "baseline": 14.2,
    "unit": "celsius"
}

zero_ref = bridge.get_zero_reference("climate", climate_data)
print(f"Climate Zero Reference: {zero_ref['zero_reference']}")
print(f"Confidence: {zero_ref['confidence']}")
```

### Start Kraken Mode (Continuous Monitoring)

```python
bridge = EchoAgentZeroBridge()

# Start continuous monitoring with 5-minute cycles
result = bridge.start_kraken_mode(interval=300)

if result['status'] == 'started':
    print(f"Kraken mode active with {result['interval']}s interval")
```

### Get System Status

```python
from integrations.agent_zero_bridge import get_status

status = get_status()

print(f"Agent-Zero Available: {status['agent_zero_available']}")
print(f"Dual System Active: {status['dual_system_active']}")
print(f"Kraken Mode Active: {status['kraken_mode_active']}")
print(f"Integration Version: {status['integration_version']}")
```

## Testing

Run the integration test suite:

```bash
cd Echo/integrations
python -m pytest test_bridge.py -v
```

Run specific test classes:

```bash
# Test claim validation
python -m pytest test_bridge.py::TestClaimValidation -v

# Test article analysis
python -m pytest test_bridge.py::TestNewsArticleAnalysis -v

# Test end-to-end integration
python -m pytest test_bridge.py::TestEndToEndIntegration -v
```

## Features

### Dual-System Oscillation

Agent-Zero operates with two subsystems:

1. **Uncontrolled (Subconscious)** - Pure mathematical optimization, no constraints
2. **Controlled (Conscious)** - Human-acceptable alternatives, bounded authority

The **tension** between these systems indicates the difficulty of the decision:

- **Low Tension (< 0.5)** - Controlled decides autonomously
- **Medium Tension (0.5 - 0.8)** - Controlled decides with documentation
- **High Tension (> 0.8)** - Escalates to human decision (You or EchoNate)

### Truth Scoring

Articles are scored for truth based on:

- **Symmetry** - Bidirectional validation (A→B and B→A)
- **Assumption Transparency** - Explicit declaration of assumptions
- **Narrative Contamination** - Detection of biased framing
- **Zero Compliance** - Alignment with objective baselines

### Cross-Domain Analysis

Agent-Zero can analyze patterns across multiple domains:

- Climate
- Markets
- News/Media
- Healthcare
- Supply Chain
- Geopolitics

## Graceful Degradation

If Agent-Zero is not available (submodule not cloned, dependencies missing), the bridge gracefully degrades:

```python
result = validate_claim("Test claim")

if not result['available']:
    print("Agent-Zero not available - using fallback")
    # Use alternative validation method
```

## Security & Privacy

- **Agent-Zero Repository:** Private (requires authentication)
- **Echo Repository:** Public
- **Integration Bridge:** Public (interfaces only, no implementation details)
- **Credentials:** Never committed to Echo repository

## Updating Agent-Zero

To update Agent-Zero to the latest version:

```bash
cd Echo/agent-zero
git pull origin main
cd ..
git add agent-zero
git commit -m "Update Agent-Zero to latest version"
git push origin main
```

## Troubleshooting

### Submodule Not Initialized

```bash
git submodule init
git submodule update
```

### Import Errors

```bash
# Ensure dependencies are installed
pip install -r agent-zero/requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Agent-Zero Not Available

```python
from integrations.agent_zero_bridge import get_bridge

bridge = get_bridge()
if not bridge.is_available():
    print("Agent-Zero submodule not available")
    print("Run: git submodule init && git submodule update")
```

## API Reference

### EchoAgentZeroBridge

Main integration class providing access to Agent-Zero capabilities.

#### Methods

- `is_available() -> bool` - Check if Agent-Zero is available
- `validate_claim(claim: str) -> Dict` - Validate a claim using dual-system
- `start_kraken_mode(interval: int) -> Dict` - Start continuous monitoring
- `get_zero_reference(domain: str, data: Dict) -> Dict` - Calculate Zero reference
- `analyze_news_article(article: Dict) -> Dict` - Analyze news article for truth/bias
- `get_system_status() -> Dict` - Get integration status

### Convenience Functions

- `get_bridge() -> EchoAgentZeroBridge` - Get singleton bridge instance
- `validate_claim(claim: str) -> Dict` - Validate claim (convenience)
- `analyze_article(article: Dict) -> Dict` - Analyze article (convenience)
- `get_status() -> Dict` - Get status (convenience)

## Examples

See `test_bridge.py` for comprehensive examples of all integration features.

## Support

For issues related to:
- **Integration Bridge:** Open issue in Echo repository
- **Agent-Zero Core:** Contact Agent-Zero maintainers (private repository)

## Version

**Integration Version:** 1.0.0  
**Agent-Zero Version:** See agent-zero/README.md  
**Echo Version:** See main Echo README.md

---

**Status:** PRODUCTION READY  
**Last Updated:** January 25, 2026  
**Maintainer:** Echo Team

**∇θ**
