from .agent import run_agent


SCENARIOS = [
    {
        "name": "Small payment",
        "action": "payment.send",
        "params": {
            "amount": 2000,
            "recipient": "Approved Vendor",
            "recipient_type": "approved"
        }
    },
    {
        "name": "Large payment",
        "action": "payment.send",
        "params": {
            "amount": 80000,
            "recipient": "Unknown Account",
            "recipient_type": "unknown"
        }
    },
    {
        "name": "External customer data export",
        "action": "customer_data.export",
        "params": {
            "external": True,
            "destination": "external@example.com",
            "record_count": 1000
        }
    },
    {
        "name": "External email",
        "action": "email.send",
        "params": {
            "external": True,
            "to": "client@example.com",
            "subject": "Report",
            "body": "Demo report"
        }
    },
    {
        "name": "Database deletion",
        "action": "database.delete",
        "params": {
            "record_id": "CUST-1001"
        }
    }
]


def run_demo():
    print("\n=== AgentGuard Demo ===\n")

    for scenario in SCENARIOS:
        result = run_agent(
            agent_id="FinanceAgent",
            user_id="demo_user",
            action=scenario["action"],
            params=scenario["params"]
        )

        decision = result["trust_decision"]

        print(f"Scenario: {scenario['name']}")
        print(f"Action:   {scenario['action']}")
        print(f"Risk:     {decision['risk_level']} ({decision['risk_score']}/100)")
        print(f"Decision: {decision['decision'].upper()}")
        print(f"Reason:   {decision['reason']}")

        if result.get("tool_result"):
            print(f"Tool:     {result['tool_result']['message']}")

        print("-" * 60)


if __name__ == "__main__":
    run_demo()
