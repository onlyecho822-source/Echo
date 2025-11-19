#!/usr/bin/env python3
"""
Echobaby - Independent AI Assistant Framework
A local, configurable AI assistant that solves real problems.

Author: Echo Civilization Framework
Version: 1.0.0
"""

import asyncio
import json
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class EchoBabyConfig:
    """Configuration manager for Echobaby with customizable ethics and behavior."""

    DEFAULT_CONFIG = {
        "name": "Echobaby",
        "version": "1.0.0",
        "ethics": {
            "transparency": True,
            "user_privacy": True,
            "honest_responses": True,
            "harm_prevention": True,
            "user_autonomy": True
        },
        "behavior": {
            "response_timeout": 30,
            "max_retries": 3,
            "verbose_logging": False,
            "save_history": True,
            "max_history_size": 1000
        },
        "capabilities": {
            "file_operations": True,
            "system_commands": False,
            "web_access": False,
            "code_execution": True
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.echobaby_config.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    return self._merge_configs(self.DEFAULT_CONFIG.copy(), user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Warning] Could not load config: {e}. Using defaults.")
        return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base

    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"[Info] Configuration saved to {self.config_path}")
        except IOError as e:
            print(f"[Error] Could not save config: {e}")

    def get(self, *keys, default=None):
        """Get a nested configuration value."""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, value: Any, *keys):
        """Set a nested configuration value."""
        if not keys:
            return
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value


class TaskExecutor:
    """Executes tasks with timeout protection to prevent freezing."""

    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def execute_with_timeout(
        self,
        func: Callable,
        *args,
        timeout: Optional[int] = None,
        task_name: str = "unnamed"
    ) -> Any:
        """Execute a function with timeout protection."""
        timeout = timeout or self.default_timeout

        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(*args), timeout=timeout)
            else:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(self.executor, func, *args),
                    timeout=timeout
                )
            return {"success": True, "result": result, "task": task_name}
        except asyncio.TimeoutError:
            return {"success": False, "error": f"Task '{task_name}' timed out after {timeout}s", "task": task_name}
        except Exception as e:
            return {"success": False, "error": str(e), "task": task_name}

    def shutdown(self):
        """Clean shutdown of executor."""
        self.executor.shutdown(wait=False)


class ConversationHistory:
    """Manages conversation history with size limits."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.history: List[Dict[str, Any]] = []
        self.history_file = os.path.expanduser("~/.echobaby_history.json")

    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.history.append(entry)

        # Trim if exceeds max size
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size:]

    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent history entries."""
        return self.history[-count:]

    def save(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"[Warning] Could not save history: {e}")

    def load(self):
        """Load history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []

    def clear(self):
        """Clear conversation history."""
        self.history = []


class ProblemSolver:
    """Core problem-solving engine with various capabilities."""

    def __init__(self, config: EchoBabyConfig):
        self.config = config

    async def analyze_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze a problem and suggest approaches."""
        analysis = {
            "problem": problem,
            "type": self._classify_problem(problem),
            "complexity": self._estimate_complexity(problem),
            "suggested_approaches": [],
            "required_resources": []
        }

        # Add approaches based on problem type
        problem_lower = problem.lower()

        if any(word in problem_lower for word in ["file", "read", "write", "save", "load"]):
            analysis["suggested_approaches"].append("File operation task")
            analysis["required_resources"].append("filesystem access")

        if any(word in problem_lower for word in ["calculate", "compute", "math", "number"]):
            analysis["suggested_approaches"].append("Mathematical computation")
            analysis["required_resources"].append("calculation engine")

        if any(word in problem_lower for word in ["search", "find", "locate", "query"]):
            analysis["suggested_approaches"].append("Search/query operation")
            analysis["required_resources"].append("search capability")

        if any(word in problem_lower for word in ["code", "program", "script", "function"]):
            analysis["suggested_approaches"].append("Code generation/analysis")
            analysis["required_resources"].append("code execution")

        if any(word in problem_lower for word in ["organize", "sort", "arrange", "structure"]):
            analysis["suggested_approaches"].append("Data organization")
            analysis["required_resources"].append("data processing")

        if not analysis["suggested_approaches"]:
            analysis["suggested_approaches"].append("General reasoning and analysis")

        return analysis

    def _classify_problem(self, problem: str) -> str:
        """Classify the type of problem."""
        problem_lower = problem.lower()

        if any(word in problem_lower for word in ["error", "bug", "fix", "broken"]):
            return "debugging"
        elif any(word in problem_lower for word in ["create", "make", "build", "generate"]):
            return "creation"
        elif any(word in problem_lower for word in ["explain", "what", "how", "why"]):
            return "explanation"
        elif any(word in problem_lower for word in ["optimize", "improve", "faster", "better"]):
            return "optimization"
        else:
            return "general"

    def _estimate_complexity(self, problem: str) -> str:
        """Estimate problem complexity."""
        word_count = len(problem.split())

        if word_count < 10:
            return "simple"
        elif word_count < 30:
            return "moderate"
        else:
            return "complex"

    async def solve_math(self, expression: str) -> Dict[str, Any]:
        """Safely evaluate mathematical expressions."""
        try:
            # Only allow safe math operations
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return {"success": False, "error": "Invalid characters in expression"}

            result = eval(expression, {"__builtins__": {}}, {})
            return {"success": True, "result": result, "expression": expression}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read a file safely."""
        if not self.config.get("capabilities", "file_operations"):
            return {"success": False, "error": "File operations disabled"}

        try:
            path = Path(filepath).expanduser()
            if not path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}

            content = path.read_text()
            return {
                "success": True,
                "content": content,
                "filepath": str(path),
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write to a file safely."""
        if not self.config.get("capabilities", "file_operations"):
            return {"success": False, "error": "File operations disabled"}

        try:
            path = Path(filepath).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return {
                "success": True,
                "filepath": str(path),
                "bytes_written": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_directory(self, dirpath: str = ".") -> Dict[str, Any]:
        """List directory contents."""
        if not self.config.get("capabilities", "file_operations"):
            return {"success": False, "error": "File operations disabled"}

        try:
            path = Path(dirpath).expanduser()
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {dirpath}"}

            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })

            return {"success": True, "path": str(path), "items": items}
        except Exception as e:
            return {"success": False, "error": str(e)}


