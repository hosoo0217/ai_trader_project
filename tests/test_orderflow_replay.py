"""Unit tests for Order Flow CSV replay."""

from __future__ import annotations

from orderflow.footprint import FootprintCandle
from orderflow.replay import OrderFlowReplayConfig, OrderFlowReplayEngine
from orderflow.sierra_chart_importer import SierraChartImportConfig, SierraChartImporter


def _load(path: str) -> list[FootprintCandle]:
    return SierraChartImporter().load_csv(path, SierraChartImportConfig())


def test_replay_bullish_sample_returns_steps() -> None:
    candles = _load("data/sample_footprint_bullish.csv")

    result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())

    assert result.passed is True
    assert len(result.steps) == 1
    assert result.final_bias == "BULLISH"
    assert result.steps[0].orderflow_bias == "BULLISH"


def test_replay_bearish_sample_returns_steps() -> None:
    candles = _load("data/sample_footprint_bearish.csv")

    result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())

    assert result.passed is True
    assert len(result.steps) == 1
    assert result.final_bias == "BEARISH"
    assert result.steps[0].orderflow_bias == "BEARISH"


def test_final_cvd_is_calculated() -> None:
    candles = _load("data/sierra_chart_footprint_template.csv")

    result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())

    assert result.final_cvd > 0.0
    assert result.final_cvd == result.steps[-1].cumulative_delta


def test_each_step_has_orderflow_bias() -> None:
    candles = _load("data/sierra_chart_footprint_template.csv")

    result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())

    assert len(result.steps) == 2
    assert all(step.orderflow_bias in {"BULLISH", "BEARISH", "NEUTRAL", "UNKNOWN"} for step in result.steps)


def test_max_steps_limits_replay_length() -> None:
    candles = _load("data/sierra_chart_footprint_template.csv")

    result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig(max_steps=1))

    assert result.passed is True
    assert len(result.steps) == 1
    assert "Replay limited to max_steps=1" in result.reasons


def test_empty_candles_return_failed_result_safely() -> None:
    result = OrderFlowReplayEngine().replay([], OrderFlowReplayConfig())

    assert result.passed is False
    assert result.steps == []
    assert result.data_quality_status == "EMPTY"
    assert "Order Flow data is empty" in result.blocking_reasons


def test_invalid_csv_does_not_crash(tmp_path) -> None:
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("not,a,footprint\n1,2,3\n", encoding="utf-8")

    result = OrderFlowReplayEngine().replay_csv(str(invalid_csv), OrderFlowReplayConfig())

    assert result.passed is False
    assert result.steps == []
    assert result.data_quality_status == "EMPTY"


def test_data_quality_failure_blocks_replay() -> None:
    bad_candle = FootprintCandle(
        time="2026-06-26T14:00:00Z",
        open=100.0,
        high=100.0,
        low=100.0,
        close=100.0,
        levels=[],
    )

    result = OrderFlowReplayEngine().replay([bad_candle], OrderFlowReplayConfig())

    assert result.passed is False
    assert result.steps == []
    assert result.data_quality_status == "FAILED"
    assert any("level count 0" in reason for reason in result.blocking_reasons)


def test_missing_csv_path_does_not_crash() -> None:
    result = OrderFlowReplayEngine().replay_csv("data/does_not_exist.csv", OrderFlowReplayConfig())

    assert result.passed is False
    assert result.steps == []
    assert result.data_quality_status == "EMPTY"


def test_explain_returns_readable_text() -> None:
    candles = _load("data/sample_footprint_bullish.csv")
    result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())

    text = OrderFlowReplayEngine().explain(result)

    assert "Order Flow replay" in text
    assert "steps=1" in text
    assert "final_bias=BULLISH" in text

def test_incremental_replay_matches_standard_replay_snapshots() -> None:
    candles = _load("data/sierra_chart_footprint_template.csv")
    config = OrderFlowReplayConfig(minimum_confidence=50.0)

    standard = OrderFlowReplayEngine().replay(candles, config)
    incremental = OrderFlowReplayEngine().replay_incremental(candles, config)

    assert incremental.passed == standard.passed
    assert incremental.final_bias == standard.final_bias
    assert incremental.final_confidence == standard.final_confidence
    assert incremental.final_cvd == standard.final_cvd
    assert len(incremental.steps) == len(standard.steps)

    for incremental_step, standard_step in zip(incremental.steps, standard.steps):
        assert incremental_step.index == standard_step.index
        assert incremental_step.time == standard_step.time
        assert incremental_step.candle_delta == standard_step.candle_delta
        assert incremental_step.cumulative_delta == standard_step.cumulative_delta
        assert incremental_step.delta_direction == standard_step.delta_direction
        assert incremental_step.imbalance_bias == standard_step.imbalance_bias
        assert incremental_step.absorption_bias == standard_step.absorption_bias
        assert incremental_step.orderflow_bias == standard_step.orderflow_bias
        assert incremental_step.orderflow_confidence == standard_step.orderflow_confidence
