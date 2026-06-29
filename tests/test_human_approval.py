from __future__ import annotations

from ai.human_approval import (
    APPROVE,
    HumanApprovalConfig,
    HumanApprovalWorkflow,
    NEEDS_REVIEW,
    REJECT,
)
from ai.strategy_improvement import StrategyImprovementSuggestion


def _suggestion() -> StrategyImprovementSuggestion:
    return StrategyImprovementSuggestion(
        category="RISK_MANAGEMENT",
        priority="HIGH",
        suggestion="Review drawdown limits before changing any strategy rule.",
        reason="Drawdown review protects strategy research from weak pass-rate assumptions.",
        risk="Changing rules without review can expose capital to poor conditions.",
        human_approval_required=True,
    )


def test_create_approval_request_from_strategy_suggestion() -> None:
    request = HumanApprovalWorkflow().create_request(_suggestion(), HumanApprovalConfig())

    assert request.request_id.startswith("approval-risk-management-")
    assert request.suggestion_category == "RISK_MANAGEMENT"
    assert request.suggestion_priority == "HIGH"
    assert "drawdown" in request.suggestion_text.lower()
    assert request.human_approval_required is True


def test_request_starts_as_pending() -> None:
    request = HumanApprovalWorkflow().create_request(_suggestion(), HumanApprovalConfig())

    assert request.status == "PENDING"
    assert request.created_at is not None


def test_approve_decision_creates_approved_result() -> None:
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(_suggestion(), HumanApprovalConfig())

    result = workflow.decide(request, APPROVE, HumanApprovalConfig(), decided_by="human")

    assert result.status == "APPROVED"
    assert result.approved is True
    assert result.allowed_to_apply is True
    assert result.decision is not None
    assert result.decision.decision == "APPROVE"
    assert result.decision.decided_by == "human"


def test_reject_decision_creates_rejected_result() -> None:
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(_suggestion(), HumanApprovalConfig())

    result = workflow.decide(request, REJECT, HumanApprovalConfig(), notes="Too risky")

    assert result.status == "REJECTED"
    assert result.approved is False
    assert result.allowed_to_apply is False
    assert result.blocking_reasons
    assert result.decision is not None
    assert result.decision.notes == "Too risky"


def test_needs_review_decision_is_safe() -> None:
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(_suggestion(), HumanApprovalConfig())

    result = workflow.decide(request, NEEDS_REVIEW, HumanApprovalConfig())

    assert result.status == "NEEDS_REVIEW"
    assert result.approved is False
    assert result.allowed_to_apply is False
    assert result.blocking_reasons


def test_missing_suggestion_does_not_crash() -> None:
    request = HumanApprovalWorkflow().create_request(None, HumanApprovalConfig())

    assert request.status == "PENDING"
    assert request.suggestion_category == "UNKNOWN"
    assert "No strategy improvement suggestion" in request.suggestion_text


def test_missing_request_does_not_crash() -> None:
    result = HumanApprovalWorkflow().decide(None, APPROVE, HumanApprovalConfig())

    assert result.status == "UNKNOWN"
    assert result.approved is False
    assert result.allowed_to_apply is False
    assert result.blocking_reasons


def test_approval_does_not_auto_change_strategy() -> None:
    suggestion = _suggestion()
    original_text = suggestion.suggestion
    config = HumanApprovalConfig()
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(suggestion, config)

    result = workflow.decide(request, APPROVE, config)

    assert suggestion.suggestion == original_text
    assert config.allow_auto_apply is False
    assert result.allowed_to_apply is True
    assert any("does not automatically change strategy rules" in reason for reason in result.reasons)


def test_allow_auto_apply_defaults_to_false() -> None:
    config = HumanApprovalConfig()

    assert config.allow_auto_apply is False


def test_explain_returns_readable_text() -> None:
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(_suggestion(), HumanApprovalConfig())
    result = workflow.decide(request, APPROVE, HumanApprovalConfig())

    text = workflow.explain(result)

    assert "Human approval status:" in text
    assert "future reviewed strategy change proposal" in text
    assert "does not automatically change rules" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(_suggestion(), HumanApprovalConfig())
    result = workflow.decide(request, APPROVE, HumanApprovalConfig())
    text = workflow.explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
