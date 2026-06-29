from __future__ import annotations

import json
from pathlib import Path

from ai.implementation_final_review import (
    APPROVE_FOR_WORK,
    NEEDS_BACKTEST,
    REJECT,
    ImplementationFinalReviewConfig,
    ImplementationFinalReviewWorkflow,
)
from ai.implementation_plan import ImplementationPlan
from storage.implementation_final_review_log import (
    ImplementationFinalReviewLogConfig,
    ImplementationFinalReviewLogStore,
)


def _config(tmp_path: Path) -> ImplementationFinalReviewLogConfig:
    return ImplementationFinalReviewLogConfig(output_dir=str(tmp_path / "final_review_logs"))


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


def _plan_and_review(decision: str = APPROVE_FOR_WORK):
    plan = _plan()
    review = ImplementationFinalReviewWorkflow().review(
        plan,
        decision,
        ImplementationFinalReviewConfig(),
        reviewed_by="human",
        notes="Reviewed",
    )
    return plan, review


def test_append_review_creates_final_review_log_file(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan, review = _plan_and_review()

    result = ImplementationFinalReviewLogStore().append_review(plan, review, config)

    assert result.saved is True
    assert result.log_path is not None
    assert Path(result.log_path).exists()


def test_append_review_adds_one_final_review_record(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan, review = _plan_and_review()

    result = ImplementationFinalReviewLogStore().append_review(plan, review, config)
    records = json.loads(Path(result.log_path or "").read_text(encoding="utf-8"))

    assert result.total_records == 1
    assert len(records) == 1
    assert records[0]["plan_id"] == plan.plan_id
    assert records[0]["source_proposal_id"] == plan.source_proposal_id
    assert records[0]["final_review_decision"] == "APPROVE_FOR_WORK"
    assert records[0]["final_review_status"] == "APPROVED_FOR_FUTURE_WORK"


def test_multiple_final_reviews_are_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ImplementationFinalReviewLogStore()
    first_plan, first_review = _plan_and_review(APPROVE_FOR_WORK)
    second_plan, second_review = _plan_and_review(REJECT)

    first_result = store.append_review(first_plan, first_review, config)
    second_result = store.append_review(second_plan, second_review, config)

    assert first_result.total_records == 1
    assert second_result.total_records == 2
    decisions = [record["final_review_decision"] for record in store.load_log(config)]
    assert decisions == ["APPROVE_FOR_WORK", "REJECT"]


def test_load_log_returns_saved_final_review_records(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ImplementationFinalReviewLogStore()
    plan, review = _plan_and_review(NEEDS_BACKTEST)
    store.append_review(plan, review, config)

    records = store.load_log(config)

    assert len(records) == 1
    assert records[0]["final_review_decision"] == "NEEDS_BACKTEST"
    assert records[0]["final_review_status"] == "NEEDS_BACKTEST"


def test_output_directory_is_created(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan, review = _plan_and_review()

    ImplementationFinalReviewLogStore().append_review(plan, review, config)

    assert Path(config.output_dir).exists()


def test_invalid_json_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True)
    (output_dir / config.log_filename).write_text("{not valid json", encoding="utf-8")
    plan, review = _plan_and_review()

    result = ImplementationFinalReviewLogStore().append_review(plan, review, config)

    assert result.saved is True
    assert result.total_records == 1
    assert len(ImplementationFinalReviewLogStore().load_log(config)) == 1


def test_missing_plan_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _, review = _plan_and_review()

    result = ImplementationFinalReviewLogStore().append_review(None, review, config)
    records = ImplementationFinalReviewLogStore().load_log(config)

    assert result.saved is True
    assert records[0]["plan_id"] == review.plan_id
    assert "Implementation plan was not provided" in records[0]["blocking_reasons"]


def test_missing_final_review_result_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan = _plan()

    result = ImplementationFinalReviewLogStore().append_review(plan, None, config)
    records = ImplementationFinalReviewLogStore().load_log(config)

    assert result.saved is True
    assert records[0]["final_review_decision"] == "UNKNOWN"
    assert records[0]["approved_for_work"] is False
    assert "Implementation final review result was not provided" in records[0]["blocking_reasons"]


def test_approve_for_work_record_has_implementation_allowed_now_false(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan, review = _plan_and_review(APPROVE_FOR_WORK)

    ImplementationFinalReviewLogStore().append_review(plan, review, config)
    record = ImplementationFinalReviewLogStore().load_log(config)[0]

    assert record["approved_for_work"] is True
    assert record["implementation_allowed_now"] is False


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan, review = _plan_and_review()
    result = ImplementationFinalReviewLogStore().append_review(plan, review, config)

    text = ImplementationFinalReviewLogStore().explain(result)

    assert "Implementation final review log:" in text
    assert "saved=True" in text
    assert "future human-reviewed work only" in text
    assert "no strategy rule is changed" in text


def test_output_does_not_contain_direct_trade_commands(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan, review = _plan_and_review()
    result = ImplementationFinalReviewLogStore().append_review(plan, review, config)
    text = ImplementationFinalReviewLogStore().explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
