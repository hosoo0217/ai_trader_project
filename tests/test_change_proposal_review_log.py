from __future__ import annotations

import json
from pathlib import Path

from ai.change_proposal import ChangeProposalConfig, ChangeProposalEngine
from ai.change_proposal_review import ACCEPT, NEEDS_BACKTEST, REJECT, ChangeProposalReviewConfig, ChangeProposalReviewWorkflow
from storage.change_proposal_review_log import ChangeProposalReviewLogConfig, ChangeProposalReviewLogStore


def _config(tmp_path: Path) -> ChangeProposalReviewLogConfig:
    return ChangeProposalReviewLogConfig(output_dir=str(tmp_path / "review_logs"))


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


def _proposal_and_review(decision: str = ACCEPT):
    proposal = _proposal()
    review = ChangeProposalReviewWorkflow().review(
        proposal,
        decision,
        ChangeProposalReviewConfig(),
        reviewed_by="human",
        notes="Reviewed",
    )
    return proposal, review


def test_append_review_creates_review_log_file(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal, review = _proposal_and_review()

    result = ChangeProposalReviewLogStore().append_review(proposal, review, config)

    assert result.saved is True
    assert result.log_path is not None
    assert Path(result.log_path).exists()


def test_append_review_adds_one_review_record(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal, review = _proposal_and_review()

    result = ChangeProposalReviewLogStore().append_review(proposal, review, config)
    records = json.loads(Path(result.log_path or "").read_text(encoding="utf-8"))

    assert result.total_records == 1
    assert len(records) == 1
    assert records[0]["proposal_id"] == proposal.proposal_id
    assert records[0]["review_decision"] == "ACCEPT"
    assert records[0]["review_status"] == "ACCEPTED_FOR_FUTURE_WORK"


def test_multiple_reviews_are_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ChangeProposalReviewLogStore()
    first_proposal, first_review = _proposal_and_review(ACCEPT)
    second_proposal, second_review = _proposal_and_review(REJECT)

    first_result = store.append_review(first_proposal, first_review, config)
    second_result = store.append_review(second_proposal, second_review, config)

    assert first_result.total_records == 1
    assert second_result.total_records == 2
    decisions = [record["review_decision"] for record in store.load_log(config)]
    assert decisions == ["ACCEPT", "REJECT"]


def test_load_log_returns_saved_review_records(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ChangeProposalReviewLogStore()
    proposal, review = _proposal_and_review(NEEDS_BACKTEST)
    store.append_review(proposal, review, config)

    records = store.load_log(config)

    assert len(records) == 1
    assert records[0]["review_decision"] == "NEEDS_BACKTEST"
    assert records[0]["review_status"] == "NEEDS_BACKTEST"


def test_output_directory_is_created(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal, review = _proposal_and_review()

    ChangeProposalReviewLogStore().append_review(proposal, review, config)

    assert Path(config.output_dir).exists()


def test_invalid_json_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True)
    (output_dir / config.log_filename).write_text("{not valid json", encoding="utf-8")
    proposal, review = _proposal_and_review()

    result = ChangeProposalReviewLogStore().append_review(proposal, review, config)

    assert result.saved is True
    assert result.total_records == 1
    assert len(ChangeProposalReviewLogStore().load_log(config)) == 1


def test_missing_proposal_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _, review = _proposal_and_review()

    result = ChangeProposalReviewLogStore().append_review(None, review, config)
    records = ChangeProposalReviewLogStore().load_log(config)

    assert result.saved is True
    assert records[0]["proposal_id"] == review.proposal_id
    assert "Change proposal was not provided" in records[0]["blocking_reasons"]


def test_missing_review_result_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal = _proposal()

    result = ChangeProposalReviewLogStore().append_review(proposal, None, config)
    records = ChangeProposalReviewLogStore().load_log(config)

    assert result.saved is True
    assert records[0]["review_decision"] == "UNKNOWN"
    assert records[0]["accepted"] is False
    assert "Change proposal review result was not provided" in records[0]["blocking_reasons"]


def test_accepted_review_still_has_implementation_allowed_false(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal, review = _proposal_and_review(ACCEPT)

    ChangeProposalReviewLogStore().append_review(proposal, review, config)
    record = ChangeProposalReviewLogStore().load_log(config)[0]

    assert record["accepted"] is True
    assert record["implementation_allowed"] is False


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal, review = _proposal_and_review()
    result = ChangeProposalReviewLogStore().append_review(proposal, review, config)

    text = ChangeProposalReviewLogStore().explain(result)

    assert "Change proposal review log:" in text
    assert "saved=True" in text
    assert "future work only" in text
    assert "no strategy rule is changed" in text


def test_output_does_not_contain_direct_trade_commands(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal, review = _proposal_and_review()
    result = ChangeProposalReviewLogStore().append_review(proposal, review, config)
    text = ChangeProposalReviewLogStore().explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
