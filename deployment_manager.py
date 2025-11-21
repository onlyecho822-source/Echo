#!/usr/bin/env python3
"""
Echo Forge - Deployment Manager
Manages deployment and lifecycle of generated AI applications
"""

import os
import json
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DeployedApp:
    """Information about a deployed application"""
    name: str
    path: str
    status: str
    port: Optional[int] = None
    container_id: Optional[str] = None
    url: Optional[str] = None


class DeploymentManager:
    """Manages deployment of generated AI applications"""

    def __init__(self, apps_dir: str = "generated_apps"):
        self.apps_dir = apps_dir
        self.deployed_apps: List[DeployedApp] = []

    def list_generated_apps(self) -> List[Dict]:
        """List all generated applications"""
        apps = []

        if not os.path.exists(self.apps_dir):
            return apps

        for app_name in os.listdir(self.apps_dir):
            app_path = os.path.join(self.apps_dir, app_name)
            blueprint_path = os.path.join(app_path, "blueprint.json")

            if os.path.exists(blueprint_path):
                with open(blueprint_path) as f:
                    blueprint = json.load(f)
                    apps.append({
                        "name": app_name,
                        "path": app_path,
                        "blueprint": blueprint
                    })

        return apps

    def deploy_docker(self, app_name: str, port: int = 8000) -> DeployedApp:
        """Deploy an app using Docker"""
        app_path = os.path.join(self.apps_dir, app_name)

        if not os.path.exists(app_path):
            raise ValueError(f"App not found: {app_name}")

        print(f"Deploying {app_name} with Docker...")

        # Build Docker image
        print("Building Docker image...")
        build_cmd = ["docker", "build", "-t", f"echo-forge-{app_name}", app_path]
        subprocess.run(build_cmd, check=True)

        # Run container
        print(f"Starting container on port {port}...")
        run_cmd = [
            "docker", "run", "-d",
            "-p", f"{port}:8000",
            "--name", f"echo-{app_name}",
            f"echo-forge-{app_name}"
        ]
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        container_id = result.stdout.strip()

        deployed = DeployedApp(
            name=app_name,
            path=app_path,
            status="running",
            port=port,
            container_id=container_id,
            url=f"http://localhost:{port}"
        )

        self.deployed_apps.append(deployed)

        print(f"✓ Deployed: {app_name}")
        print(f"  URL: {deployed.url}")
        print(f"  Container: {container_id[:12]}")

        return deployed

    def deploy_local(self, app_name: str, background: bool = False) -> DeployedApp:
        """Deploy an app locally (without Docker)"""
        app_path = os.path.join(self.apps_dir, app_name)

        if not os.path.exists(app_path):
            raise ValueError(f"App not found: {app_name}")

        print(f"Deploying {app_name} locally...")

        # Install dependencies
        requirements_path = os.path.join(app_path, "requirements.txt")
        if os.path.exists(requirements_path):
            print("Installing dependencies...")
            subprocess.run(
                ["pip", "install", "-r", requirements_path],
                check=True,
                cwd=app_path
            )

        # Determine main file
        main_files = ["api.py", "main.py", "agent.py", "index.js"]
        main_file = None

        for filename in main_files:
            file_path = os.path.join(app_path, filename)
            if os.path.exists(file_path):
                main_file = filename
                break

        if not main_file:
            raise ValueError(f"No main file found in {app_name}")

        # Run the app
        if main_file.endswith(".py"):
            cmd = ["python", main_file]
        else:
            # Node.js
            subprocess.run(["npm", "install"], cwd=app_path, check=True)
            cmd = ["npm", "start"]

        print(f"Starting {main_file}...")

        if background:
            subprocess.Popen(cmd, cwd=app_path)
            status = "running (background)"
        else:
            print(f"\nRunning {app_name}...")
            print("Press Ctrl+C to stop\n")
            subprocess.run(cmd, cwd=app_path)
            status = "stopped"

        deployed = DeployedApp(
            name=app_name,
            path=app_path,
            status=status
        )

        if background:
            self.deployed_apps.append(deployed)

        return deployed

    def stop_deployment(self, app_name: str):
        """Stop a deployed application"""
        container_name = f"echo-{app_name}"

        print(f"Stopping {app_name}...")

        try:
            subprocess.run(
                ["docker", "stop", container_name],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["docker", "rm", container_name],
                check=True,
                capture_output=True
            )
            print(f"✓ Stopped: {app_name}")

            # Update status
            for app in self.deployed_apps:
                if app.name == app_name:
                    app.status = "stopped"

        except subprocess.CalledProcessError:
            print(f"Could not stop {app_name} (may not be running)")

    def list_deployments(self) -> List[DeployedApp]:
        """List all deployed applications"""
        return self.deployed_apps

    def get_app_info(self, app_name: str) -> Optional[Dict]:
        """Get detailed information about an app"""
        app_path = os.path.join(self.apps_dir, app_name)
        blueprint_path = os.path.join(app_path, "blueprint.json")

        if not os.path.exists(blueprint_path):
            return None

        with open(blueprint_path) as f:
            blueprint = json.load(f)

        # Get file structure
        files = []
        for root, dirs, filenames in os.walk(app_path):
            for filename in filenames:
                rel_path = os.path.relpath(
                    os.path.join(root, filename),
                    app_path
                )
                files.append(rel_path)

        return {
            "name": app_name,
            "path": app_path,
            "blueprint": blueprint,
            "files": files
        }

    def test_app(self, app_name: str):
        """Run basic tests on an application"""
        app_path = os.path.join(self.apps_dir, app_name)

        print(f"Testing {app_name}...")

        # Check if main files exist
        main_files = ["api.py", "main.py", "agent.py", "index.js"]
        found_main = False

        for filename in main_files:
            if os.path.exists(os.path.join(app_path, filename)):
                found_main = True
                print(f"  ✓ Found main file: {filename}")

        if not found_main:
            print("  ✗ No main file found")
            return False

        # Check dependencies
        if os.path.exists(os.path.join(app_path, "requirements.txt")):
            print("  ✓ Python requirements found")

        if os.path.exists(os.path.join(app_path, "package.json")):
            print("  ✓ Node.js package.json found")

        # Check Docker
        if os.path.exists(os.path.join(app_path, "Dockerfile")):
            print("  ✓ Dockerfile found")

        # Check documentation
        if os.path.exists(os.path.join(app_path, "README.md")):
            print("  ✓ README found")

        print(f"\n✓ {app_name} appears to be valid")
        return True


