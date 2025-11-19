"""
ReasoningPlaybook - Correcting logical and computational faults

When the reasoning chain breaks, we:
1. Insert verified tool calls (calculator, code runner)
2. Add self-check step to verify each inference
3. Decompose complex reasoning into verifiable steps

Gate by eval suite: reasoning chain validity must improve.
"""

from typing import Any

from ..core.learning_event import LearningEvent


class ReasoningPlaybook:
    """
    Playbook for reasoning and mathematical errors.

    These errors occur when:
    - Logic is invalid
    - Math is incorrect
    - Inferences don't follow from premises
    - Assumptions are unstated
    """

    def __init__(self):
        self.tool_map = {
            "math": "calculator",
            "code": "code_runner",
            "logic": "logic_verifier"
        }

    def execute(self, event: LearningEvent) -> dict[str, Any]:
        """
        Execute the reasoning correction playbook.

        Returns intervention description and actions to take.
        """
        actions = []
        diff_parts = []

        # Determine what tools are needed
        error_classes = event.error_classes
        tools_to_add = []

        if "math" in error_classes:
            tools_to_add.append("calculator")
            diff_parts.append("+ Add calculator tool for numerical operations")

        if "reasoning" in error_classes:
            tools_to_add.append("logic_verifier")
            diff_parts.append("+ Add logic verification tool")

        # Add tool insertion action
        if tools_to_add:
            actions.append({
                "type": "add_tools",
                "description": f"Insert tools: {', '.join(tools_to_add)}",
                "tools": tools_to_add
            })

        # Add self-check step
        actions.append({
            "type": "add_self_check",
            "description": "Add step-by-step verification",
            "prompt_patch": """
+ For each reasoning step:
  1. State the assumption
  2. Verify it follows from prior steps
  3. Check numerical values with calculator
"""
        })
        diff_parts.append("+ Add self-verification protocol")

        # Add decomposition for complex reasoning
        if event.error_score > 0.4:
            actions.append({
                "type": "decompose_reasoning",
                "description": "Break complex reasoning into atomic steps",
                "max_step_complexity": "one_inference_per_step"
            })
            diff_parts.append("+ Decompose into atomic reasoning steps")

        return {
            "playbook": "tool_insertion",
            "actions": actions,
            "diff": "\n".join(diff_parts),
            "eval_gate": {
                "type": "reasoning_chain_validity",
                "metric": "logical_consistency",
                "required_improvement": 0.15
            }
        }

    def generate_prompt_patch(self, event: LearningEvent) -> str:
        """Generate a prompt patch for reasoning improvement."""
        return f"""
## Reasoning Verification Protocol

For all reasoning tasks:

1. DECOMPOSE: Break the problem into single-inference steps
2. STATE: For each step, explicitly state assumptions
3. VERIFY: Check that conclusion follows from premises
4. COMPUTE: Use calculator for any numerical operations
5. CHECK: Verify step N against steps N-1 and N+1

Self-check questions:
- Does this step follow logically from the previous?
- Are all numerical values computed, not estimated?
- Are there any hidden assumptions?

Error context: {event.task}
Primary errors: {event.error_classes}
"""
