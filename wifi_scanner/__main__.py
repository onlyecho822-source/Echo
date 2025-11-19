"""
Entry point for running wifi_scanner as a module.

Usage:
    python -m wifi_scanner [options]
"""

from .cli import main

if __name__ == "__main__":
    exit(main())
