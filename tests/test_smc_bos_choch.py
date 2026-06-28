from __future__ import annotations

import pandas as pd

from smc.bos_choch import BOSCHOCHAnalyzer, BOSCHOCHConfig
from smc.market_structure import MarketStructureResult, SwingPoint


def _make_candles(closes: list[float], highs: list[float] | None = None, lows: list[float] | None = None) -> pd.DataFrame:
    if highs is None:
        highs = [value + 0.5 for value in closes]
    if lows is None:
        lows = [value - 0.5 for value in closes]

    opens = list(closes)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=len(closes), freq="h"),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
        }
    )


def _structure_result(
    bias: str,
    last_high_index: int = 3,
    last_high_price: float = 10.0,
    last_low_index: int = 4,
    last_low_price: float = 5.0,
) -> MarketStructureResult:
    high_prev = SwingPoint(index=1, time=None, price=9.0, kind="SWING_HIGH")
    high_last = SwingPoint(index=last_high_index, time=None, price=last_high_price, kind="SWING_HIGH")
    low_prev = SwingPoint(index=2, time=None, price=6.0, kind="SWING_LOW")
    low_last = SwingPoint(index=last_low_index, time=None, price=last_low_price, kind="SWING_LOW")
    return MarketStructureResult(
        structure_bias=bias,
        swing_highs=[high_prev, high_last],
        swing_lows=[low_prev, low_last],
        last_swing_high=high_last,
        last_swing_low=low_last,
        reasons=["fixture"],
        blocking_reasons=[],
    )


def test_bullish_bos_detected() -> None:
    candles = _make_candles(closes=[8, 9, 9.5, 10.0, 9.8, 10.2, 11.0])
    structure = _structure_result("BULLISH")

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig(require_close_break=True))

    assert result.latest_break is not None
    assert result.latest_break.direction == "BULLISH"
    assert result.latest_break.break_type == "BOS"


def test_bearish_bos_detected() -> None:
    candles = _make_candles(closes=[8, 7, 6.5, 6.0, 5.5, 4.8, 4.0])
    structure = _structure_result("BEARISH", last_high_price=11.0, last_low_price=5.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig(require_close_break=True))

    assert result.latest_break is not None
    assert result.latest_break.direction == "BEARISH"
    assert result.latest_break.break_type == "BOS"


def test_bullish_choch_detected() -> None:
    candles = _make_candles(closes=[8, 8.5, 9.0, 9.2, 9.5, 10.4, 10.8])
    structure = _structure_result("BEARISH", last_high_price=10.0, last_low_price=4.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig())

    assert result.latest_break is not None
    assert any(item.direction == "BULLISH" and item.break_type == "CHOCH" for item in result.breaks)


def test_bearish_choch_detected() -> None:
    candles = _make_candles(closes=[8, 8.2, 7.8, 7.0, 6.2, 4.9, 4.6])
    structure = _structure_result("BULLISH", last_high_price=12.0, last_low_price=5.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig())

    assert result.latest_break is not None
    assert any(item.direction == "BEARISH" and item.break_type == "CHOCH" for item in result.breaks)


def test_no_break_returns_neutral() -> None:
    candles = _make_candles(closes=[8, 8.5, 8.8, 9.0, 8.7, 8.9, 8.6])
    structure = _structure_result("NEUTRAL", last_high_price=10.0, last_low_price=5.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig())

    assert result.bias == "NEUTRAL"
    assert result.latest_break is None
    assert len(result.breaks) == 0


def test_missing_swing_data_returns_unknown() -> None:
    candles = _make_candles(closes=[8, 8.5, 9.0, 8.7, 8.9])
    structure = MarketStructureResult(structure_bias="UNKNOWN")

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig())

    assert result.bias == "UNKNOWN"
    assert len(result.blocking_reasons) > 0


def test_require_close_break_works() -> None:
    candles = _make_candles(
        closes=[8, 8.5, 9.0, 9.5, 9.8, 9.9, 9.95],
        highs=[8.3, 8.7, 9.2, 9.7, 10.2, 10.3, 10.1],
        lows=[7.7, 8.1, 8.6, 9.0, 9.4, 9.5, 9.6],
    )
    structure = _structure_result("BULLISH", last_high_price=10.0, last_low_price=5.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig(require_close_break=True))

    assert result.bias == "NEUTRAL"


def test_wick_break_works_when_require_close_break_is_false() -> None:
    candles = _make_candles(
        closes=[8, 8.5, 9.0, 9.5, 9.8, 9.9, 9.95],
        highs=[8.3, 8.7, 9.2, 9.7, 10.2, 10.3, 10.1],
        lows=[7.7, 8.1, 8.6, 9.0, 9.4, 9.5, 9.6],
    )
    structure = _structure_result("BULLISH", last_high_price=10.0, last_low_price=5.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig(require_close_break=False))

    assert result.latest_break is not None
    assert result.latest_break.direction == "BULLISH"


def test_buffer_prevents_weak_break() -> None:
    candles = _make_candles(closes=[8, 8.5, 9.0, 9.5, 10.05, 10.02, 9.95])
    structure = _structure_result("BULLISH", last_high_price=10.0, last_low_price=5.0)

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig(require_close_break=True, buffer=0.1))

    assert result.bias == "NEUTRAL"
    assert result.latest_break is None


def test_explain_returns_readable_text() -> None:
    candles = _make_candles(closes=[8, 9, 9.5, 10.0, 9.8, 10.2, 11.0])
    structure = _structure_result("BULLISH")

    result = BOSCHOCHAnalyzer().analyze(candles, structure, BOSCHOCHConfig())
    text = BOSCHOCHAnalyzer().explain(result)

    assert "SMC BOS/CHOCH" in text
    assert "breaks:" in text
