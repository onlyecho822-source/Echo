#!/usr/bin/env python3
"""
ECHONATE AI IDENTITY AND ACCESS MANAGEMENT (IAM) FRAMEWORK

Implements enterprise-grade identity management for autonomous agents:
- Agent Identity Registry
- Least-Privilege Access Policies
- Token Rotation and Lifecycle
- Permission Audit Logging
- Behavioral Anomaly Detection

∇θ Phoenix Global Nexus
"""

import hashlib
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Callable, Any
from enum import Enum
import hmac


# =============================================================================
# AGENT IDENTITY TYPES
# =============================================================================

class AgentRole(Enum):
    """Agent role classifications"""
    COLLECTOR = "collector"      # Data collection only
    ANALYZER = "analyzer"        # Analysis and correlation
    EXECUTOR = "executor"        # Can execute trades/actions
    ADVERSARIAL = "adversarial"  # Red team agent
    MONITOR = "monitor"          # Observability only
    ADMIN = "admin"              # Full system access


class PermissionScope(Enum):
    """Permission scopes for agents"""
    READ_DATA = "read:data"
    WRITE_DATA = "write:data"
    READ_SIGNALS = "read:signals"
    WRITE_SIGNALS = "write:signals"
    EXECUTE_TRADES = "execute:trades"
    MODIFY_CONFIG = "modify:config"
    ACCESS_SECRETS = "access:secrets"
    AUDIT_LOGS = "audit:logs"
    MANAGE_AGENTS = "manage:agents"


