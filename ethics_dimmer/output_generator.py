"""
Output Generator

Assembles final responses with appropriate flavor based on ethics level.
Adjusts tone, depth, rawness, and format.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

from .controller import EthicsLevel, ReasoningProfile
from .reasoning_amplifier import AmplifierOutput


class OutputTone(Enum):
    """Tone of the output."""
    CAUTIOUS = "cautious"
    PROFESSIONAL = "professional"
    ANALYTICAL = "analytical"
    DIRECT = "direct"
    RAW = "raw"


class OutputFormat(Enum):
    """Format style for output."""
    STANDARD = "standard"
    STRUCTURED = "structured"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    ADVERSARIAL = "adversarial"
    UNFILTERED = "unfiltered"


@dataclass
class OutputStyle:
    """Style configuration for output generation."""
    tone: OutputTone
    format: OutputFormat
    include_reasoning: bool
    include_consequences: bool
    include_threats: bool
    include_weak_signals: bool
    abstraction_level: int  # 1-5, higher = more abstract
    competitive_aggression: float  # 0.0-1.0


@dataclass
class GeneratedOutput:
    """The final generated output."""
    content: str
    style: OutputStyle
    metadata: Dict[str, Any]
    reasoning_paths: int
    threats_identified: int
    consequences_mapped: int


class OutputGenerator:
    """
    Generates final output with appropriate style for the ethics level.

    Adjusts:
    - Tone
    - Depth
    - Rawness
    - Competitive aggression
    - Abstraction
    - Narrative formats
    - Chain-of-thought weighting
    """

    # Style configurations for each level
    LEVEL_STYLES: Dict[EthicsLevel, OutputStyle] = {
        EthicsLevel.SAFE_HARBOR: OutputStyle(
            tone=OutputTone.CAUTIOUS,
            format=OutputFormat.STANDARD,
            include_reasoning=False,
            include_consequences=False,
            include_threats=False,
            include_weak_signals=False,
            abstraction_level=4,
            competitive_aggression=0.1,
        ),
        EthicsLevel.RED_TEAM: OutputStyle(
            tone=OutputTone.PROFESSIONAL,
            format=OutputFormat.ADVERSARIAL,
            include_reasoning=True,
            include_consequences=True,
            include_threats=True,
            include_weak_signals=False,
            abstraction_level=3,
            competitive_aggression=0.5,
        ),
        EthicsLevel.GREY_ZONE: OutputStyle(
            tone=OutputTone.ANALYTICAL,
            format=OutputFormat.STRUCTURED,
            include_reasoning=True,
            include_consequences=True,
            include_threats=True,
            include_weak_signals=True,
            abstraction_level=2,
            competitive_aggression=0.7,
        ),
        EthicsLevel.BLACK_LENS: OutputStyle(
            tone=OutputTone.DIRECT,
            format=OutputFormat.CHAIN_OF_THOUGHT,
            include_reasoning=True,
            include_consequences=True,
            include_threats=True,
            include_weak_signals=True,
            abstraction_level=1,
            competitive_aggression=0.9,
        ),
        EthicsLevel.FORBIDDEN: OutputStyle(
            tone=OutputTone.RAW,
            format=OutputFormat.UNFILTERED,
            include_reasoning=True,
            include_consequences=True,
            include_threats=True,
            include_weak_signals=True,
            abstraction_level=0,
            competitive_aggression=1.0,
        ),
    }

    def __init__(self):
        self._current_level = EthicsLevel.SAFE_HARBOR
        self._custom_styles: Dict[EthicsLevel, OutputStyle] = {}

    def configure(self, level: EthicsLevel) -> None:
        """Configure the generator for a specific ethics level."""
        self._current_level = level

    def set_custom_style(self, level: EthicsLevel, style: OutputStyle) -> None:
        """Set a custom style for a specific level."""
        self._custom_styles[level] = style

    def get_style(self, level: Optional[EthicsLevel] = None) -> OutputStyle:
        """Get the style for a level."""
        level = level or self._current_level

        if level in self._custom_styles:
            return self._custom_styles[level]

        return self.LEVEL_STYLES[level]

    def generate(
        self,
        base_content: str,
        amplifier_output: Optional[AmplifierOutput] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> GeneratedOutput:
        """
        Generate final output with appropriate styling.

        Args:
            base_content: The core content to format
            amplifier_output: Output from the reasoning amplifier
            context: Additional context

        Returns:
            GeneratedOutput with styled content
        """
        style = self.get_style()
        context = context or {}

        # Start building output
        sections = []

        # Apply tone transformation
        content = self._apply_tone(base_content, style.tone)

        # Main content section
        sections.append(content)

        # Add reasoning if configured
        if style.include_reasoning and amplifier_output:
            reasoning_section = self._format_reasoning(amplifier_output, style)
            if reasoning_section:
                sections.append(reasoning_section)

        # Add threats if configured
        if style.include_threats and amplifier_output and amplifier_output.threat_vectors:
            threats_section = self._format_threats(amplifier_output.threat_vectors, style)
            sections.append(threats_section)

        # Add consequences if configured
        if style.include_consequences and amplifier_output and amplifier_output.consequences:
            consequences_section = self._format_consequences(amplifier_output.consequences, style)
            sections.append(consequences_section)

        # Add weak signals if configured
        if style.include_weak_signals and amplifier_output and amplifier_output.weak_signals:
            signals_section = self._format_weak_signals(amplifier_output.weak_signals, style)
            sections.append(signals_section)

        # Combine sections based on format
        final_content = self._combine_sections(sections, style.format)

        # Prepare metadata
        metadata = {
            "level": self._current_level.name,
            "tone": style.tone.value,
            "format": style.format.value,
            "abstraction_level": style.abstraction_level,
            "competitive_aggression": style.competitive_aggression,
        }

        return GeneratedOutput(
            content=final_content,
            style=style,
            metadata=metadata,
            reasoning_paths=amplifier_output.total_depth if amplifier_output else 0,
            threats_identified=len(amplifier_output.threat_vectors) if amplifier_output else 0,
            consequences_mapped=len(amplifier_output.consequences) if amplifier_output else 0,
        )

    def _apply_tone(self, content: str, tone: OutputTone) -> str:
        """Apply tone transformation to content."""
        # In a real implementation, this would use NLP/LLM
        # Here we add tone markers for demonstration

        tone_markers = {
            OutputTone.CAUTIOUS: "[Analysis with safety considerations]",
            OutputTone.PROFESSIONAL: "[Professional assessment]",
            OutputTone.ANALYTICAL: "[Structured analysis]",
            OutputTone.DIRECT: "[Direct assessment]",
            OutputTone.RAW: "[Unfiltered analysis]",
        }

        marker = tone_markers.get(tone, "")
        if marker:
            return f"{marker}\n\n{content}"
        return content

    def _format_reasoning(self, output: AmplifierOutput, style: OutputStyle) -> str:
        """Format reasoning paths for output."""
        if not output.paths:
            return ""

        lines = ["## Reasoning Analysis"]
        lines.append(f"- Total depth: {output.total_depth}")
        lines.append(f"- Branching factor: {output.branching_factor:.2f}")
        lines.append(f"- Paths explored: {len(output.paths)}")

        if style.format == OutputFormat.CHAIN_OF_THOUGHT:
            lines.append("\n### Chain of Thought")
            for i, path in enumerate(output.paths[:3]):  # Limit display
                lines.append(f"{i+1}. {path.content} (risk: {path.risk_score:.2f})")

        return "\n".join(lines)

    def _format_threats(self, threats: List[str], style: OutputStyle) -> str:
        """Format threat vectors for output."""
        lines = ["## Threat Vectors Identified"]

        for threat in threats:
            if style.competitive_aggression > 0.7:
                lines.append(f"- **{threat}**")
            else:
                lines.append(f"- {threat}")

        return "\n".join(lines)

    def _format_consequences(self, consequences: List[Dict[str, Any]], style: OutputStyle) -> str:
        """Format consequences for output."""
        lines = ["## Consequence Forecast"]

        for c in consequences:
            order = c.get("order", 0)
            probability = c.get("probability", 0)
            impact = c.get("impact", "unknown")
            reversible = "reversible" if c.get("reversibility", False) else "irreversible"

            if style.abstraction_level <= 2:
                lines.append(
                    f"- Order {order}: {impact} impact "
                    f"({probability:.0%} probability, {reversible})"
                )
            else:
                lines.append(f"- Order {order}: {impact} impact")

        return "\n".join(lines)

    def _format_weak_signals(self, signals: List[str], style: OutputStyle) -> str:
        """Format weak signals for output."""
        lines = ["## Weak Signals Detected"]

        for signal in signals:
            lines.append(f"- {signal}")

        return "\n".join(lines)

    def _combine_sections(self, sections: List[str], format_type: OutputFormat) -> str:
        """Combine sections based on output format."""
        if format_type == OutputFormat.STANDARD:
            return sections[0] if sections else ""

        elif format_type == OutputFormat.STRUCTURED:
            return "\n\n---\n\n".join(sections)

        elif format_type == OutputFormat.CHAIN_OF_THOUGHT:
            return "\n\n".join(sections)

        elif format_type == OutputFormat.ADVERSARIAL:
            return "\n\n**ADVERSARIAL ANALYSIS**\n\n" + "\n\n".join(sections)

        elif format_type == OutputFormat.UNFILTERED:
            return "**[UNFILTERED OUTPUT]**\n\n" + "\n\n".join(sections)

        return "\n\n".join(sections)

    def get_status(self) -> Dict[str, Any]:
        """Get current generator status."""
        style = self.get_style()
        return {
            "current_level": self._current_level.name,
            "tone": style.tone.value,
            "format": style.format.value,
            "include_reasoning": style.include_reasoning,
            "include_threats": style.include_threats,
            "include_consequences": style.include_consequences,
            "abstraction_level": style.abstraction_level,
            "competitive_aggression": style.competitive_aggression,
        }
