from __future__ import annotations

import json
from pathlib import Path

from ai.human_approval import APPROVE, NEEDS_REVIEW, REJECT, HumanApprovalConfig, HumanApprovalWorkflow
from ai.strategy_improvement import StrategyImprovementSuggestion
from storage.human_approval_log import HumanApprovalLogConfig, HumanApprovalLogStore


def _config(tmp_path: Path) -> HumanApprovalLogConfig:
    return HumanApprovalLogConfig(output_dir=str(tmp_path / "approval_logs"))


def _suggestion() -> StrategyImprovementSuggestion:
    return StrategyImprovementSuggestion(
        category="RISK_MANAGEMENT",
        priority="HIGH",
        suggestion="Review drawdown limits before changing any strategy rule.",
        reason="Drawdown review protects strategy research from weak pass-rate assumptions.",
        risk="Changing rules without review can expose capital to poor conditions.",
        human_approval_required=True,
    )


def _request_and_result(decision: str = APPROVE):
    workflow = HumanApprovalWorkflow()
    request = workflow.create_request(_suggestion(), HumanApprovalConfig())
    result = workflow.decide(request, decision, HumanApprovalConfig(), decided_by="human", notes="Reviewed")
    return request, result


def test_append_decision_creates_log_file(tmp_path: Path) -> None:
    config = _config(tmp_path)
    request, result = _request_and_result()

    log_result = HumanApprovalLogStore().append_decision(request, result, config)

    assert log_result.saved is True
    assert log_result.log_path is not None
    assert Path(log_result.log_path).exists()


def test_append_decision_adds_one_record(tmp_path: Path) -> None:
    config = _config(tmp_path)
    request, result = _request_and_result()

    log_result = HumanApprovalLogStore().append_decision(request, result, config)
    records = json.loads(Path(log_result.log_path or "").read_text(encoding="utf-8"))

    assert log_result.total_records == 1
    assert len(records) == 1
    assert records[0]["request_id"] == request.request_id
    assert records[0]["decision"] == "APPROVE"
    assert records[0]["approved"] is True


def test_multiple_decisions_are_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = HumanApprovalLogStore()
    first_request, first_result = _request_and_result(APPROVE)
    second_request, second_result = _request_and_result(REJECT)

    first_log = store.append_decision(first_request, first_result, config)
    second_log = store.append_decision(second_request, second_result, config)

    assert first_log.total_records == 1
    assert second_log.total_records == 2
    decisions = [record["decision"] for record in store.load_log(config)]
    assert decisions == ["APPROVE", "REJECT"]


def test_load_log_returns_saved_records(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = HumanApprovalLogStore()
    request, result = _request_and_result(NEEDS_REVIEW)
    store.append_decision(request, result, config)

    records = store.load_log(config)

    assert len(records) == 1
    assert records[0]["decision"] == "NEEDS_REVIEW"
    assert records[0]["request_status"] == "NEEDS_REVIEW"


def test_output_directory_is_created(tmp_path: Path) -> None:
    config = _config(tmp_path)
    request, result = _request_and_result()

    HumanApprovalLogStore().append_decision(request, result, config)

    assert Path(config.output_dir).exists()


def test_invalid_json_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True)
    (output_dir / config.log_filename).write_text("{not valid json", encoding="utf-8")
    request, result = _request_and_result()

    log_result = HumanApprovalLogStore().append_decision(request, result, config)

    assert log_result.saved is True
    assert log_result.total_records == 1
    assert len(HumanApprovalLogStore().load_log(config)) == 1


def test_missing_request_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _, result = _request_and_result()

    log_result = HumanApprovalLogStore().append_decision(None, result, config)
    records = HumanApprovalLogStore().load_log(config)

    assert log_result.saved is True
    assert records[0]["request_id"] != ""
    assert "Approval request was not provided" in records[0]["blocking_reasons"]


def test_missing_decision_result_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    request, _ = _request_and_result()

    log_result = HumanApprovalLogStore().append_decision(request, None, config)
    records = HumanApprovalLogStore().load_log(config)

    assert log_result.saved is True
    assert records[0]["decision"] == "UNKNOWN"
    assert records[0]["approved"] is False
    assert "Approval decision result was not provided" in records[0]["blocking_reasons"]


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    config = _config(tmp_path)
    request, result = _request_and_result()
    log_result = HumanApprovalLogStore().append_decision(request, result, config)

    text = HumanApprovalLogStore().explain(log_result)

    assert "Human approval decision log:" in text
    assert "saved=True" in text
    assert "no strategy rule is changed" in text
