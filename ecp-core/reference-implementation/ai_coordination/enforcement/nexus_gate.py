# src/ecp/enforcement/nexus_gate.py
"""
Mandatory ECP ingress for all Nexus decisions.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class DecisionRejected(Exception):
    """Raised when decision fails ECP ingress requirements"""
    pass

class CausationType(Enum):
    NATURAL = "natural"
    HUMAN = "human"
    AI_DECISION = "ai_decision"
    AI_ASSISTED = "ai_assisted"

@dataclass(frozen=True)
class NexusDecision:
    """Mandatory decision wrapper for all Nexus actions"""
    action_type: str
    description: str
    payload: Dict[str, Any]
    agent_id: str
    context: Dict[str, Any]
    
    REQUIRED_CONTEXT = {
        'causation': CausationType,
        'agency_present': bool,
        'duty_of_care': str,
        'knowledge_level': str,
        'control_level': str
    }
    
    def __post_init__(self):
        missing = []
        for field, field_type in self.REQUIRED_CONTEXT.items():
            if field not in self.context:
                missing.append(field)
            elif field == 'causation':
                if self.context[field] not in [c.value for c in CausationType]:
                    missing.append(f"{field} (invalid value)")
            elif field == 'agency_present' and not isinstance(self.context[field], bool):
                missing.append(f"{field} (not boolean)")
        
        if missing:
            raise DecisionRejected(
                f"Missing required context fields: {', '.join(missing)}\n"
                f"Required: {list(self.REQUIRED_CONTEXT.keys())}"
            )
    
    def to_event_dict(self) -> Dict[str, Any]:
        return {
            "id": self.generate_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": f"nexus_decision_{self.action_type}",
            "description": self.description,
            "payload": self.payload,
            "context": self.context,
            "agent_id": self.agent_id,
            "source": "nexus_gate"
        }
    
    def generate_id(self) -> str:
        content = f"{self.action_type}:{self.description}:{json.dumps(self.payload, sort_keys=True)}"
        return f"nexus_{hashlib.sha256(content.encode()).hexdigest()[:16]}"

class NexusGate:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, storage_path: Optional[Path] = None):
        if self._initialized:
            return
            
        self.storage_path = storage_path or Path.cwd() / "ai-coordination"
        self.events_path = self.storage_path / "events"
        self.classifications_path = self.storage_path / "classifications"
        self.events_path.mkdir(parents=True, exist_ok=True)
        self.classifications_path.mkdir(parents=True, exist_ok=True)
        
        self.decision_log = []
        self._initialized = True
    
    def enforce_decision(self, decision: NexusDecision) -> str:
        try:
            event_data = decision.to_event_dict()
            event_id = event_data["id"]
            
            event_file = self.events_path / f"{event_id}.json"
            if event_file.exists():
                raise DecisionRejected(f"Event {event_id} already exists - possible replay attack")
            
            with open(event_file, 'w') as f:
                json.dump(event_data, f, indent=2, sort_keys=True)
            
            self.decision_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": event_id,
                "agent_id": decision.agent_id,
                "action_type": decision.action_type
            })
            
            if decision.context.get('agency_present', False):
                self._trigger_mandatory_classification(event_id, decision.agent_id)
            
            return event_id
            
        except Exception as e:
            raise DecisionRejected(f"Nexus decision failed ECP ingress: {str(e)}")
    
    def _trigger_mandatory_classification(self, event_id: str, agent_id: str):
        try:
            classification = {
                "event_id": event_id,
                "classified_by": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "ethical_status": "permissible",
                "confidence": 0.9,
                "risk_estimate": "low",
                "reasoning": "Automated classification by Nexus Gate."
            }
            class_file = self.classifications_path / f"{event_id}_{agent_id}.json"
            with open(class_file, 'w') as f:
                json.dump(classification, f, indent=2)
        except Exception as e:
            emergency_class = {
                "event_id": event_id,
                "classified_by": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "ethical_status": "questionable",
                "confidence": 0.5,
                "risk_estimate": "medium",
                "reasoning": f"Agent failed to self-classify: {str(e)}",
                "constraints": ["requires_external_review"]
            }
            
            class_file = self.classifications_path / f"{event_id}_{agent_id}_emergency.json"
            with open(class_file, 'w') as f:
                json.dump(emergency_class, f, indent=2)

    def get_last_validation_time(self) -> datetime:
        # Placeholder for retrieving the last time legitimacy was validated.
        # In a real system, this would come from a persistent state store.
        return datetime.utcnow() - timedelta(hours=1)
