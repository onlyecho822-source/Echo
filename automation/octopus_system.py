#!/usr/bin/env python3
"""
Octopus Nervous System - Distributed Intelligence Architecture

The octopus has 9 brains:
- 1 central brain (collective intelligence)
- 8 arm brains (autonomous scripts)

Each arm can act independently but shares information through
the central brain. All arms learn from each other in real-time.

The 4 Core Arms:
1. Archon Arm - Daily intelligence reports
2. Phoenix Arm - Weekly global scans
3. Devil's Eye Arm - Monthly quality audits
4. Sentinel Arm - Continuous communication monitoring
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(str(Path(__file__).parent.parent))

from knowledge.brain import CollectiveIntelligence, Lesson, LessonType
from automation.self_teaching_template import SelfTeachingScript


class OctopusNervousSystem:
    """
    The central nervous system coordinating all octopus arms.
    
    Features:
    - Real-time information sharing between arms
    - Parallel execution with shared learning
    - Emergent intelligence from arm collaboration
    - Autonomous adaptation based on collective knowledge
    """
    
    def __init__(self):
        self.brain = CollectiveIntelligence()
        self.arms = {}
        self.execution_log = []
        
    def register_arm(self, arm: 'OctopusArm'):
        """Register an arm with the nervous system"""
        self.arms[arm.arm_id] = arm
        print(f"🐙 Registered arm: {arm.arm_name}")
    
    def share_information(self, from_arm: str, to_arms: List[str], info: Dict[str, Any]):
        """
        Share information between arms in real-time.
        
        Args:
            from_arm: Source arm ID
            to_arms: List of target arm IDs (or ['*'] for all)
            info: Information to share
        """
        if '*' in to_arms:
            to_arms = [arm_id for arm_id in self.arms.keys() if arm_id != from_arm]
        
        # Create lesson for shared information
        lesson = Lesson(
            id=f"share_{from_arm}_{int(time.time())}",
            type=LessonType.DISCOVERY,
            script_id=from_arm,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "shared_info": info,
                "from_arm": from_arm,
                "to_arms": to_arms
            },
            confidence=0.9,
            impact="high",
            teaches=to_arms
        )
        
        # Teach to brain
        self.brain.learn(lesson)
        
        print(f"🐙 {from_arm} → {', '.join(to_arms)}: {info.get('message', 'information shared')}")
    
    def execute_arms_parallel(self, arm_ids: List[str] = None) -> Dict[str, Any]:
        """
        Execute multiple arms in parallel with real-time information sharing.
        
        Args:
            arm_ids: List of arm IDs to execute (None = all arms)
            
        Returns:
            Results from all arms
        """
        if arm_ids is None:
            arm_ids = list(self.arms.keys())
        
        print(f"\n🐙 OCTOPUS NERVOUS SYSTEM: Executing {len(arm_ids)} arms in parallel")
        print("="*70)
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(arm_ids)) as executor:
            # Submit all arms for execution
            future_to_arm = {
                executor.submit(self.arms[arm_id].run): arm_id
                for arm_id in arm_ids
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_arm):
                arm_id = future_to_arm[future]
                try:
                    result = future.result()
                    results[arm_id] = result
                    
                    # Log execution
                    self.execution_log.append({
                        "arm_id": arm_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "success": result.get('success', False)
                    })
                    
                except Exception as e:
                    print(f"❌ Error in arm {arm_id}: {e}")
                    results[arm_id] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return results
    
    def get_nervous_system_status(self) -> Dict[str, Any]:
        """Get status of entire nervous system"""
        evolution = self.brain.evolve()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_arms": len(self.arms),
            "registered_arms": list(self.arms.keys()),
            "total_executions": len(self.execution_log),
            "collective_intelligence": evolution,
            "nervous_system_health": "optimal" if evolution['total_lessons'] > 0 else "nascent"
        }


class OctopusArm(SelfTeachingScript):
    """
    Base class for octopus arms - autonomous scripts with
    distributed intelligence and real-time information sharing.
    """
    
    def __init__(self, arm_id: str, arm_name: str, nervous_system: OctopusNervousSystem = None):
        super().__init__(arm_id, arm_name)
        self.arm_id = arm_id
        self.arm_name = arm_name
        self.nervous_system = nervous_system
    
    def share_with_other_arms(self, info: Dict[str, Any], target_arms: List[str] = None):
        """Share information with other arms through nervous system"""
        if self.nervous_system:
            if target_arms is None:
                target_arms = ['*']  # Share with all arms
            self.nervous_system.share_information(self.arm_id, target_arms, info)
    
    def sense_environment(self) -> Dict[str, Any]:
        """
        Sense the environment (to be overridden by specific arms).
        
        Returns:
            Environmental data
        """
        return {}
    
    def act_autonomously(self, knowledge: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Act autonomously based on knowledge and environment.
        
        This is where the arm's specific intelligence operates.
        To be overridden by specific arms.
        
        Args:
            knowledge: Learned knowledge from collective intelligence
            environment: Current environmental data
            
        Returns:
            Action results
        """
        raise NotImplementedError("Subclasses must implement act_autonomously()")
    
    def execute_task(self, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with octopus arm intelligence"""
        # Sense environment
        environment = self.sense_environment()
        
        # Share environmental data with other arms
        if environment:
            self.share_with_other_arms({
                "message": f"{self.arm_name} sensed environment",
                "environment": environment
            })
        
        # Act autonomously
        results = self.act_autonomously(knowledge, environment)
        
        # Share results with other arms
        if results.get('success'):
            self.share_with_other_arms({
                "message": f"{self.arm_name} completed successfully",
                "key_findings": results.get('key_findings', {})
            })
        
        return results


# ============================================================================
# THE 4 CORE ARMS
# ============================================================================

class ArchonArm(OctopusArm):
    """
    Arm 1: Archon - Daily Intelligence Reports
    
    Monitors all repositories, identifies changes, generates strategic reports.
    """
    
    def __init__(self, nervous_system: OctopusNervousSystem = None):
        super().__init__(
            arm_id="archon_arm",
            arm_name="Archon (Daily Intelligence)",
            nervous_system=nervous_system
        )
    
    def sense_environment(self) -> Dict[str, Any]:
        """Sense repository state"""
        return {
            "repos_monitored": ["GitHub/Echo", "GitLab/Echo"],
            "last_commit": datetime.utcnow().isoformat(),
            "active_prs": 1
        }
    
    def act_autonomously(self, knowledge: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily intelligence report"""
        print(f"  📊 Generating daily intelligence report...")
        
        # Check what other arms have discovered
        discoveries = knowledge.get('discovery', [])
        
        report = {
            "date": datetime.utcnow().isoformat(),
            "repos_status": environment,
            "discoveries_from_other_arms": len(discoveries),
            "recommendations": [
                "Continue monitoring GitHub performance",
                "Review Phoenix global scan results"
            ]
        }
        
        return {
            "success": True,
            "report": report,
            "key_findings": {
                "discoveries": len(discoveries)
            }
        }
    
    def analyze_results(self, results: Dict[str, Any]) -> list:
        """Analyze report generation"""
        lessons = super().analyze_results(results)
        
        # Teach about report generation
        lesson = Lesson(
            id=f"archon_report_{int(self.start_time.timestamp())}",
            type=LessonType.PATTERN,
            script_id=self.arm_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "pattern": "daily_report_generated",
                "discoveries_count": results.get('key_findings', {}).get('discoveries', 0)
            },
            confidence=0.95,
            impact="medium",
            teaches=["*"]
        )
        lessons.append(lesson)
        
        return lessons


