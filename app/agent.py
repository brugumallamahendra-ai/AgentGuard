from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

from .models import AgentAction
from .trust import TrustEngine
from .audit import AuditLogger
from .tools import (
    process_payment,
    send_email,
    export_customer_data,
    delete_database_record,
)


class AgentState(TypedDict, total=False):
    agent_id: str
    user_id: str
    action: str
    params: dict
    trust_decision: dict
    tool_result: dict
    status: str


trust_engine = TrustEngine()
audit_logger = AuditLogger()


def trust_check_node(state: AgentState):
    action = AgentAction(
        agent_id=state["agent_id"],
        user_id=state["user_id"],
        action=state["action"],
        params=state.get("params", {})
    )

    decision = trust_engine.evaluate(action)

    return {
        "trust_decision": decision.model_dump()
    }


def execute_node(state: AgentState):
    action = state["action"]
    params = state.get("params", {})

    if action == "payment.send":
        result = process_payment(
            params["amount"],
            params.get("recipient", "unknown")
        )

    elif action == "email.send":
        result = send_email(
            params["to"],
            params.get("subject", ""),
            params.get("body", "")
        )

    elif action == "customer_data.export":
        result = export_customer_data(
            params.get("destination", "unknown"),
            int(params.get("record_count", 0))
        )

    elif action == "database.delete":
        result = delete_database_record(
            params.get("record_id", "unknown")
        )

    else:
        result = {
            "status": "error",
            "message": f"No tool registered for {action}"
        }

    return {
        "tool_result": result,
        "status": "EXECUTED"
    }


def finalize_node(state: AgentState):
    decision = state["trust_decision"]

    event = audit_logger.create_event(
        action=state["action"],
        decision=type("Decision", (), decision)(),
        params=state.get("params", {}),
        tool_result=state.get("tool_result")
    )

    # Convert the lightweight object into the actual audit model format.
    from .models import TrustDecision
    real_decision = TrustDecision(**decision)
    event = audit_logger.create_event(
        action=state["action"],
        decision=real_decision,
        params=state.get("params", {}),
        tool_result=state.get("tool_result")
    )
    audit_logger.log(event)

    return {}


def route_after_trust(state: AgentState):
    decision = state["trust_decision"]["decision"]

    if decision == "allow":
        return "execute"

    return "finalize"


graph = StateGraph(AgentState)
graph.add_node("trust_check", trust_check_node)
graph.add_node("execute", execute_node)
graph.add_node("finalize", finalize_node)

graph.set_entry_point("trust_check")

graph.add_conditional_edges(
    "trust_check",
    route_after_trust,
    {
        "execute": "execute",
        "finalize": "finalize"
    }
)

graph.add_edge("execute", "finalize")
graph.add_edge("finalize", END)

agent = graph.compile()


def run_agent(agent_id: str, user_id: str, action: str, params: dict):
    result = agent.invoke({
        "agent_id": agent_id,
        "user_id": user_id,
        "action": action,
        "params": params
    })

    return result
