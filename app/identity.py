ALLOWED_AGENTS = {
    "FinanceAgent",
    "ResearchAgent",
    "DataAgent"
}

ALLOWED_USERS = {
    "demo_user",
    "analyst_user",
    "admin_user"
}


def verify_identity(agent_id: str, user_id: str) -> dict:
    agent_ok = agent_id in ALLOWED_AGENTS
    user_ok = user_id in ALLOWED_USERS

    if agent_ok and user_ok:
        return {
            "verified": True,
            "reason": "Agent and user identity verified"
        }

    return {
        "verified": False,
        "reason": "Unknown agent or user identity"
    }
