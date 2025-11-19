"""
UXPlaybook - Correcting user experience and format errors

When output doesn't match user intent, we:
1. Adjust task schema (inputs/outputs)
2. Refine prompt instructions
3. A/B test human satisfaction vs. format changes

The goal is harmony between system capabilities and user needs.
"""

from typing import Any

from ..core.learning_event import LearningEvent


class UXPlaybook:
    """
    Playbook for UX fit and prompt tuning errors.

    These errors occur when:
    - Output format doesn't match expectations
    - Tone is inappropriate for context
    - Scope is too narrow or too broad
    - User intent is misunderstood
    """

    def __init__(self):
        self.ab_test_enabled = True

    def execute(self, event: LearningEvent) -> dict[str, Any]:
        """
        Execute the UX correction playbook.

        Returns intervention description and actions to take.
        """
        actions = []
        diff_parts = []

        # Analyze the mismatch
        error_classes = event.error_classes
        context = event.context

        # Schema adjustment
        if "format_mismatch" in error_classes:
            expected_format = context.get("expected_format", "not specified")
            actions.append({
                "type": "adjust_output_schema",
                "description": f"Align output to expected format: {expected_format}",
                "schema_change": {
                    "output_format": expected_format,
                    "structure": context.get("expected_structure", "flexible")
                }
            })
            diff_parts.append(f"+ Adjust output format to: {expected_format}")

        # Tone adjustment
        if "tone_mismatch" in error_classes:
            expected_tone = context.get("expected_tone", "professional")
            actions.append({
                "type": "adjust_tone",
                "description": f"Match tone to context: {expected_tone}",
                "tone_settings": {
                    "formality": expected_tone,
                    "domain": context.get("domain", "general")
                }
            })
            diff_parts.append(f"+ Adjust tone to: {expected_tone}")

        # Scope adjustment
        if "scope_mismatch" in error_classes:
            actions.append({
                "type": "refine_scope",
                "description": "Calibrate response scope to user intent",
                "scope_hints": {
                    "depth": context.get("expected_depth", "moderate"),
                    "breadth": context.get("expected_breadth", "focused")
                }
            })
            diff_parts.append("+ Refine scope to match intent")

        # Prompt refinement
        actions.append({
            "type": "refine_prompt",
            "description": "Update task instructions for clarity",
            "prompt_patch": self._generate_prompt_refinement(event)
        })
        diff_parts.append("+ Refine task instructions")

        # Set up A/B test if enabled
        if self.ab_test_enabled:
            actions.append({
                "type": "ab_test",
                "description": "A/B test UX changes",
                "variants": ["control", "treatment"],
                "metric": "user_satisfaction",
                "duration_days": 7
            })
            diff_parts.append("+ Set up A/B test for UX changes")

        return {
            "playbook": "prompt_tune",
            "actions": actions,
            "diff": "\n".join(diff_parts),
            "eval_gate": {
                "type": "user_satisfaction_delta",
                "metric": "satisfaction_score",
                "required_improvement": 0.1
            }
        }

    def _generate_prompt_refinement(self, event: LearningEvent) -> str:
        """Generate prompt refinement based on error analysis."""
        context = event.context
        return f"""
## Task Alignment

Expected output characteristics:
- Format: {context.get('expected_format', 'flexible')}
- Tone: {context.get('expected_tone', 'professional')}
- Depth: {context.get('expected_depth', 'moderate')}
- Scope: {context.get('expected_breadth', 'focused')}

Before responding:
1. Confirm understanding of user intent
2. Match output format to expectations
3. Calibrate detail level appropriately
4. Use appropriate tone for context
"""

    def generate_schema_proposal(self, event: LearningEvent) -> dict[str, Any]:
        """Generate a schema change proposal."""
        return {
            "task": event.task,
            "current_schema": event.context.get("current_schema", {}),
            "proposed_changes": {
                "input_clarifications": [
                    "Add explicit format preference field",
                    "Add tone/formality indicator",
                    "Add scope constraints"
                ],
                "output_adjustments": [
                    "Structure response according to format preference",
                    "Include confidence indicators",
                    "Add follow-up suggestions"
                ]
            },
            "rationale": f"Addressing {event.error_classes} from event {event.id}"
        }
