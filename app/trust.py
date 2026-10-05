from .identity import verify_identity
from .models import AgentAction, TrustDecision
from .policies import PolicyEngine
from .risk import calculate_risk


class TrustEngine:

    def __init__(self):
        self.policy_engine = PolicyEngine()

    def evaluate(self, action: AgentAction) -> TrustDecision:
        identity = verify_identity(action.agent_id, action.user_id)

        if not identity["verified"]:
            return TrustDecision(
                decision="deny",
                risk_level="HIGH",
                risk_score=100,
                reason=identity["reason"],
                policy="identity.verification",
                action=action.action,
                agent_id=action.agent_id,
                user_id=action.user_id
            )

        risk = calculate_risk(action.action, action.params)
        policy = self.policy_engine.evaluate(action.action, action.params)

        # A security layer should not weaken a stricter policy decision.
        decision = policy["decision"]

        if risk["level"] == "HIGH" and decision == "allow":
            decision = "flag"
            reason = (
                "Risk is HIGH, so the action requires human review "
                "even though the basic policy allows it."
            )
        else:
            reason = policy["reason"]

        return TrustDecision(
            decision=decision,
            risk_level=risk["level"],
            risk_score=risk["score"],
            reason=reason,
            policy=policy["policy"],
            action=action.action,
            agent_id=action.agent_id,
            user_id=action.user_id
        )
