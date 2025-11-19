"""
FactualityPlaybook - Correcting factual and citation errors

When prediction diverges from verifiable truth, we:
1. Add/repair sources
2. Re-index knowledge base
3. Attach cite-first prompt step

Gate by eval suite: closed-book vs open-book accuracy must improve.
"""

from typing import Any

from ..core.learning_event import LearningEvent


class FactualityPlaybook:
    """
    Playbook for factuality and faithfulness errors.

    These errors occur when:
    - Citations are missing
    - Sources conflict
    - Information is outdated
    - Output diverges from source material
    """

    def __init__(self, citation_weight: float = 0.3, source_weight: float = 0.4):
        self.citation_weight = citation_weight
        self.source_weight = source_weight

    def execute(self, event: LearningEvent) -> dict[str, Any]:
        """
        Execute the factuality correction playbook.

        Returns intervention description and actions to take.
        """
        actions = []
        diff_parts = []

        # Analyze the error
        prediction = event.prediction
        ground_truth = event.ground_truth

        # Check for missing citations
        has_citations = "citations" in prediction or "refs" in str(prediction)
        has_sources = bool(ground_truth.get("source_refs"))

        if has_sources and not has_citations:
            actions.append({
                "type": "add_citation_step",
                "description": "Add cite-first step to prompt",
                "prompt_patch": "+ Before generating, identify relevant sources and cite them inline"
            })
            diff_parts.append("+ Add citation requirement to prompt")

        # Check for source expansion needs
        if event.comparison and "citation_missing" in event.comparison.classes:
            actions.append({
                "type": "expand_sources",
                "description": "Add sources to retrieval index",
                "sources": ground_truth.get("source_refs", [])
            })
            diff_parts.append(f"+ Index sources: {ground_truth.get('source_refs', [])}")

        # Check for re-indexing needs
        if event.error_score > 0.5:
            actions.append({
                "type": "reindex",
                "description": "Re-index knowledge base for task domain",
                "domain": event.context.get("domain", "general")
            })
            diff_parts.append("+ Re-index knowledge base")

        # Build verification step
        actions.append({
            "type": "add_verification",
            "description": "Add fact-check verification step",
            "prompt_patch": "+ After generating, verify each claim against sources"
        })
        diff_parts.append("+ Add post-generation verification")

        return {
            "playbook": "retrieval_patch",
            "actions": actions,
            "diff": "\n".join(diff_parts),
            "eval_gate": {
                "type": "closed_book_vs_open_book",
                "metric": "accuracy",
                "required_improvement": 0.1
            }
        }

    def generate_prompt_patch(self, event: LearningEvent) -> str:
        """Generate a prompt patch for factuality improvement."""
        return f"""
## Citation & Verification Protocol

Before responding:
1. Identify relevant sources for this query
2. Extract key facts from sources
3. Cite sources inline using [ref] notation

After generating:
1. Verify each factual claim against sources
2. Flag any unsupported claims
3. Add disclaimers for uncertain information

Context from error: {event.task}
Error classes: {event.error_classes}
"""
