from app.main import TRANSITIONS, SEVERITIES, SLA_HOURS


def test_approved_workflow_and_sla_contract() -> None:
    assert TRANSITIONS["open"] == ("in_progress", "escalated")
    assert "open" in TRANSITIONS["in_progress"]
    assert TRANSITIONS["closed"] == ("reopened",)
    assert SEVERITIES == ("critical", "high", "medium", "low")
    assert SLA_HOURS == 24