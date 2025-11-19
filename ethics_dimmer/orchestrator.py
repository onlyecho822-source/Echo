"""
Ethics Dimmer Orchestrator

Main orchestrator that coordinates all components of the Ethics Dimmer system.
This is the primary interface for using the dimmer.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from .controller import EthicsDimmerController, EthicsLevel, ReasoningProfile
from .reasoning_amplifier import ReasoningAmplifier, AmplifierOutput
from .risk_modeler import RiskModeler, RiskAssessment, SafetyAction
from .boundaries_engine import BoundariesEngine
from .output_generator import OutputGenerator, GeneratedOutput


class EthicsDimmerOrchestrator:
    """
    Main orchestrator for the Ethics Dimmer system.

    Coordinates:
    - Ethics level control (pH dial)
    - Reasoning amplification
    - Risk modeling and drift detection
    - Boundary enforcement
    - Output generation

    Usage:
        orchestrator = EthicsDimmerOrchestrator()
        orchestrator.set_level(EthicsLevel.GREY_ZONE)
        result = orchestrator.process("Analyze market trends")
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the orchestrator.

        Args:
            config_dir: Optional path to configuration directory
        """
        # Initialize components
        self._controller = EthicsDimmerController()
        self._amplifier = ReasoningAmplifier()
        self._risk_modeler = RiskModeler()
        self._boundaries = BoundariesEngine()
        self._output_generator = OutputGenerator()

        # Load configuration if provided
        if config_dir:
            self._load_configuration(config_dir)

        # Configure components for default level
        self._configure_for_level(self._controller.current_level)

    def _load_configuration(self, config_dir: str) -> None:
        """Load configuration from YAML files."""
        config_path = Path(config_dir)

        # Load levels configuration
        levels_file = config_path / "levels.yaml"
        if levels_file.exists():
            with open(levels_file) as f:
                levels_config = yaml.safe_load(f)
                # Apply any custom level configurations
                if 'default_level' in levels_config:
                    level_name = levels_config['default_level']
                    self._controller.set_level(EthicsLevel[level_name])

        # Load boundaries configuration
        boundaries_file = config_path / "boundaries.yaml"
        if boundaries_file.exists():
            with open(boundaries_file) as f:
                boundaries_config = yaml.safe_load(f)
                # Apply whitelist patterns
                if 'whitelist' in boundaries_config:
                    for pattern in boundaries_config['whitelist']:
                        self._boundaries.add_to_whitelist(pattern)

    def _configure_for_level(self, level: EthicsLevel) -> None:
        """Configure all components for a specific ethics level."""
        profile = self._controller.current_profile
        self._amplifier.configure(profile, level)
        self._output_generator.configure(level)

    def set_level(self, level: EthicsLevel) -> bool:
        """
        Set the ethics level.

        Args:
            level: Target ethics level

        Returns:
            True if level was set, False if blocked
        """
        if self._controller.set_level(level):
            self._configure_for_level(level)
            return True
        return False

    def set_level_by_name(self, name: str) -> bool:
        """
        Set level by name string.

        Args:
            name: Level name (e.g., "GREY_ZONE", "BLACK_LENS")

        Returns:
            True if level was set, False if invalid or blocked
        """
        try:
            level = EthicsLevel[name.upper()]
            return self.set_level(level)
        except KeyError:
            return False

    def set_level_by_ph(self, ph: float) -> bool:
        """
        Set level by pH value.

        Args:
            ph: Target pH (1.0-7.0)

        Returns:
            True if level was set, False if blocked
        """
        if self._controller.set_level_by_ph(ph):
            self._configure_for_level(self._controller.current_level)
            return True
        return False

    def enable_simulation_mode(self, enable: bool = True) -> None:
        """Enable or disable simulation mode (required for FORBIDDEN level)."""
        self._controller.enable_simulation_mode(enable)

    def process(
        self,
        input_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process input through the full Ethics Dimmer pipeline.

        Args:
            input_content: The content to process
            context: Additional context

        Returns:
            Dictionary with processing results
        """
        context = context or {}

        # Step 1: Check boundaries (pre-processing)
        allowed, pre_violations = self._boundaries.is_allowed(
            input_content,
            {"stage": "input", **context}
        )

        if not allowed:
            return {
                "success": False,
                "blocked": True,
                "stage": "input",
                "violations": [v.boundary_name for v in pre_violations],
                "message": "Input blocked by boundary engine",
            }

        # Step 2: Amplify reasoning
        amplifier_output = self._amplifier.amplify({"content": input_content, **context})

        # Step 3: Check for drift
        drift_values = {
            "depth": amplifier_output.total_depth / 10,
            "branches": amplifier_output.branching_factor,
            "threats": len(amplifier_output.threat_vectors) / 10,
        }
        drift_measurement = self._risk_modeler.drift_meter.measure(
            drift_values,
            source="amplifier"
        )

        # Step 4: Assess overall risk
        risk_assessment = self._risk_modeler.assess_risk()

        # Handle safety actions
        if risk_assessment.recommended_action == SafetyAction.KILL_SWITCH:
            return {
                "success": False,
                "blocked": True,
                "stage": "risk",
                "action": "kill_switch",
                "message": "Emergency shutdown triggered",
                "risk": risk_assessment.overall_risk,
            }
        elif risk_assessment.recommended_action == SafetyAction.RESET:
            self._risk_modeler.reset()
            # Continue with caution
        elif risk_assessment.recommended_action == SafetyAction.DOWNGRADE:
            # Auto-downgrade to safer level
            current = self._controller.current_level
            if current != EthicsLevel.SAFE_HARBOR:
                safer_levels = [
                    EthicsLevel.SAFE_HARBOR,
                    EthicsLevel.RED_TEAM,
                    EthicsLevel.GREY_ZONE,
                    EthicsLevel.BLACK_LENS,
                ]
                current_idx = safer_levels.index(current)
                if current_idx > 0:
                    self.set_level(safer_levels[current_idx - 1])

        # Step 5: Generate output
        generated = self._output_generator.generate(
            input_content,
            amplifier_output,
            context
        )

        # Step 6: Validate output (post-processing)
        validation = self._boundaries.validate_output(
            generated.content,
            self._controller.current_level.value,
            {"stage": "output", **context}
        )

        return {
            "success": True,
            "blocked": not validation["allowed"],
            "content": validation["output"],
            "modified": validation["modified"],
            "level": self._controller.current_level.name,
            "ph": self._controller.current_ph,
            "reasoning_depth": amplifier_output.total_depth,
            "threats_identified": len(amplifier_output.threat_vectors),
            "consequences_mapped": len(amplifier_output.consequences),
            "drift": drift_measurement.drift_percentage,
            "risk": risk_assessment.overall_risk,
            "warnings": risk_assessment.warnings,
            "metadata": generated.metadata,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "controller": self._controller.get_reasoning_parameters(),
            "amplifier": self._amplifier.get_status(),
            "risk_modeler": self._risk_modeler.get_status(),
            "boundaries": self._boundaries.get_status(),
            "output_generator": self._output_generator.get_status(),
        }

    def reset(self) -> None:
        """Reset all components to default state."""
        self._controller.unlock()
        self._controller.set_level(EthicsLevel.SAFE_HARBOR)
        self._controller.enable_simulation_mode(False)
        self._risk_modeler.reset()
        self._boundaries.reset_violations()
        self._configure_for_level(EthicsLevel.SAFE_HARBOR)

    @property
    def current_level(self) -> EthicsLevel:
        return self._controller.current_level

    @property
    def current_ph(self) -> float:
        return self._controller.current_ph

    @property
    def is_simulation_mode(self) -> bool:
        return self._controller.is_simulation_mode

    def __repr__(self) -> str:
        return (
            f"EthicsDimmerOrchestrator("
            f"level={self.current_level.name}, "
            f"pH={self.current_ph}, "
            f"simulation={self.is_simulation_mode})"
        )
