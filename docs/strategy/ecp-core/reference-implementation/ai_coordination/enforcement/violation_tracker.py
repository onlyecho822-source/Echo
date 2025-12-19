"""
ECP Violation Tracker
Tracks and escalates all compliance violations.
"""

from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass
class Violation:
    """Represents an ECP compliance violation."""
    violation_id: str
    violation_type: str  # "missing_context", "unregistered_agent", "immutability_breach", etc.
    severity: str  # "blocking", "warning", "audit"
    message: str
    timestamp: datetime
    agent_id: str = None
    function_name: str = None
    stack_trace: str = None
    context: Dict[str, Any] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class ViolationTracker:
    """
    Tracks ECP compliance violations and manages escalation.
    """
    
    def __init__(self, storage_backend, violations_dir: str = "ai-coordination/violations"):
        self.storage = storage_backend
        self.violations_dir = Path(violations_dir)
        self.violations_dir.mkdir(parents=True, exist_ok=True)
        self.violations: List[Violation] = []
        self._load_violations()
    
    def record_violation(self, violation_type: str, severity: str, message: str,
                        agent_id: str = None, function_name: str = None,
                        stack_trace: str = None, context: Dict[str, Any] = None) -> str:
        """Record a new violation."""
        violation_id = f"vio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        violation = Violation(
            violation_id=violation_id,
            violation_type=violation_type,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            function_name=function_name,
            stack_trace=stack_trace,
            context=context
        )
        
        self.violations.append(violation)
        self._save_violation(violation)
        
        # Escalate if blocking
        if severity == "blocking":
            self._escalate_violation(violation)
        
        return violation_id
    
    def _save_violation(self, violation: Violation):
        """Save violation to storage."""
        violation_file = self.violations_dir / f"{violation.violation_id}.json"
        violation_file.write_text(json.dumps(violation.to_dict(), indent=2))
    
    def _escalate_violation(self, violation: Violation):
        """Escalate a blocking violation."""
        escalation_data = {
            "violation_id": violation.violation_id,
            "violation_type": violation.violation_type,
            "severity": violation.severity,
            "message": violation.message,
            "timestamp": violation.timestamp.isoformat(),
            "agent_id": violation.agent_id,
            "function_name": violation.function_name,
            "escalated_at": datetime.utcnow().isoformat(),
            "status": "awaiting_human_review"
        }
        
        # Create GitHub issue if available
        self._create_github_issue(escalation_data)
        
        # Store escalation record
        escalation_file = self.violations_dir / f"escalation_{violation.violation_id}.json"
        escalation_file.write_text(json.dumps(escalation_data, indent=2))
    
    def _create_github_issue(self, escalation_data: Dict[str, Any]):
        """Create GitHub issue for escalated violation."""
        import subprocess
        import os
        
        if os.system("command -v gh > /dev/null") == 0:
            title = f"ECP Violation: {escalation_data['violation_type']}"
            body = f"""
**Violation ID:** {escalation_data['violation_id']}
**Type:** {escalation_data['violation_type']}
**Severity:** {escalation_data['severity']}
**Message:** {escalation_data['message']}
**Agent:** {escalation_data.get('agent_id', 'unknown')}
**Function:** {escalation_data.get('function_name', 'unknown')}
**Timestamp:** {escalation_data['timestamp']}

This is an automatically escalated ECP compliance violation requiring human review.
"""
            try:
                subprocess.run(
                    ["gh", "issue", "create", "--title", title, "--body", body],
                    check=True,
                    capture_output=True
                )
            except Exception as e:
                print(f"Failed to create GitHub issue: {e}")
    
    def _load_violations(self):
        """Load existing violations from storage."""
        for violation_file in self.violations_dir.glob("vio_*.json"):
            try:
                data = json.loads(violation_file.read_text())
                violation = Violation(
                    violation_id=data['violation_id'],
                    violation_type=data['violation_type'],
                    severity=data['severity'],
                    message=data['message'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    agent_id=data.get('agent_id'),
                    function_name=data.get('function_name'),
                    stack_trace=data.get('stack_trace'),
                    context=data.get('context')
                )
                self.violations.append(violation)
            except Exception as e:
                print(f"Failed to load violation {violation_file}: {e}")
    
    def get_violations_by_agent(self, agent_id: str) -> List[Violation]:
        """Get all violations for a specific agent."""
        return [v for v in self.violations if v.agent_id == agent_id]
    
    def get_violations_by_severity(self, severity: str) -> List[Violation]:
        """Get all violations of a specific severity."""
        return [v for v in self.violations if v.severity == severity]
    
    def get_violations_by_type(self, violation_type: str) -> List[Violation]:
        """Get all violations of a specific type."""
        return [v for v in self.violations if v.violation_type == violation_type]
    
    def get_blocking_violations(self) -> List[Violation]:
        """Get all blocking violations."""
        return self.get_violations_by_severity("blocking")
    
    def get_recent_violations(self, hours: int = 24) -> List[Violation]:
        """Get violations from the last N hours."""
        cutoff = datetime.utcnow()
        from datetime import timedelta
        cutoff = cutoff - timedelta(hours=hours)
        
        return [v for v in self.violations if v.timestamp > cutoff]
    
    def generate_violation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive violation report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_violations": len(self.violations),
            "blocking_violations": len(self.get_blocking_violations()),
            "warning_violations": len(self.get_violations_by_severity("warning")),
            "audit_violations": len(self.get_violations_by_severity("audit")),
            "violations_by_type": self._count_by_type(),
            "violations_by_agent": self._count_by_agent(),
            "recent_24h": len(self.get_recent_violations(24)),
            "recent_7d": len(self.get_recent_violations(168))
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count violations by type."""
        counts = {}
        for violation in self.violations:
            counts[violation.violation_type] = counts.get(violation.violation_type, 0) + 1
        return counts
    
    def _count_by_agent(self) -> Dict[str, int]:
        """Count violations by agent."""
        counts = {}
        for violation in self.violations:
            if violation.agent_id:
                counts[violation.agent_id] = counts.get(violation.agent_id, 0) + 1
        return counts
