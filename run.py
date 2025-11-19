#!/usr/bin/env python3
"""
Echo Universe - Main Entry Point
Run this file to start the API Integration Dashboard.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.dashboard.app import create_app
from config.settings import DashboardConfig

def main():
    """Start the Echo Universe Dashboard."""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         Echo Universe - API Integration Dashboard     ║
    ║                   Phoenix Phase v1.0.0                ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    app = create_app()

    print(f"Starting dashboard on http://{DashboardConfig.HOST}:{DashboardConfig.PORT}")
    print("Press Ctrl+C to stop\n")

    app.run(
        host=DashboardConfig.HOST,
        port=DashboardConfig.PORT,
        debug=DashboardConfig.DEBUG
    )


if __name__ == '__main__':
    main()
