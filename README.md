# Echo Life OS

A persistent, personal digital intelligence system that lives across devices, cloud, local systems, and identity.

## Overview

Echo Life OS is a **system-of-systems** architecture designed to be your:
- **Memory** - Persistent, encrypted personal history
- **Optimizer** - Financial, health, and life optimization
- **Guardian** - Zero-trust security and identity protection
- **Intelligence** - Multi-agent AI reasoning and task execution

This is not another app. It's an operating system for your digital life.

## Architecture

```
                    +----------------------------------+
                    |       Echo Life OS Core          |
                    +----------------+-----------------+
                                     |
    +----------------+---------------+---------------+----------------+
    |                |               |               |                |
+---v----+     +-----v-----+   +-----v-----+   +-----v-----+   +------v------+
| Memory |     | Cognitive |   | Financial |   |  Defense  |   |   Health    |
| Kernel |     |  Engine   |   |    OS     |   |   Wall    |   |   Engine    |
+--------+     +-----------+   +-----------+   +-----------+   +-------------+
```

### Core Modules

1. **Memory Kernel** - Encrypted, persistent personal memory with dual-memory architecture (working + long-term)
2. **Echo Council** - Multi-agent orchestration using LangGraph with 8 specialized agents
3. **Defense Wall** - Zero-trust security with 5 protection layers
4. **Financial OS** - Account aggregation via Plaid, fraud detection, spending optimization

## Technology Stack

- **Runtime:** Python 3.10+
- **Agent Framework:** LangGraph + LangChain
- **LLM:** Claude (Anthropic), GPT-4 (OpenAI)
- **Storage:** SQLite/LiteFS + ChromaDB
- **Encryption:** AES-256-GCM
- **Financial:** Plaid API

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/nathanpoinsette/echo-life-os.git
cd echo-life-os

# Install dependencies
pip install -r requirements.txt

# Or with all extras
pip install -e ".[all]"
```

### Initialize Echo

```bash
# Set up Echo Life OS
echo init --password YOUR_SECURE_PASSWORD

# Check status
echo status
```

### Basic Usage

```python
from src.core.memory_kernel import MemoryKernel, MemoryType
from src.agents.council import EchoCouncil, EthicsMode
from src.security.defense_wall import DefenseWall

# Initialize Memory Kernel
kernel = MemoryKernel(password="your_password")

# Store a memory
memory_id = kernel.store(
    content="Important project deadline: December 15th",
    memory_type=MemoryType.EPISODIC,
    tags=["work", "deadline"]
)

# Ask the Echo Council
council = EchoCouncil()
response = await council.process(
    task="Analyze my schedule and suggest optimizations",
    ethics_mode=EthicsMode.L4_RED_TEAM
)

# Security scan
defense = DefenseWall()
alerts = await defense.scan({
    "url": "https://suspicious-site.xyz",
    "email": "user@example.com"
})
```

## CLI Commands

```bash
# Initialize system
echo init --password YOUR_PASSWORD

# Store a memory
echo remember "Meeting with investors at 3pm" --type episodic --tags "meetings,important"

# Ask the council
echo ask "What are the risks of launching next month?" --mode grey_zone

# Security scan
echo scan --url "https://example.com" --email "user@example.com"

# Financial analysis
echo spending --days 30

# Emergency lock
echo lock --reason "Security concern"
```

## Echo Council Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Cortex** | Central Coordinator | Task decomposition and routing |
| **Scout** | Opportunity Detection | Market analysis and trend detection |
| **Builder** | Generation & Creation | Code, content, and solution generation |
| **Auditor** | Safety & Compliance | Legal and ethical validation |
| **Navigator** | Strategy & Planning | Long-term planning and goal alignment |
| **Devil Lens** | Adversarial Analysis | Risk assessment and threat modeling |
| **Mapper** | Pattern Recognition | Behavioral patterns and trend analysis |
| **Judge** | Final Arbitration | Conflict resolution and final decisions |

## Ethics Modes

| Mode | Level | Description |
|------|-------|-------------|
| Safe Harbor | L5 | Conservative, cautious, friendly |
| Red Team | L4 | Threat modeling, defensive analysis |
| Grey Zone | L3 | Competitive intelligence, structural analysis |
| Black Lens | L2 | Raw analysis, full consequence mapping |

## Security Architecture

The Defense Wall implements 5 security layers:

1. **Identity Firewall** - Password vault, breach monitoring, phishing detection
2. **Behavior Watchdog** - Anomaly detection, session monitoring
3. **Vendor Isolation** - API sandboxing, data sanitization
4. **Kill Switch** - Emergency lock and secure wipe
5. **Public Boundary** - Data classification enforcement

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key    # For Claude
# or
OPENAI_API_KEY=your_openai_key          # For GPT-4

# Optional
PLAID_CLIENT_ID=your_plaid_client_id    # For Financial OS
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox                        # sandbox, development, production
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
ruff check src tests

# Type checking
mypy src
```

## Project Structure

```
Echo/
├── docs/
│   └── ARCHITECTURE.md     # Full system architecture
├── src/
│   ├── core/
│   │   └── memory_kernel.py
│   ├── agents/
│   │   └── council.py
│   ├── security/
│   │   └── defense_wall.py
│   ├── financial/
│   │   └── financial_os.py
│   └── cli.py
├── tests/
├── config/
├── requirements.txt
└── pyproject.toml
```

## Roadmap

### Phase 1: Foundation (Current)
- [x] Memory Kernel with encryption
- [x] Echo Council multi-agent system
- [x] Defense Wall security
- [x] Financial OS basics

### Phase 2: Core Capabilities
- [ ] Full Plaid integration
- [ ] Health Engine
- [ ] Desktop application
- [ ] Cloud sync

### Phase 3: User Integration
- [ ] Mobile application
- [ ] Voice interface
- [ ] Browser extension

### Phase 4: Expansion
- [ ] IoT integrations
- [ ] Skills marketplace
- [ ] Enterprise features

## Author

**Nathan Poinsette**
Founder • Systems Engineer

## License

MIT License - See LICENSE file for details.

---

*Echo Life OS - The ultimate companion for your digital life.*
