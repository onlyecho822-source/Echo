"""
Aletheia - Reality Decoding System
===================================

An auditable, operator-first system for collecting sealed raw evidence,
running reproducible analyses, and producing verifiable truth-packets.

Author: Echo Nexus Omega
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Echo Nexus Omega"
__operator__ = "Nathan Poinsette"

from pathlib import Path

# Package root
ALETHEIA_ROOT = Path(__file__).parent

# Submodule paths
SCHEMAS_DIR = ALETHEIA_ROOT / "schemas"
CLI_DIR = ALETHEIA_ROOT / "cli"
PIPELINES_DIR = ALETHEIA_ROOT / "pipelines"
PROMPTS_DIR = ALETHEIA_ROOT / "prompts"
VAULT_DIR = ALETHEIA_ROOT / "vault"
LEDGER_DIR = ALETHEIA_ROOT / "ledger"
REGISTRY_DIR = ALETHEIA_ROOT / "registry"
GRAPH_DIR = ALETHEIA_ROOT / "graph"
CONFIG_DIR = ALETHEIA_ROOT / "config"

__all__ = [
    "__version__",
    "__author__",
    "__operator__",
    "ALETHEIA_ROOT",
    "SCHEMAS_DIR",
    "CLI_DIR",
    "PIPELINES_DIR",
    "PROMPTS_DIR",
    "VAULT_DIR",
    "LEDGER_DIR",
    "REGISTRY_DIR",
    "GRAPH_DIR",
    "CONFIG_DIR",
]
