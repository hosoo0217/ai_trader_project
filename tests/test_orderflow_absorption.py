"""Unit tests for order flow absorption analyzer."""

from __future__ import annotations

from orderflow.absorption import AbsorptionAnalyzer, AbsorptionConfig
from orderflow.footprint import FootprintCandle, FootprintLevel


def _make_candle(
    open_price: float,
    high: float,
    low: float,
    close: float,
    bid: float,
    ask: float,
) -> FootprintCandle:
    return FootprintCandle(
        time="2026-01-01 10:00:00",
        open=open_price,
        high=high,
        low=low,
        close=close,
        levels=[FootprintLevel(price=close, bid_volume=bid, ask_volume=ask)],
    )


def test_detects_buy_absorption() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=102.0,
        bid=250.0,
        ask=50.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig(high_volume_threshold=100.0))

    assert result.bias == "BULLISH"
    assert result.signal is not None
    assert result.signal.signal_type == "BUY_ABSORPTION"
    assert result.signal.direction == "BULLISH"
    assert result.signal.delta == -200.0


def test_detects_sell_absorption() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=98.0,
        bid=50.0,
        ask=250.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig(high_volume_threshold=100.0))

    assert result.bias == "BEARISH"
    assert result.signal is not None
    assert result.signal.signal_type == "SELL_ABSORPTION"
    assert result.signal.direction == "BEARISH"
    assert result.signal.delta == 200.0


def test_no_absorption_returns_neutral() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=109.0,
        bid=100.0,
        ask=100.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig())

    assert result.bias == "NEUTRAL"
    assert result.signal is not None
    assert result.signal.signal_type == "NO_ABSORPTION"


def test_low_volume_does_not_trigger_absorption() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=98.0,
        bid=5.0,
        ask=20.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig(high_volume_threshold=100.0))

    assert result.bias == "NEUTRAL"
    assert result.signal.signal_type == "NO_ABSORPTION"


def test_large_body_does_not_trigger_absorption() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=108.0,
        bid=50.0,
        ask=250.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig(high_volume_threshold=100.0))

    assert result.bias == "NEUTRAL"
    assert result.signal.signal_type == "NO_ABSORPTION"


def test_zero_range_candle_does_not_crash() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=100.0,
        low=100.0,
        close=100.0,
        bid=250.0,
        ask=50.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig())

    assert result.bias == "NEUTRAL"
    assert result.signal.signal_type == "NO_ABSORPTION"
    assert "Candle range is zero" in result.blocking_reasons


def test_empty_footprint_levels_do_not_crash() -> None:
    candle = FootprintCandle(
        time=None,
        open=100.0,
        high=110.0,
        low=90.0,
        close=100.0,
        levels=[],
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig())

    assert result.bias == "NEUTRAL"
    assert result.signal.signal_type == "NO_ABSORPTION"
    assert "No footprint levels available" in result.blocking_reasons


def test_negative_volume_is_handled_safely() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=98.0,
        bid=-50.0,
        ask=250.0,
    )

    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig(high_volume_threshold=100.0))

    assert result.signal is not None
    assert result.signal.total_volume == 250.0
    assert "Negative volume was treated as zero" in result.reasons


def test_explain_returns_readable_text() -> None:
    candle = _make_candle(
        open_price=100.0,
        high=110.0,
        low=90.0,
        close=98.0,
        bid=50.0,
        ask=250.0,
    )
    result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig(high_volume_threshold=100.0))

    text = AbsorptionAnalyzer().explain(result)

    assert "Order flow absorption summary" in text
    assert "SELL_ABSORPTION" in text
    assert "bias=BEARISH" in text
