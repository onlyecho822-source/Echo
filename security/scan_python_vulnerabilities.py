#!/usr/bin/env python3
"""
Python Vulnerability Scanner
Scans Python packages for known vulnerabilities using pip-audit
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def scan_python_vulnerabilities(project_path, requirements_file="requirements.txt"):
    """
    Scan Python project for vulnerabilities using pip-audit
    
    Args:
        project_path: Path to the Python project directory
        requirements_file: Name of the requirements file
        
    Returns:
        dict: Vulnerability report with counts and details
    """
    
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "project": str(project_path),
        "vulnerabilities": {
            "critical": [],
            "high": [],
            "moderate": [],
            "low": []
        },
        "summary": {
            "critical": 0,
            "high": 0,
            "moderate": 0,
            "low": 0,
            "total": 0
        }
    }
    
    req_file_path = project_path / requirements_file
    
    if not req_file_path.exists():
        report["warning"] = f"Requirements file not found: {requirements_file}"
        return report
    
    try:
        # Run pip-audit with JSON output
        result = subprocess.run(
            ["pip-audit", "--desc", "--format", "json", "-r", str(req_file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse the JSON output
        audit_data = json.loads(result.stdout)
        
        # Extract vulnerabilities
        if "vulnerabilities" in audit_data:
            for vuln in audit_data["vulnerabilities"]:
                severity = vuln.get("severity", "unknown").lower()
                vuln_entry = {
                    "package": vuln.get("name", "Unknown"),
                    "version": vuln.get("version", "Unknown"),
                    "severity": severity,
                    "title": vuln.get("description", "Unknown"),
                    "cve": vuln.get("cve", ""),
                    "fix_version": vuln.get("fix_versions", []),
                    "url": vuln.get("advisory_url", "")
                }
                
                if severity in report["vulnerabilities"]:
                    report["vulnerabilities"][severity].append(vuln_entry)
                    report["summary"][severity] += 1
        
        # Calculate totals
        report["summary"]["total"] = sum([
            report["summary"]["critical"],
            report["summary"]["high"],
            report["summary"]["moderate"],
            report["summary"]["low"]
        ])
        
    except subprocess.TimeoutExpired:
        report["error"] = "pip-audit timed out"
    except json.JSONDecodeError:
        report["error"] = "Failed to parse pip-audit output"
    except FileNotFoundError:
        report["warning"] = "pip-audit not installed. Install with: pip install pip-audit"
    except Exception as e:
        report["error"] = str(e)
    
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: scan_python_vulnerabilities.py <project_path> [requirements_file]")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    requirements_file = sys.argv[2] if len(sys.argv) > 2 else "requirements.txt"
    
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    report = scan_python_vulnerabilities(project_path, requirements_file)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
