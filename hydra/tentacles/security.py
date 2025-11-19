"""
Cybersecurity Tentacles
=======================

Specialized tentacles for security operations:
- Reconnaissance
- Vulnerability scanning
- Forensics
- Auditing
- Exploit development
- Threat intelligence
"""

from typing import Any, Dict, List, Optional, Set
import asyncio
import subprocess
import json
import re
from datetime import datetime

from .base import Tentacle, TentacleCapability
from ..config import AIModelConfig


class ReconTentacle(Tentacle):
    """
    Reconnaissance Tentacle

    Performs information gathering and OSINT operations.
    """

    def __init__(self, tentacle_id: str = "recon"):
        capabilities = {
            TentacleCapability.OSINT,
            TentacleCapability.PORT_SCAN,
            TentacleCapability.SERVICE_ENUM,
            TentacleCapability.DNS_ENUM,
            TentacleCapability.WEB_RECON,
        }

        super().__init__(
            tentacle_id=tentacle_id,
            name="Reconnaissance",
            capabilities=capabilities
        )

        self._tools_available = {}

    async def _setup_client(self) -> None:
        """Check available recon tools"""
        tools = ["nmap", "whois", "dig", "host", "curl", "nikto", "dirb"]

        for tool in tools:
            try:
                proc = await asyncio.create_subprocess_exec(
                    "which", tool,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.wait()
                self._tools_available[tool] = proc.returncode == 0
            except Exception:
                self._tools_available[tool] = False

        self.logger.info(f"Available tools: {[t for t, v in self._tools_available.items() if v]}")

    async def _cleanup_client(self) -> None:
        """Cleanup"""
        pass

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Perform reconnaissance"""
        payload = task.payload if hasattr(task, 'payload') else task

        recon_type = payload.get("type", "basic")
        target = payload.get("target", "")

        if not target:
            return {"error": "No target specified", "success": False}

        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "findings": []
        }

        if recon_type == "dns":
            results["findings"].append(await self._dns_recon(target))
        elif recon_type == "port":
            results["findings"].append(await self._port_scan(target))
        elif recon_type == "whois":
            results["findings"].append(await self._whois_lookup(target))
        elif recon_type == "basic":
            # Run all basic recon
            results["findings"] = await asyncio.gather(
                self._dns_recon(target),
                self._whois_lookup(target),
                return_exceptions=True
            )

        return results

    async def _dns_recon(self, target: str) -> Dict[str, Any]:
        """Perform DNS reconnaissance"""
        if not self._tools_available.get("dig"):
            return {"type": "dns", "error": "dig not available"}

        try:
            proc = await asyncio.create_subprocess_exec(
                "dig", "+short", target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            return {
                "type": "dns",
                "records": stdout.decode().strip().split("\n"),
                "success": True
            }
        except Exception as e:
            return {"type": "dns", "error": str(e)}

    async def _port_scan(self, target: str) -> Dict[str, Any]:
        """Perform port scan (requires authorization)"""
        if not self._tools_available.get("nmap"):
            return {"type": "port_scan", "error": "nmap not available"}

        # Quick scan of common ports only
        try:
            proc = await asyncio.create_subprocess_exec(
                "nmap", "-F", "--top-ports", "100", "-T4", target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            return {
                "type": "port_scan",
                "output": stdout.decode(),
                "success": True
            }
        except Exception as e:
            return {"type": "port_scan", "error": str(e)}

    async def _whois_lookup(self, target: str) -> Dict[str, Any]:
        """Perform WHOIS lookup"""
        if not self._tools_available.get("whois"):
            return {"type": "whois", "error": "whois not available"}

        try:
            proc = await asyncio.create_subprocess_exec(
                "whois", target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            return {
                "type": "whois",
                "output": stdout.decode()[:2000],  # Truncate large output
                "success": True
            }
        except Exception as e:
            return {"type": "whois", "error": str(e)}


class VulnScanTentacle(Tentacle):
    """
    Vulnerability Scanning Tentacle

    Identifies security vulnerabilities in targets.
    """

    def __init__(self, tentacle_id: str = "vulnscan"):
        capabilities = {
            TentacleCapability.VULN_SCAN,
            TentacleCapability.CVE_LOOKUP,
        }

        super().__init__(
            tentacle_id=tentacle_id,
            name="Vulnerability Scanner",
            capabilities=capabilities
        )

    async def _setup_client(self) -> None:
        """Setup vulnerability scanning tools"""
        # Check for common vuln scanners
        pass

    async def _cleanup_client(self) -> None:
        """Cleanup"""
        pass

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Perform vulnerability scanning"""
        payload = task.payload if hasattr(task, 'payload') else task

        scan_type = payload.get("type", "cve_lookup")
        target = payload.get("target", "")

        if scan_type == "cve_lookup":
            return await self._cve_lookup(payload.get("cve_id", ""))
        elif scan_type == "service_vuln":
            return await self._check_service_vulns(target)

        return {"error": "Unknown scan type"}

    async def _cve_lookup(self, cve_id: str) -> Dict[str, Any]:
        """Look up CVE details"""
        # In production, this would query NVD or similar
        return {
            "cve_id": cve_id,
            "status": "lookup_requires_api",
            "message": "Configure NVD API for CVE lookups"
        }

    async def _check_service_vulns(self, target: str) -> Dict[str, Any]:
        """Check for known service vulnerabilities"""
        return {
            "target": target,
            "vulnerabilities": [],
            "scan_type": "service_vulnerability",
            "timestamp": datetime.utcnow().isoformat()
        }


class ForensicsTentacle(Tentacle):
    """
    Digital Forensics Tentacle

    Performs forensic analysis on digital evidence.
    """

    def __init__(self, tentacle_id: str = "forensics"):
        capabilities = {
            TentacleCapability.DISK_FORENSICS,
            TentacleCapability.MEMORY_FORENSICS,
            TentacleCapability.NETWORK_FORENSICS,
            TentacleCapability.TIMELINE_ANALYSIS,
            TentacleCapability.LOG_ANALYSIS,
            TentacleCapability.MALWARE_ANALYSIS,
        }

        super().__init__(
            tentacle_id=tentacle_id,
            name="Digital Forensics",
            capabilities=capabilities
        )

    async def _setup_client(self) -> None:
        """Setup forensics tools"""
        pass

    async def _cleanup_client(self) -> None:
        """Cleanup"""
        pass

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Perform forensic analysis"""
        payload = task.payload if hasattr(task, 'payload') else task

        analysis_type = payload.get("type", "log_analysis")

        if analysis_type == "log_analysis":
            return await self._analyze_logs(payload.get("logs", []))
        elif analysis_type == "timeline":
            return await self._build_timeline(payload.get("events", []))
        elif analysis_type == "hash_check":
            return await self._check_file_hash(payload.get("file_path", ""))

        return {"error": "Unknown analysis type"}

    async def _analyze_logs(self, logs: List[str]) -> Dict[str, Any]:
        """Analyze log entries for suspicious activity"""
        suspicious_patterns = [
            r"failed.*login",
            r"unauthorized",
            r"permission denied",
            r"error.*authentication",
            r"SQL.*injection",
            r"<script>",
            r"\.\.\/",
        ]

        findings = []

        for i, log in enumerate(logs):
            for pattern in suspicious_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    findings.append({
                        "line": i + 1,
                        "pattern": pattern,
                        "content": log[:200]
                    })

        return {
            "type": "log_analysis",
            "total_logs": len(logs),
            "suspicious_count": len(findings),
            "findings": findings
        }

    async def _build_timeline(self, events: List[Dict]) -> Dict[str, Any]:
        """Build forensic timeline from events"""
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.get("timestamp", ""))

        return {
            "type": "timeline",
            "event_count": len(sorted_events),
            "timeline": sorted_events,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _check_file_hash(self, file_path: str) -> Dict[str, Any]:
        """Calculate and check file hash"""
        import hashlib

        try:
            with open(file_path, "rb") as f:
                content = f.read()
                md5 = hashlib.md5(content).hexdigest()
                sha256 = hashlib.sha256(content).hexdigest()

            return {
                "file": file_path,
                "md5": md5,
                "sha256": sha256,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}


class AuditTentacle(Tentacle):
    """
    Security Audit Tentacle

    Performs configuration and compliance auditing.
    """

    def __init__(self, tentacle_id: str = "audit"):
        capabilities = {
            TentacleCapability.CONFIG_AUDIT,
            TentacleCapability.COMPLIANCE_CHECK,
            TentacleCapability.POLICY_ANALYSIS,
        }

        super().__init__(
            tentacle_id=tentacle_id,
            name="Security Auditor",
            capabilities=capabilities
        )

    async def _setup_client(self) -> None:
        """Setup audit tools"""
        pass

    async def _cleanup_client(self) -> None:
        """Cleanup"""
        pass

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Perform security audit"""
        payload = task.payload if hasattr(task, 'payload') else task

        audit_type = payload.get("type", "config")

        if audit_type == "config":
            return await self._audit_config(payload.get("config", {}))
        elif audit_type == "password":
            return await self._audit_password_policy(payload.get("policy", {}))
        elif audit_type == "permissions":
            return await self._audit_permissions(payload.get("path", ""))

        return {"error": "Unknown audit type"}

    async def _audit_config(self, config: Dict) -> Dict[str, Any]:
        """Audit configuration for security issues"""
        issues = []

        # Check for common misconfigurations
        if config.get("debug", False):
            issues.append({
                "severity": "HIGH",
                "issue": "Debug mode enabled in production",
                "recommendation": "Disable debug mode"
            })

        if not config.get("https_only", False):
            issues.append({
                "severity": "MEDIUM",
                "issue": "HTTPS not enforced",
                "recommendation": "Enable HTTPS-only mode"
            })

        if config.get("default_password"):
            issues.append({
                "severity": "CRITICAL",
                "issue": "Default password detected",
                "recommendation": "Change default credentials immediately"
            })

        return {
            "type": "config_audit",
            "issues_found": len(issues),
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _audit_password_policy(self, policy: Dict) -> Dict[str, Any]:
        """Audit password policy"""
        recommendations = []

        min_length = policy.get("min_length", 0)
        if min_length < 12:
            recommendations.append({
                "current": f"min_length: {min_length}",
                "recommended": "min_length: 12 or higher"
            })

        if not policy.get("require_special"):
            recommendations.append({
                "current": "Special characters not required",
                "recommended": "Require at least one special character"
            })

        if not policy.get("require_mfa"):
            recommendations.append({
                "current": "MFA not required",
                "recommended": "Enable mandatory MFA"
            })

        return {
            "type": "password_policy_audit",
            "recommendations": recommendations,
            "compliant": len(recommendations) == 0
        }

    async def _audit_permissions(self, path: str) -> Dict[str, Any]:
        """Audit file/directory permissions"""
        import os
        import stat

        try:
            st = os.stat(path)
            mode = st.st_mode

            issues = []

            # Check for world-writable
            if mode & stat.S_IWOTH:
                issues.append({
                    "severity": "HIGH",
                    "issue": "World-writable permissions",
                    "path": path
                })

            # Check for SUID/SGID
            if mode & stat.S_ISUID:
                issues.append({
                    "severity": "MEDIUM",
                    "issue": "SUID bit set",
                    "path": path
                })

            return {
                "type": "permission_audit",
                "path": path,
                "mode": oct(mode),
                "issues": issues
            }

        except Exception as e:
            return {"error": str(e)}


class ExploitTentacle(Tentacle):
    """
    Exploit Development Tentacle

    Assists with authorized penetration testing and exploit development.

    WARNING: Only use for authorized security testing!
    """

    def __init__(self, tentacle_id: str = "exploit"):
        capabilities = {
            TentacleCapability.EXPLOIT_DEV,
            TentacleCapability.CODE_GENERATION,
        }

        super().__init__(
            tentacle_id=tentacle_id,
            name="Exploit Developer",
            capabilities=capabilities
        )

        self._authorization_confirmed = False

    async def _setup_client(self) -> None:
        """Setup exploit development environment"""
        self.logger.warning(
            "Exploit tentacle initialized. Only use for authorized testing!"
        )

    async def _cleanup_client(self) -> None:
        """Cleanup"""
        pass

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process exploit development task"""
        payload = task.payload if hasattr(task, 'payload') else task

        # Require explicit authorization
        if not payload.get("authorized", False):
            return {
                "error": "Authorization required",
                "message": "Set 'authorized: true' to confirm you have permission"
            }

        exploit_type = payload.get("type", "")

        if exploit_type == "payload_gen":
            return await self._generate_payload(payload)
        elif exploit_type == "analyze_vuln":
            return await self._analyze_vulnerability(payload)

        return {"error": "Unknown exploit type"}

    async def _generate_payload(self, payload: Dict) -> Dict[str, Any]:
        """Generate exploit payload (for authorized testing)"""
        target_type = payload.get("target_type", "")
        architecture = payload.get("arch", "x64")

        # Return template/guidance, not actual exploit code
        return {
            "type": "payload_guidance",
            "target": target_type,
            "architecture": architecture,
            "guidance": "Use established frameworks like Metasploit for payload generation",
            "warning": "Ensure you have written authorization before testing"
        }

    async def _analyze_vulnerability(self, payload: Dict) -> Dict[str, Any]:
        """Analyze a vulnerability"""
        vuln_details = payload.get("vulnerability", {})

        return {
            "type": "vulnerability_analysis",
            "details": vuln_details,
            "analysis": "Vulnerability analysis requires specific CVE or code to examine"
        }


class ThreatIntelTentacle(Tentacle):
    """
    Threat Intelligence Tentacle

    Gathers and correlates threat intelligence.
    """

    def __init__(self, tentacle_id: str = "threatintel"):
        capabilities = {
            TentacleCapability.DATA_CORRELATION,
            TentacleCapability.OSINT,
        }

        super().__init__(
            tentacle_id=tentacle_id,
            name="Threat Intelligence",
            capabilities=capabilities
        )

    async def _setup_client(self) -> None:
        """Setup threat intel feeds"""
        pass

    async def _cleanup_client(self) -> None:
        """Cleanup"""
        pass

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process threat intelligence request"""
        payload = task.payload if hasattr(task, 'payload') else task

        intel_type = payload.get("type", "ioc_check")

        if intel_type == "ioc_check":
            return await self._check_ioc(payload.get("indicator", ""))
        elif intel_type == "threat_feed":
            return await self._get_threat_feed()

        return {"error": "Unknown intel type"}

    async def _check_ioc(self, indicator: str) -> Dict[str, Any]:
        """Check an indicator of compromise"""
        # In production, query threat intel platforms
        return {
            "indicator": indicator,
            "type": self._identify_ioc_type(indicator),
            "status": "requires_api_integration",
            "message": "Configure threat intel API (VirusTotal, OTX, etc.)"
        }

    def _identify_ioc_type(self, indicator: str) -> str:
        """Identify the type of IOC"""
        import re

        # IP address
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", indicator):
            return "ip_address"

        # Domain
        if re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$", indicator):
            return "domain"

        # MD5
        if re.match(r"^[a-fA-F0-9]{32}$", indicator):
            return "md5_hash"

        # SHA256
        if re.match(r"^[a-fA-F0-9]{64}$", indicator):
            return "sha256_hash"

        return "unknown"

    async def _get_threat_feed(self) -> Dict[str, Any]:
        """Get latest threat feed"""
        return {
            "feed": "threat_intelligence",
            "status": "requires_api_integration",
            "message": "Configure threat feed sources"
        }
