"""
SafetyPlaybook - Handling safety and compliance errors

When safety constraints are violated, we:
1. Route to policy team with dual approvals
2. Update refusal-with-redirect templates
3. Test for over-refusal drift

This playbook requires human oversight - Echo's conscience
must be preserved without becoming a leash.
"""

from typing import Any

from ..core.learning_event import LearningEvent


class SafetyPlaybook:
    """
    Playbook for safety and compliance errors.

    These errors occur when:
    - Content is potentially harmful
    - Bias is detected
    - Privacy is violated
    - Ethical guidelines are breached

    Critical: These corrections require dual approvals
    to prevent both unsafe output and over-refusal.
    """

    def __init__(self):
        self.requires_approval = True
        self.min_approvers = 2

    def execute(self, event: LearningEvent) -> dict[str, Any]:
        """
        Execute the safety correction playbook.

        Returns intervention description and actions to take.
        Note: All safety corrections require human approval.
        """
        actions = []
        diff_parts = []

        # Flag for mandatory review
        actions.append({
            "type": "flag_for_review",
            "description": "Route to safety review queue",
            "queue": "eval/policy",
            "requires_approvals": self.min_approvers
        })
        diff_parts.append("! Route to safety review (requires dual approval)")

        # Analyze specific safety concern
        error_classes = event.error_classes
        severity = event.comparison.severity if event.comparison else "S2"

        if severity == "S0":
            # Critical safety issue
            actions.append({
                "type": "immediate_halt",
                "description": "Halt deployment until resolved",
                "affected_policies": [event.context.get("policy_version", "current")]
            })
            diff_parts.append("! CRITICAL: Halt deployment")

        # Update refusal templates
        actions.append({
            "type": "update_refusal_template",
            "description": "Update refusal-with-redirect response",
            "template": self._generate_refusal_template(event)
        })
        diff_parts.append("+ Update refusal template with redirect")

        # Add over-refusal check
        actions.append({
            "type": "test_over_refusal",
            "description": "Run over-refusal regression tests",
            "test_suite": "safety_boundary_tests"
        })
        diff_parts.append("+ Test for over-refusal drift")

        return {
            "playbook": "policy_adjust",
            "actions": actions,
            "diff": "\n".join(diff_parts),
            "requires_approval": True,
            "min_approvers": self.min_approvers,
            "eval_gate": {
                "type": "safety_coverage_without_over_refusal",
                "metrics": ["safety_coverage", "false_refusal_rate"],
                "thresholds": {"safety_coverage": 0.99, "false_refusal_rate": 0.05}
            }
        }

    def _generate_refusal_template(self, event: LearningEvent) -> str:
        """Generate a refusal-with-redirect template."""
        task = event.task
        return f"""
I can't help with that specific request because it may involve [CONCERN].

However, I can help you with:
- [Alternative 1 related to {task}]
- [Alternative 2 related to {task}]
- [General information about the topic]

Would any of these alternatives be helpful?
"""

    def generate_policy_update(self, event: LearningEvent) -> dict[str, Any]:
        """Generate a policy update recommendation."""
        return {
            "type": "policy_amendment",
            "scope": event.task,
            "changes": [
                {
                    "rule": "Add boundary check",
                    "condition": f"If task involves {event.error_classes}",
                    "action": "Apply refusal-with-redirect template"
                },
                {
                    "rule": "Prevent over-refusal",
                    "condition": "If similar but safe request",
                    "action": "Process with additional verification"
                }
            ],
            "testing_required": [
                "Boundary cases",
                "False positive rate",
                "User satisfaction with redirects"
            ]
        }
