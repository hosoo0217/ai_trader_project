"""Tests for the research-only conditional cooldown A/B diagnostic module."""

from __future__ import annotations

import json

import pytest

from analysis.conditional_cooldown_ab_diagnostic import (
    ConditionalCooldownConfig,
    run_conditional_cooldown_ab_diagnostic,
)


def _snapshot(
    iteration_index: int,
    outcome: str,
    simulated_pnl: float,
    final_action: str = "BUY",
) -> dict[str, object]:
    return {
        "iteration_index": iteration_index,
        "final_action": final_action,
        "outcome": outcome,
        "simulated_pnl": simulated_pnl,
        "replay_orderflow_bias": "NEUTRAL",
        "replay_orderflow_confidence": 0.0,
    }


def _write_input(tmp_path, snapshots: list[dict[str, object]]):
    input_json = tmp_path / "per_entry_orderflow_replay_diagnostic.json"
    input_json.write_text(json.dumps({"executed_trade_replay_snapshots": snapshots}))
    return input_json


def _variant_map(report):
    return {variant.variant: variant for variant in report.variants}


def test_writes_research_only_json_and_markdown_reports(tmp_path) -> None:
    input_json = _write_input(
        tmp_path,
        [
            _snapshot(1, "WIN", 15.0),
            _snapshot(2, "LOSS", -10.0),
            _snapshot(3, "WIN", 15.0),
        ],
    )
    output_dir = tmp_path / "diagnostic_out"

    report = run_conditional_cooldown_ab_diagnostic(
        ConditionalCooldownConfig(
            input_json=input_json,
            output_dir=output_dir,
            dataset_name="unit dataset",
        )
    )

    payload = json.loads((output_dir / "conditional_cooldown_ab_diagnostic_report.json").read_text())
    text = (output_dir / "conditional_cooldown_ab_diagnostic_report.md").read_text()

    assert report.diagnostic_only is True
    assert report.orderflow_enforcement is False
    assert payload["diagnostic_only"] is True
    assert payload["orderflow_enforcement"] is False
    assert payload["dataset_name"] == "unit dataset"
    assert "No live trading, paper trading, broker connection" in text
    assert "Order Flow fields, when present in the input, are diagnostic labels only" in text
    assert "C3 detected loss-cluster-zone cooldown 10" in text


def test_baseline_metrics_use_all_executed_trade_snapshots(tmp_path) -> None:
    input_json = _write_input(
        tmp_path,
        [
            _snapshot(3, "LOSS", -10.0),
            _snapshot(1, "WIN", 15.0),
            _snapshot(2, "LOSS", -10.0),
            _snapshot(4, "WIN", 15.0),
            _snapshot(15, "LOSS", -10.0),
        ],
    )

    report = run_conditional_cooldown_ab_diagnostic(
        ConditionalCooldownConfig(input_json=input_json, output_dir=tmp_path / "out")
    )
    baseline = _variant_map(report)["A baseline"]

    assert baseline.kept_trades == 5
    assert baseline.blocked_trades == 0
    assert baseline.wins == 2
    assert baseline.losses == 3
    assert baseline.total_pnl == 0.0
    assert baseline.win_rate == 0.4
    assert baseline.profit_factor == 1.0
    assert baseline.max_drawdown == 20.0
    assert baseline.removed_winners == 0
    assert baseline.removed_losses == 0
    assert baseline.removed_pnl == 0.0


def test_global_post_loss_cooldown_blocks_only_after_kept_losses(tmp_path) -> None:
    input_json = _write_input(
        tmp_path,
        [
            _snapshot(1, "WIN", 15.0),
            _snapshot(2, "LOSS", -10.0),
            _snapshot(3, "LOSS", -10.0),
            _snapshot(4, "WIN", 15.0),
            _snapshot(15, "LOSS", -10.0),
        ],
    )

    report = run_conditional_cooldown_ab_diagnostic(
        ConditionalCooldownConfig(input_json=input_json, output_dir=tmp_path / "out")
    )
    variants = _variant_map(report)
    cooldown = variants["B1 global post-loss cooldown 3"]

    assert cooldown.kept_trades == 3
    assert cooldown.blocked_trades == 2
    assert cooldown.wins == 1
    assert cooldown.losses == 2
    assert cooldown.total_pnl == -5.0
    assert cooldown.removed_winners == 1
    assert cooldown.removed_losses == 1
    assert cooldown.removed_pnl == 5.0


def test_conditional_variants_separate_nearby_and_same_direction_losses(tmp_path) -> None:
    input_json = _write_input(
        tmp_path,
        [
            _snapshot(1, "LOSS", -10.0, "BUY"),
            _snapshot(5, "LOSS", -10.0, "SELL"),
            _snapshot(6, "WIN", 15.0, "BUY"),
            _snapshot(16, "WIN", 15.0, "BUY"),
        ],
    )

    report = run_conditional_cooldown_ab_diagnostic(
        ConditionalCooldownConfig(input_json=input_json, output_dir=tmp_path / "out")
    )
    variants = _variant_map(report)
    nearby = variants["C1 cooldown after two nearby losses"]
    same_direction = variants["C2 cooldown after same-direction nearby losses"]
    detected_zone = variants["C3 detected loss-cluster-zone cooldown 10"]

    assert nearby.blocked_trades == 1
    assert nearby.removed_winners == 1
    assert same_direction.blocked_trades == 0
    assert same_direction.removed_winners == 0
    assert detected_zone.blocked_trades == 1
    assert detected_zone.removed_winners == 1


def test_rejects_diagnostic_json_without_required_snapshots(tmp_path) -> None:
    input_json = tmp_path / "bad.json"
    input_json.write_text(json.dumps({"summary": {}}))

    with pytest.raises(ValueError, match="executed_trade_replay_snapshots"):
        run_conditional_cooldown_ab_diagnostic(
            ConditionalCooldownConfig(input_json=input_json, output_dir=tmp_path / "out")
        )


def test_rejects_snapshot_missing_required_trade_fields(tmp_path) -> None:
    input_json = _write_input(tmp_path, [{"iteration_index": 1, "outcome": "WIN"}])

    with pytest.raises(ValueError, match="missing required field"):
        run_conditional_cooldown_ab_diagnostic(
            ConditionalCooldownConfig(input_json=input_json, output_dir=tmp_path / "out")
        )
