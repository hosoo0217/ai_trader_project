"""Basic market analysis for research and backtesting.

This module provides a lightweight analyzer that reads OHLC candle data and
produces a simple directional bias using moving averages. It does not connect
to brokers, execute trades, or use any live market feed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd


@dataclass
class MarketAnalyzerConfig:
    """Configuration for simple EMA-based market analysis."""

    fast_ema_period: int = 20
    slow_ema_period: int = 50
    min_required_candles: int = 50


@dataclass
class MarketAnalysisResult:
    """Outcome of a market analysis run."""

    timeframe: str = ""
    bias: str = "UNKNOWN"
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    last_close: Optional[float] = None
    fast_ema: Optional[float] = None
    slow_ema: Optional[float] = None


class MarketAnalyzer:
    """Generate a basic market bias from OHLC candle data."""

    def analyze_candles(self, candles: pd.DataFrame, timeframe: str, config: MarketAnalyzerConfig) -> MarketAnalysisResult:
        """Analyze a single candle series and return a simple bias result."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return MarketAnalysisResult(timeframe=timeframe, bias="UNKNOWN", confidence=0.0, reasons=["No candle data provided"])

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return MarketAnalysisResult(timeframe=timeframe, bias="UNKNOWN", confidence=0.0, reasons=["Missing required OHLC columns"])

        if len(candles) < config.min_required_candles:
            return MarketAnalysisResult(timeframe=timeframe, bias="UNKNOWN", confidence=0.0, reasons=["Not enough candles"])

        close_series = pd.to_numeric(candles["close"], errors="coerce")
        if close_series.isna().all():
            return MarketAnalysisResult(timeframe=timeframe, bias="UNKNOWN", confidence=0.0, reasons=["Close prices are invalid"])

        fast_ema = close_series.ewm(span=config.fast_ema_period, adjust=False).mean().iloc[-1]
        slow_ema = close_series.ewm(span=config.slow_ema_period, adjust=False).mean().iloc[-1]
        last_close = float(close_series.iloc[-1])

        if pd.isna(fast_ema) or pd.isna(slow_ema):
            return MarketAnalysisResult(timeframe=timeframe, bias="UNKNOWN", confidence=0.0, reasons=["EMA calculation failed"])

        separation = abs(fast_ema - slow_ema)
        if separation <= 0.001:
            bias = "NEUTRAL"
            confidence = 50.0
            reasons = ["Fast and slow EMA are very close"]
        elif fast_ema > slow_ema:
            bias = "BULLISH"
            confidence = min(95.0, 60.0 + (separation * 2.0))
            reasons = ["Fast EMA is above slow EMA"]
        else:
            bias = "BEARISH"
            confidence = min(95.0, 60.0 + (separation * 2.0))
            reasons = ["Fast EMA is below slow EMA"]

        return MarketAnalysisResult(
            timeframe=timeframe,
            bias=bias,
            confidence=max(0.0, min(100.0, confidence)),
            reasons=reasons,
            last_close=last_close,
            fast_ema=float(fast_ema),
            slow_ema=float(slow_ema),
        )

    def analyze_multi_timeframe(self, timeframe_data: Dict[str, pd.DataFrame], config: MarketAnalyzerConfig) -> Dict[str, MarketAnalysisResult]:
        """Analyze multiple timeframes and return a result for each provided series."""
        results: Dict[str, MarketAnalysisResult] = {}
        supported_timeframes = {"W1", "D1", "H4", "H1", "M15", "M5"}

        for timeframe, candles in timeframe_data.items():
            if timeframe not in supported_timeframes and timeframe:
                # The analyzer still supports unknown names as long as data is provided.
                pass
            results[timeframe] = self.analyze_candles(candles, timeframe, config)

        return results

    def explain(self, result: MarketAnalysisResult) -> str:
        """Return a readable explanation of the analysis result."""
        if result.bias == "UNKNOWN":
            return f"{result.timeframe}: market bias is UNKNOWN."

        if result.fast_ema is None or result.slow_ema is None:
            return f"{result.timeframe}: {result.bias} with confidence {result.confidence:.1f}."

        return f"{result.timeframe}: {result.bias} (EMA20={result.fast_ema:.2f}, EMA50={result.slow_ema:.2f}, confidence={result.confidence:.1f})."
