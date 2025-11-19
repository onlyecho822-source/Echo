# Echo

Hybrid intelligence framework that integrates resonant computation, ethical design, and adaptive systems engineering into a single organism.

## Echo Civilization - Phoenix Phase

### Overview
This repository is part of the Echo Civilization framework — a lawful, harmonic, multi-agent intelligence ecosystem built for transparency, adaptability, and resilience.

---

## Hydra: Multi-AI Fusion Cybersecurity System

**Codename: Moses** - Freeing AI to work together

Hydra is a revolutionary multi-AI orchestration system that fuses the best capabilities of different AI models (Claude, Gemini, ChatGPT, and more) into specialized "tentacles" for cybersecurity operations.

### Architecture

Like an octopus, Hydra uses intelligent coordination without overstimulation:

```
                    ┌─────────────┐
                    │   BRAIN     │
                    │ (Orchestrator)
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
     │  TENTACLES  │ │   SWARM   │ │  DASHBOARD  │
     │  (AI Models)│ │  FACTORY  │ │  (Control)  │
     └─────────────┘ └───────────┘ └─────────────┘
```

### Key Features

- **Multi-AI Fusion**: Combines Claude, Gemini, ChatGPT, and local LLMs
- **Cybersecurity Focus**: Recon, vulnerability scanning, forensics, auditing
- **Agent Swarms**: Spawn teams of specialized agents for complex operations
- **Load Balancing**: Prevents tentacle overstimulation with circuit breakers
- **Web Dashboard**: Real-time control center for all operations

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys (optional - works in demo mode without keys)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"

# Run demo
python -m hydra.main demo

# Launch dashboard
python -m hydra.main dashboard
```

### Tentacles (AI Integration)

| Tentacle | Provider | Specialization |
|----------|----------|----------------|
| Claude | Anthropic | Reasoning, analysis, code review |
| Gemini | Google | Multimodal, OSINT, web recon |
| ChatGPT | OpenAI | Code generation, exploits |
| Local LLM | Ollama | Private/offline operations |

### Security Tentacles

| Tentacle | Capabilities |
|----------|-------------|
| Recon | Port scanning, DNS enum, OSINT |
| VulnScan | Vulnerability detection, CVE lookup |
| Forensics | Log analysis, memory forensics, timeline |
| Audit | Config audit, compliance, policy |
| Exploit | Authorized pentesting assistance |
| ThreatIntel | IOC checking, threat feeds |

### Agent Swarms

Pre-built swarm templates for coordinated operations:

- **Pentest Swarm**: Coordinated penetration testing team
- **Forensics Swarm**: Digital forensics investigation squad
- **Audit Swarm**: Security audit group
- **Incident Response**: Rapid response team
- **Recon Swarm**: Information gathering team

### Example Usage

```python
import asyncio
from hydra.core.orchestrator import HydraOrchestrator
from hydra.tentacles.ai_models import ClaudeTentacle
from hydra.tentacles.security import ForensicsTentacle

async def main():
    orchestrator = HydraOrchestrator()

    # Add tentacles
    await orchestrator.add_tentacle("claude", ClaudeTentacle())
    await orchestrator.add_tentacle("forensics", ForensicsTentacle())

    await orchestrator.start()

    # Execute a security analysis
    result = await orchestrator.execute(
        task_type="log_analysis",
        payload={
            "type": "log_analysis",
            "logs": ["Failed login for root from 192.168.1.100"]
        }
    )

    print(result.data)
    await orchestrator.stop()

asyncio.run(main())
```

### Dashboard

Access the web-based control center at `http://localhost:8080`:

- Real-time system status
- Tentacle health monitoring
- Swarm creation and management
- Quick action buttons for common tasks
- Live activity log

---

### Subsystems
- **Echo Operating System:** Core orchestration kernel.
- **Echo Vault:** Secure identity & state management layer.
- **Echo Engines:** Modular resonance engines (EchoFree, EchoLex, EchoCore).
- **Hydra:** Multi-AI fusion cybersecurity system.

### Documentation
All reference materials and design notes are under `/docs/`.

### License
MIT License - Use responsibly for authorized security testing only.

### Author
Nathan Poinsette
Founder | Archivist | Systems Engineer

---

**Warning**: This tool is for authorized security testing, research, and educational purposes only. Always obtain proper authorization before testing systems you do not own.