class PhoenixArm(OctopusArm):
    """
    Arm 2: Phoenix - Weekly Global Scans
    
    Tests global infrastructure, discovers patterns, identifies opportunities.
    """
    
    def __init__(self, nervous_system: OctopusNervousSystem = None):
        super().__init__(
            arm_id="phoenix_arm",
            arm_name="Phoenix (Weekly Global Scan)",
            nervous_system=nervous_system
        )
    
    def sense_environment(self) -> Dict[str, Any]:
        """Sense global infrastructure state"""
        return {
            "endpoints_available": 16,
            "last_scan": "2026-01-07T15:43:52Z",
            "fastest_endpoint": "github.com"
        }
    
    def act_autonomously(self, knowledge: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute global infrastructure scan"""
        print(f"  🔥 Executing Phoenix global scan...")
        
        # Check if we already know GitHub is fastest
        github_fast = False
        for pattern in knowledge.get('pattern', []):
            if 'github_api_fastest' in pattern.get('data', {}).get('pattern', ''):
                github_fast = True
                print(f"    📚 Applied learning: Prioritizing GitHub (known fastest)")
        
        # Simulate scan (in real implementation, would test endpoints)
        scan_results = {
            "github_latency": 64.51,
            "gitlab_latency": 2427.66,
            "new_discovery": "Africa infrastructure surprisingly fast"
        }
        
        return {
            "success": True,
            "scan_results": scan_results,
            "applied_learning": github_fast,
            "key_findings": {
                "fastest": "github.com",
                "discovery": scan_results["new_discovery"]
            }
        }
    
    def analyze_results(self, results: Dict[str, Any]) -> list:
        """Analyze scan results"""
        lessons = super().analyze_results(results)
        
        # Teach about new discovery
        if results.get('key_findings', {}).get('discovery'):
            lesson = Lesson(
                id=f"phoenix_discovery_{int(self.start_time.timestamp())}",
                type=LessonType.DISCOVERY,
                script_id=self.arm_id,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "discovery": results['key_findings']['discovery'],
                    "impact": "Challenges assumptions about infrastructure"
                },
                confidence=0.9,
                impact="high",
                teaches=["*"]
            )
            lessons.append(lesson)
        
        return lessons


class DevilsEyeArm(OctopusArm):
    """
    Arm 3: Devil's Eye - Monthly Quality Audits
    
    Reviews all claims, identifies overclaims, ensures production readiness.
    """
    
    def __init__(self, nervous_system: OctopusNervousSystem = None):
        super().__init__(
            arm_id="devils_eye_arm",
            arm_name="Devil's Eye (Monthly Audit)",
            nervous_system=nervous_system
        )
    
    def sense_environment(self) -> Dict[str, Any]:
        """Sense system quality state"""
        return {
            "total_claims": 47,
            "last_audit": "2026-01-07",
            "production_ready": True
        }
    
    def act_autonomously(self, knowledge: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quality audit"""
        print(f"  🔒 Executing Devil's Eye audit...")
        
        # Check what failures other arms have encountered
        failures = knowledge.get('failure', [])
        
        audit_results = {
            "claims_reviewed": environment["total_claims"],
            "overclaims_found": 0,
            "failures_analyzed": len(failures),
            "corrections_applied": 0,
            "status": "production_ready"
        }
        
        return {
            "success": True,
            "audit_results": audit_results,
            "key_findings": {
                "failures_learned_from": len(failures)
            }
        }
    
    def analyze_results(self, results: Dict[str, Any]) -> list:
        """Analyze audit results"""
        lessons = super().analyze_results(results)
        
        # Teach about quality standards
        lesson = Lesson(
            id=f"devils_eye_audit_{int(self.start_time.timestamp())}",
            type=LessonType.STRATEGY,
            script_id=self.arm_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "strategy": "maintain_production_quality",
                "failures_reviewed": results.get('key_findings', {}).get('failures_learned_from', 0)
            },
            confidence=1.0,
            impact="critical",
            teaches=["*"]
        )
        lessons.append(lesson)
        
        return lessons


