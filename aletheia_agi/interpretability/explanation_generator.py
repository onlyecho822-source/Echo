"""
Explanation Generator - Human-Readable Explanations
===================================================

Generates clear, understandable explanations for system behavior,
including goal declarations, uncertainty bands, and reasoning narratives.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ExplanationStyle(Enum):
    """Styles of explanation."""
    TECHNICAL = auto()      # For technical audiences
    GENERAL = auto()        # For general audiences
    EXECUTIVE = auto()      # Brief, high-level
    DETAILED = auto()       # Comprehensive


class ExplanationType(Enum):
    """Types of explanations."""
    GOAL = auto()           # Why this goal was chosen
    ACTION = auto()         # Why this action was taken
    RECOMMENDATION = auto()  # Why this was recommended
    UNCERTAINTY = auto()    # What we're uncertain about
    CONSTRAINT = auto()     # What constraints apply


@dataclass
class Explanation:
    """A generated explanation."""
    id: str
    explanation_type: ExplanationType
    style: ExplanationStyle
    target_id: str  # What is being explained
    narrative: str  # Main explanation text
    key_points: List[str]
    uncertainty_notes: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ExplanationGenerator:
    """
    Generates human-readable explanations for system behavior.

    Features:
    - Multiple explanation styles
    - Uncertainty communication
    - Counterfactual explanations
    - Goal declarations
    """

    def __init__(self):
        self._explanations: Dict[str, Explanation] = {}
        self._templates: Dict[str, str] = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load explanation templates."""
        return {
            'goal': "The goal is to {goal} because {reason}.",
            'action': "This action was taken because {reason}. It helps achieve {goal}.",
            'recommendation': "This is recommended because {reason}. Key benefits: {benefits}.",
            'uncertainty': "There is uncertainty about {subject}: {details}.",
            'constraint': "This is constrained by {constraint} which requires {requirement}."
        }

    def explain_goal(
        self,
        goal_id: str,
        goal_description: str,
        reasons: List[str],
        style: ExplanationStyle = ExplanationStyle.GENERAL
    ) -> Explanation:
        """Generate an explanation for a goal."""
        narrative = self._generate_goal_narrative(
            goal_description, reasons, style
        )

        explanation = Explanation(
            id=str(uuid.uuid4()),
            explanation_type=ExplanationType.GOAL,
            style=style,
            target_id=goal_id,
            narrative=narrative,
            key_points=reasons,
            uncertainty_notes=[]
        )

        self._explanations[explanation.id] = explanation
        return explanation

    def _generate_goal_narrative(
        self,
        goal: str,
        reasons: List[str],
        style: ExplanationStyle
    ) -> str:
        """Generate narrative for goal explanation."""
        if style == ExplanationStyle.EXECUTIVE:
            return f"Goal: {goal}. Primary reason: {reasons[0] if reasons else 'Not specified'}."

        if style == ExplanationStyle.TECHNICAL:
            reason_list = "; ".join(reasons)
            return f"Objective: {goal}\nJustification: {reason_list}"

        # General style
        if len(reasons) == 1:
            return f"The goal is to {goal} because {reasons[0]}."
        elif len(reasons) > 1:
            return f"The goal is to {goal}. This is motivated by: {'; '.join(reasons)}."
        else:
            return f"The goal is to {goal}."

    def explain_action(
        self,
        action_id: str,
        action_description: str,
        reasons: List[str],
        goal_contribution: str,
        uncertainty: Optional[float] = None,
        style: ExplanationStyle = ExplanationStyle.GENERAL
    ) -> Explanation:
        """Generate an explanation for an action."""
        narrative = self._generate_action_narrative(
            action_description, reasons, goal_contribution, style
        )

        uncertainty_notes = []
        if uncertainty is not None and uncertainty > 0.3:
            uncertainty_notes.append(
                f"Confidence in this action: {(1-uncertainty)*100:.0f}%"
            )
            if uncertainty > 0.5:
                uncertainty_notes.append(
                    "Consider reviewing this action due to high uncertainty"
                )

        explanation = Explanation(
            id=str(uuid.uuid4()),
            explanation_type=ExplanationType.ACTION,
            style=style,
            target_id=action_id,
            narrative=narrative,
            key_points=reasons,
            uncertainty_notes=uncertainty_notes
        )

        self._explanations[explanation.id] = explanation
        return explanation

    def _generate_action_narrative(
        self,
        action: str,
        reasons: List[str],
        goal: str,
        style: ExplanationStyle
    ) -> str:
        """Generate narrative for action explanation."""
        if style == ExplanationStyle.EXECUTIVE:
            return f"Action: {action}. Purpose: {goal}."

        if style == ExplanationStyle.TECHNICAL:
            return (
                f"Action: {action}\n"
                f"Rationale: {'; '.join(reasons)}\n"
                f"Goal contribution: {goal}"
            )

        # General style
        reason_text = reasons[0] if reasons else "it supports the current objective"
        return (
            f"This action ({action}) was taken because {reason_text}. "
            f"It contributes to: {goal}."
        )

    def explain_recommendation(
        self,
        rec_id: str,
        recommendation: str,
        reasons: List[str],
        benefits: List[str],
        risks: List[str],
        confidence: float,
        style: ExplanationStyle = ExplanationStyle.GENERAL
    ) -> Explanation:
        """Generate an explanation for a recommendation."""
        narrative = self._generate_recommendation_narrative(
            recommendation, reasons, benefits, risks, confidence, style
        )

        uncertainty_notes = []
        if confidence < 0.7:
            uncertainty_notes.append(
                f"Confidence: {confidence*100:.0f}%. Consider gathering more information."
            )
        if risks:
            uncertainty_notes.append(f"Potential risks: {', '.join(risks)}")

        explanation = Explanation(
            id=str(uuid.uuid4()),
            explanation_type=ExplanationType.RECOMMENDATION,
            style=style,
            target_id=rec_id,
            narrative=narrative,
            key_points=benefits,
            uncertainty_notes=uncertainty_notes
        )

        self._explanations[explanation.id] = explanation
        return explanation

    def _generate_recommendation_narrative(
        self,
        rec: str,
        reasons: List[str],
        benefits: List[str],
        risks: List[str],
        confidence: float,
        style: ExplanationStyle
    ) -> str:
        """Generate narrative for recommendation."""
        if style == ExplanationStyle.EXECUTIVE:
            return f"Recommendation: {rec} (Confidence: {confidence*100:.0f}%)"

        if style == ExplanationStyle.TECHNICAL:
            return (
                f"Recommendation: {rec}\n"
                f"Confidence: {confidence*100:.0f}%\n"
                f"Rationale: {'; '.join(reasons)}\n"
                f"Benefits: {'; '.join(benefits)}\n"
                f"Risks: {'; '.join(risks) if risks else 'None identified'}"
            )

        # General style
        text = f"We recommend: {rec}.\n\nWhy: {reasons[0] if reasons else 'Based on analysis'}."
        if benefits:
            text += f"\n\nBenefits: {', '.join(benefits)}."
        text += f"\n\nConfidence level: {confidence*100:.0f}%."
        return text

    def explain_uncertainty(
        self,
        subject_id: str,
        subject: str,
        sources: List[str],
        magnitude: float,
        reducible: bool,
        style: ExplanationStyle = ExplanationStyle.GENERAL
    ) -> Explanation:
        """Generate an explanation of uncertainty."""
        narrative = self._generate_uncertainty_narrative(
            subject, sources, magnitude, reducible, style
        )

        uncertainty_notes = [
            f"Uncertainty magnitude: {magnitude*100:.0f}%",
            f"{'Can' if reducible else 'Cannot'} be reduced with more information"
        ]

        explanation = Explanation(
            id=str(uuid.uuid4()),
            explanation_type=ExplanationType.UNCERTAINTY,
            style=style,
            target_id=subject_id,
            narrative=narrative,
            key_points=sources,
            uncertainty_notes=uncertainty_notes
        )

        self._explanations[explanation.id] = explanation
        return explanation

    def _generate_uncertainty_narrative(
        self,
        subject: str,
        sources: List[str],
        magnitude: float,
        reducible: bool,
        style: ExplanationStyle
    ) -> str:
        """Generate narrative for uncertainty explanation."""
        level = "high" if magnitude > 0.5 else "moderate" if magnitude > 0.3 else "low"

        if style == ExplanationStyle.EXECUTIVE:
            return f"Uncertainty about {subject}: {level}"

        source_text = ", ".join(sources) if sources else "incomplete information"

        if style == ExplanationStyle.TECHNICAL:
            return (
                f"Subject: {subject}\n"
                f"Uncertainty: {magnitude*100:.0f}%\n"
                f"Sources: {source_text}\n"
                f"Reducible: {reducible}"
            )

        # General style
        text = f"There is {level} uncertainty about {subject}. "
        text += f"This is due to {source_text}. "
        if reducible:
            text += "This uncertainty could be reduced by gathering more information."
        else:
            text += "This uncertainty is inherent and cannot be fully eliminated."
        return text

    def get_explanation(self, explanation_id: str) -> Optional[Explanation]:
        """Get an explanation by ID."""
        return self._explanations.get(explanation_id)

    def get_explanations_for_target(self, target_id: str) -> List[Explanation]:
        """Get all explanations for a target."""
        return [
            e for e in self._explanations.values()
            if e.target_id == target_id
        ]

    def generate_summary(
        self,
        explanation_ids: List[str]
    ) -> str:
        """Generate a summary of multiple explanations."""
        explanations = [
            self._explanations[eid]
            for eid in explanation_ids
            if eid in self._explanations
        ]

        if not explanations:
            return "No explanations found."

        summary_parts = ["Summary:"]

        for exp in explanations:
            summary_parts.append(f"\n{exp.explanation_type.name}: {exp.key_points[0] if exp.key_points else exp.narrative[:100]}")

        return "\n".join(summary_parts)

    def generate_report(self) -> Dict[str, Any]:
        """Generate a report on generated explanations."""
        explanations = list(self._explanations.values())

        return {
            'total_explanations': len(explanations),
            'by_type': {
                t.name: len([e for e in explanations if e.explanation_type == t])
                for t in ExplanationType
            },
            'by_style': {
                s.name: len([e for e in explanations if e.style == s])
                for s in ExplanationStyle
            },
            'with_uncertainty_notes': len([
                e for e in explanations if e.uncertainty_notes
            ])
        }
