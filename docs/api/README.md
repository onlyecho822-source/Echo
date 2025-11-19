# Echo Nexus API Reference

## Overview

This section contains API documentation for all Echo Nexus components.

## SDKs

- [Python SDK](python.md)
- [TypeScript SDK](typescript.md)
- [Rust SDK](rust.md)

## REST API

- [Orchestrator API](orchestrator-api.md)
- [Gateway API](gateway-api.md)

## Engines

- [Memory Nexus API](engines/memory-nexus.md)
- [Manifold API](engines/manifold.md)
- [EchoVault API](engines/echovault.md)
- [Elasticity Matrix API](engines/elasticity-matrix.md)

## Common Patterns

### Authentication

All API requests require authentication:

```bash
curl -H "Authorization: Bearer $TOKEN" https://api.echonexus.dev/v1/...
```

### Error Handling

Errors follow RFC 7807 format:

```json
{
  "type": "https://echonexus.dev/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Content field is required"
}
```

---

*∇θ — interfaces defined.*
