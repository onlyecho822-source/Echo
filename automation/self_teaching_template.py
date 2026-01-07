#!/usr/bin/env python3
"""
Self-Teaching Script Template
Each One Teach One Architecture

This template enables any automation script to learn from collective
intelligence and teach future scripts.

Usage:
    from automation.self_teaching_template import SelfTeachingScript
    
    class MyScript(SelfTeachingScript):
        def execute_task(self, knowledge):
            # Your task logic here
            return result
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from knowledge.brain import CollectiveIntelligence, Lesson, LessonType


class SelfTeachingScript:
    """
    Base class for self-teaching automation scripts.
    
    Each script follows the pattern:
    1. LEARN: Load knowledge from collective intelligence
    2. EXECUTE: Run task with learned knowledge
    3. ANALYZE: Extract learnings from execution
    4. TEACH: Update collective intelligence
    5. EVOLVE: Contribute to system evolution
    """
    
    def __init__(self, script_id: str, script_name: str):
        """
        Initialize self-teaching script.
        
        Args:
            script_id: Unique identifier for this script
            script_name: Human-readable name
        """
        self.script_id = script_id
        self.script_name = script_name
        self.brain = CollectiveIntelligence()
        self.start_time = datetime.utcnow()
        self.knowledge = {}
        self.results = {}
        self.lessons_learned = []
    
    def learn(self, lesson_types: Optional[list] = None) -> Dict[str, Any]:
        """
        Step 1: LEARN from collective intelligence.
        
        Args:
            lesson_types: Optional filter for specific lesson types
            
        Returns:
            Relevant knowledge for this script
        """
        print(f"[{self.script_id}] LEARNING from collective intelligence...")
        
        # Get knowledge from brain
        self.knowledge = self.brain.teach(self.script_id, lesson_types)
        
        # Log what was learned
        total_lessons = sum(len(lessons) for lessons in self.knowledge.values())
        print(f"[{self.script_id}] Learned {total_lessons} lessons")
        
        for lesson_type, lessons in self.knowledge.items():
            print(f"  - {lesson_type}: {len(lessons)} lessons")
        
        return self.knowledge
    
    def execute_task(self, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: EXECUTE task with learned knowledge.
        
        This method should be overridden by subclasses.
        
        Args:
            knowledge: Knowledge learned from collective intelligence
            
        Returns:
            Task execution results
        """
        raise NotImplementedError("Subclasses must implement execute_task()")
    
    def analyze_results(self, results: Dict[str, Any]) -> list:
        """
        Step 3: ANALYZE results and extract learnings.
        
        This method should be overridden by subclasses to extract
        domain-specific learnings.
        
        Args:
            results: Results from task execution
            
        Returns:
            List of Lesson objects
        """
        # Default implementation: create basic success/failure lesson
        lessons = []
        
        if results.get('success', False):
            lesson = Lesson(
                id=f"{self.script_id}_{int(self.start_time.timestamp())}",
                type=LessonType.PATTERN,
                script_id=self.script_id,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "pattern": "task_completed_successfully",
                    "results": results
                },
                confidence=0.8,
                impact="medium",
                teaches=["*"]
            )
            lessons.append(lesson)
        else:
            lesson = Lesson(
                id=f"{self.script_id}_fail_{int(self.start_time.timestamp())}",
                type=LessonType.FAILURE,
                script_id=self.script_id,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "failure": "task_failed",
                    "error": results.get('error', 'unknown'),
                    "results": results
                },
                confidence=0.9,
                impact="high",
                teaches=["*"]
            )
            lessons.append(lesson)
        
        return lessons
    
    def teach(self, lessons: list) -> bool:
        """
        Step 4: TEACH collective intelligence with new learnings.
        
        Args:
            lessons: List of Lesson objects to teach
            
        Returns:
            True if all lessons were successfully taught
        """
        print(f"[{self.script_id}] TEACHING collective intelligence...")
        
        success = True
        for lesson in lessons:
            if self.brain.learn(lesson):
                print(f"  ✓ Taught: {lesson.type.value} - {lesson.id}")
            else:
                print(f"  ✗ Failed to teach: {lesson.id}")
                success = False
        
        return success
    
    def evolve(self) -> Dict[str, Any]:
        """
        Step 5: EVOLVE - Contribute to system evolution.
        
        Returns:
            Evolution insights
        """
        print(f"[{self.script_id}] EVOLVING collective intelligence...")
        
        evolution = self.brain.evolve()
        
        print(f"  Evolution stage: {evolution['evolution_stage']}")
        print(f"  Total lessons: {evolution['total_lessons']}")
        
        return evolution
    
    def run(self) -> Dict[str, Any]:
        """
        Main execution flow: Learn → Execute → Analyze → Teach → Evolve
        
        Returns:
            Complete execution results
        """
        print(f"\n{'='*60}")
        print(f"🧠 SELF-TEACHING SCRIPT: {self.script_name}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: LEARN
            knowledge = self.learn()
            
            # Step 2: EXECUTE
            print(f"\n[{self.script_id}] EXECUTING task...")
            self.results = self.execute_task(knowledge)
            
            # Step 3: ANALYZE
            print(f"\n[{self.script_id}] ANALYZING results...")
            self.lessons_learned = self.analyze_results(self.results)
            print(f"  Extracted {len(self.lessons_learned)} new lessons")
            
            # Step 4: TEACH
            print()
            self.teach(self.lessons_learned)
            
            # Step 5: EVOLVE
            print()
            evolution = self.evolve()
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - self.start_time).total_seconds()
            
            # Final summary
            print(f"\n{'='*60}")
            print(f"✅ COMPLETE: {self.script_name}")
            print(f"{'='*60}")
            print(f"Duration: {duration:.2f}s")
            print(f"Lessons learned: {len(self.lessons_learned)}")
            print(f"Evolution stage: {evolution['evolution_stage']}")
            print(f"{'='*60}\n")
            
            return {
                "success": True,
                "script_id": self.script_id,
                "script_name": self.script_name,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "knowledge_learned": len(sum([lessons for lessons in knowledge.values()], [])),
                "lessons_taught": len(self.lessons_learned),
                "evolution": evolution,
                "results": self.results
            }
            
        except Exception as e:
            print(f"\n❌ ERROR in {self.script_name}: {e}")
            
            # Teach failure lesson
            failure_lesson = Lesson(
                id=f"{self.script_id}_error_{int(self.start_time.timestamp())}",
                type=LessonType.FAILURE,
                script_id=self.script_id,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                confidence=1.0,
                impact="critical",
                teaches=["*"]
            )
            self.brain.learn(failure_lesson)
            
            return {
                "success": False,
                "script_id": self.script_id,
                "error": str(e),
                "error_type": type(e).__name__
            }