def main():
    """Main entry point for deployment manager"""
    import sys

    manager = DeploymentManager()

    if len(sys.argv) < 2:
        print("Echo Forge - Deployment Manager\n")
        print("Usage:")
        print("  python deployment_manager.py list               # List all apps")
        print("  python deployment_manager.py info <app>         # Get app info")
        print("  python deployment_manager.py test <app>         # Test app")
        print("  python deployment_manager.py deploy <app>       # Deploy locally")
        print("  python deployment_manager.py docker <app>       # Deploy with Docker")
        print("  python deployment_manager.py stop <app>         # Stop deployment")
        print("  python deployment_manager.py deployments        # List deployments")
        return

    command = sys.argv[1]

    if command == "list":
        apps = manager.list_generated_apps()
        print(f"\nGenerated Applications ({len(apps)}):\n")
        for app in apps:
            blueprint = app["blueprint"]
            print(f"  • {app['name']}")
            print(f"    Type: {blueprint['ai_type']}")
            print(f"    Stack: {blueprint['tech_stack']}")
            print(f"    Path: {app['path']}")
            print()

    elif command == "info":
        if len(sys.argv) < 3:
            print("Usage: python deployment_manager.py info <app_name>")
            return

        app_name = sys.argv[2]
        info = manager.get_app_info(app_name)

        if info:
            print(f"\nApp Information: {app_name}\n")
            print(f"Path: {info['path']}")
            print(f"Type: {info['blueprint']['ai_type']}")
            print(f"Stack: {info['blueprint']['tech_stack']}")
            print(f"\nFeatures:")
            for feature in info['blueprint']['features']:
                print(f"  - {feature}")
            print(f"\nFiles ({len(info['files'])}):")
            for file in info['files']:
                print(f"  - {file}")
        else:
            print(f"App not found: {app_name}")

    elif command == "test":
        if len(sys.argv) < 3:
            print("Usage: python deployment_manager.py test <app_name>")
            return

        app_name = sys.argv[2]
        manager.test_app(app_name)

    elif command == "deploy":
        if len(sys.argv) < 3:
            print("Usage: python deployment_manager.py deploy <app_name>")
            return

        app_name = sys.argv[2]
        background = "--background" in sys.argv
        manager.deploy_local(app_name, background=background)

    elif command == "docker":
        if len(sys.argv) < 3:
            print("Usage: python deployment_manager.py docker <app_name> [port]")
            return

        app_name = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        manager.deploy_docker(app_name, port=port)

    elif command == "stop":
        if len(sys.argv) < 3:
            print("Usage: python deployment_manager.py stop <app_name>")
            return

        app_name = sys.argv[2]
        manager.stop_deployment(app_name)

    elif command == "deployments":
        deployments = manager.list_deployments()
        if deployments:
            print(f"\nActive Deployments ({len(deployments)}):\n")
            for app in deployments:
                print(f"  • {app.name}")
                print(f"    Status: {app.status}")
                if app.url:
                    print(f"    URL: {app.url}")
                if app.container_id:
                    print(f"    Container: {app.container_id[:12]}")
                print()
        else:
            print("\nNo active deployments")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
