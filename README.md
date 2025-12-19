# Echo Universe

**Version:** 0.1.0  
**Status:** ✅ Production Ready  
**License:** MIT

---

## What is Echo?

Echo is **memory that refuses to lie** and **latency that refuses to wait**.

It's not a belief tracker. It's a **decision hygiene system** that reduces the time it takes for reality to correct human belief.

### Core Principles

1. **Immutable Memory** - Append-only ledger with SHA-256 hash chain
2. **Mandatory Falsification** - Every belief must specify how it could be wrong
3. **Causality Tracking** - Sequence matters, not just time
4. **Founder Constraints** - No special privileges, even for founders
5. **Shadow Decision Detection** - Retroactive justification is visible
6. **Friction as Firewall** - Difficulty filters for epistemic fitness

---

## Installation

### Requirements

- Python 3.11+
- pip

### Install from Source

```bash
# Clone repository
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

---

## Quick Start

### Create Your First Belief

```bash
echo belief create \
  --statement "Our landing page converts at >5%" \
  --falsify "If conversion <3% after 1000 visitors, belief is false" \
  --tier hypothesis \
  --confidence 0.7
```

### Add Evidence

```bash
echo belief add-evidence <belief-id> \
  --evidence "First 100 visitors: 6 conversions (6%)" \
  --source "Google Analytics, Dec 19 2025" \
  --supports
```

### List Beliefs

```bash
echo belief list
```

### Verify Integrity

```bash
echo audit
```

### Check Founder Actions

```bash
echo founder-audit
```

---

## Usage

### Commands

**Belief Management:**
- `echo belief create` - Create new belief with falsification
- `echo belief list` - List all beliefs
- `echo belief show <id>` - Show detailed belief information
- `echo belief add-evidence <id>` - Add evidence to belief
- `echo belief falsify <id>` - Mark belief as falsified

**Audit:**
- `echo audit` - Generate integrity and audit report
- `echo founder-audit` - Show all founder actions (transparency)

**Help:**
- `echo --help` - Show all commands
- `echo belief --help` - Show belief commands
- `echo belief create --help` - Show create options

---

## Architecture

### Core Components

**Immutable Ledger** (`src/echo_core/ledger.py`)
- Append-only JSONL file (`~/.echo/ledger.jsonl`)
- SHA-256 hash chain linking every entry
- Self-verifying integrity checks

**Belief Models** (`src/echo_core/models.py`)
- Pydantic models with validation
- Mandatory falsification enforcement
- Evidence tracking with sources
- Causality timestamps

**Storage Layer** (`src/echo_core/storage.py`)
- Bridges beliefs to ledger
- Hardcoded founder constraints
- Shadow decision detection
- Audit trail generation

**CLI Interface** (`src/echo_core/cli.py`)
- Click-based command line
- Friction-first UX
- Transparency by default

---

## Testing

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest -v

# Run with coverage
pytest --cov=src/echo_core --cov-report=term-missing

# Run specific test file
pytest tests/test_ledger.py -v
```

### Test Results

**Total Tests:** 51  
**Passed:** 51 (100%)  
**Coverage:** 95% of core logic

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test report.

---

## Mission Alignment

Echo is built according to the **mentor constellation**:

- **NASA** - Rigorous, safety-first engineering
- **Signal** - Principled, privacy-first design
- **Linus** - Immutable, integrity-first architecture

### What Echo Is NOT

- A truth oracle
- A moral authority
- A revolutionary tool
- An anti-power weapon
- A generic belief tracker

### What Echo IS

- A memory prosthetic that refuses to lie
- A decision hygiene system with mandatory falsification
- A latency detector for truth correction
- Selection pressure encoded in software
- Counter-incentive engineering (not revolution)

See [MISSION_VALIDATION_REPORT.md](MISSION_VALIDATION_REPORT.md) for full alignment verification.

---

## Documentation

### Core Documentation

- [README.md](README.md) - This file
- [MISSION_VALIDATION_REPORT.md](MISSION_VALIDATION_REPORT.md) - Mission alignment verification
- [MISSION_ALIGNMENT_AUDIT.md](MISSION_ALIGNMENT_AUDIT.md) - Gap analysis from initial implementation
- [TEST_RESULTS.md](TEST_RESULTS.md) - Comprehensive test report
- [DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md) - Project delivery summary

### Additional Documentation

- `docs/framework/` - Verification Ladder framework
- `docs/strategy/` - Long-term vision and strategy
- `docs/products/` - Product specifications (EchoDNS, WorldForge)
- `docs/archive/` - Historical documents

---

## Development

### Project Structure

```
Echo/
├── src/echo_core/          # Core implementation
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── ledger.py           # Immutable ledger
│   ├── models.py           # Belief models
│   └── storage.py          # Storage layer
├── tests/                  # Test suite
│   ├── test_ledger.py
│   ├── test_models.py
│   └── test_storage.py
├── docs/                   # Documentation
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

### Contributing

Echo is built with **zero compromises** on mission alignment. Before contributing:

1. Read [MISSION_VALIDATION_REPORT.md](MISSION_VALIDATION_REPORT.md)
2. Understand the mentor constellation (NASA, Signal, Linus)
3. Accept that friction is intentional, not a bug
4. Verify all tests pass: `pytest -v`

**Founder Constraint:** Even founders (nathan.odom@*) have NO special privileges. All actions are logged publicly.

---

## Roadmap

### v1.0 (Current) ✅

- [x] Immutable ledger with hash chain
- [x] Mandatory falsification with validation
- [x] Causality tracking
- [x] Founder constraints
- [x] Shadow decision detection
- [x] Comprehensive test suite (51 tests)
- [x] CLI interface

### v2.0 (Planned)

- [ ] Compliance theater detection (pattern analysis)
- [ ] Belief autopsies (why did beliefs fail?)
- [ ] Evidence quality scoring
- [ ] Multi-user support with email verification
- [ ] API layer for programmatic access
- [ ] Web interface (optional)

---

## FAQ

### Why is falsification mandatory?

Because unfalsifiable beliefs are not beliefs - they're wishes. Echo enforces epistemic hygiene by requiring you to specify how you could be wrong.

### Why is the UX so difficult?

**Friction is the firewall.** The difficulty filters for people who actually want truth over convenience. If it's too hard, you're not the target user.

### Why can't founders have admin privileges?

Because power corrupts memory. Even founders must submit to the same constraints. All founder actions are logged publicly for transparency.

### Can I delete a belief?

No. You can **deprecate** or **falsify** it, but you cannot delete it. Echo is memory that refuses to lie, and deletion is lying about the past.

### How do I know the ledger hasn't been tampered with?

Run `echo audit`. The hash chain will break if any entry is modified. Tampering is visible, not hidden.

### Is this overkill for personal use?

Maybe. But "overkill" is how you build systems that can't be corrupted later. Start with integrity, not convenience.

---

## License

MIT License - See LICENSE file for details.

---

## Contact

**Repository:** https://github.com/onlyecho822-source/Echo  
**Issues:** https://github.com/onlyecho822-source/Echo/issues

---

## Acknowledgments

Built according to the mentor constellation:
- **NASA** for rigorous engineering
- **Signal** for principled design
- **Linus Torvalds** for immutable architecture

---

**Echo v1: Memory that refuses to lie. Latency that refuses to wait.**

**Status:** ✅ Production Ready | Zero Compromises
