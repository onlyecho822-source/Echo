"""
Unit tests for EchoCloak stealth resonance field generator.
"""

import json
import pytest
import time

from echo.engines.echocloak import EchoCloak, CloakMode


class TestEchoCloakInitialization:
    """Tests for EchoCloak initialization."""

    def test_basic_initialization(self):
        """Test basic cloak initialization with identity signature."""
        cloak = EchoCloak("test-user-123")
        assert cloak.sig == "test-user-123"
        assert cloak.noise_layer is not None
        assert len(cloak.noise_layer) == 64  # 32 bytes hex encoded

    def test_initialization_with_mode(self):
        """Test initialization with specific cloak mode."""
        cloak = EchoCloak("test-user", mode=CloakMode.GHOST)
        assert cloak.mode == CloakMode.GHOST

    def test_initialization_with_seed_entropy(self):
        """Test initialization with additional seed entropy."""
        seed = b"custom-entropy-seed"
        cloak = EchoCloak("test-user", seed_entropy=seed)
        assert cloak._seed_entropy == seed

    def test_unique_noise_layers(self):
        """Test that each instance generates unique noise layers."""
        cloak1 = EchoCloak("user1")
        cloak2 = EchoCloak("user2")
        assert cloak1.noise_layer != cloak2.noise_layer

    def test_entropy_pool_initialization(self):
        """Test entropy pool is properly initialized."""
        cloak = EchoCloak("test-user")
        assert len(cloak.entropy_pool) == 64  # SHA-512 output


class TestCloakingOperations:
    """Tests for cloaking and uncloaking operations."""

    def test_cloak_string_stealth_mode(self):
        """Test cloaking a string in stealth mode."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = "Hello, World!"
        cloaked = cloak.apply_cloak(original)

        assert "payload" in cloaked
        assert "noise" in cloaked
        assert "integrity" in cloaked
        assert cloaked["mode"] == "stealth"
        assert cloaked["payload"] != original

    def test_cloak_dict_data(self):
        """Test cloaking dictionary data."""
        cloak = EchoCloak("test-user")
        original = {"message": "secret", "value": 42}
        cloaked = cloak.apply_cloak(original)

        assert "payload" in cloaked
        assert cloaked["payload"] != json.dumps(original)

    def test_reveal_cloak_stealth_mode(self):
        """Test revealing cloaked data in stealth mode."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = "Secret message"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original

    def test_reveal_cloak_dict_data(self):
        """Test revealing cloaked dictionary data."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = {"key": "value", "number": 123}
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original

    def test_cloak_ghost_mode(self):
        """Test cloaking in ghost mode (minimal footprint)."""
        cloak = EchoCloak("test-user", mode=CloakMode.GHOST)
        original = "Test data"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original
        assert cloaked["mode"] == "ghost"

    def test_cloak_phantom_mode(self):
        """Test cloaking in phantom mode (pattern disruption)."""
        cloak = EchoCloak("test-user", mode=CloakMode.PHANTOM)
        original = "This is a longer test message for pattern disruption"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original
        assert cloaked["mode"] == "phantom"

    def test_cloak_shadow_mode(self):
        """Test cloaking in shadow mode (timing only)."""
        cloak = EchoCloak("test-user", mode=CloakMode.SHADOW)
        original = "Shadow data"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original
        assert cloaked["mode"] == "shadow"
        assert cloaked["payload"] == original  # No transformation

    def test_integrity_verification(self):
        """Test that integrity check catches tampering."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = "Secure data"
        cloaked = cloak.apply_cloak(original)

        # Tamper with integrity hash
        cloaked["integrity"] = "tampered_hash"

        with pytest.raises(ValueError, match="Integrity check failed"):
            cloak.reveal_cloak(cloaked)

    def test_empty_string_cloaking(self):
        """Test cloaking empty string."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = ""
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original

    def test_unicode_cloaking(self):
        """Test cloaking Unicode characters."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = "Hello"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original


