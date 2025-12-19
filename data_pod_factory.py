#!/usr/bin/env python3
"""
Echo Library - Data Pod Factory
Vatican-level institutional preservation standard

Creates hash-sealed, tamper-evident Data Pods for immutable record keeping.
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class DataPodFactory:
    """Core factory for creating and verifying hash-sealed Data Pods."""

    @staticmethod
    def create_data_pod(
        target_uri: str,
        protocol: str,
        port: int,
        agent_id: str,
        location: str,
        engine_hash: str,
        status: str,
        latency_ms: float,
        payload_data: bytes,
        falsification_condition: str,
        retest_interval_sec: int = 3600,
        pod_type: str = "network_probe"
    ) -> Dict[str, Any]:
        """
        Creates a v1.0 Data Pod from observation inputs.
        The 'payload_data' is the raw bytes of the server response.
        
        Args:
            target_uri: The subject being verified (e.g., "api.binance.com")
            protocol: Protocol used (e.g., "https")
            port: Port number
            agent_id: The specific "Watcher" script or node
            location: Geographic/Network vantage point
            engine_hash: Hash of the script code that ran this test (Code-as-Law)
            status: Test result status (e.g., "success", "blocked_451", "timeout")
            latency_ms: Response time in milliseconds
            payload_data: Raw server response body (evidence)
            falsification_condition: Condition under which this belief dies
            retest_interval_sec: How often to retest (default: 1 hour)
            pod_type: Type of probe (default: "network_probe")
            
        Returns:
            Complete Data Pod with integrity seal
        """
        
        # 1. Generate payload hash (evidence)
        payload_hash = hashlib.sha256(payload_data).hexdigest()
        
        # 2. Construct the pod skeleton (integrity_seal is calculated last)
        pod = {
            "pod_version": "1.0",
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": pod_type,
            "target": {
                "uri": target_uri,
                "protocol": protocol,
                "port": port
            },
            "provenance": {
                "agent_id": agent_id,
                "location": location,
                "engine_hash": engine_hash
            },
            "metrics": {
                "status": status,
                "latency_ms": latency_ms,
                "payload_hash": payload_hash
            },
            "falsification_criteria": {
                "condition": falsification_condition,
                "retest_interval_sec": retest_interval_sec
            },
            "integrity_seal": ""  # Placeholder
        }
        
        # 3. Calculate and set the integrity seal (the pod's root hash)
        pod["integrity_seal"] = DataPodFactory._calculate_integrity_seal(pod)
        
        return pod

    @staticmethod
    def _calculate_integrity_seal(pod: Dict[str, Any]) -> str:
        """
        Calculates the SHA-256 hash of all pod fields EXCEPT the 'integrity_seal' itself.
        This hash becomes the pod's unique Content ID (CID).
        
        Args:
            pod: Data Pod dictionary
            
        Returns:
            SHA-256 hash with sha256: prefix - the pod's integrity seal
        """
        # Create a copy and remove the seal for calculation
        pod_for_hashing = pod.copy()
        pod_for_hashing["integrity_seal"] = ""
        
        # Convert to a canonical JSON string (sorted keys, no whitespace)
        canonical_json = json.dumps(pod_for_hashing, sort_keys=True, separators=(',', ':'))
        
        # Calculate hash and return with sha256: prefix (IPFS/Filecoin standard)
        hash_hex = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        return f"sha256:{hash_hex}"

    @staticmethod
    def verify_data_pod(pod: Dict[str, Any]) -> bool:
        """
        Verifies the integrity of a Data Pod by recalculating its seal.
        Uses constant-time comparison to prevent timing attacks.
        Returns True if the pod is tamper-evident, False if corrupted.
        
        Args:
            pod: Data Pod dictionary to verify
            
        Returns:
            True if integrity seal matches, False if tampered
        """
        stored_seal = pod.get("integrity_seal", "")
        if not stored_seal:
            return False
        
        # Support both prefixed and non-prefixed seals for backward compatibility
        if not stored_seal.startswith("sha256:"):
            stored_seal = f"sha256:{stored_seal}"
        
        # Recalculate the seal from the pod's current contents
        calculated_seal = DataPodFactory._calculate_integrity_seal(pod)
        
        # Constant-time comparison to prevent timing attacks
        # This prevents attackers from measuring verification time to guess hashes
        return hashlib.sha256(stored_seal.encode()).digest() == \
               hashlib.sha256(calculated_seal.encode()).digest()

    @staticmethod
    def save_data_pod(pod: Dict[str, Any], filepath: str) -> str:
        """
        Save Data Pod to file and return its integrity seal.
        
        Args:
            pod: Data Pod dictionary
            filepath: Path to save the pod
            
        Returns:
            Integrity seal (CID) of the saved pod
        """
        with open(filepath, 'w') as f:
            json.dump(pod, f, indent=2)
        
        return pod["integrity_seal"]

    @staticmethod
    def load_and_verify_data_pod(filepath: str) -> tuple[Dict[str, Any], bool]:
        """
        Load Data Pod from file and verify its integrity.
        
        Args:
            filepath: Path to the pod file
            
        Returns:
            Tuple of (pod_dict, is_valid)
        """
        with open(filepath, 'r') as f:
            pod = json.load(f)
        
        is_valid = DataPodFactory.verify_data_pod(pod)
        
        return pod, is_valid

    @staticmethod
    def create_engine_hash(script_content: str) -> str:
        """
        Create hash of the script code that ran the test (Code-as-Law).
        
        Args:
            script_content: Source code of the test script
            
        Returns:
            SHA-256 hash of the script
        """
        return hashlib.sha256(script_content.encode('utf-8')).hexdigest()

    @staticmethod
    def create_test_ledger_entry(pod: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a ledger entry from a Data Pod for Echo's immutable ledger.
        
        Args:
            pod: Data Pod dictionary
            
        Returns:
            Ledger entry dictionary
        """
        return {
            "entry_type": "data_pod_created",
            "data": {
                "pod_id": pod["id"],
                "pod_cid": pod["integrity_seal"],
                "target_uri": pod["target"]["uri"],
                "status": pod["metrics"]["status"],
                "timestamp": pod["timestamp"],
                "falsification_condition": pod["falsification_criteria"]["condition"]
            }
        }


