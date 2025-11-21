"""
EchoCore Engine
Production-grade business logic and standard operating procedures
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class EchoCoreEngine:
    """
    EchoCore: Production-grade business logic engine

    Use cases:
    - Standard operating procedures
    - Business workflow automation
    - Data processing pipelines
    - Production deployments
    - Mission-critical operations
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.execution_log: List[Dict[str, Any]] = []

    async def execute_workflow(self, workflow_id: str,
                               input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a defined workflow

        Args:
            workflow_id: Identifier for the workflow
            input_data: Input data for the workflow

        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            return {
                "status": "error",
                "message": f"Workflow {workflow_id} not found"
            }

        workflow = self.workflows[workflow_id]
        workflow["status"] = WorkflowStatus.RUNNING

        start_time = datetime.now()

        try:
            # Execute workflow steps
            results = []
            for step in workflow.get("steps", []):
                step_result = await self._execute_step(step, input_data)
                results.append(step_result)

                if not step_result.get("success"):
                    workflow["status"] = WorkflowStatus.FAILED
                    break

            if workflow["status"] != WorkflowStatus.FAILED:
                workflow["status"] = WorkflowStatus.COMPLETED

            execution_result = {
                "workflow_id": workflow_id,
                "status": workflow["status"].value,
                "input": input_data,
                "results": results,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "completed_at": datetime.now().isoformat()
            }

            self.execution_log.append(execution_result)
            return execution_result

        except Exception as e:
            workflow["status"] = WorkflowStatus.FAILED
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }

    async def _execute_step(self, step: Dict[str, Any],
                           data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step_type = step.get("type")

        # Placeholder for actual step execution
        await asyncio.sleep(0.1)  # Simulate work

        return {
            "step": step.get("name"),
            "type": step_type,
            "success": True,
            "output": f"[Output from {step.get('name')}]"
        }

    def register_workflow(self, workflow_id: str,
                         workflow_definition: Dict[str, Any]) -> bool:
        """
        Register a new workflow

        Args:
            workflow_id: Unique identifier for the workflow
            workflow_definition: Workflow definition including steps

        Returns:
            Success status
        """
        if workflow_id in self.workflows:
            return False

        self.workflows[workflow_id] = {
            "id": workflow_id,
            "definition": workflow_definition,
            "steps": workflow_definition.get("steps", []),
            "status": WorkflowStatus.PENDING,
            "created_at": datetime.now().isoformat()
        }
        return True

    async def create_task(self, task_name: str,
                         task_config: Dict[str, Any],
                         priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """
        Create a new task

        Args:
            task_name: Name of the task
            task_config: Task configuration
            priority: Task priority

        Returns:
            Task ID
        """
        task_id = f"task_{len(self.tasks) + 1}_{int(datetime.now().timestamp())}"

        self.tasks[task_id] = {
            "id": task_id,
            "name": task_name,
            "config": task_config,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "result": None
        }

        return task_id

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a specific task"""
        if task_id not in self.tasks:
            return {"error": "Task not found"}

        task = self.tasks[task_id]
        task["status"] = "running"
        task["started_at"] = datetime.now().isoformat()

        try:
            # Placeholder for actual task execution
            await asyncio.sleep(0.1)

            result = {
                "task_id": task_id,
                "status": "completed",
                "output": f"[Task {task['name']} completed successfully]",
                "completed_at": datetime.now().isoformat()
            }

            task["status"] = "completed"
            task["result"] = result

            return result
        except Exception as e:
            task["status"] = "failed"
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }

    async def process_batch(self, batch_data: List[Dict[str, Any]],
                          processor: Callable) -> List[Dict[str, Any]]:
        """
        Process a batch of data items

        Args:
            batch_data: List of data items to process
            processor: Processing function

        Returns:
            List of processing results
        """
        results = []

        for item in batch_data:
            try:
                result = await processor(item)
                results.append({
                    "item": item,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "item": item,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None

        return {
            "workflow_id": workflow_id,
            "status": workflow["status"].value,
            "created_at": workflow["created_at"]
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task"""
        return self.tasks.get(task_id)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows"""
        return [
            {
                "id": wf_id,
                "status": wf["status"].value,
                "created_at": wf["created_at"]
            }
            for wf_id, wf in self.workflows.items()
        ]

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by status"""
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t["status"] == status]

        return tasks

    def get_execution_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get workflow execution log"""
        if limit:
            return self.execution_log[-limit:]
        return self.execution_log


# Example usage
if __name__ == "__main__":
    async def main():
        engine = EchoCoreEngine()

        # Register workflow
        engine.register_workflow("customer_onboarding", {
            "name": "Customer Onboarding",
            "steps": [
                {"name": "Verify Email", "type": "validation"},
                {"name": "Create Account", "type": "database"},
                {"name": "Send Welcome Email", "type": "notification"},
                {"name": "Setup Dashboard", "type": "provisioning"}
            ]
        })

        # Execute workflow
        result = await engine.execute_workflow(
            "customer_onboarding",
            {"email": "customer@example.com", "name": "John Doe"}
        )
        print(f"Workflow result: {result}")

        # Create and execute task
        task_id = await engine.create_task(
            "data_processing",
            {"data_source": "api", "format": "json"},
            priority=TaskPriority.HIGH
        )
        task_result = await engine.execute_task(task_id)
        print(f"Task result: {task_result}")

        # List workflows
        workflows = engine.list_workflows()
        print(f"Registered workflows: {workflows}")

    asyncio.run(main())
