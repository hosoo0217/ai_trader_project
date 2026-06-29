from __future__ import annotations

from ai.change_proposal import ChangeProposalConfig, ChangeProposalEngine
from ai.change_proposal_review import (
    ACCEPT,
    NEEDS_BACKTEST,
    NEEDS_MORE_DATA,
    REJECT,
    ChangeProposalReviewConfig,
    ChangeProposalReviewWorkflow,
)
from ai.implementation_plan import ImplementationPlanConfig, ImplementationPlanWorkflow


def _proposal():
    result = ChangeProposalEngine().create_from_approval_record(
        {
            "request_id": "approval-risk-management-12345678",
            "suggestion_category": "RISK_MANAGEMENT",
            "suggestion_priority": "HIGH",
            "suggestion_text": "Review drawdown limits before changing any strategy rule.",
            "decision": "APPROVE",
            "approved": True,
            "allowed_to_apply": True,
            "reasons": ["A human approved this future reviewed change proposal"],
            "blocking_reasons": [],
        },
        ChangeProposalConfig(),
    )
    assert result.proposal is not None
    return result.proposal


def _review(decision: str = ACCEPT):
    proposal = _proposal()
    return ChangeProposalReviewWorkflow().review(proposal, decision, ChangeProposalReviewConfig())


def test_accepted_review_creates_implementation_plan() -> None:
    proposal = _proposal()
    review = ChangeProposalReviewWorkflow().review(proposal, ACCEPT, ChangeProposalReviewConfig())

    result = ImplementationPlanWorkflow().create_from_review(proposal, review, ImplementationPlanConfig())

    assert result.created is True
    assert result.status == "PLAN_CREATED"
    assert result.plan is not None
    assert result.plan.source_proposal_id == proposal.proposal_id


def test_rejected_review_does_not_create_plan() -> None:
    result = ImplementationPlanWorkflow().create_from_review(
        _proposal(),
        _review(REJECT),
        ImplementationPlanConfig(),
    )

    assert result.created is False
    assert result.status == "NO_ACCEPTED_REVIEW"
    assert result.plan is None


def test_needs_more_data_review_does_not_create_plan() -> None:
    result = ImplementationPlanWorkflow().create_from_review(
        _proposal(),
        _review(NEEDS_MORE_DATA),
        ImplementationPlanConfig(),
    )

    assert result.created is False
    assert result.status == "NO_ACCEPTED_REVIEW"
    assert result.plan is None


def test_needs_backtest_review_creates_safe_blocked_result() -> None:
    result = ImplementationPlanWorkflow().create_from_review(
        _proposal(),
        _review(NEEDS_BACKTEST),
        ImplementationPlanConfig(),
    )

    assert result.created is False
    assert result.status == "NEEDS_BACKTEST"
    assert result.plan is None
    assert result.blocking_reasons


def test_missing_proposal_does_not_crash() -> None:
    result = ImplementationPlanWorkflow().create_from_review(None, _review(), ImplementationPlanConfig())

    assert result.created is False
    assert result.status == "UNKNOWN"
    assert result.blocking_reasons


def test_missing_review_does_not_crash() -> None:
    result = ImplementationPlanWorkflow().create_from_review(_proposal(), None, ImplementationPlanConfig())

    assert result.created is False
    assert result.status == "UNKNOWN"
    assert result.blocking_reasons


def test_plan_has_auto_implementation_allowed_false() -> None:
    result = ImplementationPlanWorkflow().create_from_review(
        _proposal(),
        _review(ACCEPT),
        ImplementationPlanConfig(allow_auto_implementation=True),
    )

    assert result.plan is not None
    assert result.plan.auto_implementation_allowed is False


def test_plan_has_human_final_approval_required_true() -> None:
    result = ImplementationPlanWorkflow().create_from_review(_proposal(), _review(ACCEPT), ImplementationPlanConfig())

    assert result.plan is not None
    assert result.plan.human_final_approval_required is True


def test_plan_includes_required_tests() -> None:
    result = ImplementationPlanWorkflow().create_from_review(_proposal(), _review(ACCEPT), ImplementationPlanConfig())

    assert result.plan is not None
    assert "unit tests" in result.plan.required_tests
    assert "regression tests" in result.plan.required_tests
    assert "backtest comparison" in result.plan.required_tests
    assert "safety gate tests" in result.plan.required_tests


def test_plan_includes_risk_checks() -> None:
    result = ImplementationPlanWorkflow().create_from_review(_proposal(), _review(ACCEPT), ImplementationPlanConfig())

    assert result.plan is not None
    assert "drawdown check" in result.plan.risk_checks
    assert "capital protection check" in result.plan.risk_checks
    assert "session/news/spread filter check" in result.plan.risk_checks
    assert "no live trading confirmation" in result.plan.risk_checks


def test_explain_returns_readable_text() -> None:
    workflow = ImplementationPlanWorkflow()
    result = workflow.create_from_review(_proposal(), _review(ACCEPT), ImplementationPlanConfig())

    text = workflow.explain(result)

    assert "Implementation plan status:" in text
    assert "planning only" in text
    assert "no strategy rule was changed" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    workflow = ImplementationPlanWorkflow()
    result = workflow.create_from_review(_proposal(), _review(ACCEPT), ImplementationPlanConfig())
    plan_text = " ".join(result.plan.proposed_steps + result.plan.required_tests + result.plan.risk_checks) if result.plan else ""
    text = (workflow.explain(result) + " " + plan_text).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
