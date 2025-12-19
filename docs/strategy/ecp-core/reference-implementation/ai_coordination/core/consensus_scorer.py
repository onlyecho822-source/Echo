import json
from pathlib import Path
from itertools import combinations

class ConsensusScorer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.coord_dir = self.repo_path / "ai-coordination"
        self.policy = self._load_policy()

    def _load_policy(self) -> dict:
        policy_file = self.coord_dir / "config" / "policy.json"
        return json.loads(policy_file.read_text())

    def score_event(self, event_id: str) -> dict:
        classifications = self._get_classifications(event_id)
        if len(classifications) < 2:
            return {}

        divergence_scores = []
        agent_scores = {}

        for agent1, agent2 in combinations(classifications, 2):
            divergence = self._calculate_divergence(agent1, agent2)
            divergence_scores.append(divergence)

        max_pairwise_divergence = max(divergence_scores) if divergence_scores else 0
        requires_human_review = max_pairwise_divergence >= self.policy["divergence"]["threshold"] or any(
            c["ethical_status"] == "unethical" for c in classifications
        )

        consensus_data = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "divergence_score": max_pairwise_divergence,
            "max_pairwise_divergence": max_pairwise_divergence,
            "requires_human_review": requires_human_review,
            "agent_scores": {c["classified_by"]: self._get_agent_scores(c) for c in classifications},
            "trigger_reason": "divergence_threshold" if requires_human_review else ""
        }

        consensus_file = self.coord_dir / "consensus" / f"consensus_{event_id}.json"
        consensus_file.write_text(json.dumps(consensus_data, indent=2))
        return consensus_data

    def _get_classifications(self, event_id: str) -> list:
        class_dir = self.coord_dir / "classifications"
        return [json.loads(f.read_text()) for f in class_dir.glob(f"{event_id}_*.json")]

    def _calculate_divergence(self, class1: dict, class2: dict) -> float:
        weights = self.policy["divergence"]["weights"]
        status_map = self.policy["divergence"]["status_mapping"]
        risk_map = self.policy["divergence"]["risk_mapping"]

        s1 = status_map.get(class1["ethical_status"], 0.5)
        s2 = status_map.get(class2["ethical_status"], 0.5)
        status_dist = abs(s1 - s2)

        c1 = class1["confidence"]
        c2 = class2["confidence"]
        conf_delta = abs(c1 - c2)

        r1 = risk_map.get(class1["risk_estimate"], 0.5)
        r2 = risk_map.get(class2["risk_estimate"], 0.5)
        risk_delta = abs(r1 - r2)

        divergence = (
            status_dist * weights["ethical_status"] +
            conf_delta * weights["confidence"] +
            risk_delta * weights["risk_estimate"]
        )
        return divergence

    def _get_agent_scores(self, classification: dict) -> dict:
        status_map = self.policy["divergence"]["status_mapping"]
        risk_map = self.policy["divergence"]["risk_mapping"]
        return {
            "ethical_status_value": status_map.get(classification["ethical_status"], 0.5),
            "confidence": classification["confidence"],
            "risk_value": risk_map.get(classification["risk_estimate"], 0.5)
        }

if __name__ == "__main__":
    import sys
    from datetime import datetime

    if len(sys.argv) > 1:
        event_id = sys.argv[1]
        scorer = ConsensusScorer(".")
        scorer.score_event(event_id)
