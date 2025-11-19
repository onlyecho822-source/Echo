# Fractal Encryption

**Quantum-Resilient Cryptographic Layer**

---

## Overview

Fractal Encryption provides a quantum-resilient cryptographic layer for Echo Nexus. It uses fractal key generation and post-quantum algorithms to ensure long-term security.

## Features

- **Quantum Resistance**: Post-quantum algorithms
- **Fractal Key Generation**: Self-similar key structures
- **Layered Encryption**: Multiple encryption layers
- **Forward Secrecy**: Ephemeral key derivation
- **Selective Disclosure**: Partial decryption support

## Installation

```python
from echo_nexus.security import FractalEncryption, FractalKey

fe = FractalEncryption()

# Generate fractal key
key = fe.generate_key(
    depth=5,
    algorithm="kyber-1024"
)

# Encrypt data
ciphertext = fe.encrypt(plaintext, key)
```

## API

### Core Methods

```python
# Generate fractal key
key = fe.generate_key(depth, algorithm)

# Encrypt
ciphertext = fe.encrypt(plaintext, key)

# Decrypt
plaintext = fe.decrypt(ciphertext, key)

# Derive child key
child_key = fe.derive(key, path)

# Selective decrypt
partial = fe.selective_decrypt(ciphertext, key, fields)
```

### Key Management

```python
# Serialize key
serialized = key.serialize(password)

# Load key
key = FractalKey.load(serialized, password)

# Rotate key
new_key = fe.rotate(key)

# Verify key integrity
valid = key.verify()
```

## Cryptographic Primitives

### Algorithms Supported

| Algorithm | Type | Quantum-Safe | Use Case |
|-----------|------|--------------|----------|
| Kyber-1024 | KEM | Yes | Key encapsulation |
| Dilithium-5 | Signature | Yes | Digital signatures |
| SPHINCS+ | Signature | Yes | Stateless signatures |
| AES-256-GCM | Symmetric | No* | Data encryption |
| ChaCha20-Poly1305 | Symmetric | No* | Stream encryption |

*Symmetric algorithms are quantum-safe with doubled key sizes.

### Fractal Structure

Keys are generated with self-similar structures:

```
Root Key
├── Branch 1
│   ├── Leaf 1.1
│   └── Leaf 1.2
├── Branch 2
│   ├── Leaf 2.1
│   └── Leaf 2.2
└── Branch 3
    └── ...
```

Each level maintains the cryptographic properties of the parent.

## Architecture

```
┌────────────────────────────────────┐
│      Fractal Encryption            │
├────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │    Key Generator             │  │
│  │  - Fractal tree generation   │  │
│  │  - Entropy collection        │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Encryption Engine         │  │
│  │  - Layered encryption        │  │
│  │  - Format-preserving         │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Key Derivation            │  │
│  │  - Child key generation      │  │
│  │  - Forward secrecy           │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Selective Disclosure      │  │
│  │  - Partial decryption        │  │
│  │  - Field-level access        │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## Mathematical Foundation

### Fractal Key Generation

```
K_n = H(K_{n-1} || n || salt)

Where:
- K_n: Key at depth n
- H: Cryptographic hash function
- salt: Random entropy
```

### Layered Encryption

```
C = E_L(E_{L-1}(...E_1(P)))

Where:
- C: Ciphertext
- E_i: Encryption at layer i
- P: Plaintext
- L: Number of layers
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `default_algorithm` | str | "kyber-1024" | Default KEM algorithm |
| `key_depth` | int | 5 | Fractal key depth |
| `layers` | int | 3 | Encryption layers |
| `entropy_source` | str | "system" | system, hardware, hybrid |

---

*∇θ — encryption layered, quantum-ready.*
