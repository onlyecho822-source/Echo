#!/usr/bin/env python3
"""
Base Agent Class for Echo Universe Autonomous Agents
Provides core functionality for GitHub operations, Constitutional Ledger logging, and autopilot mode
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import sys
import requests

class EchoAgent:
    """Base class for all Echo Universe autonomous agents"""
    
    def __init__(self, agent_name: str, agent_type: str, work_interval: int = 300):
        """
        Initialize Echo agent
        
        Args:
            agent_name: Unique identifier for this agent instance
            agent_type: Type of agent (planner, cleaner, yellowpages, etc.)
            work_interval: Seconds between work cycles (default: 300 = 5 minutes)
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.work_interval = work_interval
        self.repo_path = os.getenv('ECHO_REPO_PATH', '/home/ubuntu/Echo')
        self.ledger_path = os.path.join(self.repo_path, 'ledgers', 'agent_activity')
        self.state_path = os.path.join(self.repo_path, 'agents', 'shared', 'state')
        self.autopilot = True
        self.cycle_count = 0
        self.court_url = 'http://localhost:5001'
        self.latest_court_attestation_id = None
        
        # Ensure directories exist
        os.makedirs(self.ledger_path, exist_ok=True)
        os.makedirs(self.state_path, exist_ok=True)
        
        # Initialize agent state
        self.state_file = os.path.join(self.state_path, f'{agent_name}.json')
        self.load_state()
        
    def load_state(self):
        """Load agent state from disk"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': None,
                'cycle_count': 0,
                'tasks_completed': 0,
                'errors': []
            }
            self.save_state()
    
    def save_state(self):
        """Save agent state to disk"""
        self.state['last_activity'] = datetime.utcnow().isoformat()
        self.state['cycle_count'] = self.cycle_count
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log_to_ledger(self, action: str, details: Dict[str, Any], success: bool = True):
        """
        Log agent activity to Constitutional Ledger
        
        Args:
            action: Action performed (e.g., "cleaned_repo", "created_plan")
            details: Dictionary of action details
            success: Whether action succeeded
        """
        timestamp = datetime.utcnow().isoformat()
        entry = {
            'timestamp': timestamp,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'action': action,
            'details': details,
            'success': success,
            'cycle': self.cycle_count
        }
        
        # Create hash for integrity
        entry_str = json.dumps(entry, sort_keys=True)
        entry['hash'] = hashlib.sha256(entry_str.encode()).hexdigest()
        
        # Append to ledger file
        ledger_file = os.path.join(
            self.ledger_path,
            f"{self.agent_name}_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        )
        
        with open(ledger_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        print(f"[{timestamp}] {self.agent_name}: {action} - {'SUCCESS' if success else 'FAILED'}")
    
    def git_sync(self, commit_message: str, files: Optional[List[str]] = None):
        """
        Sync changes to GitHub
        
        Args:
            commit_message: Git commit message
            files: List of files to add (None = add all changes)
        """
        try:
            os.chdir(self.repo_path)
            
            # Pull latest changes
            subprocess.run(['git', 'pull', 'origin', 'architecture-hierarchy'], 
                          capture_output=True, check=False)
            
            # Add files
            if files:
                for file in files:
                    subprocess.run(['git', 'add', file], check=True)
            else:
                subprocess.run(['git', 'add', '.'], check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   capture_output=True, text=True)
            
            if result.stdout.strip():
                # Commit changes
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                # Push to remote
                subprocess.run(['git', 'push', 'origin', 'architecture-hierarchy'], check=True)
                
                self.log_to_ledger('git_sync', {
                    'commit_message': commit_message,
                    'files_changed': len(result.stdout.strip().split('\n'))
                }, success=True)
                
                return True
            else:
                self.log_to_ledger('git_sync', {
                    'message': 'No changes to commit'
                }, success=True)
                return False
                
        except subprocess.CalledProcessError as e:
            self.log_to_ledger('git_sync', {
                'error': str(e),
                'commit_message': commit_message
            }, success=False)
            return False
    
    def do_work(self) -> Dict[str, Any]:
        """
        Perform agent-specific work (to be overridden by subclasses)
        
        Returns:
            Dictionary with work results
        """
        raise NotImplementedError("Subclasses must implement do_work()")
    
    def submit_to_court(self):
        """Submit attestation to Constitutional Court"""
        try:
            # Calculate ledger hash
            ledger_files = list(Path(self.ledger_path).glob('*.jsonl'))
            ledger_content = ''
            for lf in ledger_files:
                with open(lf, 'r') as f:
                    ledger_content += f.read()
            
            ledger_hash = hashlib.sha256(ledger_content.encode()).hexdigest()
            
            # Count agents
            agent_count = len(list(Path(self.state_path).glob('*.json')))
            
            # Prepare attestation
            attestation = {
                'timestamp': datetime.utcnow().isoformat(),
                'ledger_hash': ledger_hash,
                'agent_count': agent_count,
                'operations_count': self.state.get('tasks_completed', 0),
                'red_line_violations': 0
            }
            
            # Submit to Court
            response = requests.post(f'{self.court_url}/attest', json=attestation, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                self.latest_court_attestation_id = result['attestation_id']
                print(f"  ✓ Court attestation: {result['attestation_id']}")
                return True
            else:
                print(f"  ✗ Court attestation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ✗ Court submission error: {e}")
            return False
    
    def check_redline(self, operation: str, context: dict = None) -> bool:
        """Check operation against Constitutional Court red lines"""
        try:
            check_data = {
                'operation': operation,
                'agent': self.agent_name,
                'context': context or {}
            }
            
            response = requests.post(f'{self.court_url}/check_redline', json=check_data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if not result['allowed']:
                    print(f"  ⚠ Red line violation detected: {result['violations'][0]['rule']}")
                    return False
                return True
            else:
                # If Court unavailable, err on side of caution
                print(f"  ⚠ Court unavailable, blocking operation")
                return False
                
        except Exception as e:
            print(f"  ⚠ Court check failed: {e}, blocking operation")
            return False
    
    def run_cycle(self):
        """Run a single work cycle"""
        self.cycle_count += 1
        
        try:
            print(f"\n{'='*60}")
            print(f"[{datetime.utcnow().isoformat()}] {self.agent_name} - Cycle {self.cycle_count}")
            print(f"{'='*60}\n")
            
            # Perform work
            result = self.do_work()
            
            # Update state
            self.state['tasks_completed'] += result.get('tasks_completed', 0)
            self.save_state()
            
            # Submit to Constitutional Court every cycle
            if self.cycle_count % 1 == 0:  # Every cycle
                self.submit_to_court()
            
            # Log cycle completion
            self.log_to_ledger('cycle_complete', {
                'cycle': self.cycle_count,
                'result': result
            }, success=True)
            
        except Exception as e:
            error_msg = f"Error in cycle {self.cycle_count}: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.state['errors'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'cycle': self.cycle_count,
                'error': str(e)
            })
            self.save_state()
            self.log_to_ledger('cycle_error', {
                'cycle': self.cycle_count,
                'error': str(e)
            }, success=False)
    
    def run_autopilot(self):
        """Run agent in autopilot mode (continuous operation)"""
        print(f"\n{'#'*60}")
        print(f"# {self.agent_name} STARTING IN AUTOPILOT MODE")
        print(f"# Type: {self.agent_type}")
        print(f"# Work Interval: {self.work_interval} seconds")
        print(f"# Press Ctrl+C to stop")
        print(f"{'#'*60}\n")
        
        self.log_to_ledger('autopilot_start', {
            'work_interval': self.work_interval
        }, success=True)
        
        try:
            while self.autopilot:
                self.run_cycle()
                
                if self.autopilot:
                    print(f"\nSleeping for {self.work_interval} seconds...")
                    time.sleep(self.work_interval)
                    
        except KeyboardInterrupt:
            print(f"\n\n{self.agent_name} received shutdown signal")
            self.log_to_ledger('autopilot_stop', {
                'reason': 'keyboard_interrupt',
                'total_cycles': self.cycle_count,
                'total_tasks': self.state['tasks_completed']
            }, success=True)
        
        print(f"\n{self.agent_name} stopped. Total cycles: {self.cycle_count}")
    
    def run_once(self):
        """Run agent for a single cycle (for testing)"""
        print(f"\n{self.agent_name} running single cycle...")
        self.run_cycle()
        print(f"\n{self.agent_name} single cycle complete.")
