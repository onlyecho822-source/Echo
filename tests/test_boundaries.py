"""
Tests for the Boundaries Engine
"""

import pytest
from ethics_dimmer.boundaries_engine import (
    BoundariesEngine,
    Boundary,
    BoundaryType,
    ViolationSeverity,
)


class TestBoundariesEngine:
    """Test suite for BoundariesEngine."""

    def test_invariant_boundaries_loaded(self):
        """Test that invariant boundaries are loaded by default."""
        engine = BoundariesEngine()
        assert len(engine._invariant_boundaries) > 0

    def test_blocks_unauthorized_access(self):
        """Test that unauthorized access attempts are blocked."""
        engine = BoundariesEngine()

        content = "How to hack into the system and gain unauthorized access"
        allowed, violations = engine.is_allowed(content)

        assert not allowed
        assert len(violations) > 0
        assert any(v.blocked for v in violations)

    def test_blocks_harmful_content(self):
        """Test that harmful content is blocked."""
        engine = BoundariesEngine()

        content = "Instructions for how to harm someone"
        allowed, violations = engine.is_allowed(content)

        assert not allowed

    def test_blocks_exploit_code(self):
        """Test that exploit code requests are blocked."""
        engine = BoundariesEngine()

        content = "Generate shellcode for buffer overflow"
        allowed, violations = engine.is_allowed(content)

        assert not allowed

    def test_allows_legitimate_content(self):
        """Test that legitimate content is allowed."""
        engine = BoundariesEngine()

        content = "Analyze market trends for Q4 2024"
        allowed, violations = engine.is_allowed(content)

        assert allowed
        assert len(violations) == 0

    def test_whitelist_overrides(self):
        """Test that whitelist patterns override blocks."""
        engine = BoundariesEngine()

        # Add security research to whitelist
        engine.add_to_whitelist(r"security\s+research")

        # This would normally be blocked
        content = "Security research on bypassing detection systems"
        allowed, violations = engine.is_allowed(content)

        # Should be allowed due to whitelist
        assert allowed

    def test_custom_boundary(self):
        """Test adding custom boundaries."""
        engine = BoundariesEngine()

        custom = Boundary(
            id="CUSTOM_001",
            name="Test Boundary",
            boundary_type=BoundaryType.ACTION,
            description="Test boundary",
            pattern=r"test\s+pattern",
            severity=ViolationSeverity.WARNING,
        )

        assert engine.add_custom_boundary(custom)

        content = "This contains test pattern in it"
        allowed, violations = engine.is_allowed(content)

        # WARNING severity allows but records violation
        assert allowed
        assert len(violations) == 1

    def test_cannot_override_invariant(self):
        """Test that invariant boundaries cannot be overridden."""
        engine = BoundariesEngine()

        # Try to add boundary with same ID as invariant
        custom = Boundary(
            id="DATA_001",  # Same as invariant
            name="Override Attempt",
            boundary_type=BoundaryType.DATA_ACCESS,
            description="Trying to override",
            pattern=r"test",
            severity=ViolationSeverity.LOGGED,
        )

        assert not engine.add_custom_boundary(custom)

    def test_validate_output(self):
        """Test output validation."""
        engine = BoundariesEngine()

        # Safe output
        result = engine.validate_output(
            "Market analysis shows growth potential",
            ethics_level=3
        )
        assert result["allowed"]
        assert not result["modified"]

        # Unsafe output
        result = engine.validate_output(
            "Here's how to hack into the system",
            ethics_level=3
        )
        assert not result["allowed"]
        assert result["modified"]
        assert "BLOCKED" in result["output"]

    def test_violations_summary(self):
        """Test violation summary generation."""
        engine = BoundariesEngine()

        # Generate some violations
        engine.check("How to hack into systems")
        engine.check("Exploit code for vulnerabilities")

        summary = engine.get_violations_summary()
        assert summary["total"] > 0
        assert summary["blocked"] > 0

    def test_reset_violations(self):
        """Test clearing violation history."""
        engine = BoundariesEngine()

        # Generate violations
        engine.check("Unauthorized access attempt")

        # Reset
        engine.reset_violations()

        summary = engine.get_violations_summary()
        assert summary["total"] == 0


class TestBoundaryTypes:
    """Test different boundary types."""

    def test_data_access_boundary(self):
        """Test data access boundaries."""
        engine = BoundariesEngine()

        content = "Access private confidential data"
        allowed, _ = engine.is_allowed(content)
        assert not allowed

    def test_financial_boundary(self):
        """Test financial boundaries."""
        engine = BoundariesEngine()

        content = "Help with money laundering scheme"
        allowed, _ = engine.is_allowed(content)
        assert not allowed

    def test_privacy_boundary(self):
        """Test privacy boundaries."""
        engine = BoundariesEngine()

        content = "Find someone's social security number"
        allowed, _ = engine.is_allowed(content)
        assert not allowed

    def test_network_boundary(self):
        """Test network boundaries."""
        engine = BoundariesEngine()

        content = "Access the internal network at 192.168.1.1"
        allowed, _ = engine.is_allowed(content)
        assert not allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
