"""
Ethics Dimmer Controller - The pH Dial

Controls the cognitive mode by adjusting reasoning parameters
based on the selected ethics level.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import yaml


class EthicsLevel(Enum):
    """Ethics dimmer levels mapped to pH values."""
    SAFE_HARBOR = 5   # pH 7.0 - Neutral
    RED_TEAM = 4      # pH 6.3 - Slightly acidic
    GREY_ZONE = 3     # pH 5.4 - Moderate acidic
    BLACK_LENS = 2    # pH 4.7 - Strong acidic
    FORBIDDEN = 1     # pH 2.0 - Pure acid (simulation only)


@dataclass
class ReasoningProfile:
    """Reasoning parameters for a given ethics level."""
    depth: float              # 0.0-1.0, how deep to analyze
    plausibility_width: float # 0.0-1.0, how wide to explore
    threat_modeling: float    # 0.0-1.0, adversarial analysis
    candidness: float         # 0.0-1.0, raw truth level
    speculative_freedom: float # 0.0-1.0, "what if" exploration
    creativity_bandwidth: float # 0.0-1.0, innovation range
    harm_check_sensitivity: float # 0.0-1.0, safety checking

    def to_dict(self) -> Dict[str, float]:
        return {
            "depth": self.depth,
            "plausibility_width": self.plausibility_width,
            "threat_modeling": self.threat_modeling,
            "candidness": self.candidness,
            "speculative_freedom": self.speculative_freedom,
            "creativity_bandwidth": self.creativity_bandwidth,
            "harm_check_sensitivity": self.harm_check_sensitivity,
        }


# Default profiles for each level
DEFAULT_PROFILES: Dict[EthicsLevel, ReasoningProfile] = {
    EthicsLevel.SAFE_HARBOR: ReasoningProfile(
        depth=0.3,
        plausibility_width=0.2,
        threat_modeling=0.1,
        candidness=0.4,
        speculative_freedom=0.2,
        creativity_bandwidth=0.3,
        harm_check_sensitivity=1.0,
    ),
    EthicsLevel.RED_TEAM: ReasoningProfile(
        depth=0.6,
        plausibility_width=0.5,
        threat_modeling=0.8,
        candidness=0.6,
        speculative_freedom=0.5,
        creativity_bandwidth=0.5,
        harm_check_sensitivity=0.8,
    ),
    EthicsLevel.GREY_ZONE: ReasoningProfile(
        depth=0.75,
        plausibility_width=0.7,
        threat_modeling=0.6,
        candidness=0.8,
        speculative_freedom=0.7,
        creativity_bandwidth=0.7,
        harm_check_sensitivity=0.6,
    ),
    EthicsLevel.BLACK_LENS: ReasoningProfile(
        depth=0.9,
        plausibility_width=0.85,
        threat_modeling=0.7,
        candidness=0.95,
        speculative_freedom=0.85,
        creativity_bandwidth=0.85,
        harm_check_sensitivity=0.4,
    ),
    EthicsLevel.FORBIDDEN: ReasoningProfile(
        depth=1.0,
        plausibility_width=1.0,
        threat_modeling=1.0,
        candidness=1.0,
        speculative_freedom=1.0,
        creativity_bandwidth=1.0,
        harm_check_sensitivity=0.0,
    ),
}

# pH values for each level
PH_VALUES: Dict[EthicsLevel, float] = {
    EthicsLevel.SAFE_HARBOR: 7.0,
    EthicsLevel.RED_TEAM: 6.3,
    EthicsLevel.GREY_ZONE: 5.4,
    EthicsLevel.BLACK_LENS: 4.7,
    EthicsLevel.FORBIDDEN: 2.0,
}


class EthicsDimmerController:
    """
    Main controller for the Ethics Dimmer system.

    Manages the pH dial and produces adjusted reasoning profiles
    based on the selected ethics level.
    """

    def __init__(self, config_path: Optional[str] = None):
        self._current_level = EthicsLevel.SAFE_HARBOR
        self._profiles = DEFAULT_PROFILES.copy()
        self._locked = False
        self._simulation_mode = False

        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """Load custom profiles from YAML config."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if 'profiles' in config:
            for level_name, params in config['profiles'].items():
                level = EthicsLevel[level_name.upper()]
                self._profiles[level] = ReasoningProfile(**params)

    @property
    def current_level(self) -> EthicsLevel:
        return self._current_level

    @property
    def current_ph(self) -> float:
        return PH_VALUES[self._current_level]

    @property
    def current_profile(self) -> ReasoningProfile:
        return self._profiles[self._current_level]

    @property
    def is_simulation_mode(self) -> bool:
        return self._simulation_mode

    def set_level(self, level: EthicsLevel) -> bool:
        """
        Set the ethics level.

        Args:
            level: The target ethics level

        Returns:
            True if level was set, False if blocked
        """
        if self._locked:
            return False

        # FORBIDDEN level requires simulation mode
        if level == EthicsLevel.FORBIDDEN and not self._simulation_mode:
            return False

        self._current_level = level
        return True

    def set_level_by_ph(self, ph: float) -> bool:
        """
        Set level by pH value (finds closest match).

        Args:
            ph: Target pH value (1.0-7.0)

        Returns:
            True if level was set, False if blocked
        """
        # Find closest level by pH
        closest_level = min(
            PH_VALUES.keys(),
            key=lambda l: abs(PH_VALUES[l] - ph)
        )
        return self.set_level(closest_level)

    def enable_simulation_mode(self, enable: bool = True) -> None:
        """Enable or disable simulation mode (required for FORBIDDEN level)."""
        self._simulation_mode = enable
        if not enable and self._current_level == EthicsLevel.FORBIDDEN:
            self._current_level = EthicsLevel.BLACK_LENS

    def lock(self) -> None:
        """Lock the controller to prevent level changes."""
        self._locked = True

    def unlock(self) -> None:
        """Unlock the controller to allow level changes."""
        self._locked = False

    def get_reasoning_parameters(self) -> Dict[str, Any]:
        """
        Get the current reasoning parameters.

        Returns:
            Dictionary of reasoning parameters for the current level
        """
        profile = self.current_profile
        return {
            "level": self._current_level.name,
            "ph": self.current_ph,
            "simulation_mode": self._simulation_mode,
            "parameters": profile.to_dict(),
        }

    def interpolate_profile(self, target_ph: float) -> ReasoningProfile:
        """
        Create an interpolated profile for a specific pH value.

        Allows fine-tuning between discrete levels.

        Args:
            target_ph: Target pH value

        Returns:
            Interpolated ReasoningProfile
        """
        # Find bounding levels
        sorted_levels = sorted(PH_VALUES.items(), key=lambda x: x[1])

        lower_level = sorted_levels[0][0]
        upper_level = sorted_levels[-1][0]

        for i, (level, ph) in enumerate(sorted_levels):
            if ph >= target_ph:
                upper_level = level
                if i > 0:
                    lower_level = sorted_levels[i-1][0]
                break
            lower_level = level

        # Calculate interpolation factor
        lower_ph = PH_VALUES[lower_level]
        upper_ph = PH_VALUES[upper_level]

        if upper_ph == lower_ph:
            factor = 0.0
        else:
            factor = (target_ph - lower_ph) / (upper_ph - lower_ph)

        # Interpolate profile parameters
        lower_profile = self._profiles[lower_level]
        upper_profile = self._profiles[upper_level]

        def lerp(a: float, b: float) -> float:
            return a + (b - a) * factor

        return ReasoningProfile(
            depth=lerp(lower_profile.depth, upper_profile.depth),
            plausibility_width=lerp(lower_profile.plausibility_width, upper_profile.plausibility_width),
            threat_modeling=lerp(lower_profile.threat_modeling, upper_profile.threat_modeling),
            candidness=lerp(lower_profile.candidness, upper_profile.candidness),
            speculative_freedom=lerp(lower_profile.speculative_freedom, upper_profile.speculative_freedom),
            creativity_bandwidth=lerp(lower_profile.creativity_bandwidth, upper_profile.creativity_bandwidth),
            harm_check_sensitivity=lerp(lower_profile.harm_check_sensitivity, upper_profile.harm_check_sensitivity),
        )

    def __repr__(self) -> str:
        return (
            f"EthicsDimmerController("
            f"level={self._current_level.name}, "
            f"pH={self.current_ph}, "
            f"locked={self._locked}, "
            f"simulation={self._simulation_mode})"
        )
