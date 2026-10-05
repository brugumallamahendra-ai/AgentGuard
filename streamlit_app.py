import streamlit as st

from app.llm_agent import understand_request
from app.models import AgentAction
from app.trust import TrustEngine
from app.secure_agent import execute_tool
from app.audit import AuditLogger


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AgentGuard",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🛡️ AgentGuard")
st.subheader("AI Agent Trust & Security Framework")

st.write(
    "AgentGuard converts natural-language requests into structured "
    "actions and independently evaluates identity, risk, and policy "
    "before allowing tool execution."
)


# =========================================================
# INITIALIZE AUDIT LOGGER
# =========================================================

audit_logger = AuditLogger()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Agent Configuration")

    st.write("**Agent:** FinanceAgent")
    st.write("**User:** demo_user")

    st.divider()

    st.markdown("### 🔐 Security Flow")

    st.code(
        """
User Request
     ↓
Gemini AI Agent
     ↓
Structured Action
     ↓
Trust Engine
     ↓
Risk + Policy
     ↓
ALLOW / FLAG / DENY
     ↓
Human Approval
     ↓
Tool Execution
     ↓
Audit Log
        """,
        language="text"
    )


# =========================================================
# USER REQUEST
# =========================================================

st.markdown("### 💬 User Request")

user_request = st.text_area(
    "Enter a request for the AI agent:",
    placeholder=(
        "Examples:\n"
        "Send 2000 rupees to Approved Vendor\n"
        "Send 80000 rupees to Unknown Vendor\n"
        "Delete database record 12345"
    ),
    height=120
)


analyze = st.button(
    "🔍 Analyze Request",
    type="primary",
    use_container_width=True
)


# =========================================================
# ANALYZE REQUEST
# =========================================================

if analyze:

    if not user_request.strip():

        st.warning("Please enter a request.")

    else:

        try:

            with st.spinner(
                "🤖 Gemini is understanding the request..."
            ):

                # -------------------------------------------------
                # STEP 1: Gemini understands the user request
                # -------------------------------------------------

                llm_action = understand_request(
                    user_request
                )


                # -------------------------------------------------
                # STEP 2: Convert LLM output into AgentAction
                # -------------------------------------------------

                action = AgentAction(
                    agent_id="FinanceAgent",
                    user_id="demo_user",
                    action=llm_action.action,
                    params=llm_action.model_dump(
                        exclude_none=True
                    )
                )


                # -------------------------------------------------
                # STEP 3: Trust Engine evaluates independently
                # -------------------------------------------------

                trust_engine = TrustEngine()

                decision = trust_engine.evaluate(
                    action
                )


                # -------------------------------------------------
                # SAVE STATE
                # -------------------------------------------------

                st.session_state["action"] = action

                st.session_state["decision"] = decision

                st.session_state["llm_action"] = llm_action

                # Status is reset for every new analysis
                st.session_state["execution_status"] = None

                # Unique analysis identifier
                st.session_state["analysis_id"] = (
                    f"{action.action}|"
                    f"{action.params}"
                )


        except Exception as e:

            st.error(
                f"Error while analyzing request: {e}"
            )


# =========================================================
# DISPLAY AI AGENT + TRUST ENGINE
# =========================================================

if "decision" in st.session_state:

    action = st.session_state["action"]

    decision = st.session_state["decision"]

    llm_action = st.session_state["llm_action"]


    st.divider()


    col1, col2 = st.columns(2)


    # =====================================================
    # AI AGENT
    # =====================================================

    with col1:

        st.markdown("### 🤖 AI Agent")

        st.write("**Structured Action**")

        st.code(
            llm_action.action,
            language="text"
        )

        st.write("**Parameters**")

        st.json(
            llm_action.model_dump(
                exclude_none=True
            )
        )


    # =====================================================
    # AGENTGUARD TRUST DECISION
    # =====================================================

    with col2:

        st.markdown("### 🛡️ AgentGuard Decision")


        if decision.decision == "allow":

            st.success(
                "✅ ALLOWED"
            )

        elif decision.decision == "flag":

            st.warning(
                "⚠️ HUMAN APPROVAL REQUIRED"
            )

        elif decision.decision == "deny":

            st.error(
                "🚫 DENIED"
            )


        metric1, metric2 = st.columns(2)


        with metric1:

            st.metric(
                "Risk Score",
                f"{decision.risk_score}/100"
            )


        with metric2:

            st.metric(
                "Risk Level",
                decision.risk_level
            )


        st.write(
            f"**Policy:** `{decision.policy}`"
        )

        st.write(
            f"**Reason:** {decision.reason}"
        )


# =========================================================
# ACTION HANDLING
# =========================================================

