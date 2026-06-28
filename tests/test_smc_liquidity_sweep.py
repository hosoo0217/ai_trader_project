from __future__ import annotations

import pandas as pd

from smc.liquidity_sweep import LiquiditySweepAnalyzer, LiquiditySweepConfig
from smc.market_structure import MarketStructureResult, SwingPoint


def _make_candles(highs: list[float], lows: list[float], closes: list[float]) -> pd.DataFrame:
    opens = list(closes)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=len(highs), freq="h"),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
        }
    )


def _structure_result(last_high_price: float = 10.0, last_low_price: float = 5.0) -> MarketStructureResult:
    high_prev = SwingPoint(index=1, time=None, price=9.0, kind="SWING_HIGH")
    high_last = SwingPoint(index=3, time=None, price=last_high_price, kind="SWING_HIGH")
    low_prev = SwingPoint(index=2, time=None, price=6.0, kind="SWING_LOW")
    low_last = SwingPoint(index=4, time=None, price=last_low_price, kind="SWING_LOW")
    return MarketStructureResult(
        structure_bias="NEUTRAL",
        swing_highs=[high_prev, high_last],
        swing_lows=[low_prev, low_last],
        last_swing_high=high_last,
        last_swing_low=low_last,
        reasons=["fixture"],
        blocking_reasons=[],
    )


def _structure_result_custom(
    prev_high_price: float,
    last_high_price: float,
    prev_low_price: float,
    last_low_price: float,
) -> MarketStructureResult:
    high_prev = SwingPoint(index=1, time=None, price=prev_high_price, kind="SWING_HIGH")
    high_last = SwingPoint(index=3, time=None, price=last_high_price, kind="SWING_HIGH")
    low_prev = SwingPoint(index=2, time=None, price=prev_low_price, kind="SWING_LOW")
    low_last = SwingPoint(index=4, time=None, price=last_low_price, kind="SWING_LOW")
    return MarketStructureResult(
        structure_bias="NEUTRAL",
        swing_highs=[high_prev, high_last],
        swing_lows=[low_prev, low_last],
        last_swing_high=high_last,
        last_swing_low=low_last,
        reasons=["fixture"],
        blocking_reasons=[],
    )


def test_detects_high_sweep() -> None:
    candles = _make_candles(
        highs=[8, 9, 10, 10, 9.5, 10.6, 9.8],
        lows=[7, 7.5, 8, 8.5, 8.2, 8.7, 8.6],
        closes=[7.8, 8.6, 9.5, 9.8, 9.2, 9.6, 9.1],
    )
    structure = _structure_result(last_high_price=10.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())

    assert any(item.sweep_type == "HIGH_SWEEP" for item in result.sweeps)


def test_detects_low_sweep() -> None:
    candles = _make_candles(
        highs=[8, 8.5, 9, 9.3, 9.0, 9.1, 9.2],
        lows=[6.5, 6.0, 5.8, 5.4, 5.2, 4.6, 5.3],
        closes=[7.5, 7.8, 8.1, 8.0, 7.9, 5.4, 5.8],
    )
    structure = _structure_result(last_high_price=12.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())

    assert any(item.sweep_type == "LOW_SWEEP" for item in result.sweeps)


def test_high_sweep_gives_bearish_bias() -> None:
    candles = _make_candles(
        highs=[8, 9, 10, 10, 9.5, 10.6, 9.8],
        lows=[7, 7.5, 8, 8.5, 8.2, 8.7, 8.6],
        closes=[7.8, 8.6, 9.5, 9.8, 9.2, 9.6, 9.1],
    )
    structure = _structure_result(last_high_price=10.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())

    assert result.latest_sweep is not None
    assert result.latest_sweep.sweep_type == "HIGH_SWEEP"
    assert result.bias == "BEARISH"


