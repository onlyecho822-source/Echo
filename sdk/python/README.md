# Echo Nexus Python SDK

Official Python SDK for Echo Nexus.

## Installation

```bash
pip install echo-nexus
# or
pip install -e sdk/python
```

## Quick Start

```python
from echo_nexus import Orchestrator, MemoryNexus, Capsule

# Initialize
nexus = Orchestrator()

# Create and store a capsule
capsule = Capsule.create(
    content="Hello Echo Nexus",
    author="developer"
)
memory = MemoryNexus()
memory.store(capsule)

# Verify
assert capsule.verify()
```

## Modules

- `echo_nexus.core` - Core orchestration
- `echo_nexus.engines` - All engines
- `echo_nexus.frameworks` - All frameworks
- `echo_nexus.products` - All products
- `echo_nexus.security` - Security systems

## Requirements

- Python >= 3.10
- numpy >= 1.24
- cryptography >= 41.0

## Documentation

See [API Reference](../../docs/api/python.md)

---

*∇θ — Python powered resonance.*