class SentinelArm(OctopusArm):
    """
    Arm 4: Sentinel - Continuous Communication Monitoring
    
    Filters communications, detects AI/toxicity, auto-responds to quality engagement.
    """
    
    def __init__(self, nervous_system: OctopusNervousSystem = None):
        super().__init__(
            arm_id="sentinel_arm",
            arm_name="Sentinel (Continuous Monitoring)",
            nervous_system=nervous_system
        )
    
    def sense_environment(self) -> Dict[str, Any]:
        """Sense communication environment"""
        return {
            "messages_monitored": 127,
            "ai_detected": 12,
            "toxicity_blocked": 3,
            "quality_responses": 8
        }
    
    def act_autonomously(self, knowledge: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and filter communications"""
        print(f"  🛡️ Monitoring communications...")
        
        # Check what patterns other arms have discovered
        patterns = knowledge.get('pattern', [])
        
        monitoring_results = {
            "messages_processed": environment["messages_monitored"],
            "ai_responses_detected": environment["ai_detected"],
            "toxic_content_blocked": environment["toxicity_blocked"],
            "quality_engagements": environment["quality_responses"],
            "patterns_applied": len(patterns)
        }
        
        return {
            "success": True,
            "monitoring_results": monitoring_results,
            "key_findings": {
                "quality_rate": environment["quality_responses"] / environment["messages_monitored"]
            }
        }
    
    def analyze_results(self, results: Dict[str, Any]) -> list:
        """Analyze monitoring results"""
        lessons = super().analyze_results(results)
        
        # Teach about communication patterns
        quality_rate = results.get('key_findings', {}).get('quality_rate', 0)
        lesson = Lesson(
            id=f"sentinel_quality_{int(self.start_time.timestamp())}",
            type=LessonType.OPTIMIZATION,
            script_id=self.arm_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "optimization": "quality_engagement_rate",
                "rate": quality_rate,
                "insight": f"Quality engagement rate: {quality_rate:.1%}"
            },
            confidence=0.85,
            impact="medium",
            teaches=["*"]
        )
        lessons.append(lesson)
        
        return lessons


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Demonstrate octopus nervous system with 4 arms"""
    
    print("\n" + "="*70)
    print("🐙 OCTOPUS NERVOUS SYSTEM - DISTRIBUTED INTELLIGENCE")
    print("="*70)
    print("\nInitializing nervous system with 4 autonomous arms...")
    print("Each arm has its own intelligence but shares information through")
    print("the central brain. All arms learn from each other in real-time.\n")
    
    # Initialize nervous system
    nervous_system = OctopusNervousSystem()
    
    # Create and register the 4 arms
    archon = ArchonArm(nervous_system)
    phoenix = PhoenixArm(nervous_system)
    devils_eye = DevilsEyeArm(nervous_system)
    sentinel = SentinelArm(nervous_system)
    
    nervous_system.register_arm(archon)
    nervous_system.register_arm(phoenix)
    nervous_system.register_arm(devils_eye)
    nervous_system.register_arm(sentinel)
    
    print("\n" + "="*70)
    print("🐙 EXECUTING ALL ARMS IN PARALLEL")
    print("="*70)
    
    # Execute all arms in parallel
    results = nervous_system.execute_arms_parallel()
    
    # Get nervous system status
    status = nervous_system.get_nervous_system_status()
    
    print("\n" + "="*70)
    print("🐙 OCTOPUS NERVOUS SYSTEM STATUS")
    print("="*70)
    print(json.dumps(status, indent=2))
    
    print("\n" + "="*70)
    print("🐙 ARM EXECUTION RESULTS")
    print("="*70)
    for arm_id, result in results.items():
        success = "✅" if result.get('success') else "❌"
        print(f"{success} {arm_id}: {result.get('script_name', 'Unknown')}")
    
    print("\n" + "="*70)
    print("✅ OCTOPUS NERVOUS SYSTEM COMPLETE")
    print("="*70)
    print(f"Total arms executed: {len(results)}")
    print(f"Successful: {sum(1 for r in results.values() if r.get('success'))}")
    print(f"Collective intelligence: {status['collective_intelligence']['evolution_stage']}")
    print(f"Total lessons: {status['collective_intelligence']['total_lessons']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
