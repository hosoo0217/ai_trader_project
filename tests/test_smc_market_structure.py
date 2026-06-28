from __future__ import annotations

import pandas as pd

from smc.market_structure import MarketStructureAnalyzer, MarketStructureConfig


def _make_candles(highs: list[float], lows: list[float]) -> pd.DataFrame:
    opens = [(high + low) / 2.0 for high, low in zip(highs, lows)]
    closes = list(opens)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=len(highs), freq="h"),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
        }
    )


def test_detects_swing_highs() -> None:
    candles = _make_candles(
        highs=[1, 2, 4, 2, 1, 2, 6, 2, 1],
        lows=[0, 0, 0, 0, 0, 0, 0, 0, 0],
    )
    analyzer = MarketStructureAnalyzer()

    swings = analyzer.find_swing_highs(candles, MarketStructureConfig(swing_lookback=1))

    assert len(swings) == 2
    assert swings[0].kind == "SWING_HIGH"
    assert swings[0].price == 4.0
    assert swings[1].price == 6.0


def test_detects_swing_lows() -> None:
    candles = _make_candles(
        highs=[10, 10, 10, 10, 10, 10, 10, 10, 10],
        lows=[5, 3, 1, 3, 5, 4, 0, 4, 5],
    )
    analyzer = MarketStructureAnalyzer()

    swings = analyzer.find_swing_lows(candles, MarketStructureConfig(swing_lookback=1))

    assert len(swings) == 2
    assert swings[0].kind == "SWING_LOW"
    assert swings[0].price == 1.0
    assert swings[1].price == 0.0


def test_bullish_market_structure() -> None:
    candles = _make_candles(
        highs=[5, 7, 10, 7, 5, 8, 12, 8, 6],
        lows=[4, 3, 4, 2, 4, 5, 6, 5, 6],
    )
    analyzer = MarketStructureAnalyzer()

    result = analyzer.analyze(candles, MarketStructureConfig(swing_lookback=1))

    assert result.structure_bias == "BULLISH"


def test_bearish_market_structure() -> None:
    candles = _make_candles(
        highs=[8, 10, 14, 10, 8, 9, 11, 9, 7],
        lows=[6, 5, 6, 4, 6, 3, 6, 5, 4],
    )
    analyzer = MarketStructureAnalyzer()

    result = analyzer.analyze(candles, MarketStructureConfig(swing_lookback=1))

    assert result.structure_bias == "BEARISH"


def test_neutral_market_structure() -> None:
    candles = _make_candles(
        highs=[6, 8, 12, 8, 6, 9, 10, 9, 7],
        lows=[5, 4, 5, 2, 5, 3, 6, 4, 6],
    )
    analyzer = MarketStructureAnalyzer()

    result = analyzer.analyze(candles, MarketStructureConfig(swing_lookback=1))

    assert result.structure_bias == "NEUTRAL"


def test_unknown_when_not_enough_candles() -> None:
    candles = _make_candles(highs=[1, 2, 3], lows=[0, 0, 0])
    analyzer = MarketStructureAnalyzer()

    result = analyzer.analyze(candles, MarketStructureConfig(swing_lookback=2))

    assert result.structure_bias == "UNKNOWN"
    assert len(result.blocking_reasons) > 0


def test_unknown_when_columns_missing() -> None:
    candles = pd.DataFrame({"high": [1, 2, 3], "low": [0, 1, 0]})
    analyzer = MarketStructureAnalyzer()

    result = analyzer.analyze(candles, MarketStructureConfig())

    assert result.structure_bias == "UNKNOWN"
    assert "Missing required OHLC columns" in result.blocking_reasons[0]


def test_explain_returns_readable_text() -> None:
    candles = _make_candles(
        highs=[5, 7, 10, 7, 5, 8, 12, 8, 6],
        lows=[4, 3, 4, 2, 4, 5, 6, 5, 6],
    )
    analyzer = MarketStructureAnalyzer()

    result = analyzer.analyze(candles, MarketStructureConfig(swing_lookback=1))
    text = analyzer.explain(result)

    assert "SMC market structure" in text
    assert "BULLISH" in text
    assert "swing highs" in text
