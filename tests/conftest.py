"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_generated_apps(tmp_path):
    """Fixture to create temporary directory for generated apps"""
    apps_dir = tmp_path / "generated_apps"
    apps_dir.mkdir()
    return apps_dir


@pytest.fixture(autouse=True)
def cleanup_test_apps():
    """Automatically cleanup test generated apps after each test"""
    yield
    # Cleanup happens in teardown methods of test classes
