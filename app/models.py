from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


Decision = Literal["allow", "flag", "deny"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class AgentAction(BaseModel):
    agent_id: str
    user_id: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)


class TrustDecision(BaseModel):
    decision: Decision
    risk_level: RiskLevel
    risk_score: int
    reason: str
    policy: str
    action: str
    agent_id: str
    user_id: str
    approved_by_human: bool = False


class AuditEvent(BaseModel):
    timestamp: str
    agent_id: str
    user_id: str
    action: str
    params: Dict[str, Any]
    decision: Decision
    risk_level: RiskLevel
    risk_score: int
    policy: str
    reason: str
    approved_by_human: bool = False
    tool_result: Optional[Dict[str, Any]] = None
