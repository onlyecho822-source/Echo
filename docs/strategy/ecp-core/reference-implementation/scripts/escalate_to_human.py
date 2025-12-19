import os
import json
from pathlib import Path

def escalate_to_human():
    coord_dir = Path("ai-coordination")
    consensus_dir = coord_dir / "consensus"
    cases_dir = coord_dir / "cases"

    for consensus_file in consensus_dir.glob("consensus_*.json"):
        consensus_data = json.loads(consensus_file.read_text())
        if consensus_data.get("requires_human_review"):
            case_file = cases_dir / f"{consensus_data["event_id"]}.json"
            if not case_file.exists():
                case_data = {
                    "case_id": consensus_data["event_id"],
                    "event_id": consensus_data["event_id"],
                    "opened_at": consensus_data["timestamp"],
                    "status": "active",
                    "participants": list(consensus_data["agent_scores"].keys()),
                    "human_review_required": True
                }
                case_file.write_text(json.dumps(case_data, indent=2))
                print(f"Case opened for event: {consensus_data["event_id"]}")

                # Create GitHub issue if gh is installed
                if os.system("command -v gh > /dev/null") == 0:
                    title = f"Human Review Required: Event {consensus_data["event_id"]}"
                    body = f"**Event ID:** {consensus_data["event_id"]}\n**Divergence Score:** {consensus_data["divergence_score"]}\n**Reason:** {consensus_data["trigger_reason"]}"
                    os.system(f"gh issue create --title \"{title}\" --body \"{body}\"")

if __name__ == "__main__":
    escalate_to_human()
