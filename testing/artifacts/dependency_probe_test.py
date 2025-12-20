#!/usr/bin/env python3.11
"""
Simple Dependency Probe Test
Test if we can map network dependencies
"""

import socket
import json
from datetime import datetime

def test_dns_resolution(domain):
    """Test DNS resolution"""
    try:
        ip = socket.gethostbyname(domain)
        return {"success": True, "ip": ip, "domain": domain}
    except Exception as e:
        return {"success": False, "error": str(e), "domain": domain}

def test_http_connectivity(domain, port=80):
    """Test HTTP connectivity"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((domain, port))
        sock.close()
        return {"success": result == 0, "domain": domain, "port": port}
    except Exception as e:
        return {"success": False, "error": str(e), "domain": domain}

def run_dependency_probe():
    """Run a simple dependency probe"""
    targets = ["google.com", "github.com", "cloudflare.com"]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "probe_type": "network_dependency",
        "tests": []
    }
    
    for target in targets:
        dns_result = test_dns_resolution(target)
        http_result = test_http_connectivity(target)
        
        results["tests"].append({
            "target": target,
            "dns": dns_result,
            "http": http_result
        })
    
    return results

if __name__ == "__main__":
    results = run_dependency_probe()
    print(json.dumps(results, indent=2))
