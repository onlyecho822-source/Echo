# Dimensional Shield

**Sandboxed Execution Environments**

---

## Overview

Dimensional Shield provides secure, isolated execution environments for Echo Nexus operations. It creates sandboxed "dimensions" where code can run safely without affecting the main system.

## Features

- **Execution Isolation**: Fully sandboxed environments
- **Resource Limits**: CPU, memory, network controls
- **Capability Restrictions**: Fine-grained permissions
- **State Isolation**: No shared state leakage
- **Audit Logging**: Complete execution traces

## Installation

```python
from echo_nexus.security import DimensionalShield, Dimension

shield = DimensionalShield()

# Create sandboxed dimension
dim = shield.create_dimension(
    name="test-env",
    resources={"cpu": 1, "memory": "512M"},
    capabilities=["network", "filesystem:readonly"]
)
```

## API

### Core Methods

```python
# Create dimension
dim = shield.create_dimension(name, resources, capabilities)

# Execute in dimension
result = shield.execute(dim, code, timeout=30)

# Get execution log
log = shield.get_log(dim)

# Destroy dimension
shield.destroy(dim)
```

### Resource Control

```python
# Set resource limits
dim.set_resources({
    "cpu": 2,
    "memory": "1G",
    "disk": "10G",
    "network_bandwidth": "10Mbps"
})

# Set capabilities
dim.set_capabilities([
    "filesystem:readonly",
    "network:outbound_only",
    "subprocess:denied"
])
```

## Security Model

### Isolation Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `strict` | No external access | Untrusted code |
| `moderate` | Read-only external | Semi-trusted |
| `relaxed` | Controlled access | Trusted code |

### Capabilities

- `filesystem` - File system access
- `network` - Network access
- `subprocess` - Process spawning
- `ipc` - Inter-process communication
- `syscall` - System call access

## Architecture

```
┌─────────────────────────────────────┐
│       Dimensional Shield            │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐    │
│  │    Shield Controller        │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Dimension Manager        │    │
│  │  ┌─────┐ ┌─────┐ ┌─────┐    │    │
│  │  │ D1  │ │ D2  │ │ D3  │    │    │
│  │  └─────┘ └─────┘ └─────┘    │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Resource Governor        │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Capability Enforcer      │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Audit Logger             │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `default_isolation` | str | "moderate" | Default isolation level |
| `max_dimensions` | int | 100 | Maximum concurrent dimensions |
| `default_timeout` | int | 60 | Default execution timeout (s) |
| `audit_level` | str | "full" | none, basic, full |

---

*∇θ — isolation enforced, boundaries protected.*