# Example implementation
class ExampleScript(SelfTeachingScript):
    """Example self-teaching script"""
    
    def __init__(self):
        super().__init__(
            script_id="example_script",
            script_name="Example Self-Teaching Script"
        )
    
    def execute_task(self, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Example task execution"""
        # Check if we learned anything about GitHub being fast
        github_fast = False
        if 'pattern' in knowledge:
            for lesson in knowledge['pattern']:
                if 'github_api_fastest' in lesson.get('data', {}).get('pattern', ''):
                    github_fast = True
                    print(f"  📚 Applied learning: GitHub API is fastest ({lesson['data']['latency']}ms)")
        
        # Execute task (example: just return success)
        return {
            "success": True,
            "applied_learning": github_fast,
            "message": "Task completed successfully"
        }
    
    def analyze_results(self, results: Dict[str, Any]) -> list:
        """Example result analysis"""
        lessons = super().analyze_results(results)
        
        # Add custom lesson
        if results.get('applied_learning'):
            lesson = Lesson(
                id=f"{self.script_id}_applied_{int(self.start_time.timestamp())}",
                type=LessonType.OPTIMIZATION,
                script_id=self.script_id,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "optimization": "applied_github_fast_learning",
                    "impact": "Used learned knowledge to optimize execution"
                },
                confidence=0.95,
                impact="high",
                teaches=["*"]
            )
            lessons.append(lesson)
        
        return lessons


if __name__ == "__main__":
    # Run example script
    script = ExampleScript()
    result = script.run()
    
    print("\nFinal Result:")
    print(json.dumps(result, indent=2))
