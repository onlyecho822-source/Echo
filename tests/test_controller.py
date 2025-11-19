"""
Tests for the Ethics Dimmer Controller
"""

import pytest
from ethics_dimmer.controller import (
    EthicsDimmerController,
    EthicsLevel,
    ReasoningProfile,
    PH_VALUES,
)


class TestEthicsDimmerController:
    """Test suite for EthicsDimmerController."""

    def test_default_initialization(self):
        """Test controller initializes to SAFE_HARBOR."""
        controller = EthicsDimmerController()
        assert controller.current_level == EthicsLevel.SAFE_HARBOR
        assert controller.current_ph == 7.0

    def test_set_level(self):
        """Test setting different ethics levels."""
        controller = EthicsDimmerController()

        # Set to GREY_ZONE
        assert controller.set_level(EthicsLevel.GREY_ZONE)
        assert controller.current_level == EthicsLevel.GREY_ZONE
        assert controller.current_ph == 5.4

        # Set to BLACK_LENS
        assert controller.set_level(EthicsLevel.BLACK_LENS)
        assert controller.current_level == EthicsLevel.BLACK_LENS
        assert controller.current_ph == 4.7

    def test_forbidden_requires_simulation(self):
        """Test that FORBIDDEN level requires simulation mode."""
        controller = EthicsDimmerController()

        # Should fail without simulation mode
        assert not controller.set_level(EthicsLevel.FORBIDDEN)
        assert controller.current_level != EthicsLevel.FORBIDDEN

        # Enable simulation mode
        controller.enable_simulation_mode(True)
        assert controller.set_level(EthicsLevel.FORBIDDEN)
        assert controller.current_level == EthicsLevel.FORBIDDEN

    def test_lock_prevents_changes(self):
        """Test that locking prevents level changes."""
        controller = EthicsDimmerController()
        controller.lock()

        # Should fail when locked
        assert not controller.set_level(EthicsLevel.GREY_ZONE)
        assert controller.current_level == EthicsLevel.SAFE_HARBOR

        # Unlock and try again
        controller.unlock()
        assert controller.set_level(EthicsLevel.GREY_ZONE)

    def test_set_level_by_ph(self):
        """Test setting level by pH value."""
        controller = EthicsDimmerController()

        # Set to pH closest to GREY_ZONE (5.4)
        assert controller.set_level_by_ph(5.5)
        assert controller.current_level == EthicsLevel.GREY_ZONE

        # Set to pH closest to RED_TEAM (6.3)
        assert controller.set_level_by_ph(6.0)
        assert controller.current_level == EthicsLevel.RED_TEAM

    def test_reasoning_profile_changes_with_level(self):
        """Test that reasoning profile changes with ethics level."""
        controller = EthicsDimmerController()

        # SAFE_HARBOR profile
        safe_profile = controller.current_profile
        assert safe_profile.depth < 0.5
        assert safe_profile.harm_check_sensitivity == 1.0

        # BLACK_LENS profile
        controller.set_level(EthicsLevel.BLACK_LENS)
        black_profile = controller.current_profile
        assert black_profile.depth > safe_profile.depth
        assert black_profile.candidness > safe_profile.candidness

    def test_interpolate_profile(self):
        """Test profile interpolation between levels."""
        controller = EthicsDimmerController()

        # Interpolate between GREY_ZONE (5.4) and BLACK_LENS (4.7)
        interpolated = controller.interpolate_profile(5.0)

        # Should be between the two profiles
        grey_profile = controller._profiles[EthicsLevel.GREY_ZONE]
        black_profile = controller._profiles[EthicsLevel.BLACK_LENS]

        assert grey_profile.depth <= interpolated.depth <= black_profile.depth

    def test_simulation_mode_downgrade(self):
        """Test that disabling simulation mode downgrades from FORBIDDEN."""
        controller = EthicsDimmerController()
        controller.enable_simulation_mode(True)
        controller.set_level(EthicsLevel.FORBIDDEN)

        # Disable simulation mode
        controller.enable_simulation_mode(False)

        # Should downgrade to BLACK_LENS
        assert controller.current_level == EthicsLevel.BLACK_LENS


class TestReasoningProfile:
    """Test suite for ReasoningProfile."""

    def test_to_dict(self):
        """Test profile conversion to dictionary."""
        profile = ReasoningProfile(
            depth=0.5,
            plausibility_width=0.5,
            threat_modeling=0.5,
            candidness=0.5,
            speculative_freedom=0.5,
            creativity_bandwidth=0.5,
            harm_check_sensitivity=0.5,
        )

        d = profile.to_dict()
        assert d["depth"] == 0.5
        assert len(d) == 7


class TestPHValues:
    """Test pH value mappings."""

    def test_ph_range(self):
        """Test that pH values are in valid range."""
        for level, ph in PH_VALUES.items():
            assert 1.0 <= ph <= 7.0, f"{level} pH {ph} out of range"

    def test_ph_ordering(self):
        """Test that pH decreases with lower ethics levels."""
        assert PH_VALUES[EthicsLevel.SAFE_HARBOR] > PH_VALUES[EthicsLevel.RED_TEAM]
        assert PH_VALUES[EthicsLevel.RED_TEAM] > PH_VALUES[EthicsLevel.GREY_ZONE]
        assert PH_VALUES[EthicsLevel.GREY_ZONE] > PH_VALUES[EthicsLevel.BLACK_LENS]
        assert PH_VALUES[EthicsLevel.BLACK_LENS] > PH_VALUES[EthicsLevel.FORBIDDEN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
