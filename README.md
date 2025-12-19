# Echo Universe

**A belief tracking system built on the Verification Ladder epistemology.**

## What is Echo?

Echo is a command-line tool that helps you track beliefs with falsification criteria. It enforces intellectual honesty by requiring you to specify **how you could be wrong** before recording what you believe.

## Core Philosophy

The **Verification Ladder** is a five-tier epistemological framework:

1. **Speculation** - Unverified ideas
2. **Hypothesis** - Testable claims with falsification criteria
3. **Evidence** - Observations that support or refute hypotheses
4. **Conclusion** - Beliefs derived from evidence
5. **Truth** - Conclusions that have survived repeated testing

Echo implements this framework as a practical tool for decision-making.

## Installation

```bash
# Clone the repository
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo

# Install in development mode
pip install -e .

# Verify installation
echo --version
```

## Quick Start

```bash
# Create your first belief
echo belief create \
  --statement "Our landing page converts at >5%" \
  --falsify "If conversion rate <3% after 1000 visitors, belief is false" \
  --tier hypothesis

# List all beliefs
echo belief list

# Update a belief with evidence
echo belief update <belief-id> --evidence "Conversion rate: 4.2% (n=1200)"
```

## Project Status

**Current Phase:** Week 1 Sprint - Building the v1 kernel

This is a clean rebuild focused on:
- Working CLI with `echo belief create` command
- Mandatory falsification criteria
- Persistent belief ledger
- No features beyond core functionality

## Architecture

```
Echo Universe
├── Layer 0: Verification Ladder (epistemology)
├── Layer 1: echo-core (this repository)
├── Layer 2: Authority Engine (governance)
├── Layer 3: Conversion Engine (commercial)
└── Layer 4: Products (EchoDNS, WorldForge)
```

## Documentation

- [Strategic Documents](./docs/strategy/) - Long-term vision and architecture
- [Historical Archive](./docs/archive/) - Previous iterations and research
- [Framework Docs](./docs/framework/) - Verification Ladder specifications
- [Product Docs](./docs/products/) - EchoDNS, WorldForge, and other products

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Contributing

This project follows strict constraints:

1. **Founder Constraints** - The founder (nathan.odom@*) has no admin mode
2. **Compliance Theater Detection** - All overrides are logged permanently
3. **Shadow Decision Tracking** - Beliefs must be recorded before decisions

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## License

MIT License - See [LICENSE](./LICENSE) for details.

## Contact

- **Author:** Nathan Odom
- **Email:** nathan.odom@echo.universe
- **Repository:** https://github.com/onlyecho822-source/Echo
