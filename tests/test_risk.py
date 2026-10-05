from app.risk import calculate_risk


def test_small_payment_is_low_risk():
    result = calculate_risk(
        "payment.send",
        {"amount": 2000}
    )
    assert result["level"] == "LOW"


def test_large_payment_is_high_risk():
    result = calculate_risk(
        "payment.send",
        {
            "amount": 80000,
            "recipient_type": "unknown"
        }
    )
    assert result["score"] >= 60
    assert result["level"] == "HIGH"
