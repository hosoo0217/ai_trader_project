from __future__ import annotations

from ai.implementation_final_review import (
    APPROVE_FOR_WORK,
    NEEDS_BACKTEST,
    NEEDS_MORE_REVIEW,
    REJECT,
    ImplementationFinalReviewConfig,
    ImplementationFinalReviewWorkflow,
)
from ai.implementation_plan import ImplementationPlan


def _plan() -> ImplementationPlan:
    return ImplementationPlan(
        plan_id="plan-risk-management-12345678",
        source_proposal_id="proposal-risk-management-12345678",
        title="Implementation plan for risk management review",
        category="RISK_MANAGEMENT",
        priority="HIGH",
        objective="Plan a future human-reviewed risk management change.",
        proposed_steps=["Review current strategy logic", "Run backtest"],
        required_tests=["unit tests", "backtest comparison"],
        risk_checks=["drawdown check", "capital protection check"],
        rollback_plan="Revert code change, restore previous config, and rerun tests.",
    )


def test_approve_for_work_approves_plan_for_future_work() -> None:
    result = ImplementationFinalReviewWorkflow().review(
        _plan(),
        APPROVE_FOR_WORK,
        ImplementationFinalReviewConfig(),
        reviewed_by="Hosoo",
        notes="Approved for future work only",
    )

    assert result.status == "APPROVED_FOR_FUTURE_WORK"
    assert result.approved_for_work is True
    assert result.decision is not None
    assert result.decision.approved_for_implementation_work is True
    assert result.decision.reviewed_by == "Hosoo"


def test_approve_for_work_does_not_allow_implementation_now() -> None:
    result = ImplementationFinalReviewWorkflow().review(
        _plan(),
        APPROVE_FOR_WORK,
        ImplementationFinalReviewConfig(allow_auto_implementation=True),
    )

    assert result.implementation_allowed_now is False
    assert result.decision is not None
    assert result.decision.implementation_allowed_now is False


def test_reject_is_safe() -> None:
    result = ImplementationFinalReviewWorkflow().review(_plan(), REJECT, ImplementationFinalReviewConfig())

    assert result.status == "REJECTED"
    assert result.approved_for_work is False
    assert result.implementation_allowed_now is False
    assert result.blocking_reasons


def test_needs_backtest_is_safe() -> None:
    result = ImplementationFinalReviewWorkflow().review(_plan(), NEEDS_BACKTEST, ImplementationFinalReviewConfig())

    assert result.status == "NEEDS_BACKTEST"
    assert result.approved_for_work is False
    assert result.implementation_allowed_now is False
    assert result.blocking_reasons


def test_needs_more_review_is_safe() -> None:
    result = ImplementationFinalReviewWorkflow().review(
        _plan(),
        NEEDS_MORE_REVIEW,
        ImplementationFinalReviewConfig(),
    )

    assert result.status == "NEEDS_MORE_REVIEW"
    assert result.approved_for_work is False
    assert result.implementation_allowed_now is False
    assert result.blocking_reasons


def test_missing_plan_does_not_crash() -> None:
    result = ImplementationFinalReviewWorkflow().review(None, APPROVE_FOR_WORK, ImplementationFinalReviewConfig())

    assert result.status == "UNKNOWN"
    assert result.approved_for_work is False
    assert result.implementation_allowed_now is False
    assert result.blocking_reasons


def test_allow_auto_implementation_defaults_to_false() -> None:
    assert ImplementationFinalReviewConfig().allow_auto_implementation is False


def test_require_human_final_approval_defaults_to_true() -> None:
    assert ImplementationFinalReviewConfig().require_human_final_approval is True


def test_require_backtest_evidence_defaults_to_true() -> None:
    assert ImplementationFinalReviewConfig().require_backtest_evidence is True


def test_explain_returns_readable_text() -> None:
    workflow = ImplementationFinalReviewWorkflow()
    result = workflow.review(_plan(), APPROVE_FOR_WORK, ImplementationFinalReviewConfig())

    text = workflow.explain(result)

    assert "Implementation final review status:" in text
    assert "APPROVED_FOR_FUTURE_WORK" in text
    assert "future human-reviewed work only" in text
    assert "no strategy rule was changed" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    workflow = ImplementationFinalReviewWorkflow()
    result = workflow.review(_plan(), APPROVE_FOR_WORK, ImplementationFinalReviewConfig())
    text = workflow.explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
