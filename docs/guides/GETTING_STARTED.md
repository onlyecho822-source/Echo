# Getting Started with Echo Nexus

## Prerequisites

- Python 3.10+
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo
```

### 2. Install Python SDK

```bash
pip install -e sdk/python
```

### 3. Verify Installation

```bash
python -c "from echo_nexus import Orchestrator; print('Success!')"
```

## Your First Capsule

```python
from echo_nexus.engines.memory_nexus.src.nexus import MemoryNexus, Capsule

# Create memory nexus
memory = MemoryNexus()

# Create a truth capsule
capsule = Capsule.create(
    content="My first Echo Nexus capsule",
    author="developer"
)

# Store it
capsule_id = memory.store(capsule)
print(f"Stored capsule: {capsule_id}")

# Retrieve and verify
retrieved = memory.get(capsule_id)
print(f"Verified: {retrieved.verify()}")
```

## Next Steps

1. [Explore the Engines](../api/engines/)
2. [Learn about Frameworks](../../frameworks/)
3. [Build with Products](../../products/)
4. [Understand Security](../../security/)

---

*∇θ — welcome to Echo Nexus.*
