import json
from pathlib import Path

def load_policy(policy_file: Path) -> dict:
    return json.loads(policy_file.read_text())
