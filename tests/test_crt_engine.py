from __future__ import annotations

import pandas as pd

from crt.crt_engine import CRTConfig, CRTEngine


def _make_candles(
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=len(opens), freq="h"),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
        }
    )


def test_detects_low_manipulation() -> None:
    candles = _make_candles([10, 11], [20, 19], [10, 9], [15, 11])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert any(signal.signal_type == "LOW_MANIPULATION" for signal in result.signals)


def test_detects_high_manipulation() -> None:
    candles = _make_candles([10, 11], [20, 21], [10, 11], [15, 19])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert any(signal.signal_type == "HIGH_MANIPULATION" for signal in result.signals)


def test_detects_bullish_expansion() -> None:
    candles = _make_candles([10, 11], [20, 22], [10, 11], [15, 21])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert any(signal.signal_type == "BULLISH_EXPANSION" for signal in result.signals)


def test_detects_bearish_expansion() -> None:
    candles = _make_candles([10, 11], [20, 11], [10, 8], [15, 9])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert any(signal.signal_type == "BEARISH_EXPANSION" for signal in result.signals)


def test_low_manipulation_gives_bullish_bias() -> None:
    candles = _make_candles([10, 11], [20, 19], [10, 9], [15, 11])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert result.bias == "BULLISH"


def test_high_manipulation_gives_bearish_bias() -> None:
    candles = _make_candles([10, 11], [20, 21], [10, 11], [15, 19])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert result.bias == "BEARISH"


def test_no_signal_returns_neutral() -> None:
    candles = _make_candles([10, 11], [20, 19.5], [10, 10.2], [15, 15.5])
    result = CRTEngine().analyze(candles, CRTConfig())

    assert result.bias == "NEUTRAL"
    assert result.latest_signal is None


def test_missing_columns_returns_unknown() -> None:
    candles = pd.DataFrame({"high": [20, 21], "low": [10, 9], "close": [15, 11]})
    result = CRTEngine().analyze(candles, CRTConfig())

    assert result.bias == "UNKNOWN"


def test_not_enough_candles_returns_unknown() -> None:
    candles = _make_candles([10], [20], [10], [15])
    result = CRTEngine().analyze(candles, CRTConfig(reference_candle_offset=1))

    assert result.bias == "UNKNOWN"


def test_close_back_inside_requirement_works() -> None:
    candles = _make_candles([10, 11], [20, 19], [10, 9], [15, 9.5])
    result = CRTEngine().analyze(candles, CRTConfig(require_close_back_inside=True))

    assert not any(signal.signal_type == "LOW_MANIPULATION" for signal in result.signals)


def test_buffer_prevents_weak_manipulation() -> None:
    candles = _make_candles([10, 11], [20, 19], [10, 9.98], [15, 11])
    result = CRTEngine().analyze(candles, CRTConfig(buffer=0.05))

    assert not any(signal.signal_type == "LOW_MANIPULATION" for signal in result.signals)


def test_explain_returns_readable_text() -> None:
    candles = _make_candles([10, 11], [20, 19], [10, 9], [15, 11])
    result = CRTEngine().analyze(candles, CRTConfig())
    text = CRTEngine().explain(result)

    assert "CRT context" in text
    assert "signals:" in text
