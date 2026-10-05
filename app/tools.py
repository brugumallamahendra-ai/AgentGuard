from typing import Dict, Any


def process_payment(amount: float, recipient: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "tool": "payment_service",
        "message": f"Demo payment of ₹{amount:,.2f} sent to {recipient}."
    }


def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "tool": "email_service",
        "message": f"Demo email prepared for {to}.",
        "subject": subject
    }


def export_customer_data(destination: str, record_count: int) -> Dict[str, Any]:
    return {
        "status": "success",
        "tool": "customer_data_export",
        "message": (
            f"Demo export of {record_count} customer records "
            f"to {destination}."
        )
    }


def delete_database_record(record_id: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "tool": "database",
        "message": f"Demo deletion of record {record_id}."
    }