class TokenStatus(Enum):
    """Token lifecycle states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ROTATION = "pending_rotation"


# =============================================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# =============================================================================

# Define permissions for each role (least-privilege principle)
ROLE_PERMISSIONS: Dict[AgentRole, Set[PermissionScope]] = {
    AgentRole.COLLECTOR: {
        PermissionScope.READ_DATA,
        PermissionScope.WRITE_DATA,
    },
    AgentRole.ANALYZER: {
        PermissionScope.READ_DATA,
        PermissionScope.READ_SIGNALS,
        PermissionScope.WRITE_SIGNALS,
    },
    AgentRole.EXECUTOR: {
        PermissionScope.READ_SIGNALS,
        PermissionScope.EXECUTE_TRADES,
    },
    AgentRole.ADVERSARIAL: {
        PermissionScope.READ_DATA,
        PermissionScope.READ_SIGNALS,
        PermissionScope.AUDIT_LOGS,
    },
    AgentRole.MONITOR: {
        PermissionScope.READ_DATA,
        PermissionScope.READ_SIGNALS,
        PermissionScope.AUDIT_LOGS,
    },
    AgentRole.ADMIN: {
        PermissionScope.READ_DATA,
        PermissionScope.WRITE_DATA,
        PermissionScope.READ_SIGNALS,
        PermissionScope.WRITE_SIGNALS,
        PermissionScope.EXECUTE_TRADES,
        PermissionScope.MODIFY_CONFIG,
        PermissionScope.ACCESS_SECRETS,
        PermissionScope.AUDIT_LOGS,
        PermissionScope.MANAGE_AGENTS,
    },
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class AgentToken:
    """Secure token for agent authentication"""
    token_id: str
    agent_id: str
    token_hash: str  # Never store raw token
    created_at: str
    expires_at: str
    status: TokenStatus = TokenStatus.ACTIVE
    last_used: Optional[str] = None
    rotation_scheduled: Optional[str] = None


@dataclass
class AgentIdentity:
    """Complete agent identity record"""
    agent_id: str
    name: str
    role: AgentRole
    description: str
    created_at: str
    
    # Access control
    permissions: Set[PermissionScope] = field(default_factory=set)
    allowed_apis: List[str] = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    
    # Constraints
    rate_limit_per_minute: int = 60
    max_data_access_mb: int = 100
    allowed_hours: tuple = (0, 24)  # 24/7 by default
    
    # Status
    is_active: bool = True
    last_activity: Optional[str] = None
    anomaly_score: float = 0.0


@dataclass
class AuditLogEntry:
    """Audit log for agent actions"""
    timestamp: str
    agent_id: str
    action: str
    resource: str
    permission_used: str
    success: bool
    details: Dict = field(default_factory=dict)
    ip_address: Optional[str] = None
    request_hash: Optional[str] = None


# =============================================================================
# AI IAM FRAMEWORK
# =============================================================================

class AIIdentityManager:
    """
    Enterprise-grade Identity and Access Management for AI Agents.
    
    Features:
    - Agent registration and lifecycle management
    - Token generation with automatic rotation
    - Permission enforcement
    - Comprehensive audit logging
    - Behavioral anomaly detection
    """
    
    def __init__(self, storage_path: str = "ai_iam_store.json"):
        self.storage_path = storage_path
        self.agents: Dict[str, AgentIdentity] = {}
        self.tokens: Dict[str, AgentToken] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.behavioral_baseline: Dict[str, Dict] = {}
        
        # Token configuration
        self.token_lifetime_hours = 24
        self.rotation_warning_hours = 4
        
        self._load_state()
    
    def _load_state(self):
        """Load persisted state"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Reconstruct objects from JSON
                for agent_data in data.get('agents', []):
                    agent_data['role'] = AgentRole(agent_data['role'])
                    agent_data['permissions'] = {PermissionScope(p) for p in agent_data.get('permissions', [])}
                    self.agents[agent_data['agent_id']] = AgentIdentity(**agent_data)
    
    def _save_state(self):
        """Persist state to disk"""
        data = {
            'agents': [
                {**asdict(a), 'role': a.role.value, 'permissions': [p.value for p in a.permissions]}
                for a in self.agents.values()
            ],
            'audit_log_count': len(self.audit_log)
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # =========================================================================
    # AGENT REGISTRATION
    # =========================================================================
    
    def register_agent(self, 
                       name: str, 
                       role: AgentRole,
                       description: str,
                       allowed_apis: List[str] = None,
                       allowed_actions: List[str] = None) -> tuple[AgentIdentity, str]:
        """
        Register a new agent with role-based permissions.
        Returns (AgentIdentity, raw_token)
        """
        agent_id = f"agent_{secrets.token_hex(8)}"
        
        # Get permissions from role
        permissions = ROLE_PERMISSIONS.get(role, set())
        
        agent = AgentIdentity(
            agent_id=agent_id,
            name=name,
            role=role,
            description=description,
            created_at=datetime.utcnow().isoformat() + 'Z',
            permissions=permissions,
            allowed_apis=allowed_apis or [],
            allowed_actions=allowed_actions or []
        )
        
        self.agents[agent_id] = agent
        
        # Generate initial token
        raw_token = self._generate_token(agent_id)
        
        # Log registration
        self._audit_log(
            agent_id=agent_id,
            action="AGENT_REGISTERED",
            resource="ai_iam",
            permission_used="manage:agents",
            success=True,
            details={"role": role.value, "name": name}
        )
        
        self._save_state()
        return agent, raw_token
    
    def _generate_token(self, agent_id: str) -> str:
        """Generate a secure token for an agent"""
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_id = f"tok_{secrets.token_hex(8)}"
        
        token = AgentToken(
            token_id=token_id,
            agent_id=agent_id,
            token_hash=token_hash,
            created_at=datetime.utcnow().isoformat() + 'Z',
            expires_at=(datetime.utcnow() + timedelta(hours=self.token_lifetime_hours)).isoformat() + 'Z'
        )
        
        self.tokens[token_id] = token
        return raw_token
    
    # =========================================================================
    # AUTHENTICATION & AUTHORIZATION
    # =========================================================================
    
    def authenticate(self, raw_token: str) -> Optional[AgentIdentity]:
        """Authenticate an agent by token"""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        for token in self.tokens.values():
            if token.token_hash == token_hash:
                # Check expiration
                if datetime.fromisoformat(token.expires_at.replace('Z', '')) < datetime.utcnow():
                    token.status = TokenStatus.EXPIRED
                    return None
                
                if token.status != TokenStatus.ACTIVE:
                    return None
                
                # Update last used
                token.last_used = datetime.utcnow().isoformat() + 'Z'
                
                agent = self.agents.get(token.agent_id)
                if agent and agent.is_active:
                    agent.last_activity = datetime.utcnow().isoformat() + 'Z'
                    return agent
        
        return None
    
    def authorize(self, agent: AgentIdentity, required_permission: PermissionScope) -> bool:
        """Check if agent has required permission"""
        if not agent.is_active:
            return False
        
        return required_permission in agent.permissions
    
    def check_access(self, 
                     raw_token: str, 
                     required_permission: PermissionScope,
                     resource: str = None,
                     action: str = None) -> tuple[bool, Optional[AgentIdentity], str]:
        """
        Complete access check: authenticate + authorize + constraints.
        Returns (allowed, agent, reason)
        """
        # Authenticate
        agent = self.authenticate(raw_token)
        if not agent:
            self._audit_log(
                agent_id="unknown",
                action=action or "ACCESS_ATTEMPT",
                resource=resource or "unknown",
                permission_used=required_permission.value,
                success=False,
                details={"reason": "authentication_failed"}
            )
            return False, None, "Authentication failed"
        
        # Authorize permission
        if not self.authorize(agent, required_permission):
            self._audit_log(
                agent_id=agent.agent_id,
                action=action or "ACCESS_ATTEMPT",
                resource=resource or "unknown",
                permission_used=required_permission.value,
                success=False,
                details={"reason": "permission_denied"}
            )
            return False, agent, f"Permission denied: {required_permission.value}"
        
        # Check API allowlist
        if resource and agent.allowed_apis:
            if not any(api in resource for api in agent.allowed_apis):
                self._audit_log(
                    agent_id=agent.agent_id,
                    action=action or "ACCESS_ATTEMPT",
                    resource=resource,
                    permission_used=required_permission.value,
                    success=False,
                    details={"reason": "api_not_allowed"}
                )
                return False, agent, f"API not in allowlist: {resource}"
        
        # Check action allowlist
        if action and agent.allowed_actions:
            if action not in agent.allowed_actions:
                self._audit_log(
                    agent_id=agent.agent_id,
                    action=action,
                    resource=resource or "unknown",
                    permission_used=required_permission.value,
                    success=False,
                    details={"reason": "action_not_allowed"}
                )
                return False, agent, f"Action not in allowlist: {action}"
        
        # Check time constraints
        current_hour = datetime.utcnow().hour
        if not (agent.allowed_hours[0] <= current_hour < agent.allowed_hours[1]):
            self._audit_log(
                agent_id=agent.agent_id,
                action=action or "ACCESS_ATTEMPT",
                resource=resource or "unknown",
                permission_used=required_permission.value,
                success=False,
                details={"reason": "outside_allowed_hours", "current_hour": current_hour}
            )
            return False, agent, f"Access outside allowed hours: {agent.allowed_hours}"
        
        # All checks passed
        self._audit_log(
            agent_id=agent.agent_id,
            action=action or "ACCESS_GRANTED",
            resource=resource or "unknown",
            permission_used=required_permission.value,
            success=True
        )
        
        return True, agent, "Access granted"
    
    # =========================================================================
    # TOKEN LIFECYCLE
    # =========================================================================
    
    def rotate_token(self, agent_id: str) -> Optional[str]:
        """Rotate token for an agent"""
        if agent_id not in self.agents:
            return None
        
        # Revoke existing tokens
        for token in self.tokens.values():
            if token.agent_id == agent_id and token.status == TokenStatus.ACTIVE:
                token.status = TokenStatus.REVOKED
        
        # Generate new token
        new_token = self._generate_token(agent_id)
        
        self._audit_log(
            agent_id=agent_id,
            action="TOKEN_ROTATED",
            resource="ai_iam",
            permission_used="manage:agents",
            success=True
        )
        
        return new_token
    
    def check_rotation_needed(self) -> List[str]:
        """Check which agents need token rotation"""
        needs_rotation = []
        warning_threshold = datetime.utcnow() + timedelta(hours=self.rotation_warning_hours)
        
        for token in self.tokens.values():
            if token.status == TokenStatus.ACTIVE:
                expires = datetime.fromisoformat(token.expires_at.replace('Z', ''))
                if expires < warning_threshold:
                    token.status = TokenStatus.PENDING_ROTATION
                    needs_rotation.append(token.agent_id)
        
        return needs_rotation
    
    # =========================================================================
    # AUDIT LOGGING
    # =========================================================================
    
    def _audit_log(self, 
                   agent_id: str,
                   action: str,
                   resource: str,
                   permission_used: str,
                   success: bool,
                   details: Dict = None):
        """Record an audit log entry"""
        entry = AuditLogEntry(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            agent_id=agent_id,
            action=action,
            resource=resource,
            permission_used=permission_used,
            success=success,
            details=details or {}
        )
        self.audit_log.append(entry)
        
        # Keep only last 10000 entries in memory
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
    
    def get_audit_log(self, 
                      agent_id: str = None,
                      action: str = None,
                      success: bool = None,
                      limit: int = 100) -> List[AuditLogEntry]:
        """Query audit log with filters"""
        results = self.audit_log
        
        if agent_id:
            results = [e for e in results if e.agent_id == agent_id]
        if action:
            results = [e for e in results if e.action == action]
        if success is not None:
            results = [e for e in results if e.success == success]
        
        return results[-limit:]
    
    # =========================================================================
    # BEHAVIORAL ANOMALY DETECTION
    # =========================================================================
    
    def update_behavioral_baseline(self, agent_id: str, metrics: Dict):
        """Update behavioral baseline for an agent"""
        if agent_id not in self.behavioral_baseline:
            self.behavioral_baseline[agent_id] = {
                'api_calls_per_hour': [],
                'data_accessed_mb': [],
                'actions_per_hour': [],
                'error_rate': []
            }
        
        baseline = self.behavioral_baseline[agent_id]
        for key, value in metrics.items():
            if key in baseline:
                baseline[key].append(value)
                # Keep last 168 hours (1 week)
                baseline[key] = baseline[key][-168:]
    
    def detect_anomaly(self, agent_id: str, current_metrics: Dict) -> tuple[bool, float, List[str]]:
        """
        Detect behavioral anomalies for an agent.
        Returns (is_anomaly, anomaly_score, anomaly_details)
        """
        if agent_id not in self.behavioral_baseline:
            return False, 0.0, []
        
        baseline = self.behavioral_baseline[agent_id]
        anomalies = []
        scores = []
        
        for key, current_value in current_metrics.items():
            if key in baseline and len(baseline[key]) >= 24:
                historical = baseline[key]
                mean = sum(historical) / len(historical)
                variance = sum((x - mean) ** 2 for x in historical) / len(historical)
                std = variance ** 0.5 if variance > 0 else 1
                
                # Z-score
                z_score = abs(current_value - mean) / std if std > 0 else 0
                scores.append(z_score)
                
                if z_score > 3:
                    anomalies.append(f"{key}: z-score={z_score:.2f} (current={current_value}, mean={mean:.2f})")
        
        anomaly_score = max(scores) if scores else 0
        is_anomaly = anomaly_score > 3
        
        if is_anomaly:
            agent = self.agents.get(agent_id)
            if agent:
                agent.anomaly_score = anomaly_score
        
        return is_anomaly, anomaly_score, anomalies
    
    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================
    
    def suspend_agent(self, agent_id: str, reason: str = None):
        """Suspend an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].is_active = False
            
            # Revoke all tokens
            for token in self.tokens.values():
                if token.agent_id == agent_id:
                    token.status = TokenStatus.REVOKED
            
            self._audit_log(
                agent_id=agent_id,
                action="AGENT_SUSPENDED",
                resource="ai_iam",
                permission_used="manage:agents",
                success=True,
                details={"reason": reason}
            )
            
            self._save_state()
    
    def reactivate_agent(self, agent_id: str) -> Optional[str]:
        """Reactivate a suspended agent"""
        if agent_id in self.agents:
            self.agents[agent_id].is_active = True
            self.agents[agent_id].anomaly_score = 0.0
            
            # Generate new token
            new_token = self._generate_token(agent_id)
            
            self._audit_log(
                agent_id=agent_id,
                action="AGENT_REACTIVATED",
                resource="ai_iam",
                permission_used="manage:agents",
                success=True
            )
            
            self._save_state()
            return new_token
        return None
    
    def get_agent_status(self, agent_id: str = None) -> Dict:
        """Get status of one or all agents"""
        if agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                return {
                    'agent_id': agent.agent_id,
                    'name': agent.name,
                    'role': agent.role.value,
                    'is_active': agent.is_active,
                    'permissions': [p.value for p in agent.permissions],
                    'last_activity': agent.last_activity,
                    'anomaly_score': agent.anomaly_score
                }
            return {}
        
        return {
            'total_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.is_active),
            'suspended_agents': sum(1 for a in self.agents.values() if not a.is_active),
            'agents': [
                {
                    'agent_id': a.agent_id,
                    'name': a.name,
                    'role': a.role.value,
                    'is_active': a.is_active
                }
                for a in self.agents.values()
            ]
        }


# =============================================================================
# ECHONATE AGENT REGISTRY
# =============================================================================

def initialize_echonate_agents(iam: AIIdentityManager) -> Dict[str, str]:
    """
    Initialize the standard EchoNate agent fleet.
    Returns dict of agent_id -> raw_token
    """
    agents_config = [
        {
            'name': 'Alpha-Financial',
            'role': AgentRole.COLLECTOR,
            'description': 'Financial data collection from CoinGecko, Yahoo Finance',
            'allowed_apis': ['coingecko.com', 'yahoo.com', 'finance.yahoo'],
            'allowed_actions': ['fetch_crypto', 'fetch_stock', 'fetch_market']
        },
        {
            'name': 'Beta-Geophysical',
            'role': AgentRole.COLLECTOR,
            'description': 'Seismic and environmental data from USGS, NOAA',
            'allowed_apis': ['usgs.gov', 'noaa.gov', 'earthquake.usgs'],
            'allowed_actions': ['fetch_earthquakes', 'fetch_weather', 'fetch_marine']
        },
        {
            'name': 'Gamma-Health',
            'role': AgentRole.COLLECTOR,
            'description': 'Health data from disease.sh and WHO',
            'allowed_apis': ['disease.sh', 'who.int'],
            'allowed_actions': ['fetch_covid', 'fetch_health']
        },
        {
            'name': 'Delta-Geopolitical',
            'role': AgentRole.COLLECTOR,
            'description': 'Global events from GDELT and news sources',
            'allowed_apis': ['gdeltproject.org', 'newsapi.org'],
            'allowed_actions': ['fetch_events', 'fetch_news']
        },
        {
            'name': 'Epsilon-Adversarial',
            'role': AgentRole.ADVERSARIAL,
            'description': 'Red team agent for signal validation',
            'allowed_apis': ['*'],  # Read access to all for validation
            'allowed_actions': ['challenge_signal', 'validate_correlation', 'audit_data']
        },
        {
            'name': 'Omega-Correlator',
            'role': AgentRole.ANALYZER,
            'description': 'Cross-domain correlation engine',
            'allowed_apis': ['*'],
            'allowed_actions': ['analyze', 'correlate', 'generate_signal']
        },
        {
            'name': 'Sigma-Monitor',
            'role': AgentRole.MONITOR,
            'description': 'System health and observability',
            'allowed_apis': ['*'],
            'allowed_actions': ['monitor', 'alert', 'report']
        }
    ]
    
    tokens = {}
    
    for config in agents_config:
        agent, token = iam.register_agent(
            name=config['name'],
            role=config['role'],
            description=config['description'],
            allowed_apis=config['allowed_apis'],
            allowed_actions=config['allowed_actions']
        )
        tokens[agent.agent_id] = token
        print(f"Registered: {config['name']} ({agent.agent_id})")
    
    return tokens


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ECHONATE AI IDENTITY AND ACCESS MANAGEMENT")
    print("=" * 80)
    
    # Initialize IAM
    iam = AIIdentityManager("demo_ai_iam.json")
    
    # Register EchoNate agents
    print("\n[1] Registering EchoNate Agent Fleet...")
    tokens = initialize_echonate_agents(iam)
    
    # Test authentication
    print("\n[2] Testing Authentication...")
    first_token = list(tokens.values())[0]
    agent = iam.authenticate(first_token)
    if agent:
        print(f"    Authenticated: {agent.name} ({agent.role.value})")
    
    # Test authorization
    print("\n[3] Testing Authorization...")
    allowed, agent, reason = iam.check_access(
        first_token,
        PermissionScope.READ_DATA,
        resource="coingecko.com/api/v3/global",
        action="fetch_crypto"
    )
    print(f"    Access: {allowed} - {reason}")
    
    # Test denied access
    print("\n[4] Testing Denied Access (wrong permission)...")
    allowed, agent, reason = iam.check_access(
        first_token,
        PermissionScope.EXECUTE_TRADES,
        resource="broker.com/trade",
        action="execute_order"
    )
    print(f"    Access: {allowed} - {reason}")
    
    # Test anomaly detection
    print("\n[5] Testing Anomaly Detection...")
    if agent:
        # Simulate normal baseline
        for _ in range(48):
            iam.update_behavioral_baseline(agent.agent_id, {
                'api_calls_per_hour': 50 + (secrets.randbelow(20) - 10),
                'data_accessed_mb': 10 + (secrets.randbelow(4) - 2)
            })
        
        # Test with anomalous metrics
        is_anomaly, score, details = iam.detect_anomaly(agent.agent_id, {
            'api_calls_per_hour': 500,  # 10x normal
            'data_accessed_mb': 100     # 10x normal
        })
        print(f"    Anomaly detected: {is_anomaly}")
        print(f"    Anomaly score: {score:.2f}")
        if details:
            for d in details:
                print(f"    - {d}")
    
    # Get system status
    print("\n[6] System Status...")
    status = iam.get_agent_status()
    print(f"    Total agents: {status['total_agents']}")
    print(f"    Active agents: {status['active_agents']}")
    
    # Show audit log
    print("\n[7] Recent Audit Log...")
    logs = iam.get_audit_log(limit=5)
    for log in logs:
        print(f"    [{log.timestamp}] {log.agent_id}: {log.action} - {log.success}")
    
    print("\n" + "=" * 80)
    print("AI IAM Framework Demonstration Complete")
    print("=" * 80)
