#!/usr/bin/env python3.11
"""
Feedback OS - Minimal Working Prototype
Test 3: Prove the core concept works
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

class FeedbackOS:
    def __init__(self, data_file="feedback_data.json"):
        self.data_file = Path(data_file)
        self.data = self._load_data()
    
    def _load_data(self):
        """Load existing data or create new file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {"entries": [], "hash_chain": []}
    
    def _save_data(self):
        """Save data with hash verification"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _create_hash(self, entry):
        """Create cryptographic hash of entry"""
        content = json.dumps(entry, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()
    
    def morning_checkin(self):
        """Morning protocol"""
        print("☀️  MORNING CHECK-IN")
        print("-" * 40)
        
        sleep = input("Sleep Quality (Great/Okay/Bad): ").strip()
        first_input = input("First Input (Phone/Water/Silence): ").strip()
        intention = input("Today's Intention (one word): ").strip()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "morning",
            "sleep": sleep,
            "first_input": first_input,
            "intention": intention
        }
        
        # Create hash and add to chain
        entry_hash = self._create_hash(entry)
        entry["hash"] = entry_hash
        
        # Link to previous hash
        if self.data["hash_chain"]:
            entry["previous_hash"] = self.data["hash_chain"][-1]
        else:
            entry["previous_hash"] = "GENESIS"
        
        self.data["entries"].append(entry)
        self.data["hash_chain"].append(entry_hash)
        self._save_data()
        
        print(f"\n✅ Morning check-in saved")
        print(f"🔒 Hash: {entry_hash[:16]}...")
        return entry
    
    def evening_checkin(self):
        """Evening protocol"""
        print("\n🌙  EVENING CHECK-IN")
        print("-" * 40)
        
        energy = input("Energy Level (High/Medium/Low): ").strip()
        mood = input("Mood (Good/Neutral/Bad): ").strip()
        mirror = input("Daily Mirror - 'Today I noticed...': ").strip()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "evening",
            "energy": energy,
            "mood": mood,
            "mirror": mirror
        }
        
        # Create hash and add to chain
        entry_hash = self._create_hash(entry)
        entry["hash"] = entry_hash
        
        # Link to previous hash
        if self.data["hash_chain"]:
            entry["previous_hash"] = self.data["hash_chain"][-1]
        else:
            entry["previous_hash"] = "GENESIS"
        
        self.data["entries"].append(entry)
        self.data["hash_chain"].append(entry_hash)
        self._save_data()
        
        print(f"\n✅ Evening check-in saved")
        print(f"🔒 Hash: {entry_hash[:16]}...")
        
        # Show simple pattern if we have data
        self._show_patterns()
        
        return entry
    
    def _show_patterns(self):
        """Show simple patterns from data"""
        if len(self.data["entries"]) < 3:
            print("\n📊 Not enough data yet for patterns (need 3+ entries)")
            return
        
        print("\n📊 SIMPLE PATTERNS:")
        print("-" * 40)
        
        # Count first inputs
        first_inputs = {}
        for entry in self.data["entries"]:
            if entry["type"] == "morning":
                inp = entry.get("first_input", "Unknown")
                first_inputs[inp] = first_inputs.get(inp, 0) + 1
        
        if first_inputs:
            print("First Input Frequency:")
            for inp, count in sorted(first_inputs.items(), key=lambda x: x[1], reverse=True):
                print(f"  {inp}: {count} times")
        
        # Count energy levels
        energy_levels = {}
        for entry in self.data["entries"]:
            if entry["type"] == "evening":
                energy = entry.get("energy", "Unknown")
                energy_levels[energy] = energy_levels.get(energy, 0) + 1
        
        if energy_levels:
            print("\nEnergy Level Frequency:")
            for energy, count in sorted(energy_levels.items(), key=lambda x: x[1], reverse=True):
                print(f"  {energy}: {count} times")
    
    def show_status(self):
        """Show current status"""
        print("\n📋 FEEDBACK OS STATUS")
        print("=" * 40)
        print(f"Total Entries: {len(self.data['entries'])}")
        print(f"Hash Chain Length: {len(self.data['hash_chain'])}")
        
        if self.data["entries"]:
            last_entry = self.data["entries"][-1]
            print(f"Last Entry: {last_entry['type']} at {last_entry['timestamp'][:19]}")
        
        print("=" * 40)

def main():
    """Main entry point"""
    import sys
    
    os_instance = FeedbackOS()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python feedback_minimal.py morning   # Morning check-in")
        print("  python feedback_minimal.py evening   # Evening check-in")
        print("  python feedback_minimal.py status    # Show status")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "morning":
        os_instance.morning_checkin()
    elif command == "evening":
        os_instance.evening_checkin()
    elif command == "status":
        os_instance.show_status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
