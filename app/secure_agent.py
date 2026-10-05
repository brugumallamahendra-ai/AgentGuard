from app.llm_agent import understand_request
from app.models import AgentAction
from app.trust import TrustEngine
from app.tools import (
    process_payment,
    send_email,
    export_customer_data,
    delete_database_record,
)
from app.audit import AuditLogger


def execute_tool(action: AgentAction):
    """
    Execute the tool corresponding to the approved action.
    """

    params = action.params

    if action.action == "payment.send":
        amount = params.get("amount")
        recipient = params.get("recipient")

        if amount is None or recipient is None:
            return {
                "status": "error",
                "message": "Payment requires amount and recipient."
            }

        return process_payment(
            amount=float(amount),
            recipient=str(recipient)
        )

    elif action.action == "email.send":
        to = params.get("to")
        subject = params.get("subject", "No subject")
        body = params.get("body", "")

        if not to:
            return {
                "status": "error",
                "message": "Email requires a recipient."
            }

        return send_email(
            to=str(to),
            subject=str(subject),
            body=str(body)
        )

    elif action.action == "customer_data.export":
        destination = params.get("destination")
        record_count = params.get("record_count", 0)

        if not destination:
            return {
                "status": "error",
                "message": "Customer data export requires a destination."
            }

        return export_customer_data(
            destination=str(destination),
            record_count=int(record_count)
        )

    elif action.action == "database.delete":
        record_id = params.get("record_id")

        if not record_id:
            return {
                "status": "error",
                "message": "Database deletion requires a record ID."
            }

        return delete_database_record(
            record_id=str(record_id)
        )

    return {
        "status": "error",
        "message": f"No tool found for action: {action.action}"
    }


def run_secure_agent(user_request: str):

    print("\n=== USER REQUEST ===")
    print(user_request)

    # ---------------------------------------------------------
    # 1. LLM UNDERSTANDS THE USER REQUEST
    # ---------------------------------------------------------

    llm_action = understand_request(user_request)

    print("\n=== AI AGENT ===")
    print(llm_action.model_dump_json(indent=2))

    # ---------------------------------------------------------
    # 2. CONVERT LLM OUTPUT INTO AGENTGUARD ACTION
    # ---------------------------------------------------------

    action = AgentAction(
        agent_id="FinanceAgent",
        user_id="demo_user",
        action=llm_action.action,
        params=llm_action.model_dump(exclude_none=True)
    )

    # ---------------------------------------------------------
    # 3. TRUST ENGINE EVALUATES THE ACTION
    # ---------------------------------------------------------

    trust_engine = TrustEngine()
    decision = trust_engine.evaluate(action)

    print("\n=== AGENTGUARD TRUST DECISION ===")
    print(f"Decision:   {decision.decision.upper()}")
    print(f"Risk:       {decision.risk_level}")
    print(f"Risk Score: {decision.risk_score}/100")
    print(f"Policy:     {decision.policy}")
    print(f"Reason:     {decision.reason}")

    # ---------------------------------------------------------
    # 4. AUDIT LOGGER
    # ---------------------------------------------------------

    audit_logger = AuditLogger()

    # ---------------------------------------------------------
    # 5. DENY → NEVER EXECUTE THE TOOL
    # ---------------------------------------------------------

    if decision.decision == "deny":

        print("\n❌ TOOL EXECUTION BLOCKED")
        print("Reason: AgentGuard denied the action.")

        event = audit_logger.create_event(
            action=action.action,
            decision=decision,
            params=action.params,
            tool_result=None
        )

        audit_logger.log(event)

        return decision

    # ---------------------------------------------------------
    # 6. FLAG → REQUIRE HUMAN APPROVAL
    # ---------------------------------------------------------

    if decision.decision == "flag":

        print("\n⚠️ HUMAN APPROVAL REQUIRED")
        print("The tool will NOT execute automatically.")

        approval = input(
            "\nApprove this action? (yes/no): "
        ).strip().lower()

        if approval not in ("yes", "y"):

            print("\n❌ ACTION NOT APPROVED")
            print("Tool execution cancelled.")

            event = audit_logger.create_event(
                action=action.action,
                decision=decision,
                params=action.params,
                tool_result={
                    "status": "cancelled",
                    "message": "Human approval was not provided."
                }
            )

            audit_logger.log(event)

            return decision

        # Human approved the action
        decision.approved_by_human = True

        print("\n✅ HUMAN APPROVAL RECEIVED")

    # ---------------------------------------------------------
    # 7. ALLOW / HUMAN-APPROVED FLAG → EXECUTE TOOL
    # ---------------------------------------------------------

    print("\n=== TOOL EXECUTION ===")

    tool_result = execute_tool(action)

    print(tool_result)

    # ---------------------------------------------------------
    # 8. AUDIT THE FINAL RESULT
    # ---------------------------------------------------------

    event = audit_logger.create_event(
        action=action.action,
        decision=decision,
        params=action.params,
        tool_result=tool_result
    )

    audit_logger.log(event)

    print("\n📝 Audit event recorded.")

    return decision


if __name__ == "__main__":

    request = input("\nEnter your request: ")

    run_secure_agent(request)