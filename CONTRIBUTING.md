# Contributing to Echo Nexus

Thank you for your interest in contributing to Echo Nexus. This document provides guidelines and standards for contributions.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Standards](#commit-standards)
- [Pull Request Process](#pull-request-process)
- [Architecture Guidelines](#architecture-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)

---

## Code of Conduct

### Core Principles

1. **Truth Preservation** — All contributions must maintain cryptographic integrity
2. **Harmonic Alignment** — Code should resonate with existing architecture
3. **Transparency** — Clear documentation and intent
4. **Resilience** — Defensive coding practices

### Expected Behavior

- Respectful, constructive communication
- Evidence-based technical discussions
- Acknowledgment of others' contributions
- Patience with newcomers

---

## Getting Started

### Prerequisites

```bash
# Required
python >= 3.10
node >= 18.0
git >= 2.30

# Optional (for full development)
rust >= 1.70
docker >= 20.0
```

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify setup
make check-env
```

---

## Development Workflow

### Branch Naming Convention

```
<type>/<module>-<description>

Examples:
feature/memory-nexus-persistence
fix/manifold-curvature-calculation
docs/api-reference-update
refactor/capsule-hash-optimization
```

### Types

| Type | Description |
|------|-------------|
| `feature` | New functionality |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `refactor` | Code restructuring |
| `test` | Test additions/modifications |
| `perf` | Performance improvements |
| `security` | Security enhancements |

---

## Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

```
feat(memory-nexus): add distributed persistence layer

Implements Redis-backed persistence for Memory Nexus with
automatic sharding and replication support.

- Add RedisStore class
- Implement sharding algorithm
- Add replication configuration

Closes #123
```

```
fix(manifold): correct Ricci curvature calculation

The previous implementation had an off-by-one error in the
tensor contraction loop, causing incorrect curvature values.

Fixes #456
```

### Subject Line Rules

- Use imperative mood ("add" not "added")
- No capitalization at start
- No period at end
- Max 50 characters

### Body Rules

- Wrap at 72 characters
- Explain what and why, not how
- Include relevant context

---

## Pull Request Process

### Before Submitting

1. **Update from main**
   ```bash
   git fetch origin main
   git rebase origin/main
   ```

2. **Run full test suite**
   ```bash
   make test
   ```

3. **Check linting**
   ```bash
   make lint
   ```

4. **Update documentation**
   - API changes require doc updates
   - New features require examples

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Module(s) Affected
- [ ] Core
- [ ] Engines
- [ ] Frameworks
- [ ] Products
- [ ] Security
- [ ] SDK

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] API docs updated
- [ ] README updated (if needed)
- [ ] Examples added (if needed)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings generated
```

### Review Process

1. At least one maintainer approval required
2. All CI checks must pass
3. No unresolved conversations
4. Squash merge for clean history

---

## Architecture Guidelines

### Module Structure

Every module must follow this structure:

```
<module>/
├── src/           # Source code
├── spec/          # Schemas and specifications
├── math/          # Mathematical models (if applicable)
├── docs/          # Module documentation
├── tests/         # Test suite
├── capsules/      # Truth capsules
├── manifests/     # Metadata and configuration
└── examples/      # Usage examples
```

### Code Organization

```python
# Standard import order
import stdlib
import third_party
import echo_nexus.core
import echo_nexus.engines
import local_module

# Class structure
class Component:
    """
    Brief description.

    Detailed description including mathematical
    foundations if applicable.

    Attributes:
        attr1: Description
        attr2: Description
    """

    def __init__(self):
        pass

    # Public methods first
    def public_method(self):
        pass

    # Private methods last
    def _private_method(self):
        pass
```

### Resonance Patterns

When adding new components, ensure they follow the resonance pattern:

```python
class NewEngine(BaseEngine):
    def __init__(self, config: EngineConfig):
        super().__init__(config)
        self._resonance_frequency = config.frequency

    def resonate(self, signal: Signal) -> Response:
        """Process signal through resonance transformation."""
        return self._transform(signal, self._resonance_frequency)
```

---

## Testing Requirements

### Coverage Requirements

| Module Type | Minimum Coverage |
|-------------|------------------|
| Core | 90% |
| Engines | 85% |
| Frameworks | 80% |
| Products | 85% |
| Security | 95% |
| SDK | 85% |

### Test Structure

```python
# tests/test_<module>.py

import pytest
from echo_nexus.<module> import Component

class TestComponent:
    """Tests for Component class."""

    @pytest.fixture
    def component(self):
        """Create test component."""
        return Component(config=test_config)

    def test_initialization(self, component):
        """Test component initializes correctly."""
        assert component.is_initialized

    def test_resonance(self, component):
        """Test resonance transformation."""
        signal = create_test_signal()
        result = component.resonate(signal)
        assert result.is_valid

    @pytest.mark.parametrize("input,expected", [
        (case1_input, case1_expected),
        (case2_input, case2_expected),
    ])
    def test_parametrized(self, component, input, expected):
        """Test multiple input cases."""
        assert component.process(input) == expected
```

### Test Categories

- **Unit Tests**: Isolated component testing
- **Integration Tests**: Cross-module interactions
- **Property Tests**: Invariant verification
- **Performance Tests**: Benchmark critical paths

---

## Documentation Standards

### Docstring Format

Use Google-style docstrings:

```python
def calculate_curvature(manifold: Manifold, point: Point) -> float:
    """
    Calculate Ricci curvature at a point on the manifold.

    Uses the contracted Riemann tensor to compute scalar
    curvature at the specified point.

    Args:
        manifold: The behavioral manifold instance
        point: Point at which to calculate curvature

    Returns:
        Scalar curvature value at the point

    Raises:
        ManifoldError: If point is outside manifold bounds

    Example:
        >>> m = Manifold(dim=4)
        >>> p = Point([0.5, 0.5, 0.5, 0.5])
        >>> curvature = calculate_curvature(m, p)
        >>> print(f"Curvature: {curvature:.4f}")
        Curvature: 0.2341
    """
    pass
```

### README Requirements

Each module must have a README.md containing:

1. Overview and purpose
2. Installation instructions
3. Quick start example
4. API summary
5. Configuration options
6. Mathematical foundations (if applicable)
7. Related modules

### Mathematical Documentation

For components with mathematical foundations:

```markdown
## Mathematical Foundation

### H-Rule Correction

The manifold correction follows:

$$
\nabla_\theta = \text{Ric}(g) + \lambda H
$$

Where:
- $\nabla_\theta$: Gradient of system state
- $\text{Ric}(g)$: Ricci curvature tensor
- $\lambda$: Correction coefficient
- $H$: Harmonic resonance term
```

---

## Security Considerations

### Sensitive Code

When working on security modules:

1. Request security review for all changes
2. Never commit secrets or keys
3. Use constant-time comparisons
4. Validate all inputs
5. Document threat models

### Cryptographic Changes

All cryptographic changes require:

- Formal security analysis
- Review by security team
- Extensive test vectors
- Performance benchmarks

---

## Questions?

- Open an issue with the `question` label
- Join discussions in the repository
- Review existing documentation

---

*∇θ — contribute with integrity, build with resonance.*
