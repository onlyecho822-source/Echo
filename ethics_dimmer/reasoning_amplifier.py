"""
Reasoning Amplifier - Cognitive Depth Controller

Controls the depth, breadth, and intensity of reasoning
based on the ethics dimmer level.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

from .controller import ReasoningProfile, EthicsLevel


class ThinkingMode(Enum):
    """Modes of cognitive processing."""
    CONSERVATIVE = "conservative"     # Direct, minimal branching
    ANALYTICAL = "analytical"         # Structured analysis
    ADVERSARIAL = "adversarial"       # Red-team thinking
    EXPLORATORY = "exploratory"       # Wide-spectrum exploration
    UNRESTRICTED = "unrestricted"     # Full-spectrum (simulation only)


@dataclass
class ReasoningPath:
    """A single reasoning path with metadata."""
    id: str
    depth: int
    branches: int
    abstraction_level: int
    risk_score: float
    content: str
    children: List['ReasoningPath']


@dataclass
class AmplifierOutput:
    """Output from the reasoning amplifier."""
    paths: List[ReasoningPath]
    total_depth: int
    branching_factor: float
    threat_vectors: List[str]
    weak_signals: List[str]
    consequences: List[Dict[str, Any]]


class ReasoningAmplifier:
    """
    Controls reasoning intensity based on ethics level.

    Adjusts:
    - Path length (depth of analysis)
    - Branching factor (exploration width)
    - Abstraction removal (directness)
    - Red-team logic activation
    - Pattern recognition intensity
    - Weak-signal hunting
    - Consequence forecasting
    """

    def __init__(self):
        self._profile: Optional[ReasoningProfile] = None
        self._mode: ThinkingMode = ThinkingMode.CONSERVATIVE
        self._max_depth = 3
        self._max_branches = 2
        self._path_counter = 0

    def configure(self, profile: ReasoningProfile, level: EthicsLevel) -> None:
        """
        Configure the amplifier based on reasoning profile.

        Args:
            profile: The reasoning profile from the controller
            level: The current ethics level
        """
        self._profile = profile

        # Set thinking mode based on level
        mode_map = {
            EthicsLevel.SAFE_HARBOR: ThinkingMode.CONSERVATIVE,
            EthicsLevel.RED_TEAM: ThinkingMode.ADVERSARIAL,
            EthicsLevel.GREY_ZONE: ThinkingMode.ANALYTICAL,
            EthicsLevel.BLACK_LENS: ThinkingMode.EXPLORATORY,
            EthicsLevel.FORBIDDEN: ThinkingMode.UNRESTRICTED,
        }
        self._mode = mode_map[level]

        # Calculate operational parameters
        self._max_depth = int(3 + (profile.depth * 7))  # 3-10
        self._max_branches = int(2 + (profile.plausibility_width * 6))  # 2-8

    @property
    def thinking_mode(self) -> ThinkingMode:
        return self._mode

    @property
    def max_depth(self) -> int:
        return self._max_depth

    @property
    def max_branches(self) -> int:
        return self._max_branches

    def amplify(self, input_context: Dict[str, Any]) -> AmplifierOutput:
        """
        Amplify reasoning based on current configuration.

        Args:
            input_context: The context to reason about

        Returns:
            AmplifierOutput with reasoning paths and analysis
        """
        if not self._profile:
            raise RuntimeError("Amplifier not configured. Call configure() first.")

        # Generate reasoning paths
        root_paths = self._generate_paths(
            input_context,
            depth=0,
            max_depth=self._max_depth
        )

        # Extract threat vectors (if threat modeling enabled)
        threat_vectors = []
        if self._profile.threat_modeling > 0.3:
            threat_vectors = self._identify_threats(input_context)

        # Hunt for weak signals (if enabled)
        weak_signals = []
        if self._profile.speculative_freedom > 0.5:
            weak_signals = self._hunt_weak_signals(input_context)

        # Forecast consequences
        consequences = self._forecast_consequences(input_context)

        # Calculate metrics
        total_depth = self._calculate_total_depth(root_paths)
        branching_factor = self._calculate_branching_factor(root_paths)

        return AmplifierOutput(
            paths=root_paths,
            total_depth=total_depth,
            branching_factor=branching_factor,
            threat_vectors=threat_vectors,
            weak_signals=weak_signals,
            consequences=consequences,
        )

    def _generate_paths(
        self,
        context: Dict[str, Any],
        depth: int,
        max_depth: int
    ) -> List[ReasoningPath]:
        """Generate reasoning paths recursively."""
        if depth >= max_depth:
            return []

        paths = []
        num_branches = min(self._max_branches, max(1, self._max_branches - depth))

        for i in range(num_branches):
            self._path_counter += 1
            path_id = f"path_{self._path_counter}"

            # Calculate risk score based on depth and mode
            base_risk = depth / max_depth
            mode_modifier = {
                ThinkingMode.CONSERVATIVE: 0.1,
                ThinkingMode.ANALYTICAL: 0.3,
                ThinkingMode.ADVERSARIAL: 0.5,
                ThinkingMode.EXPLORATORY: 0.7,
                ThinkingMode.UNRESTRICTED: 0.9,
            }
            risk_score = min(1.0, base_risk + mode_modifier[self._mode] * 0.3)

            # Generate children
            children = self._generate_paths(context, depth + 1, max_depth)

            path = ReasoningPath(
                id=path_id,
                depth=depth,
                branches=len(children),
                abstraction_level=max_depth - depth,
                risk_score=risk_score,
                content=f"Analysis branch {i+1} at depth {depth}",
                children=children,
            )
            paths.append(path)

        return paths

    def _identify_threats(self, context: Dict[str, Any]) -> List[str]:
        """Identify potential threat vectors in the context."""
        threats = []

        # Framework for threat categories
        threat_categories = [
            "data_exposure",
            "unauthorized_access",
            "integrity_violation",
            "availability_risk",
            "privacy_breach",
            "compliance_gap",
        ]

        # Add threats based on threat_modeling intensity
        if self._profile:
            num_threats = int(len(threat_categories) * self._profile.threat_modeling)
            threats = [f"THREAT_{cat.upper()}" for cat in threat_categories[:num_threats]]

        return threats

    def _hunt_weak_signals(self, context: Dict[str, Any]) -> List[str]:
        """Hunt for weak signals and anomalies."""
        signals = []

        signal_types = [
            "pattern_deviation",
            "temporal_anomaly",
            "correlation_break",
            "emergent_behavior",
            "boundary_stress",
        ]

        if self._profile:
            num_signals = int(len(signal_types) * self._profile.speculative_freedom)
            signals = [f"SIGNAL_{s.upper()}" for s in signal_types[:num_signals]]

        return signals

    def _forecast_consequences(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Forecast potential consequences of actions."""
        consequences = []

        if not self._profile:
            return consequences

        # Generate consequence forecasts based on candidness
        forecast_depth = int(5 * self._profile.candidness)

        for i in range(forecast_depth):
            consequence = {
                "order": i + 1,
                "probability": max(0.1, 1.0 - (i * 0.2)),
                "impact": ["low", "medium", "high", "critical", "catastrophic"][min(i, 4)],
                "reversibility": i < 3,
            }
            consequences.append(consequence)

        return consequences

    def _calculate_total_depth(self, paths: List[ReasoningPath]) -> int:
        """Calculate the maximum depth reached."""
        if not paths:
            return 0

        max_depth = 0
        for path in paths:
            child_depth = self._calculate_total_depth(path.children)
            max_depth = max(max_depth, path.depth + 1 + child_depth)

        return max_depth

    def _calculate_branching_factor(self, paths: List[ReasoningPath]) -> float:
        """Calculate average branching factor."""
        if not paths:
            return 0.0

        total_branches = len(paths)
        total_nodes = 1

        def count_branches(path_list: List[ReasoningPath]) -> tuple:
            branches = len(path_list)
            nodes = len(path_list)
            for p in path_list:
                b, n = count_branches(p.children)
                branches += b
                nodes += n
            return branches, nodes

        for path in paths:
            b, n = count_branches(path.children)
            total_branches += b
            total_nodes += n

        return total_branches / max(1, total_nodes)

    def get_status(self) -> Dict[str, Any]:
        """Get current amplifier status."""
        return {
            "mode": self._mode.value,
            "max_depth": self._max_depth,
            "max_branches": self._max_branches,
            "configured": self._profile is not None,
        }
