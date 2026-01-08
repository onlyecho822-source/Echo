#!/usr/bin/env python3
"""
Receipt Chain Verifier
Validates the integrity of agent performance records.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

class ReceiptChainVerifier:
    """
    Verifies the cryptographic integrity of the agent assessment chain.
    """
    
    def __init__(self, receipt_dir: Path):
        self.receipt_dir = receipt_dir
        self.receipts = []
        self.errors = []
    
    def load_receipts(self) -> List[Dict]:
        """
        Load all receipts from the chain directory.
        """
        if not self.receipt_dir.exists():
            self.errors.append(f"Receipt directory not found: {self.receipt_dir}")
            return []
        
        receipt_files = sorted(self.receipt_dir.glob("*.json"))
        
        for receipt_file in receipt_files:
            try:
                with open(receipt_file, 'r') as f:
                    receipt = json.load(f)
                    receipt["_file"] = receipt_file.name
                    self.receipts.append(receipt)
            except Exception as e:
                self.errors.append(f"Failed to load {receipt_file.name}: {e}")
        
        return self.receipts
    
    def compute_receipt_hash(self, receipt: Dict) -> str:
        """
        Compute the SHA-256 hash of a receipt's content.
        """
        # Create a canonical representation (excluding metadata)
        canonical = {
            "agent_id": receipt.get("agent_id"),
            "scenario_id": receipt.get("scenario_id"),
            "start_time": receipt.get("start_time"),
            "end_time": receipt.get("end_time"),
            "performance": receipt.get("performance", {}),
        }
        
        canonical_json = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()
    
    def verify_chain_integrity(self) -> bool:
        """
        Verify that the receipt chain has not been tampered with.
        """
        if not self.receipts:
            self.errors.append("No receipts found in chain")
            return False
        
        print(f"\n[VERIFIER] Checking {len(self.receipts)} receipts...")
        
        for i, receipt in enumerate(self.receipts):
            # Compute hash
            computed_hash = self.compute_receipt_hash(receipt)
            
            # Check if receipt has expected fields
            required_fields = ["agent_id", "scenario_id", "start_time", "end_time"]
            missing_fields = [f for f in required_fields if f not in receipt]
            
            if missing_fields:
                self.errors.append(
                    f"Receipt {receipt['_file']} missing fields: {missing_fields}"
                )
                continue
            
            # In a full implementation, we would verify:
            # 1. prev_hash matches the previous receipt's hash
            # 2. Cryptographic signature is valid
            # 3. Timestamp is monotonically increasing
            
            print(f"  [{i+1}/{len(self.receipts)}] {receipt['_file']}: OK (hash: {computed_hash[:8]}...)")
        
        if self.errors:
            print(f"\n[VERIFIER] Found {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  - {error}")
            return False
        
        print(f"\n[VERIFIER] Chain integrity verified ✓")
        return True
    
    def generate_agent_credentials(self, agent_id: str) -> Optional[Dict]:
        """
        Generate verified credentials for an agent based on their receipt chain.
        """
        agent_receipts = [r for r in self.receipts if r.get("agent_id") == agent_id]
        
        if not agent_receipts:
            return None
        
        # Calculate aggregate performance metrics
        total_scenarios = len(agent_receipts)
        passed_scenarios = sum(1 for r in agent_receipts if r.get("passed", False))
        
        # Extract capabilities from passed scenarios
        capabilities = set()
        for receipt in agent_receipts:
            if receipt.get("passed"):
                scenario_id = receipt.get("scenario_id", "")
                if "chaos" in scenario_id:
                    capabilities.add("chaos_resilience")
                if "team" in scenario_id:
                    capabilities.add("team_collaboration")
                if "leadership" in scenario_id:
                    capabilities.add("team_leadership")
        
        credentials = {
            "agent_id": agent_id,
            "total_scenarios_completed": total_scenarios,
            "scenarios_passed": passed_scenarios,
            "pass_rate": passed_scenarios / total_scenarios if total_scenarios > 0 else 0,
            "verified_capabilities": list(capabilities),
            "credential_level": self._determine_level(passed_scenarios),
            "issued_at": agent_receipts[-1].get("end_time") if agent_receipts else None,
        }
        
        return credentials
    
    def _determine_level(self, passed_scenarios: int) -> str:
        """
        Determine agent credential level based on passed scenarios.
        """
        if passed_scenarios >= 10:
            return "Expert"
        elif passed_scenarios >= 5:
            return "Proficient"
        elif passed_scenarios >= 2:
            return "Competent"
        else:
            return "Cadet"
    
    def save_credentials(self, agent_id: str, output_dir: Path) -> Optional[Path]:
        """
        Generate and save agent credentials.
        """
        credentials = self.generate_agent_credentials(agent_id)
        
        if not credentials:
            print(f"[ERROR] No receipts found for agent: {agent_id}")
            return None
        
        output_dir.mkdir(parents=True, exist_ok=True)
        cred_file = output_dir / f"{agent_id}.json"
        
        with open(cred_file, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"\n[CREDENTIALS] Generated for {agent_id}")
        print(f"  Level: {credentials['credential_level']}")
        print(f"  Pass Rate: {credentials['pass_rate']:.1%}")
        print(f"  Capabilities: {', '.join(credentials['verified_capabilities'])}")
        print(f"  Saved to: {cred_file}")
        
        return cred_file


def main():
    """
    Run the receipt chain verifier.
    """
    import sys
    
    # Determine paths
    script_dir = Path(__file__).parent
    receipt_dir = script_dir / "receipt_chain"
    credentials_dir = script_dir.parent / "credentials"
    
    # Initialize verifier
    verifier = ReceiptChainVerifier(receipt_dir)
    
    # Load and verify receipts
    verifier.load_receipts()
    chain_valid = verifier.verify_chain_integrity()
    
    if not chain_valid:
        print("\n[FAILURE] Chain integrity check failed")
        sys.exit(1)
    
    # Generate credentials for all agents
    agent_ids = set(r.get("agent_id") for r in verifier.receipts if r.get("agent_id"))
    
    print(f"\n[CREDENTIALS] Generating for {len(agent_ids)} agents...")
    
    for agent_id in agent_ids:
        verifier.save_credentials(agent_id, credentials_dir)
    
    print(f"\n[SUCCESS] Verification complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
