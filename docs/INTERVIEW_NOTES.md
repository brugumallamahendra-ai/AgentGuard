# AgentGuard Interview Notes

## What problem does it solve?

Autonomous agents can call tools and perform consequential actions. AgentGuard inserts a deterministic governance layer before those actions execute.

## Why not rely only on a system prompt?

A prompt is not a security boundary. An LLM can misunderstand instructions, produce unexpected tool calls, or be influenced by malicious input. Sensitive actions should be enforced outside the model's natural-language reasoning.

## Why three decisions?

- ALLOW: action satisfies identity, policy and risk controls.
- FLAG: action needs human review.
- DENY: action violates a mandatory security policy.

## Why is risk separate from policy?

Policy answers "Is this action permitted?"
Risk answers "How dangerous is this action?"

An action can be policy-allowed but still require review if its calculated risk is high.

## Why LangGraph?

LangGraph makes agent state and transitions explicit. It is useful when an agent has multiple steps, tools, approvals and routing decisions.

## What is the security boundary?

The TrustEngine is the boundary. Tool execution happens only after the trust decision returns ALLOW.

## What would you improve for production?

- Strong cryptographic identity
- OAuth/OIDC
- Database-backed immutable audit storage
- Fine-grained policy language
- Approval service
- Distributed tracing
- Secrets management
- Rate limits
- Tool sandboxing
- Monitoring and alerting
- Security testing and red-team evaluation