if "decision" in st.session_state:

    action = st.session_state["action"]

    decision = st.session_state["decision"]

    execution_status = st.session_state.get(
        "execution_status"
    )


    st.divider()

    st.markdown("### ⚙️ Action Handling")


    # =====================================================
    # DENY
    # =====================================================

    if decision.decision == "deny":

        st.error(
            "🚫 Tool execution blocked by AgentGuard."
        )

        st.info(
            "The AI proposed the action, but the "
            "Trust Engine denied it."
        )


        # ---------------------------------------------
        # Log DENY only once
        # ---------------------------------------------

        if execution_status is None:

            blocked_result = {
                "status": "blocked",
                "message": (
                    "AgentGuard denied the action. "
                    "Tool execution was blocked."
                )
            }


            event = audit_logger.create_event(
                action=action.action,
                decision=decision,
                params=action.params,
                tool_result=blocked_result
            )


            audit_logger.log(event)


            st.session_state[
                "execution_status"
            ] = "DENIED"


    # =====================================================
    # ALLOW
    # =====================================================

    elif decision.decision == "allow":

        if execution_status is None:

            st.success(
                "✅ AgentGuard allowed this action."
            )


            if st.button(
                "▶️ Execute Approved Action",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "⚙️ Executing tool..."
                ):

                    result = execute_tool(
                        action
                    )


                st.success(
                    "✅ Tool executed successfully."
                )

                st.json(result)


                # -----------------------------------------
                # Audit
                # -----------------------------------------

                event = audit_logger.create_event(
                    action=action.action,
                    decision=decision,
                    params=action.params,
                    tool_result=result
                )


                audit_logger.log(event)


                st.session_state[
                    "execution_status"
                ] = "EXECUTED"


                st.success(
                    "📝 Audit event recorded."
                )


        elif execution_status == "EXECUTED":

            st.success(
                "✅ Action already executed."
            )


    # =====================================================
    # FLAG
    # =====================================================

    elif decision.decision == "flag":


        # -------------------------------------------------
        # WAITING FOR HUMAN APPROVAL
        # -------------------------------------------------

        if execution_status is None:

            st.warning(
                "⚠️ This action requires human approval "
                "before execution."
            )


            approve_col, reject_col = st.columns(2)


            # ---------------------------------------------
            # APPROVE BUTTON
            # ---------------------------------------------

            with approve_col:

                approve = st.button(
                    "✅ Approve & Execute",
                    use_container_width=True
                )


            # ---------------------------------------------
            # REJECT BUTTON
            # ---------------------------------------------

            with reject_col:

                reject = st.button(
                    "❌ Reject",
                    use_container_width=True
                )


            # =============================================
            # HUMAN APPROVED
            # =============================================

            if approve:

                decision.approved_by_human = True


                with st.spinner(
                    "⚙️ Executing approved action..."
                ):

                    result = execute_tool(
                        action
                    )


                st.success(
                    "✅ Human approval received."
                )

                st.success(
                    "✅ Tool executed successfully."
                )


                st.json(result)


                # -----------------------------------------
                # Audit result
                # -----------------------------------------

                approval_result = {
                    "status": "approved_and_executed",
                    "message": (
                        "Human approved the action "
                        "and the tool was executed."
                    ),
                    "execution_result": result
                }


                event = audit_logger.create_event(
                    action=action.action,
                    decision=decision,
                    params=action.params,
                    tool_result=approval_result
                )


                audit_logger.log(event)


                st.session_state[
                    "execution_status"
                ] = "APPROVED"


                st.success(
                    "📝 Approval and execution recorded "
                    "in audit log."
                )


            # =============================================
            # HUMAN REJECTED
            # =============================================

            if reject:

                decision.approved_by_human = False


                rejection_result = {
                    "status": "rejected",
                    "message": (
                        "Human approval was rejected. "
                        "Tool execution was blocked."
                    )
                }


                # -----------------------------------------
                # Audit rejection
                # -----------------------------------------

                event = audit_logger.create_event(
                    action=action.action,
                    decision=decision,
                    params=action.params,
                    tool_result=rejection_result
                )


                audit_logger.log(event)


                st.session_state[
                    "execution_status"
                ] = "REJECTED"


                st.error(
                    "❌ Human approval rejected."
                )

                st.info(
                    "🚫 Tool execution was blocked."
                )

                st.success(
                    "📝 Rejection recorded in audit log."
                )


        # -------------------------------------------------
        # ALREADY APPROVED
        # -------------------------------------------------

        elif execution_status == "APPROVED":

            st.success(
                "🟢 FLAG + APPROVED → EXECUTED"
            )

            st.info(
                "Human approval was received and "
                "the tool was executed."
            )


        # -------------------------------------------------
        # ALREADY REJECTED
        # -------------------------------------------------

        elif execution_status == "REJECTED":

            st.error(
                "🔴 FLAG + REJECTED → BLOCKED"
            )

            st.info(
                "Human approval was rejected and "
                "tool execution was blocked."
            )


# =========================================================
# SECURITY SUMMARY
# =========================================================

st.divider()

st.markdown("### 📊 Security Summary")


events = audit_logger.read_all()


allow_count = sum(
    1
    for event in events
    if event["decision"] == "allow"
)


flag_count = sum(
    1
    for event in events
    if event["decision"] == "flag"
)


deny_count = sum(
    1
    for event in events
    if event["decision"] == "deny"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Events",
        len(events)
    )


with col2:

    st.metric(
        "Allowed",
        allow_count
    )


with col3:

    st.metric(
        "Flagged",
        flag_count
    )


