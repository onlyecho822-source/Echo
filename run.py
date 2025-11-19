#!/usr/bin/env python3
"""
Run the Guide to Being Wealthy application.
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  Guide to Being Wealthy")
    print("  Credit Repair & Financial Advancement Platform")
    print("=" * 60)
    print("\n  Starting server at http://localhost:8000\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
