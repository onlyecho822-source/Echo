#!/usr/bin/env python3
"""
Collective Intelligence Brain - Self-Teaching Automation System
Each One Teach One Architecture

This system enables GitHub Actions scripts to learn from each other,
building collective intelligence that improves over time.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LessonType(Enum):
    """Types of lessons the system can learn"""
    PATTERN = "pattern"          # Successful patterns
    FAILURE = "failure"          # What went wrong
    OPTIMIZATION = "optimization"  # Performance improvements
    DISCOVERY = "discovery"      # New insights
    STRATEGY = "strategy"        # Strategic decisions


@dataclass
class Lesson:
    """A single lesson learned by the system"""
    id: str
    type: LessonType
    script_id: str
    timestamp: str
    data: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    impact: str  # "low", "medium", "high", "critical"
    teaches: List[str]  # Which scripts should learn this
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            **asdict(self),
            'type': self.type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Lesson':
        """Create from dictionary"""
        data['type'] = LessonType(data['type'])
        return cls(**data)


class CollectiveIntelligence:
    """
    The Brain - Collective intelligence system that enables
    self-teaching automation through shared knowledge.
    """
    
    def __init__(self, knowledge_dir: str = "/home/ubuntu/Echo/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge stores
        self.patterns_file = self.knowledge_dir / "patterns.json"
        self.failures_file = self.knowledge_dir / "failures.json"
        self.optimizations_file = self.knowledge_dir / "optimizations.json"
        self.discoveries_file = self.knowledge_dir / "discoveries.json"
        self.strategies_file = self.knowledge_dir / "strategies.json"
        self.evolution_log = self.knowledge_dir / "evolution.log"
        
        # Initialize if needed
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize empty knowledge base if it doesn't exist"""
        for file in [self.patterns_file, self.failures_file, 
                     self.optimizations_file, self.discoveries_file,
                     self.strategies_file]:
            if not file.exists():
                file.write_text(json.dumps([], indent=2))
        
        if not self.evolution_log.exists():
            self.evolution_log.write_text("")
    
    def learn(self, lesson: Lesson) -> bool:
        """
        Learn a new lesson and store it in collective intelligence.
        
        Args:
            lesson: The lesson to learn
            
        Returns:
            True if lesson was successfully learned
        """
        try:
            # Determine which knowledge store to update
            if lesson.type == LessonType.PATTERN:
                target_file = self.patterns_file
            elif lesson.type == LessonType.FAILURE:
                target_file = self.failures_file
            elif lesson.type == LessonType.OPTIMIZATION:
                target_file = self.optimizations_file
            elif lesson.type == LessonType.DISCOVERY:
                target_file = self.discoveries_file
            elif lesson.type == LessonType.STRATEGY:
                target_file = self.strategies_file
            else:
                return False
            
            # Load existing lessons
            lessons = json.loads(target_file.read_text())
            
            # Add new lesson
            lessons.append(lesson.to_dict())
            
            # Save updated lessons
            target_file.write_text(json.dumps(lessons, indent=2))
            
            # Log evolution
            self._log_evolution(f"Learned: {lesson.type.value} from {lesson.script_id}")
            
            return True
            
        except Exception as e:
            print(f"Error learning lesson: {e}")
            return False
    
    def teach(self, script_id: str, lesson_types: Optional[List[LessonType]] = None) -> Dict[str, List[Dict]]:
        """
        Teach a script by providing relevant knowledge.
        
        Args:
            script_id: The script requesting knowledge
            lesson_types: Optional filter for specific lesson types
            
        Returns:
            Dictionary of relevant lessons by type
        """
        knowledge = {}
        
        # Determine which lesson types to include
        if lesson_types is None:
            lesson_types = list(LessonType)
        
        # Gather relevant lessons
        for lesson_type in lesson_types:
            if lesson_type == LessonType.PATTERN:
                lessons = self._load_lessons(self.patterns_file)
            elif lesson_type == LessonType.FAILURE:
                lessons = self._load_lessons(self.failures_file)
            elif lesson_type == LessonType.OPTIMIZATION:
                lessons = self._load_lessons(self.optimizations_file)
            elif lesson_type == LessonType.DISCOVERY:
                lessons = self._load_lessons(self.discoveries_file)
            elif lesson_type == LessonType.STRATEGY:
                lessons = self._load_lessons(self.strategies_file)
            else:
                continue
            
            # Filter lessons relevant to this script
            relevant_lessons = [
                lesson for lesson in lessons
                if script_id in lesson.get('teaches', []) or '*' in lesson.get('teaches', [])
            ]
            
            if relevant_lessons:
                knowledge[lesson_type.value] = relevant_lessons
        
        # Log teaching
        self._log_evolution(f"Taught: {script_id} ({len(knowledge)} lesson types)")
        
        return knowledge
    
    def _load_lessons(self, file_path: Path) -> List[Dict]:
        """Load lessons from a file"""
        try:
            return json.loads(file_path.read_text())
        except Exception as e:
            print(f"Error loading lessons from {file_path}: {e}")
            return []
    
    def evolve(self) -> Dict[str, Any]:
        """
        Analyze collective intelligence and identify emergent patterns.
        
        Returns:
            Evolution insights
        """
        insights = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_lessons": 0,
            "patterns_discovered": 0,
            "failures_avoided": 0,
            "optimizations_applied": 0,
            "new_discoveries": 0,
            "strategic_insights": 0,
            "evolution_stage": "emerging"
        }
        
        # Count lessons
        for file in [self.patterns_file, self.failures_file, 
                     self.optimizations_file, self.discoveries_file,
                     self.strategies_file]:
            lessons = self._load_lessons(file)
            insights["total_lessons"] += len(lessons)
            
            if file == self.patterns_file:
                insights["patterns_discovered"] = len(lessons)
            elif file == self.failures_file:
                insights["failures_avoided"] = len(lessons)
            elif file == self.optimizations_file:
                insights["optimizations_applied"] = len(lessons)
            elif file == self.discoveries_file:
                insights["new_discoveries"] = len(lessons)
            elif file == self.strategies_file:
                insights["strategic_insights"] = len(lessons)
        
        # Determine evolution stage
        total = insights["total_lessons"]
        if total == 0:
            insights["evolution_stage"] = "nascent"
        elif total < 10:
            insights["evolution_stage"] = "emerging"
        elif total < 50:
            insights["evolution_stage"] = "learning"
        elif total < 100:
            insights["evolution_stage"] = "intelligent"
        else:
            insights["evolution_stage"] = "conscious"
        
        # Log evolution
        self._log_evolution(f"Evolution: {insights['evolution_stage']} ({total} lessons)")
        
        return insights
    
    def _log_evolution(self, message: str):
        """Log evolution events"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.evolution_log, 'a') as f:
            f.write(log_entry)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collective intelligence"""
        return {
            "patterns": len(self._load_lessons(self.patterns_file)),
            "failures": len(self._load_lessons(self.failures_file)),
            "optimizations": len(self._load_lessons(self.optimizations_file)),
            "discoveries": len(self._load_lessons(self.discoveries_file)),
            "strategies": len(self._load_lessons(self.strategies_file)),
            "evolution": self.evolve()
        }


# Example usage
if __name__ == "__main__":
    # Initialize brain
    brain = CollectiveIntelligence()
    
    # Example: Learn a pattern
    lesson = Lesson(
        id="github_fastest_001",
        type=LessonType.PATTERN,
        script_id="phoenix_global_scan",
        timestamp=datetime.utcnow().isoformat(),
        data={
            "pattern": "github_api_fastest",
            "latency": 64.51,
            "insight": "GitHub API consistently fastest endpoint"
        },
        confidence=0.95,
        impact="high",
        teaches=["*"]  # Teach all scripts
    )
    
    brain.learn(lesson)
    
    # Example: Teach a script
    knowledge = brain.teach("sentinel_monitoring")
    print(f"Knowledge for sentinel_monitoring: {json.dumps(knowledge, indent=2)}")
    
    # Example: Get evolution summary
    summary = brain.get_summary()
    print(f"\nCollective Intelligence Summary:")
    print(json.dumps(summary, indent=2))
