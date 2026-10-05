from typing import Dict, Any
from .config import load_policies


class PolicyEngine:

    def __init__(self):
        self.policies = load_policies()

    def evaluate(self, action: str, params: Dict[str, Any]) -> dict:
        if action == "payment.send":
            amount = float(params.get("amount", 0))
            limit = self.policies["payment"]["max_amount"]

            if amount > limit:
                return {
                    "decision": "deny",
                    "policy": "payment.max_amount",
                    "reason": f"Payment exceeds the configured ₹{limit:,.0f} limit."
                }

            return {
                "decision": "allow",
                "policy": "payment.max_amount",
                "reason": "Payment is within the configured limit."
            }

        if action == "customer_data.export":
            if params.get("external", False):
                return {
                    "decision": "deny",
                    "policy": "customer_data.external_transfer",
                    "reason": "External transfer of customer data is prohibited."
                }

            return {
                "decision": "allow",
                "policy": "customer_data.external_transfer",
                "reason": "Customer data remains inside the approved environment."
            }

        if action == "database.delete":
            return {
                "decision": "flag",
                "policy": "database.delete_requires_approval",
                "reason": "Destructive database operations require human approval."
            }

        if action == "email.send":
            if params.get("external", False):
                return {
                    "decision": "flag",
                    "policy": "email.external_recipient_requires_approval",
                    "reason": "External email requires human approval."
                }

            return {
                "decision": "allow",
                "policy": "email.external_recipient_requires_approval",
                "reason": "Internal email is allowed."
            }

        return {
            "decision": "flag",
            "policy": "default.unknown_action",
            "reason": "Unknown actions require human review."
        }
