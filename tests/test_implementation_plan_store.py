from __future__ import annotations

import json
from pathlib import Path

from ai.change_proposal import ChangeProposalConfig, ChangeProposalEngine
from ai.change_proposal_review import ACCEPT, ChangeProposalReviewConfig, ChangeProposalReviewWorkflow
from ai.implementation_plan import ImplementationPlanConfig, ImplementationPlanWorkflow
from storage.implementation_plan_store import ImplementationPlanStore, ImplementationPlanStoreConfig


def _config(tmp_path: Path) -> ImplementationPlanStoreConfig:
    return ImplementationPlanStoreConfig(output_dir=str(tmp_path / "plan_store"))


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


def _plan():
    proposal = _proposal()
    review = ChangeProposalReviewWorkflow().review(proposal, ACCEPT, ChangeProposalReviewConfig())
    result = ImplementationPlanWorkflow().create_from_review(
        proposal,
        review,
        ImplementationPlanConfig(),
    )
    assert result.plan is not None
    return result.plan


def test_append_plan_creates_plans_file(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = ImplementationPlanStore().append_plan(_plan(), config)

    assert result.saved is True
    assert result.plans_path is not None
    assert Path(result.plans_path).exists()


def test_append_plan_adds_one_plan(tmp_path: Path) -> None:
    config = _config(tmp_path)
    plan = _plan()

    result = ImplementationPlanStore().append_plan(plan, config)
    records = json.loads(Path(result.plans_path or "").read_text(encoding="utf-8"))

    assert result.total_plans == 1
    assert len(records) == 1
    assert records[0]["plan_id"] == plan.plan_id
    assert records[0]["source_proposal_id"] == plan.source_proposal_id


def test_multiple_plans_are_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ImplementationPlanStore()

    first = store.append_plan(_plan(), config)
    second = store.append_plan(_plan(), config)

    assert first.total_plans == 1
    assert second.total_plans == 2
    assert len(store.load_plans(config)) == 2


def test_load_plans_returns_saved_plans(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = ImplementationPlanStore()
    store.append_plan(_plan(), config)

    records = store.load_plans(config)

    assert len(records) == 1
    assert records[0]["status"] == "PLANNED"
    assert records[0]["category"] == "RISK_MANAGEMENT"


def test_output_directory_is_created(tmp_path: Path) -> None:
    config = _config(tmp_path)

    ImplementationPlanStore().append_plan(_plan(), config)

    assert Path(config.output_dir).exists()


def test_invalid_json_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True)
    (output_dir / config.plans_filename).write_text("{not valid json", encoding="utf-8")

    result = ImplementationPlanStore().append_plan(_plan(), config)

    assert result.saved is True
    assert result.total_plans == 1
    assert len(ImplementationPlanStore().load_plans(config)) == 1


def test_missing_plan_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)

    result = ImplementationPlanStore().append_plan(None, config)
    records = ImplementationPlanStore().load_plans(config)

    assert result.saved is True
    assert records[0]["plan_id"] == "UNKNOWN"
    assert "Implementation plan was not provided" in records[0]["blocking_reasons"]


def test_stored_plan_has_auto_implementation_allowed_false(tmp_path: Path) -> None:
    config = _config(tmp_path)
    ImplementationPlanStore().append_plan(_plan(), config)

    record = ImplementationPlanStore().load_plans(config)[0]

    assert record["auto_implementation_allowed"] is False


def test_stored_plan_has_human_final_approval_required_true(tmp_path: Path) -> None:
    config = _config(tmp_path)
    ImplementationPlanStore().append_plan(_plan(), config)

    record = ImplementationPlanStore().load_plans(config)[0]

    assert record["human_final_approval_required"] is True


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = ImplementationPlanStore().append_plan(_plan(), config)

    text = ImplementationPlanStore().explain(result)

    assert "Implementation plan store:" in text
    assert "saved=True" in text
    assert "future human-reviewed work" in text
    assert "no strategy rule is changed" in text


def test_output_does_not_contain_direct_trade_commands(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = ImplementationPlanStore().append_plan(_plan(), config)
    text = ImplementationPlanStore().explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