def test_low_sweep_gives_bullish_bias() -> None:
    candles = _make_candles(
        highs=[8, 8.5, 9, 9.3, 9.0, 9.1, 9.2],
        lows=[6.5, 6.0, 5.8, 5.4, 5.2, 4.6, 5.3],
        closes=[7.5, 7.8, 8.1, 8.0, 7.9, 5.4, 5.8],
    )
    structure = _structure_result_custom(
        prev_high_price=20.0,
        last_high_price=12.0,
        prev_low_price=6.0,
        last_low_price=5.0,
    )

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())

    assert result.latest_sweep is not None
    assert result.latest_sweep.sweep_type == "LOW_SWEEP"
    assert result.bias == "BULLISH"


def test_no_sweep_returns_neutral() -> None:
    candles = _make_candles(
        highs=[8, 8.5, 9, 9.3, 9.0, 9.1, 9.2],
        lows=[6.5, 6.0, 5.8, 5.6, 5.4, 5.3, 5.2],
        closes=[7.5, 7.8, 8.1, 8.0, 7.9, 7.8, 7.7],
    )
    structure = _structure_result_custom(
        prev_high_price=10.0,
        last_high_price=10.0,
        prev_low_price=4.8,
        last_low_price=5.0,
    )

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())

    assert result.bias == "NEUTRAL"
    assert result.latest_sweep is None


def test_missing_swing_data_returns_unknown() -> None:
    candles = _make_candles(
        highs=[8, 8.5, 9],
        lows=[6.5, 6.0, 5.8],
        closes=[7.5, 7.8, 8.1],
    )
    structure = MarketStructureResult(structure_bias="UNKNOWN")

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())

    assert result.bias == "UNKNOWN"
    assert len(result.blocking_reasons) > 0


def test_close_back_inside_requirement_works() -> None:
    candles = _make_candles(
        highs=[8, 9, 10, 10, 9.5, 10.6, 9.8],
        lows=[7, 7.5, 8, 8.5, 8.2, 8.7, 8.6],
        closes=[7.8, 8.6, 9.5, 9.8, 9.2, 10.2, 10.1],
    )
    structure = _structure_result(last_high_price=10.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(
        candles,
        structure,
        LiquiditySweepConfig(require_close_back_inside=True),
    )

    assert result.bias == "NEUTRAL"


def test_wick_only_sweep_works_when_require_close_back_inside_is_false() -> None:
    candles = _make_candles(
        highs=[8, 9, 10, 10, 9.5, 10.6, 9.8],
        lows=[7, 7.5, 8, 8.5, 8.2, 8.7, 8.6],
        closes=[7.8, 8.6, 9.5, 9.8, 9.2, 10.2, 10.1],
    )
    structure = _structure_result(last_high_price=10.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(
        candles,
        structure,
        LiquiditySweepConfig(require_close_back_inside=False),
    )

    assert result.latest_sweep is not None
    assert result.latest_sweep.sweep_type == "HIGH_SWEEP"


def test_buffer_prevents_weak_sweep() -> None:
    candles = _make_candles(
        highs=[8, 9, 10, 10, 9.5, 10.03, 9.8],
        lows=[7, 7.5, 8, 8.5, 8.2, 8.7, 8.6],
        closes=[7.8, 8.6, 9.5, 9.8, 9.2, 9.95, 9.1],
    )
    structure = _structure_result(last_high_price=10.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig(buffer=0.05))

    assert result.bias == "NEUTRAL"
    assert result.latest_sweep is None


def test_explain_returns_readable_text() -> None:
    candles = _make_candles(
        highs=[8, 9, 10, 10, 9.5, 10.6, 9.8],
        lows=[7, 7.5, 8, 8.5, 8.2, 8.7, 8.6],
        closes=[7.8, 8.6, 9.5, 9.8, 9.2, 9.6, 9.1],
    )
    structure = _structure_result(last_high_price=10.0, last_low_price=5.0)

    result = LiquiditySweepAnalyzer().analyze(candles, structure, LiquiditySweepConfig())
    text = LiquiditySweepAnalyzer().explain(result)

    assert "SMC liquidity sweep" in text
    assert "sweeps:" in text
