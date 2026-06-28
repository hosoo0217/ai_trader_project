"""Unit tests for the market analyzer."""

import pandas as pd

from core.market_analyzer import MarketAnalysisResult, MarketAnalyzer, MarketAnalyzerConfig


def test_bullish_bias():
    """A strong bullish EMA crossover should produce a bullish bias."""
    analyzer = MarketAnalyzer()
    candles = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=60, freq="D"),
            "open": [100 + i for i in range(60)],
            "high": [101 + i for i in range(60)],
            "low": [99 + i for i in range(60)],
            "close": [100 + i for i in range(60)],
        }
    )

    result = analyzer.analyze_candles(candles, "D1", MarketAnalyzerConfig())

    assert result.bias == "BULLISH"
    assert result.confidence >= 70.0


def test_bearish_bias():
    """A bearish EMA crossover should produce a bearish bias."""
    analyzer = MarketAnalyzer()
    candles = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=60, freq="D"),
            "open": [100 - i for i in range(60)],
            "high": [101 - i for i in range(60)],
            "low": [99 - i for i in range(60)],
            "close": [100 - i for i in range(60)],
        }
    )

    result = analyzer.analyze_candles(candles, "D1", MarketAnalyzerConfig())

    assert result.bias == "BEARISH"
    assert result.confidence >= 70.0


def test_unknown_when_not_enough_candles():
    """Too few candles should return UNKNOWN."""
    analyzer = MarketAnalyzer()
    candles = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=20, freq="D"),
            "open": [100] * 20,
            "high": [101] * 20,
            "low": [99] * 20,
            "close": [100] * 20,
        }
    )

    result = analyzer.analyze_candles(candles, "D1", MarketAnalyzerConfig())

    assert result.bias == "UNKNOWN"
    assert result.confidence == 0.0


def test_unknown_when_required_columns_missing():
    """Missing required columns should yield UNKNOWN."""
    analyzer = MarketAnalyzer()
    candles = pd.DataFrame({"time": [1, 2], "close": [100, 101]})

    result = analyzer.analyze_candles(candles, "D1", MarketAnalyzerConfig())

    assert result.bias == "UNKNOWN"
    assert result.confidence == 0.0


def test_multi_timeframe_analysis_returns_results_for_provided_timeframes():
    """Multi-timeframe analysis should return results for the provided data."""
    analyzer = MarketAnalyzer()
    timeframe_data = {
        "D1": pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=60, freq="D"),
                "open": [100 + i for i in range(60)],
                "high": [101 + i for i in range(60)],
                "low": [99 + i for i in range(60)],
                "close": [100 + i for i in range(60)],
            }
        ),
        "H1": pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=60, freq="h"),
                "open": [100 + i for i in range(60)],
                "high": [101 + i for i in range(60)],
                "low": [99 + i for i in range(60)],
                "close": [100 + i for i in range(60)],
            }
        ),
    }

    results = analyzer.analyze_multi_timeframe(timeframe_data, MarketAnalyzerConfig())

    assert set(results.keys()) == {"D1", "H1"}
    assert results["D1"].bias == "BULLISH"
    assert results["H1"].bias == "BULLISH"


def test_explain_returns_readable_text():
    """The explanation text should be readable and include the main signal."""
    analyzer = MarketAnalyzer()
    candles = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=60, freq="D"),
            "open": [100 + i for i in range(60)],
            "high": [101 + i for i in range(60)],
            "low": [99 + i for i in range(60)],
            "close": [100 + i for i in range(60)],
        }
    )

    result = analyzer.analyze_candles(candles, "D1", MarketAnalyzerConfig())
    explanation = analyzer.explain(result)

    assert "BULLISH" in explanation
    assert "D1" in explanation
