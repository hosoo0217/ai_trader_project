"""Unit tests for order flow imbalance analyzer."""

from __future__ import annotations

from orderflow.footprint import FootprintCandle, FootprintLevel
from orderflow.imbalance import ImbalanceAnalyzer, ImbalanceConfig


def _make_candle(levels: list[FootprintLevel]) -> FootprintCandle:
    return FootprintCandle(
        time="2026-01-01 10:00:00",
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
        levels=levels,
    )


def test_detects_ask_imbalance() -> None:
    candle = _make_candle([FootprintLevel(price=100.0, bid_volume=20.0, ask_volume=80.0)])

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig(imbalance_ratio_threshold=3.0, min_volume=10.0))

    assert result.ask_imbalances == 1
    assert result.bid_imbalances == 0
    assert result.imbalances[0].imbalance_type == "ASK_IMBALANCE"


def test_detects_bid_imbalance() -> None:
    candle = _make_candle([FootprintLevel(price=100.0, bid_volume=90.0, ask_volume=20.0)])

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig(imbalance_ratio_threshold=3.0, min_volume=10.0))

    assert result.bid_imbalances == 1
    assert result.ask_imbalances == 0
    assert result.imbalances[0].imbalance_type == "BID_IMBALANCE"


def test_zero_bid_with_strong_ask_detects_ask_imbalance() -> None:
    candle = _make_candle([FootprintLevel(price=100.0, bid_volume=0.0, ask_volume=25.0)])

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig(min_volume=10.0))

    assert result.ask_imbalances == 1
    assert result.imbalances[0].ratio == float("inf")


def test_zero_ask_with_strong_bid_detects_bid_imbalance() -> None:
    candle = _make_candle([FootprintLevel(price=100.0, bid_volume=30.0, ask_volume=0.0)])

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig(min_volume=10.0))

    assert result.bid_imbalances == 1
    assert result.imbalances[0].ratio == float("inf")


def test_low_volume_ignored() -> None:
    candle = _make_candle([FootprintLevel(price=100.0, bid_volume=2.0, ask_volume=8.0)])

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig(min_volume=20.0))

    assert result.ask_imbalances == 0
    assert result.bid_imbalances == 0
    assert result.bias == "NEUTRAL"


def test_bullish_bias_from_more_ask_imbalances() -> None:
    candle = _make_candle(
        [
            FootprintLevel(price=100.0, bid_volume=10.0, ask_volume=60.0),
            FootprintLevel(price=101.0, bid_volume=15.0, ask_volume=50.0),
            FootprintLevel(price=99.0, bid_volume=90.0, ask_volume=20.0),
        ]
    )

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())

    assert result.ask_imbalances == 2
    assert result.bid_imbalances == 1
    assert result.bias == "BULLISH"


def test_bearish_bias_from_more_bid_imbalances() -> None:
    candle = _make_candle(
        [
            FootprintLevel(price=100.0, bid_volume=90.0, ask_volume=20.0),
            FootprintLevel(price=101.0, bid_volume=70.0, ask_volume=10.0),
            FootprintLevel(price=99.0, bid_volume=20.0, ask_volume=90.0),
        ]
    )

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())

    assert result.bid_imbalances == 2
    assert result.ask_imbalances == 1
    assert result.bias == "BEARISH"


def test_neutral_bias_from_equal_imbalance_count() -> None:
    candle = _make_candle(
        [
            FootprintLevel(price=100.0, bid_volume=90.0, ask_volume=20.0),
            FootprintLevel(price=101.0, bid_volume=20.0, ask_volume=90.0),
        ]
    )

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())

    assert result.ask_imbalances == 1
    assert result.bid_imbalances == 1
    assert result.bias == "NEUTRAL"


def test_empty_candle_returns_unknown() -> None:
    candle = _make_candle([])

    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())

    assert result.bias == "UNKNOWN"
    assert "No footprint levels available" in result.blocking_reasons


def test_explain_returns_readable_text() -> None:
    candle = _make_candle([FootprintLevel(price=100.0, bid_volume=20.0, ask_volume=80.0)])
    result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())

    text = ImbalanceAnalyzer().explain(result)

    assert "Order flow imbalance summary" in text
    assert "bias=" in text
    assert "ask_imbalances=" in text
