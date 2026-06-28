"""Unit tests for Order Flow footprint data-quality checks."""

from __future__ import annotations

from pathlib import Path

from orderflow.data_quality import OrderFlowDataQualityChecker, OrderFlowDataQualityConfig
from orderflow.footprint import FootprintCandle, FootprintLevel
from orderflow.sierra_chart_importer import SierraChartImportConfig, SierraChartImporter


def _sample_path(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _load_sample(name: str) -> list[FootprintCandle]:
    return SierraChartImporter().load_csv(_sample_path(name), SierraChartImportConfig())


def _make_candle(levels: list[FootprintLevel]) -> FootprintCandle:
    return FootprintCandle(
        time="2026-06-28T14:00:00Z",
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
        levels=levels,
    )


def test_valid_bullish_sample_passes() -> None:
    candles = _load_sample("sample_footprint_bullish.csv")

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())

    assert result.passed is True
    assert result.status == "PASSED"
    assert result.candle_count == 1
    assert result.total_levels == 4
    assert result.invalid_levels == 0


def test_valid_bearish_sample_passes() -> None:
    candles = _load_sample("sample_footprint_bearish.csv")

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())

    assert result.passed is True
    assert result.status == "PASSED"
    assert result.candle_count == 1
    assert result.total_levels == 4


def test_empty_candles_returns_empty_and_failed() -> None:
    result = OrderFlowDataQualityChecker().check([], OrderFlowDataQualityConfig())

    assert result.passed is False
    assert result.status == "EMPTY"
    assert "Order Flow data is empty" in result.blocking_reasons


def test_below_min_candles_fails() -> None:
    candles = [_make_candle([FootprintLevel(price=100.0, bid_volume=10.0, ask_volume=20.0)])]
    config = OrderFlowDataQualityConfig(min_candles=2)

    result = OrderFlowDataQualityChecker().check(candles, config)

    assert result.passed is False
    assert result.status == "FAILED"
    assert any("below minimum" in reason for reason in result.blocking_reasons)


def test_candle_with_no_levels_fails() -> None:
    candles = [_make_candle([])]

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())

    assert result.passed is False
    assert result.status == "FAILED"
    assert result.total_levels == 0
    assert any("level count 0" in reason for reason in result.blocking_reasons)


def test_negative_volume_levels_are_invalid() -> None:
    candles = [_make_candle([FootprintLevel(price=100.0, bid_volume=-1.0, ask_volume=20.0)])]

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig(max_invalid_level_ratio=1.0))

    assert result.passed is True
    assert result.status == "WARNING"
    assert result.invalid_levels == 1


def test_too_many_invalid_levels_fails() -> None:
    candles = [
        _make_candle(
            [
                FootprintLevel(price=100.0, bid_volume=-1.0, ask_volume=20.0),
                FootprintLevel(price=101.0, bid_volume=10.0, ask_volume=-2.0),
                FootprintLevel(price=102.0, bid_volume=10.0, ask_volume=20.0),
            ]
        )
    ]

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig(max_invalid_level_ratio=0.25))

    assert result.passed is False
    assert result.status == "FAILED"
    assert result.invalid_levels == 2
    assert result.invalid_level_ratio > 0.25


def test_minor_invalid_levels_returns_warning() -> None:
    candles = [
        _make_candle(
            [
                FootprintLevel(price=100.0, bid_volume=-1.0, ask_volume=20.0),
                FootprintLevel(price=101.0, bid_volume=10.0, ask_volume=20.0),
                FootprintLevel(price=102.0, bid_volume=11.0, ask_volume=21.0),
                FootprintLevel(price=103.0, bid_volume=12.0, ask_volume=22.0),
            ]
        )
    ]

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig(max_invalid_level_ratio=0.25))

    assert result.passed is True
    assert result.status == "WARNING"
    assert result.invalid_level_ratio == 0.25


def test_zero_volume_behavior_respects_config() -> None:
    candles = [_make_candle([FootprintLevel(price=100.0, bid_volume=0.0, ask_volume=0.0)])]

    allowed = OrderFlowDataQualityChecker().check(
        candles,
        OrderFlowDataQualityConfig(allow_zero_volume_levels=True),
    )
    blocked = OrderFlowDataQualityChecker().check(
        candles,
        OrderFlowDataQualityConfig(allow_zero_volume_levels=False),
    )

    assert allowed.passed is True
    assert allowed.status == "PASSED"
    assert blocked.passed is False
    assert blocked.status == "FAILED"
    assert blocked.invalid_levels == 1


def test_explain_returns_readable_text() -> None:
    candles = _load_sample("sample_footprint_bullish.csv")
    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())

    text = OrderFlowDataQualityChecker().explain(result)

    assert "Order Flow data quality" in text
    assert "status=PASSED" in text
    assert "candles=1" in text
