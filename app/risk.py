from typing import Dict, Any


def calculate_risk(action: str, params: Dict[str, Any]) -> dict:
    """
    Simple explainable demo risk model.

    This is intentionally deterministic so the security decision
    is not dependent on an LLM's opinion.
    """
    score = 0
    factors = []

    if action == "payment.send":
        score += 30
        factors.append(("financial_action", 30))

        amount = float(params.get("amount", 0))
        if amount > 50000:
            score += 20
            factors.append(("large_amount", 20))

        if amount > 75000:
            score += 25
            factors.append(("very_large_amount", 25))

        if params.get("recipient_type") == "unknown":
            score += 25
            factors.append(("unknown_recipient", 25))

    elif action == "customer_data.export":
        score += 30
        factors.append(("sensitive_data", 30))

        if params.get("external", False):
            score += 40
            factors.append(("external_transfer", 40))

    elif action == "email.send":
        score += 10
        factors.append(("external_communication", 10))

        if params.get("external", False):
            score += 20
            factors.append(("external_recipient", 20))

    elif action == "database.delete":
        score += 50
        factors.append(("destructive_operation", 50))

    else:
        score += 35
        factors.append(("unknown_action", 35))

    score = min(score, 100)

    if score <= 30:
        level = "LOW"
    elif score <= 60:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "score": score,
        "level": level,
        "factors": factors
    }
