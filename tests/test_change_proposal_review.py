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


def test_accept_marks_proposal_accepted_for_future_work() -> None:
    result = ChangeProposalReviewWorkflow().review(
        _proposal(),
        ACCEPT,
        ChangeProposalReviewConfig(),
        reviewed_by="human",
    )

    assert result.status == "ACCEPTED_FOR_FUTURE_WORK"
    assert result.accepted is True
    assert result.decision is not None
    assert result.decision.accepted_for_future_work is True


def test_accept_does_not_allow_implementation() -> None:
    result = ChangeProposalReviewWorkflow().review(
        _proposal(),
        ACCEPT,
        ChangeProposalReviewConfig(allow_auto_implementation=True),
    )

    assert result.implementation_allowed is False
    assert result.decision is not None
    assert result.decision.implementation_allowed is False


def test_reject_is_safe() -> None:
    result = ChangeProposalReviewWorkflow().review(_proposal(), REJECT, ChangeProposalReviewConfig())

    assert result.status == "REJECTED"
    assert result.accepted is False
    assert result.implementation_allowed is False
    assert result.blocking_reasons


def test_needs_more_data_is_safe() -> None:
    result = ChangeProposalReviewWorkflow().review(
        _proposal(),
        NEEDS_MORE_DATA,
        ChangeProposalReviewConfig(),
    )

    assert result.status == "NEEDS_MORE_DATA"
    assert result.accepted is False
    assert result.implementation_allowed is False
    assert result.blocking_reasons


def test_needs_backtest_is_safe() -> None:
    result = ChangeProposalReviewWorkflow().review(
        _proposal(),
        NEEDS_BACKTEST,
        ChangeProposalReviewConfig(),
    )

    assert result.status == "NEEDS_BACKTEST"
    assert result.accepted is False
    assert result.implementation_allowed is False
    assert result.blocking_reasons


def test_missing_proposal_does_not_crash() -> None:
    result = ChangeProposalReviewWorkflow().review(None, ACCEPT, ChangeProposalReviewConfig())

    assert result.status == "UNKNOWN"
    assert result.accepted is False
    assert result.implementation_allowed is False
    assert result.blocking_reasons


def test_allow_auto_implementation_defaults_to_false() -> None:
    config = ChangeProposalReviewConfig()

    assert config.allow_auto_implementation is False


def test_require_final_human_review_defaults_to_true() -> None:
    config = ChangeProposalReviewConfig()

    assert config.require_final_human_review is True


def test_explain_returns_readable_text() -> None:
    workflow = ChangeProposalReviewWorkflow()
    result = workflow.review(_proposal(), ACCEPT, ChangeProposalReviewConfig())

    text = workflow.explain(result)

    assert "Change proposal review status:" in text
    assert "does not implement it" in text
    assert "no strategy rule was changed" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    workflow = ChangeProposalReviewWorkflow()
    result = workflow.review(_proposal(), ACCEPT, ChangeProposalReviewConfig())
    text = workflow.explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
