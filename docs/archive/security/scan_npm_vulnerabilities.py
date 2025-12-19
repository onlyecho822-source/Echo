#!/usr/bin/env python3
"""
NPM Vulnerability Scanner
Scans npm packages for known vulnerabilities using npm audit
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def scan_npm_vulnerabilities(project_path):
    """
    Scan npm project for vulnerabilities using npm audit
    
    Args:
        project_path: Path to the npm project directory
        
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
    
    try:
        # Run npm audit with JSON output
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse the JSON output
        audit_data = json.loads(result.stdout)
        
        # Extract vulnerabilities
        if "vulnerabilities" in audit_data:
            for package_name, vuln_info in audit_data["vulnerabilities"].items():
                if isinstance(vuln_info, dict) and "via" in vuln_info:
                    for via in vuln_info["via"]:
                        if isinstance(via, dict):
                            severity = via.get("severity", "unknown").lower()
                            vuln_entry = {
                                "package": package_name,
                                "severity": severity,
                                "title": via.get("title", "Unknown"),
                                "cve": via.get("cves", []),
                                "fix_available": vuln_info.get("fixAvailable", False),
                                "url": via.get("url", "")
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
        report["error"] = "npm audit timed out"
    except json.JSONDecodeError:
        report["error"] = "Failed to parse npm audit output"
    except Exception as e:
        report["error"] = str(e)
    
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: scan_npm_vulnerabilities.py <project_path>")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    report = scan_npm_vulnerabilities(project_path)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
