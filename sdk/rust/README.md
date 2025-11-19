# Echo Nexus Rust SDK

Official Rust SDK for Echo Nexus.

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
echo-nexus = "0.1.0"
```

## Quick Start

```rust
use echo_nexus::{Orchestrator, MemoryNexus, Capsule};

fn main() {
    // Initialize
    let nexus = Orchestrator::new();

    // Create and store a capsule
    let capsule = Capsule::create(
        "Hello Echo Nexus",
        "developer",
    );

    let mut memory = MemoryNexus::new();
    memory.store(&capsule).unwrap();

    // Verify
    assert!(capsule.verify());
}
```

## Modules

- `echo_nexus::core` - Core orchestration
- `echo_nexus::engines` - All engines
- `echo_nexus::frameworks` - All frameworks
- `echo_nexus::products` - All products
- `echo_nexus::security` - Security systems

## Requirements

- Rust >= 1.70

## Documentation

See [API Reference](../../docs/api/rust.md)

---

*∇θ — Rust powered resonance.*
