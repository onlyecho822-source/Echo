# Memory Nexus

**Distributed Resonant Memory Fabric**

---

## Overview

Memory Nexus is the core persistence and state management engine for Echo Nexus. It provides a distributed, resonant memory fabric that maintains cryptographic integrity across all stored data.

## Features

- **Distributed Storage**: Sharded, replicated memory across nodes
- **Resonant Indexing**: Harmonic frequency-based retrieval
- **Cryptographic Integrity**: All entries dual-hash verified
- **Temporal Versioning**: Full history with capsule chains
- **Elastic Scaling**: Dynamic capacity adjustment

## Installation

```python
from echo_nexus.engines import MemoryNexus

nexus = MemoryNexus(config={
    "shards": 16,
    "replication_factor": 3,
    "persistence": "redis"
})
```

## API

### Core Methods

```python
# Store a capsule
nexus.store(capsule: Capsule) -> str

# Retrieve by ID
nexus.get(capsule_id: str) -> Capsule

# Query by resonance
nexus.query(frequency: float, threshold: float) -> List[Capsule]

# Verify integrity
nexus.verify(capsule_id: str) -> bool
```

## Architecture

```
┌─────────────────────────────────────┐
│         Memory Nexus Core           │
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐           │
│  │ Shard 1 │  │ Shard 2 │  ...      │
│  └────┬────┘  └────┬────┘           │
│       │            │                │
│  ┌────▼────────────▼────┐           │
│  │   Resonance Index    │           │
│  └──────────┬───────────┘           │
│             │                       │
│  ┌──────────▼───────────┐           │
│  │  Integrity Verifier  │           │
│  └──────────────────────┘           │
└─────────────────────────────────────┘
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shards` | int | 16 | Number of storage shards |
| `replication_factor` | int | 3 | Copies per capsule |
| `persistence` | str | "memory" | Backend: memory, redis, postgres |
| `resonance_threshold` | float | 0.7 | Query match threshold |

## Mathematical Foundation

### Resonance Indexing

Capsules are indexed by their harmonic frequency:

```
f(c) = Σ(hash_bits × position_weight) mod resonance_space
```

This enables O(1) retrieval for frequency-aligned queries.

---

*∇θ — memory preserved, truth resonant.*