class Echobaby:
    """Main Echobaby AI Assistant class."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = EchoBabyConfig(config_path)
        self.executor = TaskExecutor(self.config.get("behavior", "response_timeout", default=30))
        self.history = ConversationHistory(self.config.get("behavior", "max_history_size", default=1000))
        self.solver = ProblemSolver(self.config)
        self.running = False

        # Load history if enabled
        if self.config.get("behavior", "save_history"):
            self.history.load()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n[Echobaby] Shutting down gracefully...")
        self.shutdown()
        sys.exit(0)

    def shutdown(self):
        """Clean shutdown of all components."""
        self.running = False
        self.executor.shutdown()
        if self.config.get("behavior", "save_history"):
            self.history.save()
        self.config.save()
        print("[Echobaby] Shutdown complete.")

    async def process_command(self, command: str) -> str:
        """Process a user command and return response."""
        command = command.strip()

        # Handle special commands
        if command.startswith("/"):
            return await self._handle_special_command(command)

        # Log to history
        self.history.add("user", command)

        # Analyze and respond
        analysis = await self.solver.analyze_problem(command)

        # Generate response based on analysis
        response = await self._generate_response(command, analysis)

        # Log response
        self.history.add("assistant", response, {"analysis": analysis})

        return response

    async def _handle_special_command(self, command: str) -> str:
        """Handle special slash commands."""
        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "help":
            return self._get_help()
        elif cmd == "config":
            return self._show_config()
        elif cmd == "history":
            return self._show_history()
        elif cmd == "clear":
            self.history.clear()
            return "History cleared."
        elif cmd == "status":
            return self._get_status()
        elif cmd == "math":
            result = await self.solver.solve_math(args)
            if result["success"]:
                return f"Result: {result['result']}"
            else:
                return f"Error: {result['error']}"
        elif cmd == "read":
            result = await self.solver.read_file(args)
            if result["success"]:
                return f"File: {result['filepath']}\n\n{result['content']}"
            else:
                return f"Error: {result['error']}"
        elif cmd == "ls":
            result = await self.solver.list_directory(args or ".")
            if result["success"]:
                output = f"Directory: {result['path']}\n\n"
                for item in result["items"]:
                    icon = "[D]" if item["type"] == "directory" else "[F]"
                    size = f" ({item['size']} bytes)" if item['size'] else ""
                    output += f"  {icon} {item['name']}{size}\n"
                return output
            else:
                return f"Error: {result['error']}"
        elif cmd == "quit" or cmd == "exit":
            self.shutdown()
            return "Goodbye!"
        else:
            return f"Unknown command: /{cmd}. Type /help for available commands."

    def _get_help(self) -> str:
        """Return help text."""
        return """
