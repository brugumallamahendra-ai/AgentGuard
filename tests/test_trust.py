from app.trust import TrustEngine
from app.models import AgentAction


def test_payment_allowed():
    engine = TrustEngine()

    decision = engine.evaluate(
        AgentAction(
            agent_id="FinanceAgent",
            user_id="demo_user",
            action="payment.send",
            params={"amount": 2000}
        )
    )

    assert decision.decision == "allow"


def test_large_payment_denied():
    engine = TrustEngine()

    decision = engine.evaluate(
        AgentAction(
            agent_id="FinanceAgent",
            user_id="demo_user",
            action="payment.send",
            params={"amount": 80000}
        )
    )

    assert decision.decision == "deny"


def test_unknown_identity_denied():
    engine = TrustEngine()

    decision = engine.evaluate(
        AgentAction(
            agent_id="UnknownAgent",
            user_id="demo_user",
            action="payment.send",
            params={"amount": 1000}
        )
    )

    assert decision.decision == "deny"
