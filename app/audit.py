from datetime import datetime, timezone
import json
from pathlib import Path
from .config import AUDIT_FILE
from .models import AuditEvent


class AuditLogger:

    def __init__(self, file_path: Path = AUDIT_FILE):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def log(self, event: AuditEvent):
        with self.file_path.open("r", encoding="utf-8") as f:
            events = json.load(f)

        events.append(event.model_dump())

        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

    def create_event(self, action, decision, params, tool_result=None):
        return AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=decision.agent_id,
            user_id=decision.user_id,
            action=action,
            params=params,
            decision=decision.decision,
            risk_level=decision.risk_level,
            risk_score=decision.risk_score,
            policy=decision.policy,
            reason=decision.reason,
            approved_by_human=decision.approved_by_human,
            tool_result=tool_result
        )

    def read_all(self):
        with self.file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
