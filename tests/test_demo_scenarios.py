from pathlib import Path

import pandas as pd

from core.market_analyzer import MarketAnalyzer, MarketAnalyzerConfig


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _load_sample(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def test_bullish_sample_produces_bullish_bias() -> None:
    candles = _load_sample("bullish_sample_xauusd.csv")
    analyzer = MarketAnalyzer()

    result = analyzer.analyze_candles(candles, "M5", MarketAnalyzerConfig())

    assert result.bias == "BULLISH"
    assert result.confidence >= 60.0


def test_bearish_sample_produces_bearish_bias() -> None:
    candles = _load_sample("bearish_sample_xauusd.csv")
    analyzer = MarketAnalyzer()

    result = analyzer.analyze_candles(candles, "M5", MarketAnalyzerConfig())

    assert result.bias == "BEARISH"
    assert result.confidence >= 60.0


def test_weak_sample_produces_unknown_or_no_trade() -> None:
    candles = _load_sample("weak_sample_xauusd.csv")
    analyzer = MarketAnalyzer()

    result = analyzer.analyze_candles(candles, "M5", MarketAnalyzerConfig())

    assert result.bias == "UNKNOWN"


def test_all_demo_csv_files_load_without_crashing() -> None:
    for file_name in ["bullish_sample_xauusd.csv", "bearish_sample_xauusd.csv", "weak_sample_xauusd.csv"]:
        candles = _load_sample(file_name)
        assert {"time", "open", "high", "low", "close"}.issubset(candles.columns)
