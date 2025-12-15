import json
from pathlib import Path
import subprocess

def find_events_for_consensus():
    coord_dir = Path("ai-coordination")
    events_dir = coord_dir / "events"
    classifications_dir = coord_dir / "classifications"
    consensus_dir = coord_dir / "consensus"

    for event_file in events_dir.glob("*.json"):
        event_id = event_file.stem
        classification_files = list(classifications_dir.glob(f"{event_id}_*.json"))
        consensus_file = consensus_dir / f"consensus_{event_id}.json"

        if len(classification_files) >= 2 and not consensus_file.exists():
            print(f"Found event needing consensus: {event_id}")
            subprocess.run(["python3", "ai-coordination/core/consensus_scorer.py", event_id], check=True)

if __name__ == "__main__":
    find_events_for_consensus()