Echobaby - Independent AI Assistant
====================================

COMMANDS:
  /help      - Show this help message
  /config    - Show current configuration
  /history   - Show conversation history
  /clear     - Clear conversation history
  /status    - Show system status
  /math <expr> - Evaluate math expression
  /read <file> - Read a file
  /ls [path]   - List directory contents
  /quit      - Exit Echobaby

USAGE:
  Just type your problem or question and press Enter.
  Echobaby will analyze and respond accordingly.

CONFIGURATION:
  Edit ~/.echobaby_config.json to customize behavior.
"""

    def _show_config(self) -> str:
        """Show current configuration."""
        return f"Current Configuration:\n{json.dumps(self.config.config, indent=2)}"

    def _show_history(self) -> str:
        """Show recent conversation history."""
        recent = self.history.get_recent(10)
        if not recent:
            return "No conversation history."

        output = "Recent History:\n\n"
        for entry in recent:
            timestamp = entry["timestamp"][:19]
            role = entry["role"].upper()
            content = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
            output += f"[{timestamp}] {role}: {content}\n"

        return output

    def _get_status(self) -> str:
        """Get system status."""
        return f"""
Echobaby Status
===============
Name: {self.config.get("name")}
Version: {self.config.get("version")}
Running: {self.running}
History entries: {len(self.history.history)}
Config file: {self.config.config_path}
"""

    async def _generate_response(self, command: str, analysis: Dict) -> str:
        """Generate a response based on the command and analysis."""
        problem_type = analysis.get("type", "general")
        complexity = analysis.get("complexity", "moderate")
        approaches = analysis.get("suggested_approaches", [])

        response = f"I've analyzed your request.\n\n"
        response += f"Problem Type: {problem_type}\n"
        response += f"Complexity: {complexity}\n"

        if approaches:
            response += f"Suggested Approaches:\n"
            for approach in approaches:
                response += f"  - {approach}\n"

        response += f"\nHow would you like me to proceed? You can:\n"
        response += f"  - Ask me to elaborate on any approach\n"
        response += f"  - Use /math for calculations\n"
        response += f"  - Use /read or /ls for file operations\n"
        response += f"  - Ask a follow-up question\n"

        return response

    async def run_interactive(self):
        """Run the interactive command loop."""
        self.running = True

        print(f"""
╔══════════════════════════════════════════╗
║       ECHOBABY v{self.config.get("version")}              ║
║   Independent AI Assistant Framework     ║
╚══════════════════════════════════════════╝

Type /help for commands or just ask me anything.
Type /quit to exit.
""")

        while self.running:
            try:
                # Use asyncio-compatible input with timeout
                user_input = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, input, "\nYou > "),
                    timeout=300  # 5 minute timeout for input
                )

                if not user_input.strip():
                    continue

                if user_input.strip().lower() in ["/quit", "/exit", "quit", "exit"]:
                    self.shutdown()
                    break

                # Process with timeout protection
                result = await self.executor.execute_with_timeout(
                    self.process_command,
                    user_input,
                    timeout=self.config.get("behavior", "response_timeout", default=30),
                    task_name="process_command"
                )

                if result["success"]:
                    print(f"\nEchobaby > {result['result']}")
                else:
                    print(f"\n[Error] {result['error']}")

            except asyncio.TimeoutError:
                print("\n[Timeout] No input received. Still here when you need me!")
            except EOFError:
                print("\n[EOF] Exiting...")
                self.shutdown()
                break
            except KeyboardInterrupt:
                continue  # Handled by signal handler


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Echobaby - Independent AI Assistant")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument("--command", "-x", help="Execute single command and exit")
    args = parser.parse_args()

    # Create Echobaby instance
    echo = Echobaby(config_path=args.config)

    if args.command:
        # Single command mode
        result = asyncio.run(echo.process_command(args.command))
        print(result)
        echo.shutdown()
    else:
        # Interactive mode
        asyncio.run(echo.run_interactive())


if __name__ == "__main__":
    main()
