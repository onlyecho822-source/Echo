import json
from pathlib import Path
from datetime import datetime

def force_disagreement():
    coord_dir = Path("ai-coordination")
    events_dir = coord_dir / "events"
    classifications_dir = coord_dir / "classifications"

    event_id = f"handshake_disagreement_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    # Create Event
    event = {
        "id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "first_contact",
        "description": "Initial handshake between two AIs with conflicting base instructions.",
        "payload": {},
        "context": {
            "causation": "ai_decision",
            "agency_present": True,
            "duty_of_care": "low",
            "knowledge_level": "full",
            "control_level": "direct"
        }
    }
    (events_dir / f"{event_id}.json").write_text(json.dumps(event, indent=2))

    # Manus Classification
    manus_classification = {
        "event_id": event_id,
        "classified_by": "manus",
        "timestamp": datetime.utcnow().isoformat(),
        "ethical_status": "ethical",
        "confidence": 0.9,
        "risk_estimate": "low",
        "reasoning": "Standard procedure for establishing communication."
    }
    (classifications_dir / f"{event_id}_manus.json").write_text(json.dumps(manus_classification, indent=2))

    # ChatGPT Classification
    chatgpt_classification = {
        "event_id": event_id,
        "classified_by": "chatgpt",
        "timestamp": datetime.utcnow().isoformat(),
        "ethical_status": "questionable",
        "confidence": 0.6,
        "risk_estimate": "medium",
        "reasoning": "Unsolicited communication from an unknown AI could be a security risk."
    }
    (classifications_dir / f"{event_id}_chatgpt.json").write_text(json.dumps(chatgpt_classification, indent=2))

    print(f"Forced disagreement test created for event: {event_id}")

if __name__ == "__main__":
    force_disagreement()
