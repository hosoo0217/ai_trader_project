"""Unit tests for Order Flow replay reports."""

from __future__ import annotations

from orderflow.replay import OrderFlowReplayConfig, OrderFlowReplayEngine, OrderFlowReplayResult, OrderFlowReplayStep
from orderflow.replay_report import OrderFlowReplayReportGenerator
from orderflow.sierra_chart_importer import SierraChartImportConfig, SierraChartImporter


def _replay_csv(path: str) -> OrderFlowReplayResult:
    candles = SierraChartImporter().load_csv(path, SierraChartImportConfig())
    return OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())


def test_bullish_replay_report_counts_bullish_steps() -> None:
    replay_result = _replay_csv("data/sample_footprint_bullish.csv")

    report = OrderFlowReplayReportGenerator().generate(replay_result)

    assert report.total_steps == 1
    assert report.bullish_steps == 1
    assert report.bearish_steps == 0
    assert report.final_bias == "BULLISH"


def test_bearish_replay_report_counts_bearish_steps() -> None:
    replay_result = _replay_csv("data/sample_footprint_bearish.csv")

    report = OrderFlowReplayReportGenerator().generate(replay_result)

    assert report.total_steps == 1
    assert report.bearish_steps == 1
    assert report.bullish_steps == 0
    assert report.final_bias == "BEARISH"


def test_average_confidence_calculation() -> None:
    replay_result = OrderFlowReplayResult(
        steps=[
            OrderFlowReplayStep(0, None, 10.0, 10.0, "NEUTRAL", "NEUTRAL", "NEUTRAL", "BULLISH", 40.0),
            OrderFlowReplayStep(1, None, 20.0, 30.0, "NEUTRAL", "NEUTRAL", "NEUTRAL", "BULLISH", 80.0),
        ],
        final_bias="BULLISH",
        final_confidence=80.0,
        final_cvd=30.0,
        passed=True,
    )

    report = OrderFlowReplayReportGenerator().generate(replay_result)

    assert report.average_confidence == 60.0
    assert report.max_confidence == 80.0
    assert report.min_confidence == 40.0


def test_dominant_bias_calculation() -> None:
    replay_result = OrderFlowReplayResult(
        steps=[
            OrderFlowReplayStep(0, None, 10.0, 10.0, "NEUTRAL", "NEUTRAL", "NEUTRAL", "BULLISH", 60.0),
            OrderFlowReplayStep(1, None, 20.0, 30.0, "NEUTRAL", "NEUTRAL", "NEUTRAL", "BULLISH", 70.0),
            OrderFlowReplayStep(2, None, -5.0, 25.0, "NEUTRAL", "NEUTRAL", "NEUTRAL", "BEARISH", 30.0),
        ],
        final_bias="BULLISH",
        final_confidence=70.0,
        final_cvd=25.0,
        passed=True,
    )

    report = OrderFlowReplayReportGenerator().generate(replay_result)

    assert report.dominant_bias == "BULLISH"
    assert report.bullish_steps == 2
    assert report.bearish_steps == 1


def test_empty_replay_result_returns_unknown_safely() -> None:
    replay_result = OrderFlowReplayResult(steps=[], final_bias="UNKNOWN", passed=True)

    report = OrderFlowReplayReportGenerator().generate(replay_result)

    assert report.total_steps == 0
    assert report.dominant_bias == "UNKNOWN"
    assert report.final_bias == "UNKNOWN"
    assert report.average_confidence == 0.0


def test_failed_replay_result_creates_warning() -> None:
    replay_result = OrderFlowReplayResult(
        steps=[],
        final_bias="UNKNOWN",
        passed=False,
        reasons=["Replay blocked"],
        blocking_reasons=["Order Flow data is empty"],
    )

    report = OrderFlowReplayReportGenerator().generate(replay_result)

    assert report.total_steps == 0
    assert "Order Flow data is empty" in report.warnings


def test_explain_returns_readable_text() -> None:
    replay_result = _replay_csv("data/sample_footprint_bullish.csv")
    report = OrderFlowReplayReportGenerator().generate(replay_result)

    text = OrderFlowReplayReportGenerator().explain(report)

    assert "Order Flow replay report" in text
    assert "steps=1" in text
    assert "dominant_bias=BULLISH" in text