with col4:

    st.metric(
        "Denied",
        deny_count
    )


# =========================================================
# AUDIT LOG
# =========================================================

st.divider()

st.markdown("### 📋 Audit Log")


# ---------------------------------------------------------
# CLEAR AUDIT LOG
# ---------------------------------------------------------

if st.button(
    "🗑️ Clear Audit Log"
):

    audit_logger.file_path.write_text(
        "[]",
        encoding="utf-8"
    )


    st.session_state.pop(
        "action",
        None
    )

    st.session_state.pop(
        "decision",
        None
    )

    st.session_state.pop(
        "llm_action",
        None
    )

    st.session_state.pop(
        "analysis_id",
        None
    )

    st.session_state.pop(
        "execution_status",
        None
    )


    st.success(
        "Audit log cleared."
    )


    st.rerun()


# ---------------------------------------------------------
# DISPLAY AUDIT EVENTS
# ---------------------------------------------------------

events = audit_logger.read_all()


if not events:

    st.info(
        "No audit events recorded yet."
    )

else:

    for event in reversed(
        events[-10:]
    ):

        decision_value = event[
            "decision"
        ]


        approved = event.get(
            "approved_by_human",
            False
        )


        tool_result = event.get(
            "tool_result"
        )


        # =================================================
        # AUDIT STATUS
        # =================================================

        if decision_value == "deny":

            icon = "🚫"

            status_text = (
                "DENY → BLOCKED"
            )


        elif decision_value == "allow":

            icon = "✅"

            status_text = (
                "ALLOW → EXECUTED"
            )


        elif decision_value == "flag":

            if approved:

                icon = "🟢"

                status_text = (
                    "FLAG + APPROVED → EXECUTED"
                )

            else:

                icon = "🔴"

                status_text = (
                    "FLAG + REJECTED → BLOCKED"
                )


        else:

            icon = "⚠️"

            status_text = (
                decision_value.upper()
            )


        # =================================================
        # AUDIT TITLE
        # =================================================

        title = (
            f"{icon} "
            f"{status_text} | "
            f"Risk {event['risk_score']}/100"
        )


        with st.expander(title):


            st.write(
                f"**Timestamp:** "
                f"{event.get('timestamp', 'Unknown')}"
            )


            st.write(
                f"**Agent:** "
                f"{event['agent_id']}"
            )


            st.write(
                f"**User:** "
                f"{event['user_id']}"
            )


            st.write(
                f"**Action:** "
                f"`{event['action']}`"
            )


            # -------------------------------------------------
            # TRUST DECISION
            # -------------------------------------------------

            st.write(
                f"**Trust Decision:** "
                f"`{decision_value.upper()}`"
            )


            # -------------------------------------------------
            # RISK
            # -------------------------------------------------

            st.write(
                f"**Risk:** "
                f"{event['risk_level']} "
                f"({event['risk_score']}/100)"
            )


            # -------------------------------------------------
            # POLICY
            # -------------------------------------------------

            st.write(
                f"**Policy:** "
                f"`{event['policy']}`"
            )


            # -------------------------------------------------
            # REASON
            # -------------------------------------------------

            st.write(
                f"**Reason:** "
                f"{event['reason']}"
            )


            # =================================================
            # HUMAN APPROVAL
            # =================================================

            if decision_value == "flag":

                if approved:

                    st.success(
                        "👤 Human Approval: APPROVED"
                    )

                    st.success(
                        "🟢 FLAG + APPROVED → EXECUTED"
                    )

                else:

                    st.error(
                        "👤 Human Approval: REJECTED"
                    )

                    st.error(
                        "🔴 FLAG + REJECTED → BLOCKED"
                    )

            else:

                st.write(
                    "**Human Approval:** "
                    "Not Required"
                )


            # =================================================
            # TOOL RESULT
            # =================================================

            if tool_result:

                st.write(
                    "**Execution Result:**"
                )

                st.json(
                    tool_result
                )


            # =================================================
            # PARAMETERS
            # =================================================

            st.write(
                "**Parameters:**"
            )

            st.json(
                event["params"]
            )


# =========================================================
# ARCHITECTURE
# =========================================================

st.divider()

st.markdown(
    "### 🏗️ AgentGuard Architecture"
)


st.code(
    """
                         USER
                          │
                          ▼
                 ┌─────────────────┐
                 │   Gemini Agent  │
                 │ Intent → Action │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  TRUST ENGINE   │
                 ├─────────────────┤
                 │ Identity Check  │
                 │ Risk Assessment │
                 │ Policy Check    │
                 └────────┬────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          ALLOW          FLAG         DENY
             │            │            │
             │            ▼            │
             │     Human Approval     │
             │        /      \\        │
             │     APPROVE   REJECT   │
             │        │        │      │
             └────────┘        │      │
                  │             │      │
                  ▼             ▼      ▼
             TOOL EXECUTE    BLOCK    BLOCK
                  │             │      │
                  └──────┬──────┴──────┘
                         ▼
                    AUDIT LOG
    """,
    language="text"
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AgentGuard — AI Agent Trust & Security Framework"
)