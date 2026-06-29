from __future__ import annotations

from ai.implementation_final_review import (
    APPROVE_FOR_WORK,
    REJECT,
    ImplementationFinalReviewConfig,
    ImplementationFinalReviewWorkflow,
)
from ai.implementation_plan import ImplementationPlan
from ai.implementation_readiness import ImplementationReadinessChecker, ImplementationReadinessConfig


def _plan(**overrides) -> ImplementationPlan:
    values = {
        "plan_id": "plan-risk-management-12345678",
        "source_proposal_id": "proposal-risk-management-12345678",
        "title": "Implementation plan for risk management review",
        "category": "RISK_MANAGEMENT",
        "priority": "HIGH",
        "objective": "Plan a future human-reviewed risk management change.",
        "proposed_steps": ["Review current strategy logic", "Run backtest"],
        "required_tests": ["unit tests", "backtest comparison"],
        "risk_checks": ["drawdown check", "capital protection check"],
        "rollback_plan": "Revert code change, restore previous config, and rerun tests.",
        "reasons": ["Backtest evidence exists for this future work review."],
    }
    values.update(overrides)
    return ImplementationPlan(**values)


def _approved_review(plan: ImplementationPlan | None = None):
    plan = plan or _plan()
    return ImplementationFinalReviewWorkflow().review(
        plan,
        APPROVE_FOR_WORK,
        ImplementationFinalReviewConfig(),
    )


def test_approved_final_review_with_complete_plan_can_become_ready() -> None:
    plan = _plan()
    review = _approved_review(plan)

    checklist = ImplementationReadinessChecker().check(plan, review, ImplementationReadinessConfig())

    assert checklist.ready is True
    assert checklist.status == "READY_FOR_HUMAN_WORK"
    assert checklist.checklist_items["final_review_approved"] is True
    assert checklist.checklist_items["backtest_evidence_required"] is True


def test_missing_plan_returns_unknown_safely() -> None:
    checklist = ImplementationReadinessChecker().check(None, _approved_review(), ImplementationReadinessConfig())

    assert checklist.ready is False
    assert checklist.status == "UNKNOWN"
    assert checklist.blocking_reasons


def test_missing_final_review_returns_not_ready() -> None:
    checklist = ImplementationReadinessChecker().check(_plan(), None, ImplementationReadinessConfig())

    assert checklist.ready is False
    assert checklist.status == "NOT_READY"
    assert "final_review_approved" in checklist.missing_items


def test_rejected_final_review_returns_not_ready() -> None:
    plan = _plan()
    review = ImplementationFinalReviewWorkflow().review(plan, REJECT, ImplementationFinalReviewConfig())

    checklist = ImplementationReadinessChecker().check(plan, review, ImplementationReadinessConfig())

    assert checklist.ready is False
    assert checklist.status == "NOT_READY"
    assert "final_review_approved" in checklist.missing_items


def test_missing_tests_returns_needs_tests() -> None:
    plan = _plan(required_tests=[])

    checklist = ImplementationReadinessChecker().check(plan, _approved_review(plan), ImplementationReadinessConfig())

    assert checklist.ready is False
    assert checklist.status == "NEEDS_TESTS"
    assert "required_tests_defined" in checklist.missing_items


def test_missing_risk_checks_returns_needs_risk_review() -> None:
    plan = _plan(risk_checks=[])

    checklist = ImplementationReadinessChecker().check(plan, _approved_review(plan), ImplementationReadinessConfig())

    assert checklist.ready is False
    assert checklist.status == "NEEDS_RISK_REVIEW"
    assert "risk_checks_defined" in checklist.missing_items


def test_missing_rollback_plan_blocks_readiness() -> None:
    plan = _plan(rollback_plan="")

    checklist = ImplementationReadinessChecker().check(plan, _approved_review(plan), ImplementationReadinessConfig())

    assert checklist.ready is False
    assert checklist.status == "NOT_READY"
    assert "rollback_plan_defined" in checklist.missing_items


def test_allow_live_trading_changes_defaults_false() -> None:
    assert ImplementationReadinessConfig().allow_live_trading_changes is False


def test_no_auto_implementation_checklist_is_required() -> None:
    checklist = ImplementationReadinessChecker().check(
        _plan(auto_implementation_allowed=True),
        _approved_review(),
        ImplementationReadinessConfig(),
    )

    assert checklist.ready is False
    assert checklist.checklist_items["no_auto_implementation"] is False
    assert "no_auto_implementation" in checklist.missing_items


def test_explain_returns_readable_text() -> None:
    checker = ImplementationReadinessChecker()
    checklist = checker.check(_plan(), _approved_review(), ImplementationReadinessConfig())

    text = checker.explain(checklist)

    assert "Implementation readiness status:" in text
    assert "READY_FOR_HUMAN_WORK" in text
    assert "future human-reviewed coding work only" in text
    assert "no strategy rule was changed" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    checker = ImplementationReadinessChecker()
    checklist = checker.check(_plan(), _approved_review(), ImplementationReadinessConfig())
    text = checker.explain(checklist).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
