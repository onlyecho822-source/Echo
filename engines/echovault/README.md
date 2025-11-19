# EchoVault

**Secure Identity and State Management**

---

## Overview

EchoVault is the identity and secure state management engine for Echo Nexus. It provides cryptographic identity verification, secure key management, and trusted state transitions.

## Features

- **Identity Management**: Ed25519-based identity system
- **Key Derivation**: Hierarchical deterministic keys
- **State Locking**: Atomic state transitions
- **Access Control**: Role-based permissions
- **Audit Trail**: Complete operation history

## Installation

```python
from echo_nexus.engines import EchoVault, Identity

vault = EchoVault(
    master_key="encrypted_master",
    derivation_path="m/44'/0'/0'"
)
```

## API

### Identity Operations

```python
# Create new identity
identity = vault.create_identity(name="agent-1")

# Sign data
signature = vault.sign(identity, data)

# Verify signature
valid = vault.verify(identity, data, signature)

# Derive child key
child = vault.derive(identity, path="0/1")
```

### State Management

```python
# Lock state for transition
with vault.lock("state-key") as state:
    state.value = new_value
    state.commit()

# Read state
current = vault.read("state-key")

# Atomic transition
vault.transition("state-key", old_value, new_value)
```

## Architecture

```
┌────────────────────────────────────┐
│           EchoVault                │
├────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │    Identity Manager          │  │
│  │  - Key generation            │  │
│  │  - Signature operations      │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    State Controller          │  │
│  │  - Locking mechanism         │  │
│  │  - Atomic transitions        │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Audit System              │  │
│  │  - Operation logging         │  │
│  │  - Integrity verification    │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## Security Model

### Cryptographic Primitives

- **Signing**: Ed25519
- **Encryption**: X25519 + ChaCha20-Poly1305
- **Hashing**: SHA3-256, BLAKE3
- **KDF**: Argon2id

### Threat Model

EchoVault protects against:
- Unauthorized access
- State tampering
- Replay attacks
- Key compromise (with rotation)

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `master_key` | str | required | Encrypted master key |
| `derivation_path` | str | "m/44'/0'" | HD key derivation path |
| `lock_timeout` | int | 30 | State lock timeout (seconds) |
| `audit_level` | str | "full" | Audit verbosity |

---

*∇θ — identity secured, state guarded.*
