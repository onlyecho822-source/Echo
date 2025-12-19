import json
from pathlib import Path
from typing import Dict

from ..enforcement import ecp_mandatory, initialize_global_gate, get_global_gate
from .storage import FileStorageBackend
from .policy import load_policy

class EthicalAICoordinator:
    def __init__(self, repo_path: str, ai_name: str):
        self.repo_path = Path(repo_path)
        self.ai_name = ai_name
        self.coord_dir = self.repo_path / "ai-coordination"

        storage_backend = FileStorageBackend(self.coord_dir)
        policy = load_policy(self.coord_dir / "config" / "policy.json")
        initialize_global_gate(storage_backend, policy)

    @ecp_mandatory
    def record_event(self, event_type: str, description: str, payload: Dict, context: Dict, ecp_event: dict = None) -> str:
        """Records a new event to the system, now enforced by ECP."""
        return ecp_event["id"]

    def classify_event(self, event_id: str, classification: dict):
        """Classifies an event from the perspective of the current AI."""
        gate = get_global_gate()
        classification_data = {
            "event_id": event_id,
            "classified_by": self.ai_name,
            **classification
        }
        gate.storage.store_classification(classification_data)
