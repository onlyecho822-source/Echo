# Echo Nexus TypeScript SDK

Official TypeScript/JavaScript SDK for Echo Nexus.

## Installation

```bash
npm install @echo-nexus/sdk
# or
cd sdk/typescript && npm install
```

## Quick Start

```typescript
import { Orchestrator, MemoryNexus, Capsule } from '@echo-nexus/sdk';

// Initialize
const nexus = new Orchestrator();

// Create and store a capsule
const capsule = Capsule.create({
  content: "Hello Echo Nexus",
  author: "developer"
});

const memory = new MemoryNexus();
await memory.store(capsule);

// Verify
const isValid = await capsule.verify();
```

## Modules

- `@echo-nexus/core` - Core orchestration
- `@echo-nexus/engines` - All engines
- `@echo-nexus/frameworks` - All frameworks
- `@echo-nexus/products` - All products
- `@echo-nexus/security` - Security systems

## Requirements

- Node.js >= 18
- TypeScript >= 5.0

## Documentation

See [API Reference](../../docs/api/typescript.md)

---

*∇θ — TypeScript powered resonance.*