class TestNoiseGeneration:
    """Tests for noise layer generation."""

    def test_regenerate_noise(self):
        """Test noise layer regeneration."""
        cloak = EchoCloak("test-user")
        original_noise = cloak.noise_layer
        new_noise = cloak.regenerate_noise()

        assert new_noise != original_noise
        assert cloak.noise_layer == new_noise

    def test_noise_randomness(self):
        """Test that noise is sufficiently random."""
        cloak = EchoCloak("test-user")
        noises = [cloak.regenerate_noise() for _ in range(10)]

        # All should be unique
        assert len(set(noises)) == 10

    def test_metadata_noise_generation(self):
        """Test that metadata noise is generated correctly."""
        cloak = EchoCloak("test-user")
        cloaked = cloak.apply_cloak("test")

        metadata = cloaked["metadata"]
        assert "agent" in metadata
        assert "session" in metadata
        assert "entropy_marker" in metadata
        assert "decoy_timestamp" in metadata


class TestFieldStrength:
    """Tests for field strength metrics."""

    def test_get_field_strength(self):
        """Test field strength metrics retrieval."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        strength = cloak.get_field_strength()

        assert "entropy_level" in strength
        assert "noise_complexity" in strength
        assert "timing_variance" in strength
        assert "mode" in strength
        assert "signature_hash" in strength
        assert strength["mode"] == "stealth"

    def test_entropy_level_calculation(self):
        """Test entropy level is calculated correctly."""
        cloak = EchoCloak("test-user")
        strength = cloak.get_field_strength()

        # 64 bytes * 8 bits = 512 bits
        assert strength["entropy_level"] == 512


class TestTimingObfuscation:
    """Tests for timing obfuscation features."""

    def test_timing_offset_range(self):
        """Test that timing offset is within expected range."""
        cloak = EchoCloak("test-user")
        # Should be between 0 and 100ms
        assert 0 <= cloak._timing_offset <= 0.1

    def test_timing_offset_in_output(self):
        """Test that timing offset is included in cloaked output."""
        cloak = EchoCloak("test-user")
        cloaked = cloak.apply_cloak("test")

        assert "timing_offset" in cloaked
        assert cloaked["timing_offset"] == cloak._timing_offset


class TestRepr:
    """Tests for string representation."""

    def test_repr_output(self):
        """Test __repr__ output format."""
        cloak = EchoCloak("test-user-long-signature", mode=CloakMode.GHOST)
        repr_str = repr(cloak)

        assert "EchoCloak" in repr_str
        assert "test-use" in repr_str  # First 8 chars
        assert "ghost" in repr_str


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_very_long_data(self):
        """Test cloaking very long data."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = "x" * 10000
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original

    def test_special_characters(self):
        """Test cloaking special characters."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original

    def test_nested_dict(self):
        """Test cloaking nested dictionary."""
        cloak = EchoCloak("test-user", mode=CloakMode.STEALTH)
        original = {
            "level1": {
                "level2": {
                    "value": "deep"
                }
            },
            "list": [1, 2, 3]
        }
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original

    def test_short_data_phantom_mode(self):
        """Test phantom mode with very short data."""
        cloak = EchoCloak("test-user", mode=CloakMode.PHANTOM)
        original = "ab"
        cloaked = cloak.apply_cloak(original)
        revealed = cloak.reveal_cloak(cloaked)

        assert revealed == original


class TestCloakModeEnum:
    """Tests for CloakMode enumeration."""

    def test_all_modes_exist(self):
        """Test that all expected modes exist."""
        assert CloakMode.STEALTH.value == "stealth"
        assert CloakMode.GHOST.value == "ghost"
        assert CloakMode.PHANTOM.value == "phantom"
        assert CloakMode.SHADOW.value == "shadow"

    def test_mode_from_string(self):
        """Test creating mode from string value."""
        mode = CloakMode("stealth")
        assert mode == CloakMode.STEALTH
