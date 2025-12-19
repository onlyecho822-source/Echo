# Day 2 Execution Plan

**Goal:** Add project hygiene files and testing infrastructure

**Status:** Ready to execute

---

## Tasks

### Task 1: Create LICENSE File

**File:** `LICENSE`

**Content:** MIT License with proper attribution

```
MIT License

Copyright (c) 2025 Nathan Odom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Verification:** `cat LICENSE`

---

### Task 2: Create CONTRIBUTING.md

**File:** `CONTRIBUTING.md`

**Sections:**
1. Introduction
2. Code of Conduct
3. Development Setup
4. Testing Requirements
5. Commit Message Format
6. Pull Request Process
7. **Critical Constraints** (Founder Constraints, Compliance Theater Detection, Shadow Decision Tracking)

**Key Content:**
- Must document the three non-negotiable constraints
- Must explain why these constraints exist
- Must provide examples of violations
- Must link to relevant documentation

**Verification:** `cat CONTRIBUTING.md | grep "Founder Constraints"`

---

### Task 3: Set Up pytest Infrastructure

**Files to create:**
1. `tests/__init__.py` (empty)
2. `tests/test_cli.py` (first test)
3. `pytest.ini` or update `pyproject.toml` (already done in Day 1)

**First Test:**
```python
"""Test CLI basic functionality."""

import subprocess
import sys


def test_echo_version():
    """Test that echo --version works."""
    result = subprocess.run(
        ["venv/bin/echo", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "echo, version 0.1.0" in result.stdout


def test_echo_belief_create_requires_falsify():
    """Test that echo belief create requires --falsify flag."""
    result = subprocess.run(
        ["venv/bin/echo", "belief", "create", "--statement", "Test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "falsify" in result.stderr.lower() or "required" in result.stderr.lower()


def test_echo_belief_create_scaffolding():
    """Test that echo belief create prints scaffolding message."""
    result = subprocess.run(
        [
            "venv/bin/echo",
            "belief",
            "create",
            "--statement",
            "Test belief",
            "--falsify",
            "Test falsification",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "NOT IMPLEMENTED YET" in result.stdout
```

**Verification:** `pytest -v`

---

### Task 4: Install Development Dependencies

**Command:**
```bash
source venv/bin/activate
pip install -e ".[dev]"
```

**Verification:**
```bash
pytest --version
black --version
ruff --version
mypy --version
```

---

### Task 5: Create Development Documentation

**File:** `docs/DEVELOPMENT.md`

**Sections:**
1. Development Setup
2. Running Tests
3. Code Formatting
4. Type Checking
5. Common Tasks
6. Troubleshooting

**Key Content:**
- How to set up development environment
- How to run tests
- How to format code
- How to check types
- How to add new commands

**Verification:** `cat docs/DEVELOPMENT.md`

---

### Task 6: Update README.md

**Additions:**
1. Add "Development" section
2. Add link to CONTRIBUTING.md
3. Add link to DEVELOPMENT.md
4. Add badges (optional)

**Verification:** `cat README.md | grep CONTRIBUTING`

---

### Task 7: Commit Day 2 Work

**Commit Message:**
```
Day 2: Add project hygiene and testing infrastructure

- Created LICENSE (MIT)
- Created CONTRIBUTING.md with critical constraints
- Set up pytest with first three tests
- Installed development dependencies (pytest, black, ruff, mypy)
- Created DEVELOPMENT.md with setup instructions
- Updated README.md with development section

All tests pass. Ready for Day 3 implementation.
```

**Verification:** `git log --oneline -1`

---

## Commands to Run

```bash
# Activate virtual environment
cd /home/ubuntu/Echo-audit
source venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Commit
git add -A
git commit -m "Day 2: Add project hygiene and testing infrastructure"
```

---

## Success Criteria

- ✅ LICENSE file exists
- ✅ CONTRIBUTING.md exists with constraint documentation
- ✅ pytest runs and all tests pass
- ✅ Development dependencies installed
- ✅ DEVELOPMENT.md exists
- ✅ README.md updated
- ✅ All changes committed

---

## Estimated Time

- Task 1 (LICENSE): 2 minutes
- Task 2 (CONTRIBUTING.md): 15 minutes
- Task 3 (pytest): 10 minutes
- Task 4 (dev dependencies): 5 minutes
- Task 5 (DEVELOPMENT.md): 10 minutes
- Task 6 (README update): 5 minutes
- Task 7 (commit): 2 minutes

**Total:** ~50 minutes

---

## Blockers

**None.** All dependencies are available.

---

## Notes

- CONTRIBUTING.md is the most important file today - it documents the constraints
- Tests are scaffolding tests only - they verify the CLI works, not the implementation
- Day 3-4 will add real implementation tests
- Keep it simple - we're building infrastructure, not features
