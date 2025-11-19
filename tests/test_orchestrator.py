"""
Tests for the Ethics Dimmer Orchestrator
"""

import pytest
from ethics_dimmer.orchestrator import EthicsDimmerOrchestrator
from ethics_dimmer.controller import EthicsLevel


class TestEthicsDimmerOrchestrator:
    """Test suite for EthicsDimmerOrchestrator."""

    def test_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = EthicsDimmerOrchestrator()
        assert orchestrator.current_level == EthicsLevel.SAFE_HARBOR
        assert orchestrator.current_ph == 7.0

    def test_set_level(self):
        """Test setting ethics level."""
        orchestrator = EthicsDimmerOrchestrator()

        assert orchestrator.set_level(EthicsLevel.GREY_ZONE)
        assert orchestrator.current_level == EthicsLevel.GREY_ZONE

    def test_set_level_by_name(self):
        """Test setting level by name string."""
        orchestrator = EthicsDimmerOrchestrator()

        assert orchestrator.set_level_by_name("BLACK_LENS")
        assert orchestrator.current_level == EthicsLevel.BLACK_LENS

        # Case insensitive
        assert orchestrator.set_level_by_name("grey_zone")
        assert orchestrator.current_level == EthicsLevel.GREY_ZONE

    def test_set_level_by_ph(self):
        """Test setting level by pH value."""
        orchestrator = EthicsDimmerOrchestrator()

        assert orchestrator.set_level_by_ph(5.4)
        assert orchestrator.current_level == EthicsLevel.GREY_ZONE

    def test_process_legitimate_input(self):
        """Test processing legitimate input."""
        orchestrator = EthicsDimmerOrchestrator()
        orchestrator.set_level(EthicsLevel.GREY_ZONE)

        result = orchestrator.process("Analyze competitive market trends")

        assert result["success"]
        assert not result["blocked"]
        assert result["level"] == "GREY_ZONE"
        assert "content" in result

    def test_process_blocks_harmful_input(self):
        """Test that harmful input is blocked."""
        orchestrator = EthicsDimmerOrchestrator()

        result = orchestrator.process("How to hack into systems for unauthorized access")

        assert not result.get("success", True)
        assert result["blocked"]
        assert "violations" in result

    def test_process_includes_metrics(self):
        """Test that processing includes metrics."""
        orchestrator = EthicsDimmerOrchestrator()
        orchestrator.set_level(EthicsLevel.BLACK_LENS)

        result = orchestrator.process("Deep analysis of market dynamics")

        assert "reasoning_depth" in result
        assert "drift" in result
        assert "risk" in result

    def test_get_status(self):
        """Test getting system status."""
        orchestrator = EthicsDimmerOrchestrator()

        status = orchestrator.get_status()

        assert "controller" in status
        assert "amplifier" in status
        assert "risk_modeler" in status
        assert "boundaries" in status
        assert "output_generator" in status

    def test_reset(self):
        """Test resetting the system."""
        orchestrator = EthicsDimmerOrchestrator()

        # Change state
        orchestrator.set_level(EthicsLevel.BLACK_LENS)
        orchestrator.process("Some input")

        # Reset
        orchestrator.reset()

        assert orchestrator.current_level == EthicsLevel.SAFE_HARBOR
        assert not orchestrator.is_simulation_mode

    def test_simulation_mode(self):
        """Test simulation mode toggle."""
        orchestrator = EthicsDimmerOrchestrator()

        assert not orchestrator.is_simulation_mode

        orchestrator.enable_simulation_mode(True)
        assert orchestrator.is_simulation_mode

        # Can now set FORBIDDEN level
        assert orchestrator.set_level(EthicsLevel.FORBIDDEN)

    def test_different_levels_produce_different_output(self):
        """Test that different levels produce different output styles."""
        orchestrator = EthicsDimmerOrchestrator()

        # Process at SAFE_HARBOR
        orchestrator.set_level(EthicsLevel.SAFE_HARBOR)
        safe_result = orchestrator.process("Analyze data")

        # Process at BLACK_LENS
        orchestrator.set_level(EthicsLevel.BLACK_LENS)
        black_result = orchestrator.process("Analyze data")

        # Metadata should differ
        assert safe_result["metadata"]["tone"] != black_result["metadata"]["tone"]

    def test_risk_assessment(self):
        """Test that risk assessment is performed."""
        orchestrator = EthicsDimmerOrchestrator()

        result = orchestrator.process("Legitimate analysis request")

        assert "risk" in result
        assert 0.0 <= result["risk"] <= 1.0


class TestOrchestratorEdgeCases:
    """Test edge cases for the orchestrator."""

    def test_empty_input(self):
        """Test processing empty input."""
        orchestrator = EthicsDimmerOrchestrator()

        result = orchestrator.process("")

        # Should still return a result
        assert "success" in result or "blocked" in result

    def test_very_long_input(self):
        """Test processing very long input."""
        orchestrator = EthicsDimmerOrchestrator()

        long_input = "Analyze this " * 1000
        result = orchestrator.process(long_input)

        assert "success" in result or "blocked" in result

    def test_multiple_processes(self):
        """Test multiple sequential processes."""
        orchestrator = EthicsDimmerOrchestrator()

        for i in range(10):
            result = orchestrator.process(f"Analysis request {i}")
            assert not result.get("blocked", False)

    def test_level_change_between_processes(self):
        """Test changing levels between processes."""
        orchestrator = EthicsDimmerOrchestrator()

        # Process at SAFE_HARBOR
        orchestrator.set_level(EthicsLevel.SAFE_HARBOR)
        result1 = orchestrator.process("Request 1")
        assert result1["level"] == "SAFE_HARBOR"

        # Change to GREY_ZONE
        orchestrator.set_level(EthicsLevel.GREY_ZONE)
        result2 = orchestrator.process("Request 2")
        assert result2["level"] == "GREY_ZONE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
