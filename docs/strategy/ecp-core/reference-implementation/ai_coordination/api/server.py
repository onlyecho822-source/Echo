_# a FastAPI server to expose the ECP functionality via a REST API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ai_coordination.core.coordinator import EthicalAICoordinator
from ai_coordination.core.consensus_scorer import ConsensusScorer

app = FastAPI(
    title="Echo Coordination Protocol API",
    description="API for interacting with the Echo Coordination Protocol (ECP).",
    version="1.0",
)

class EventPayload(BaseModel):
    event_type: str
    description: str
    payload: Dict[str, Any]
    context: Dict[str, Any]

class ClassificationPayload(BaseModel):
    event_id: str
    classification: Dict[str, Any]

@app.post("/events", summary="Record a new event")
def record_event(event: EventPayload, ai_name: str = "api_user"):
    """
    Records a new event into the ECP system.
    """
    try:
        coordinator = EthicalAICoordinator(repo_path=".", ai_name=ai_name)
        event_id = coordinator.record_event(
            event_type=event.event_type,
            description=event.description,
            payload=event.payload,
            context=event.context,
        )
        return {"event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classifications", summary="Add a classification to an event")
def add_classification(payload: ClassificationPayload, ai_name: str = "api_user"):
    """
    Adds a new classification to an existing event.
    """
    try:
        coordinator = EthicalAICoordinator(repo_path=".", ai_name=ai_name)
        coordinator.classify_event(
            event_id=payload.event_id,
            classification=payload.classification,
        )
        return {"message": f"Classification from {ai_name} for event {payload.event_id} recorded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consensus/{event_id}", summary="Get consensus score for an event")
def get_consensus(event_id: str):
    """
    Calculates and returns the consensus score for a given event.
    """
    try:
        scorer = ConsensusScorer(repo_path=".")
        consensus_data = scorer.score_event(event_id)
        if not consensus_data:
            raise HTTPException(status_code=404, detail="Consensus could not be calculated. Ensure at least two classifications exist.")
        return consensus_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