class DataPodCollection:
    """Collection of Data Pods with aggregate verification."""
    
    def __init__(self):
        self.pods = []
        self.collection_hash = None
    
    def add_pod(self, pod: Dict[str, Any]):
        """Add a Data Pod to the collection."""
        if not DataPodFactory.verify_data_pod(pod):
            raise ValueError(f"Invalid pod integrity: {pod.get('id')}")
        self.pods.append(pod)
        self._update_collection_hash()
    
    def _update_collection_hash(self):
        """Calculate hash of all pod integrity seals."""
        if not self.pods:
            self.collection_hash = None
            return
        
        # Concatenate all pod seals and hash
        all_seals = ''.join(pod["integrity_seal"] for pod in self.pods)
        self.collection_hash = hashlib.sha256(all_seals.encode('utf-8')).hexdigest()
    
    def verify_collection(self) -> bool:
        """Verify integrity of all pods in collection."""
        for pod in self.pods:
            if not DataPodFactory.verify_data_pod(pod):
                return False
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the collection."""
        if not self.pods:
            return {
                "total_pods": 0,
                "collection_hash": None
            }
        
        statuses = {}
        for pod in self.pods:
            status = pod["metrics"]["status"]
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_pods": len(self.pods),
            "collection_hash": self.collection_hash,
            "status_breakdown": statuses,
            "earliest_timestamp": min(pod["timestamp"] for pod in self.pods),
            "latest_timestamp": max(pod["timestamp"] for pod in self.pods)
        }
    
    def save_collection(self, filepath: str):
        """Save entire collection to file."""
        collection_data = {
            "collection_version": "1.0",
            "collection_hash": self.collection_hash,
            "pod_count": len(self.pods),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pods": self.pods
        }
        
        with open(filepath, 'w') as f:
            json.dump(collection_data, f, indent=2)


if __name__ == "__main__":
    # Test the Data Pod Factory
    print("Testing Data Pod Factory...")
    
    # Create a test pod
    test_pod = DataPodFactory.create_data_pod(
        target_uri="api.example.com",
        protocol="https",
        port=443,
        agent_id="echo_probe_test",
        location="local_test",
        engine_hash="test_hash_123",
        status="success",
        latency_ms=45.2,
        payload_data=b"test response data",
        falsification_condition="latency_ms > 100 OR status != success"
    )
    
    print(f"✓ Pod created: {test_pod['id']}")
    print(f"  Integrity seal: {test_pod['integrity_seal'][:16]}...")
    
    # Verify the pod
    is_valid = DataPodFactory.verify_data_pod(test_pod)
    print(f"✓ Pod verification: {'VALID' if is_valid else 'INVALID'}")
    
    # Test tampering detection
    test_pod_tampered = test_pod.copy()
    test_pod_tampered["metrics"]["latency_ms"] = 999.9
    is_valid_tampered = DataPodFactory.verify_data_pod(test_pod_tampered)
    print(f"✓ Tampered pod detection: {'FAILED (should be invalid)' if is_valid_tampered else 'SUCCESS (detected tampering)'}")
    
    print("\nData Pod Factory ready for production use.")
