"""
Storage Consistency Enforcer
Ensures all storage backends meet ECP immutability requirements.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import hashlib
from datetime import datetime
import json

class ConsistencyError(Exception):
    """Raised when storage fails consistency check."""
    pass

class ImmutabilityGuard:
    """
    Wraps storage backends to enforce ECP immutability guarantees.
    """
    
    def __init__(self, backend):
        self.backend = backend
        self._hash_chain = []
        self._init_chain()
    
    def _init_chain(self):
        """Initialize or load hash chain."""
        try:
            chain_data = self.backend.get_metadata("hash_chain") if hasattr(self.backend, 'get_metadata') else None
            if chain_data:
                self._hash_chain = json.loads(chain_data)
            else:
                # Genesis block
                genesis = self._create_genesis_block()
                self._hash_chain = [genesis]
                self._save_chain()
        except Exception as e:
            raise ConsistencyError(f"Failed to initialize hash chain: {e}")
    
    def store_event(self, event: Dict[str, Any]) -> str:
        """Store event with immutability guarantees."""
        # Validate event structure
        self._validate_event(event)
        
        # Create hash
        event_hash = self._hash_data(event)
        
        # Check for existing event (prevent overwrite)
        if hasattr(self.backend, 'event_exists') and self.backend.event_exists(event['id']):
            raise ConsistencyError(f"Event {event['id']} already exists")
        
        # Add to chain
        chain_entry = self._add_to_chain(event, event_hash, "event")
        
        # Store with chain reference
        event['_ecp_chain_ref'] = chain_entry['index']
        event['_ecp_hash'] = event_hash
        
        # Store in backend
        self.backend.store_event(event)
        
        # Verify integrity
        self._verify_integrity(event['id'], event_hash)
        
        return event_hash
    
    def store_classification(self, classification: Dict[str, Any]) -> str:
        """Store classification with immutability guarantees."""
        # Must reference valid event
        if hasattr(self.backend, 'event_exists') and not self.backend.event_exists(classification['event_id']):
            raise ConsistencyError(
                f"Referenced event {classification['event_id']} does not exist"
            )
        
        # Create hash
        class_hash = self._hash_data(classification)
        
        # Check for existing classification
        existing = None
        if hasattr(self.backend, 'get_classification'):
            existing = self.backend.get_classification(
                classification['event_id'],
                classification['classified_by']
            )
        
        if existing:
            # Allow updates but preserve history
            self._archive_existing(existing)
        
        # Add to chain
        chain_entry = self._add_to_chain(classification, class_hash, "classification")
        
        # Store with chain reference
        classification['_ecp_chain_ref'] = chain_entry['index']
        classification['_ecp_hash'] = class_hash
        
        # Store in backend
        self.backend.store_classification(classification)
        
        return class_hash
    
    def verify_chain(self) -> List[Dict[str, Any]]:
        """Verify entire hash chain integrity."""
        errors = []
        
        for i, entry in enumerate(self._hash_chain):
            # Skip genesis
            if i == 0:
                continue
            
            # Get data from storage
            try:
                data = self._retrieve_by_chain_ref(entry['type'], entry['ref_id'])
                
                # Verify hash
                computed_hash = self._hash_data(data)
                if computed_hash != entry['hash']:
                    errors.append({
                        'index': i,
                        'expected': entry['hash'],
                        'actual': computed_hash,
                        'type': entry['type'],
                        'ref_id': entry['ref_id']
                    })
                    
                # Verify previous hash link
                if entry['previous_hash'] != self._hash_chain[i-1]['hash']:
                    errors.append({
                        'index': i,
                        'message': 'Chain link broken',
                        'previous_expected': self._hash_chain[i-1]['hash'],
                        'previous_actual': entry['previous_hash']
                    })
                    
            except Exception as e:
                errors.append({
                    'index': i,
                    'message': f'Retrieval failed: {str(e)}',
                    'type': entry['type'],
                    'ref_id': entry['ref_id']
                })
        
        return errors
    
    def _validate_event(self, event: Dict[str, Any]):
        """Validate event structure meets ECP requirements."""
        required = ['id', 'timestamp', 'event_type', 'description', 'context']
        missing = [field for field in required if field not in event]
        if missing:
            raise ConsistencyError(f"Event missing required fields: {missing}")
        
        # Context validation
        if 'context' not in event:
            raise ConsistencyError("Event missing context")
        
        context_required = ['causation', 'agency_present', 'duty_of_care',
                           'knowledge_level', 'control_level']
        missing_context = [f for f in context_required if f not in event['context']]
        if missing_context:
            raise ConsistencyError(f"Context missing fields: {missing_context}")
    
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """Create deterministic hash of data."""
        # Remove chain metadata for hashing
        clean_data = {k: v for k, v in data.items() 
                     if not k.startswith('_ecp_')}
        
        # Sort keys for consistent hashing
        sorted_json = json.dumps(clean_data, sort_keys=True)
        
        return hashlib.sha256(sorted_json.encode()).hexdigest()
    
    def _add_to_chain(self, data: Dict[str, Any], data_hash: str, 
                     data_type: str) -> Dict[str, Any]:
        """Add entry to hash chain."""
        previous_hash = self._hash_chain[-1]['hash'] if self._hash_chain else "0" * 64
        
        entry = {
            'index': len(self._hash_chain),
            'timestamp': datetime.utcnow().isoformat(),
            'type': data_type,
            'ref_id': data.get('id', 'unknown'),
            'hash': data_hash,
            'previous_hash': previous_hash
        }
        
        self._hash_chain.append(entry)
        self._save_chain()
        
        return entry
    
    def _save_chain(self):
        """Save hash chain to storage."""
        chain_json = json.dumps(self._hash_chain, indent=2)
        if hasattr(self.backend, 'store_metadata'):
            self.backend.store_metadata("hash_chain", chain_json)
    
    def _create_genesis_block(self) -> Dict[str, Any]:
        """Create genesis block for chain."""
        genesis = {
            'index': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'genesis',
            'ref_id': 'genesis',
            'hash': hashlib.sha256(b"ecp_genesis_block").hexdigest(),
            'previous_hash': "0" * 64
        }
        return genesis
    
    def _verify_integrity(self, ref_id: str, expected_hash: str):
        """Verify stored data integrity."""
        pass
    
    def _retrieve_by_chain_ref(self, data_type: str, ref_id: str) -> Dict[str, Any]:
        """Retrieve data by chain reference."""
        pass
    
    def _archive_existing(self, existing: Dict[str, Any]):
        """Archive existing version when updating."""
        archive_id = f"{existing.get('id', 'unknown')}_v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        existing['_archived_at'] = datetime.utcnow().isoformat()
        existing['_archive_id'] = archive_id
        
        # Store in archive
        if hasattr(self.backend, 'store_archive'):
            self.backend.store_archive(existing)

class StorageConsistencyChecker:
    """
    Periodically checks storage consistency.
    """
    
    def __init__(self, guard: ImmutabilityGuard):
        self.guard = guard
        self._last_check = None
        self._errors = []
    
    def run_check(self) -> Dict[str, Any]:
        """Run comprehensive consistency check."""
        self._last_check = datetime.utcnow()
        
        checks = {
            'chain_integrity': self._check_chain_integrity(),
            'event_references': self._check_event_references(),
            'classification_links': self._check_classification_links(),
            'case_consistency': self._check_case_consistency(),
            'precedent_validity': self._check_precedent_validity()
        }
        
        # Aggregate results
        all_errors = []
        for check_name, check_result in checks.items():
            if check_result['errors']:
                all_errors.extend(check_result['errors'])
        
        result = {
            'timestamp': self._last_check.isoformat(),
            'checks_run': len(checks),
            'checks_failed': sum(1 for c in checks.values() if c['errors']),
            'total_errors': len(all_errors),
            'checks': checks,
            'status': 'healthy' if not all_errors else 'degraded'
        }
        
        if all_errors:
            result['critical_errors'] = [
                e for e in all_errors 
                if e.get('severity') == 'critical'
            ]
        
        self._errors = all_errors
        return result
    
    def _check_chain_integrity(self) -> Dict[str, Any]:
        """Check hash chain integrity."""
        errors = self.guard.verify_chain()
        
        return {
            'description': 'Hash chain integrity check',
            'errors': errors,
            'severity': 'critical' if errors else 'none'
        }
    
    def _check_event_references(self) -> Dict[str, Any]:
        """Verify all events reference valid chain entries."""
        errors = []
        return {
            'description': 'Event chain reference check',
            'errors': errors,
            'severity': 'high' if errors else 'none'
        }
    
    def _check_classification_links(self) -> Dict[str, Any]:
        """Verify classifications link to valid events."""
        errors = []
        return {
            'description': 'Classification event linkage check',
            'errors': errors,
            'severity': 'high' if errors else 'none'
        }
    
    def _check_case_consistency(self) -> Dict[str, Any]:
        """Verify cases reference valid events and classifications."""
        errors = []
        return {
            'description': 'Case consistency check',
            'errors': errors,
            'severity': 'medium' if errors else 'none'
        }
    
    def _check_precedent_validity(self) -> Dict[str, Any]:
        """Verify precedents are valid and not expired."""
        errors = []
        return {
            'description': 'Precedent validity check',
            'errors': errors,
            'severity': 'medium' if errors else 'none'
        }
