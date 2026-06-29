from __future__ import annotations

import json
from pathlib import Path

from ai.change_proposal import ChangeProposalConfig, ChangeProposalEngine
from storage.change_proposal_store import ChangeProposalStore, ChangeProposalStoreConfig


def _config(tmp_path: Path) -> ChangeProposalStoreConfig:
    return ChangeProposalStoreConfig(output_dir=str(tmp_path / "proposal_store"))


def _approval_record(request_id: str = "approval-risk-management-12345678") -> dict:
    return {
        "request_id": request_id,
        "suggestion_category": "RISK_MANAGEMENT",
        "suggestion_priority": "HIGH",
        "suggestion_text": "Review drawdown limits before changing any strategy rule.",
        "decision": "APPROVE",
        "approved": True,
        "allowed_to_apply": True,
        "reasons": ["A human approved this future reviewed change proposal"],
        "blocking_reasons": [],
    }


def _proposal(request_id: str = "approval-risk-management-12345678"):
    result = ChangeProposalEngine().create_from_approval_record(
        _approval_record(request_id),
        ChangeProposalConfig(),
    )
    assert result.proposal is not None
    return result.proposal


def test_append_proposal_creates_proposals_file(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = ChangeProposalStore().append_proposal(_proposal(), config)

    assert result.saved is True
    assert result.proposals_path is not None
    assert Path(result.proposals_path).exists()


def test_append_proposal_adds_one_proposal(tmp_path: Path) -> None:
    config = _config(tmp_path)
    proposal = _proposal()

    result = ChangeProposalStore().append_proposal(proposal, config)
    records = json.loads(Path(result.proposals_path or "").read_text(encoding="utf-8"))

    assert result.total_proposals == 1
    assert len(records) == 1
    assert records[0]["proposal_id"] == proposal.proposal_id
    assert records[0]["source_request_id"] == proposal.source_request_id


def test_multiple_proposals_are_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ChangeProposalStore()

    first = store.append_proposal(_proposal("approval-one"), config)
    second = store.append_proposal(_proposal("approval-two"), config)

    assert first.total_proposals == 1
    assert second.total_proposals == 2
    records = store.load_proposals(config)
    assert len(records) == 2
    assert records[0]["source_request_id"] == "approval-one"
    assert records[1]["source_request_id"] == "approval-two"


def test_load_proposals_returns_saved_proposals(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ChangeProposalStore()
    proposal = _proposal()
    store.append_proposal(proposal, config)

    records = store.load_proposals(config)

    assert len(records) == 1
    assert records[0]["status"] == "PROPOSED"
    assert records[0]["category"] == "RISK_MANAGEMENT"


def test_output_directory_is_created(tmp_path: Path) -> None:
    config = _config(tmp_path)
    ChangeProposalStore().append_proposal(_proposal(), config)

    assert Path(config.output_dir).exists()


def test_invalid_json_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True)
    (output_dir / config.proposals_filename).write_text("{not valid json", encoding="utf-8")

    result = ChangeProposalStore().append_proposal(_proposal(), config)

    assert result.saved is True
    assert result.total_proposals == 1
    assert len(ChangeProposalStore().load_proposals(config)) == 1


def test_missing_proposal_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)

    result = ChangeProposalStore().append_proposal(None, config)
    records = ChangeProposalStore().load_proposals(config)

    assert result.saved is True
    assert records[0]["proposal_id"] == "UNKNOWN"
    assert "Change proposal was not provided" in records[0]["blocking_reasons"]


def test_stored_proposal_has_auto_implementation_allowed_false(tmp_path: Path) -> None:
    config = _config(tmp_path)
    ChangeProposalStore().append_proposal(_proposal(), config)

    record = ChangeProposalStore().load_proposals(config)[0]

    assert record["auto_implementation_allowed"] is False


def test_stored_proposal_has_human_review_required_true(tmp_path: Path) -> None:
    config = _config(tmp_path)
    ChangeProposalStore().append_proposal(_proposal(), config)

    record = ChangeProposalStore().load_proposals(config)[0]

    assert record["human_review_required"] is True


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = ChangeProposalStore().append_proposal(_proposal(), config)

    text = ChangeProposalStore().explain(result)

    assert "Change proposal store:" in text
    assert "saved=True" in text
    assert "final human review" in text
    assert "no strategy rule is changed" in text
