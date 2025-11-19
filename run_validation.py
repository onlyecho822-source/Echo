#!/usr/bin/env python3
"""
ECHO ORGANISM v2.1 - VALIDATION RUNNER
Quick command to run full validation suite.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_organism import run_all_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
