#!/usr/bin/env python3
"""
GitHub Dependabot Vulnerability Scanner
Fetches vulnerability data from GitHub's Dependabot API
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def scan_github_vulnerabilities(repo_owner, repo_name):
    """
    Scan GitHub repository for vulnerabilities using GitHub CLI
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        
    Returns:
        dict: Vulnerability report with counts and details
    """
    
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "repository": f"{repo_owner}/{repo_name}",
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
        # Use GitHub CLI to get security advisories
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_owner}/{repo_name}/security/advisories", "--paginate"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            report["warning"] = "GitHub CLI not authenticated or repository not accessible"
            return report
        
        # Parse the JSON output
        advisories = json.loads(result.stdout)
        
        # Extract vulnerabilities
        if isinstance(advisories, list):
            for advisory in advisories:
                severity = advisory.get("severity", "unknown").lower()
                vuln_entry = {
                    "title": advisory.get("summary", "Unknown"),
                    "severity": severity,
                    "cve": advisory.get("cve_id", ""),
                    "ghsa": advisory.get("ghsa_id", ""),
                    "state": advisory.get("state", "open"),
                    "url": advisory.get("html_url", ""),
                    "published_at": advisory.get("published_at", "")
                }
                
                if severity in report["vulnerabilities"] and advisory.get("state") == "open":
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
        report["error"] = "GitHub API request timed out"
    except json.JSONDecodeError:
        report["error"] = "Failed to parse GitHub API response"
    except Exception as e:
        report["error"] = str(e)
    
    return report

def main():
    if len(sys.argv) < 3:
        print("Usage: scan_github_vulnerabilities.py <repo_owner> <repo_name>")
        sys.exit(1)
    
    repo_owner = sys.argv[1]
    repo_name = sys.argv[2]
    
    report = scan_github_vulnerabilities(repo_owner, repo_name)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
