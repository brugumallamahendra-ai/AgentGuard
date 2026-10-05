from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent.parent
POLICY_FILE = ROOT / "config" / "policies.json"
AUDIT_FILE = ROOT / "data" / "audit_logs.json"


def load_policies() -> dict:
    with POLICY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)
