# AgentGuard — AI Agent Trust & Security Framework

AgentGuard is a portfolio/demo project inspired by the idea of a trust layer for autonomous AI agents.

It demonstrates:

- AI agent workflow using LangGraph
- Runtime policy enforcement
- Risk scoring
- Allow / Flag / Deny decisions
- Human approval simulation
- Protected mock tools
- Audit logging
- Streamlit security dashboard
- Optional Gemini integration

> This is an educational/demo implementation. It is not a production security system and is not affiliated with AgentTrustCore.

## Architecture

```text
User Request
     |
     v
+----------------+
|    AI Agent    |
|  LangGraph     |
+-------+--------+
        |
        v
+----------------+
| Trust Engine   |
| Identity       |
| Policy         |
| Risk           |
+-------+--------+
        |
   +----+----+
   |         |
 ALLOW     FLAG/DENY
   |         |
   v       Human
 Tool     Approval
   |
   v
Audit Logger
```

## Project Structure

```text
AgentGuard/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── audit.py
│   ├── config.py
│   ├── identity.py
│   ├── models.py
│   ├── policies.py
│   ├── risk.py
│   ├── tools.py
│   ├── trust.py
│   └── demo.py
├── config/
│   └── policies.json
├── data/
│   └── audit_logs.json
├── tests/
│   ├── test_risk.py
│   └── test_trust.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run_demo.py
└── streamlit_app.py
```

## 1. Create environment

Windows:

```cmd
cd /d D:\AgentGuard
python -m venv venv
venv\Scripts\activate
```

## 2. Install

```cmd
pip install -r requirements.txt
```

## 3. Run the local demo

No API key is required:

```cmd
python run_demo.py
```

## 4. Run the dashboard

```cmd
streamlit run streamlit_app.py
```

## 5. Optional Gemini setup

Copy:

```text
.env.example
```

to:

```text
.env
```

Add your API key:

```text
GOOGLE_API_KEY=your_key_here
```

The Gemini/LangGraph integration is optional. The deterministic demo works without an API key.

## Example decisions

- ₹2,000 payment → ALLOW
- ₹40,000 payment → ALLOW
- ₹80,000 payment → DENY
- External customer-data export → DENY
- Unknown action → FLAG

## Interview explanation

"I built AgentGuard as a simplified trust layer for an AI agent. Instead of allowing an LLM to directly execute sensitive tools, every proposed action passes through identity, policy and risk checks. The trust layer returns ALLOW, FLAG or DENY. Approved actions can execute a protected tool, while every decision is recorded in an audit log."

## Important design choice

The security decision is deterministic and policy-driven. The LLM does not get final authority over whether a sensitive action is allowed. This avoids relying only on prompts for security controls.

## Future improvements

- Database-backed audit logs
- OAuth/OIDC agent identity
- JWT verification
- More sophisticated policy language
- Real human approval workflow
- OpenTelemetry tracing
- Model/tool evaluation
- Docker deployment
- Production authentication
