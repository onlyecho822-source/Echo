# Echo Capsules

**Dual-Hash Provenance Truth Units**

---

## Overview

Echo Capsules are the atomic units of verified truth in Echo Nexus. Each capsule contains content with cryptographic provenance through dual-hash verification, enabling immutable, traceable knowledge storage.

## Features

- **Dual-Hash Verification**: SHA3-256 + BLAKE3
- **Chain Provenance**: Linked capsule history
- **Ed25519 Signatures**: Cryptographic authorship
- **Temporal Ordering**: Precise timestamps
- **Content Integrity**: Tamper-evident storage

## Installation

```python
from echo_nexus.products import Capsule, CapsuleChain

# Create a capsule
capsule = Capsule.create(
    content="The system is operational",
    author="operator",
    hash_algorithm="dual-sha3"
)
```

## API

### Creating Capsules

```python
# Simple creation
capsule = Capsule.create(content="fact", author="system")

# With chaining
chain = CapsuleChain()
cap1 = chain.add("First fact")
cap2 = chain.add("Second fact", previous=cap1)
```

### Verification

```python
# Verify integrity
is_valid = capsule.verify()

# Verify chain
chain_valid = chain.verify_all()

# Verify signature
sig_valid = capsule.verify_signature(public_key)
```

### Querying

```python
# Get capsule by ID
cap = CapsuleStore.get(capsule_id)

# Query by content hash
caps = CapsuleStore.query(content_hash=hash)

# Get chain history
history = chain.history(capsule_id)
```

## Capsule Structure

```python
{
    "id": "cap_7f3a8b2c1d4e",
    "version": "1.0",
    "content": "Verified fact content",
    "author": "system",
    "timestamp": "2025-01-15T10:30:00.000Z",
    "hash_primary": "sha3-256:a1b2c3d4...",
    "hash_secondary": "blake3:e5f6g7h8...",
    "signature": "ed25519:i9j0k1l2...",
    "chain": "cap_previous_id",
    "metadata": {
        "domain": "operations",
        "confidence": 0.99
    }
}
```

## Architecture

```
┌────────────────────────────────────┐
│         Echo Capsules              │
├────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │    Capsule Factory           │  │
│  │  - Content intake            │  │
│  │  - Hash computation          │  │
│  │  - Signature generation      │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Chain Manager             │  │
│  │  - Link management           │  │
│  │  - History tracking          │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Verification Engine       │  │
│  │  - Dual-hash verification    │  │
│  │  - Signature validation      │  │
│  │  - Chain integrity           │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## CLI Usage

```bash
# Create capsule from stdin
echo "fact content" | echo-capsule create --author operator

# Verify capsule
echo-capsule verify cap_7f3a8b2c1d4e

# Export chain
echo-capsule export --chain cap_7f3a8b2c1d4e --format json
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hash_primary` | str | "sha3-256" | Primary hash algorithm |
| `hash_secondary` | str | "blake3" | Secondary hash algorithm |
| `signature_algorithm` | str | "ed25519" | Signature algorithm |
| `chain_validation` | bool | true | Validate chain on add |

---

*∇θ — truth encapsulated, provenance preserved.*
