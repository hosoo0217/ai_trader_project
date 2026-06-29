from __future__ import annotations

from ai.change_proposal import ChangeProposalConfig, ChangeProposalEngine


def _approval_record(decision: str = "APPROVE", approved: bool = True) -> dict:
    return {
        "request_id": "approval-risk-management-12345678",
        "suggestion_category": "RISK_MANAGEMENT",
        "suggestion_priority": "HIGH",
        "suggestion_text": "Review drawdown limits before changing any strategy rule.",
        "request_status": "APPROVED" if approved else decision,
        "decision": decision,
        "approved": approved,
        "allowed_to_apply": approved,
        "decided_by": "human",
        "decided_at": "2026-06-29T00:00:00+00:00",
        "notes": "Reviewed",
        "reasons": ["A human approved this future reviewed change proposal"],
        "blocking_reasons": [],
    }


def test_approved_approval_record_creates_proposal() -> None:
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(),
        ChangeProposalConfig(),
    )

    assert result.created is True
    assert result.status == "PROPOSAL_CREATED"
    assert result.proposal is not None
    assert result.proposal.source_request_id == "approval-risk-management-12345678"
    assert result.proposal.category == "RISK_MANAGEMENT"


def test_rejected_approval_record_does_not_create_proposal() -> None:
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(decision="REJECT", approved=False),
        ChangeProposalConfig(),
    )

    assert result.created is False
    assert result.status == "NO_APPROVED_DECISION"
    assert result.proposal is None


def test_needs_review_approval_record_does_not_create_proposal() -> None:
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(decision="NEEDS_REVIEW", approved=False),
        ChangeProposalConfig(),
    )

    assert result.created is False
    assert result.status == "NO_APPROVED_DECISION"
    assert result.proposal is None


def test_missing_approval_record_does_not_crash() -> None:
    result = ChangeProposalEngine().create_from_approval_record(None, ChangeProposalConfig())

    assert result.created is False
    assert result.status == "UNKNOWN"
    assert result.blocking_reasons


def test_proposal_status_is_proposed_when_created() -> None:
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(),
        ChangeProposalConfig(),
    )

    assert result.proposal is not None
    assert result.proposal.status == "PROPOSED"


def test_auto_implementation_allowed_is_false() -> None:
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(),
        ChangeProposalConfig(),
    )

    assert result.proposal is not None
    assert result.proposal.auto_implementation_allowed is False


def test_human_review_required_is_true() -> None:
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(),
        ChangeProposalConfig(),
    )

    assert result.proposal is not None
    assert result.proposal.human_review_required is True


def test_allow_auto_implementation_defaults_to_false() -> None:
    config = ChangeProposalConfig()

    assert config.allow_auto_implementation is False


def test_explain_returns_readable_text() -> None:
    engine = ChangeProposalEngine()
    result = engine.create_from_approval_record(_approval_record(), ChangeProposalConfig())

    text = engine.explain(result)

    assert "Change proposal status:" in text
    assert "final human review is required" in text
    assert "no strategy rule was changed" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    engine = ChangeProposalEngine()
    result = engine.create_from_approval_record(_approval_record(), ChangeProposalConfig())
    text = (engine.explain(result) + " " + (result.proposal.proposed_change if result.proposal else "")).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
