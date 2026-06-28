"""Unit tests for order flow delta/CVD analyzer."""

from __future__ import annotations

from orderflow.delta_cvd import DeltaCVDAnalyzer, DeltaCVDConfig
from orderflow.footprint import FootprintCandle, FootprintLevel


def _make_candle(time_value: str, bid: float, ask: float) -> FootprintCandle:
    return FootprintCandle(
        time=time_value,
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.0,
        levels=[FootprintLevel(price=100.0, bid_volume=bid, ask_volume=ask)],
    )


def test_calculates_single_candle_delta() -> None:
    candles = [_make_candle("2026-01-01 10:00:00", bid=20.0, ask=50.0)]

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=10.0))

    assert len(result.points) == 1
    assert result.points[0].delta == 30.0


def test_calculates_cumulative_delta_across_multiple_candles() -> None:
    candles = [
        _make_candle("2026-01-01 10:00:00", bid=20.0, ask=50.0),
        _make_candle("2026-01-01 10:05:00", bid=40.0, ask=10.0),
        _make_candle("2026-01-01 10:10:00", bid=10.0, ask=30.0),
    ]

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=10.0))

    assert result.points[0].cumulative_delta == 30.0
    assert result.points[1].cumulative_delta == 0.0
    assert result.points[2].cumulative_delta == 20.0


def test_buying_pressure_detection() -> None:
    candles = [_make_candle("2026-01-01 10:00:00", bid=10.0, ask=200.0)]

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=100.0))

    assert result.latest_direction == "BUYING_PRESSURE"


def test_selling_pressure_detection() -> None:
    candles = [_make_candle("2026-01-01 10:00:00", bid=250.0, ask=10.0)]

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=100.0))

    assert result.latest_direction == "SELLING_PRESSURE"


def test_neutral_delta_detection() -> None:
    candles = [_make_candle("2026-01-01 10:00:00", bid=100.0, ask=120.0)]

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=100.0))

    assert result.latest_direction == "NEUTRAL"


def test_empty_candles_do_not_crash() -> None:
    result = DeltaCVDAnalyzer().analyze([], DeltaCVDConfig())

    assert result.points == []
    assert result.latest_delta is None
    assert result.final_cvd == 0.0


def test_final_cvd_is_correct() -> None:
    candles = [
        _make_candle("2026-01-01 10:00:00", bid=10.0, ask=30.0),
        _make_candle("2026-01-01 10:05:00", bid=25.0, ask=5.0),
    ]

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=10.0))

    assert result.final_cvd == 0.0


def test_explain_returns_readable_text() -> None:
    candles = [_make_candle("2026-01-01 10:00:00", bid=10.0, ask=30.0)]
    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=10.0))

    text = DeltaCVDAnalyzer().explain(result)

    assert "Delta/CVD summary" in text
    assert "final_cvd=" in text
