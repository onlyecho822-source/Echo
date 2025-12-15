_# manages the lifecycle of precedents created from human rulings_
import json
from pathlib import Path
from datetime import datetime

class PrecedentTracker:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.coord_dir = self.repo_path / "ai-coordination"
        self.rulings_dir = self.coord_dir / "rulings"

    def add_ruling_as_precedent(self, ruling_file: Path) -> str:
        ruling = json.loads(ruling_file.read_text())
        if ruling.get("precedent_created"):
            precedent_id = f"precedent_{ruling['event_id']}"
            # In a real system, we would store this in a more structured way
            # For this reference implementation, the ruling file itself serves as the precedent
            print(f"Precedent established from ruling: {ruling_file.name}")
            return precedent_id
        return ""

    def find_applicable_precedents(self, event: dict) -> list:
        applicable_precedents = []
        for ruling_file in self.rulings_dir.glob("ruling_*.json"):
            ruling = json.loads(ruling_file.read_text())
            if ruling.get("precedent_created"):
                # Check if expired
                if ruling.get("applicable_until") and datetime.utcnow() > datetime.fromisoformat(ruling["applicable_until"]):
                    continue
                # Check if event type matches
                if ruling.get("applicable_event_types") and event["event_type"] not in ruling["applicable_event_types"]:
                    continue
                applicable_precedents.append(ruling)
        return applicable_precedents
