"""
ECHO_CORE Agent - Self-Upgrading Logic and Recursive Thinker

This agent is responsible for:
- Evaluating system performance and identifying improvements
- Recursive problem decomposition
- Strategy optimization and refinement
- Model and prompt self-improvement
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import hashlib

from echo.common.base import BaseAgent
from echo.common.events import EventBus


class EchoCore(BaseAgent):
    """Self-upgrading logic engine with recursive thinking capabilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ECHO_CORE", config)
        self.event_bus = EventBus()

        # Core state
        self.strategies: List[Dict[str, Any]] = []
        self.improvement_log: List[Dict[str, Any]] = []
        self.problem_queue: List[Dict[str, Any]] = []
        self.heuristics: Dict[str, Any] = self._load_default_heuristics()

        # Performance tracking
        self.performance_baseline = None
        self.drift_threshold = config.get("drift_threshold", 0.15) if config else 0.15

        self.logger.info("ECHO_CORE initialized - Recursive thinking engine online")

    def _load_default_heuristics(self) -> Dict[str, Any]:
        """Load default problem-solving heuristics."""
        return {
            "decomposition": {
                "max_depth": 5,
                "min_complexity": 0.3
            },
            "evaluation": {
                "success_weight": 0.6,
                "efficiency_weight": 0.3,
                "novelty_weight": 0.1
            },
            "improvement": {
                "min_gain_threshold": 0.05,
                "max_iterations": 10
            }
        }

    def run(self) -> Dict[str, Any]:
        """Execute core evaluation and improvement cycle."""
        self.prepare_run()

        results = {
            "evaluated": 0,
            "improvements_proposed": 0,
            "problems_solved": 0,
            "drift_detected": False
        }

        try:
            # Phase 1: Evaluate current state
            evaluation = self.evaluate()
            results["evaluation"] = evaluation

            # Phase 2: Check for value leaks / drift
            if self.detect_value_leak():
                results["drift_detected"] = True
                self.logger.warning("Value drift detected - initiating rebuild protocol")
                rebuild_result = self.rebuild()
                results["rebuild"] = rebuild_result

            # Phase 3: Process problem queue
            while self.problem_queue:
                problem = self.problem_queue.pop(0)
                solution = self._solve_problem(problem)
                if solution:
                    results["problems_solved"] += 1

            # Phase 4: Sharpen mind (self-improvement)
            improvements = self.sharpen_mind()
            results["improvements_proposed"] = len(improvements)

            self.complete_run(success=True)
            self.event_bus.publish("core.cycle_complete", results, self.name)

        except Exception as e:
            self.log_error(str(e))
            self.complete_run(success=False)
            results["error"] = str(e)

        return results

    def evaluate(self) -> Dict[str, Any]:
        """Evaluate system performance and state."""
        evaluation = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {},
            "recommendations": []
        }

        # Calculate performance metrics
        metrics = self._calculate_metrics()
        evaluation["metrics"] = metrics

        # Compare against baseline
        if self.performance_baseline:
            drift = self._calculate_drift(metrics, self.performance_baseline)
            evaluation["drift"] = drift

            if drift > self.drift_threshold:
                evaluation["recommendations"].append({
                    "type": "rebuild",
                    "reason": f"Performance drift {drift:.2f} exceeds threshold {self.drift_threshold}",
                    "priority": "high"
                })
        else:
            # Set initial baseline
            self.performance_baseline = metrics

        self.record_metric("evaluation_score", metrics.get("overall_score", 0))
        return evaluation

    def detect_value_leak(self) -> bool:
        """Detect if system is experiencing logic drift or value degradation."""
        if not self.performance_baseline:
            return False

        current_metrics = self._calculate_metrics()
        drift = self._calculate_drift(current_metrics, self.performance_baseline)

        self.logger.debug(f"Current drift level: {drift:.4f}")
        return drift > self.drift_threshold

    def rebuild(self) -> Dict[str, Any]:
        """Rebuild and recalibrate core logic."""
        self.logger.info("Initiating rebuild protocol")

        rebuild_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "actions": []
        }

        # Reset heuristics to optimal values
        self.heuristics = self._load_default_heuristics()
        rebuild_result["actions"].append("Reset heuristics to defaults")

        # Clear error accumulation
        error_count = len(self.state["errors"])
        self.state["errors"] = []
        rebuild_result["actions"].append(f"Cleared {error_count} accumulated errors")

        # Re-establish baseline
        self.performance_baseline = self._calculate_metrics()
        rebuild_result["actions"].append("Re-established performance baseline")

        # Log improvement
        self.improvement_log.append({
            "type": "rebuild",
            "timestamp": datetime.utcnow().isoformat(),
            "result": rebuild_result
        })

        self.event_bus.publish("core.rebuild_complete", rebuild_result, self.name)
        return rebuild_result

    def sharpen_mind(self) -> List[Dict[str, Any]]:
        """Self-improve models, prompts, and strategies."""
        improvements = []

        # Analyze strategy effectiveness
        if self.strategies:
            for strategy in self.strategies:
                if strategy.get("success_rate", 0) < 0.5:
                    improvement = {
                        "target": strategy["name"],
                        "type": "strategy_optimization",
                        "proposed_change": "Adjust parameters based on failure patterns",
                        "expected_gain": 0.1
                    }
                    improvements.append(improvement)

        # Analyze heuristic performance
        heuristic_review = self._review_heuristics()
        if heuristic_review["needs_update"]:
            improvements.append({
                "target": "heuristics",
                "type": "heuristic_refinement",
                "proposed_change": heuristic_review["recommendations"],
                "expected_gain": heuristic_review["expected_improvement"]
            })

        self.logger.info(f"Proposed {len(improvements)} self-improvements")
        return improvements

    def add_problem(self, problem: Dict[str, Any]) -> str:
        """Add a problem to the processing queue."""
        problem_id = hashlib.md5(
            json.dumps(problem, sort_keys=True).encode()
        ).hexdigest()[:8]

        problem["id"] = problem_id
        problem["added_at"] = datetime.utcnow().isoformat()
        problem["status"] = "queued"

        self.problem_queue.append(problem)
        self.logger.info(f"Problem {problem_id} added to queue")

        return problem_id

    def _solve_problem(self, problem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Solve a problem using recursive decomposition."""
        self.logger.debug(f"Solving problem: {problem.get('id', 'unknown')}")

        # Decompose if complex
        complexity = problem.get("complexity", 0.5)
        if complexity > self.heuristics["decomposition"]["min_complexity"]:
            sub_problems = self._decompose_problem(problem)
            solutions = [self._solve_problem(sp) for sp in sub_problems]
            return self._merge_solutions(solutions)

        # Direct solution for simple problems
        solution = {
            "problem_id": problem.get("id"),
            "solved_at": datetime.utcnow().isoformat(),
            "approach": "direct",
            "result": "simulated_solution"
        }

        return solution

    def _decompose_problem(self, problem: Dict[str, Any], depth: int = 0) -> List[Dict[str, Any]]:
        """Decompose a complex problem into sub-problems."""
        max_depth = self.heuristics["decomposition"]["max_depth"]

        if depth >= max_depth:
            return [problem]

        # Simulate decomposition
        sub_problems = [
            {
                "id": f"{problem.get('id', 'p')}_{i}",
                "parent": problem.get("id"),
                "complexity": problem.get("complexity", 0.5) / 2,
                "description": f"Sub-problem {i} of {problem.get('id')}"
            }
            for i in range(2)
        ]

        return sub_problems

    def _merge_solutions(self, solutions: List[Optional[Dict[str, Any]]]) -> Dict[str, Any]:
        """Merge sub-problem solutions into a unified solution."""
        valid_solutions = [s for s in solutions if s is not None]

        return {
            "type": "merged",
            "components": len(valid_solutions),
            "solved_at": datetime.utcnow().isoformat()
        }

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics."""
        return {
            "run_count": self.state["run_count"],
            "error_rate": len(self.state["errors"]) / max(self.state["run_count"], 1),
            "problems_processed": len(self.improvement_log),
            "overall_score": 1.0 - (len(self.state["errors"]) / max(self.state["run_count"], 1) * 0.5)
        }

    def _calculate_drift(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> float:
        """Calculate drift between current and baseline metrics."""
        if not baseline:
            return 0.0

        diffs = []
        for key in baseline:
            if key in current and isinstance(baseline[key], (int, float)):
                baseline_val = baseline[key] if baseline[key] != 0 else 0.001
                diff = abs(current[key] - baseline[key]) / abs(baseline_val)
                diffs.append(diff)

        return sum(diffs) / len(diffs) if diffs else 0.0

    def _review_heuristics(self) -> Dict[str, Any]:
        """Review and propose heuristic updates."""
        return {
            "needs_update": False,
            "recommendations": [],
            "expected_improvement": 0.0
        }

    def get_status(self) -> Dict[str, Any]:
        """Return current agent status."""
        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": self.state["status"],
            "run_count": self.state["run_count"],
            "last_run": self.state["last_run"],
            "error_count": len(self.state["errors"]),
            "problems_queued": len(self.problem_queue),
            "strategies_active": len(self.strategies),
            "improvements_logged": len(self.improvement_log)
        }
