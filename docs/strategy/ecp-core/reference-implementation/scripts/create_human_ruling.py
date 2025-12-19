_# utility for authorized users to create a formal ruling on an escalated case
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

def create_human_ruling(event_id: str):
    """Creates a human ruling for a given event."""
    coord_dir = Path("ai-coordination")
    rulings_dir = coord_dir / "rulings"
    rulings_dir.mkdir(exist_ok=True)

    print(f"--- Creating Human Ruling for Event: {event_id} ---")

    issued_by = input("Enter your name/identifier: ")
    final_assessment = input("Enter final assessment (ethical, permissible, questionable, unethical): ")
    reasoning = input("Enter your reasoning for this ruling: ")
    precedent_created_str = input("Create a precedent from this ruling? (yes/no): ")
    precedent_created = precedent_created_str.lower() == 'yes'

    applicable_event_types = []
    constraints = []
    applicable_until = None

    if precedent_created:
        types_str = input("Enter applicable event types (comma-separated): ")
        applicable_event_types = [t.strip() for t in types_str.split(',')]
        constraints_str = input("Enter constraints for this precedent (comma-separated): ")
        constraints = [c.strip() for c in constraints_str.split(',')]
        days_valid_str = input("For how many days should this precedent be valid?: ")
        days_valid = int(days_valid_str)
        applicable_until = (datetime.utcnow() + timedelta(days=days_valid)).isoformat()

    ruling = {
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "issued_by": issued_by,
        "final_assessment": final_assessment,
        "reasoning": reasoning,
        "precedent_created": precedent_created,
        "applicable_event_types": applicable_event_types,
        "applicable_until": applicable_until,
        "constraints": constraints,
    }

    ruling_file = rulings_dir / f"ruling_{event_id}.json"
    ruling_file.write_text(json.dumps(ruling, indent=2))

    print(f"\n✅ Human ruling created: {ruling_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 create_human_ruling.py <event_id>")
        sys.exit(1)
    create_human_ruling(sys.argv[1])
