"""Multi-timeframe bias combination for research and backtesting.

This module combines several timeframe-specific market analysis results into a
single, safe market bias. It does not execute orders or connect to brokers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from core.market_analyzer import MarketAnalysisResult


@dataclass
class MultiTimeframeConfig:
    """Configuration for combining multiple timeframe results."""

    required_higher_timeframes: List[str] = field(
        default_factory=lambda: ["W1", "D1", "H4"]
    )
    required_entry_timeframes: List[str] = field(
        default_factory=lambda: ["H1", "M15", "M5"]
    )
    minimum_confidence: float = 70.0


@dataclass
class MultiTimeframeDecision:
    """Outcome of combining multiple timeframe biases."""

    bias: str = "NO_TRADE"
    allowed: bool = False
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)
    timeframe_summary: Dict[str, str] = field(default_factory=dict)


class MultiTimeframeBiasCombiner:
    """Combine multiple timeframe results into a single safe market bias."""

    def combine(self, results: Dict[str, MarketAnalysisResult], config: MultiTimeframeConfig) -> MultiTimeframeDecision:
        """Combine timeframe results with conservative safety rules."""
        if not results:
            return MultiTimeframeDecision(
                bias="NO_TRADE",
                allowed=False,
                confidence=0.0,
                reasons=["No timeframe results provided"],
                blocking_reasons=["No timeframe results provided"],
                timeframe_summary={},
            )

        reasons: List[str] = []
        blocking_reasons: List[str] = []
        timeframe_summary: Dict[str, str] = {}

        for timeframe, result in results.items():
            timeframe_summary[timeframe] = result.bias if result is not None else "UNKNOWN"

        # Required higher timeframes must be present and usable.
        for timeframe in config.required_higher_timeframes:
            if timeframe not in results:
                blocking_reasons.append(f"Missing required higher timeframe: {timeframe}")
                reasons.append("Required higher timeframe is missing")
                break

            result = results[timeframe]
            if result is None or result.bias == "UNKNOWN":
                blocking_reasons.append(f"Required higher timeframe is unknown: {timeframe}")
                reasons.append("Required higher timeframe is unknown")
                break

        if blocking_reasons:
            return MultiTimeframeDecision(
                bias="NO_TRADE",
                allowed=False,
                confidence=0.0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
                timeframe_summary=timeframe_summary,
            )

        higher_biases = [results[tf].bias for tf in config.required_higher_timeframes if tf in results]
        if len(set(higher_biases)) > 1:
            return MultiTimeframeDecision(
                bias="WAIT",
                allowed=False,
                confidence=self._average_confidence(results, config.required_higher_timeframes),
                reasons=["Higher timeframes conflict"],
                blocking_reasons=["Higher timeframes conflict"],
                timeframe_summary=timeframe_summary,
            )

        higher_bias = higher_biases[0]
        if higher_bias == "BULLISH":
            decision_bias = "BUY_BIAS"
        elif higher_bias == "BEARISH":
            decision_bias = "SELL_BIAS"
        else:
            decision_bias = "WAIT"

        available_entry_results = [result for timeframe, result in results.items() if timeframe in config.required_entry_timeframes]
        if available_entry_results:
            entry_biases = {result.bias for result in available_entry_results}
            if len(entry_biases) > 1 and entry_biases != {"NEUTRAL"}:
                return MultiTimeframeDecision(
                    bias="WAIT",
                    allowed=False,
                    confidence=self._average_confidence(results, config.required_higher_timeframes),
                    reasons=["Entry timeframes conflict"],
                    blocking_reasons=["Entry timeframes conflict"],
                    timeframe_summary=timeframe_summary,
                )

        confidence = self._average_confidence(results, config.required_higher_timeframes)
        if confidence < config.minimum_confidence:
            return MultiTimeframeDecision(
                bias="WAIT",
                allowed=False,
                confidence=confidence,
                reasons=["Confidence below threshold"],
                blocking_reasons=["Confidence below threshold"],
                timeframe_summary=timeframe_summary,
            )

        return MultiTimeframeDecision(
            bias=decision_bias,
            allowed=True,
            confidence=confidence,
            reasons=["Higher timeframes are aligned"],
            blocking_reasons=[],
            timeframe_summary=timeframe_summary,
        )

    def explain(self, decision: MultiTimeframeDecision) -> str:
        """Create a readable explanation for a combined decision."""
        if decision.allowed:
            if decision.reasons:
                return f"{decision.bias} with confidence {decision.confidence:.1f}: " + "; ".join(decision.reasons)
            return f"{decision.bias} with confidence {decision.confidence:.1f}."

        if decision.blocking_reasons:
            return f"{decision.bias} because: " + "; ".join(decision.blocking_reasons)

        return f"{decision.bias} for unknown reasons."

    def _average_confidence(self, results: Dict[str, MarketAnalysisResult], timeframes: List[str]) -> float:
        """Average the confidence of the supplied timeframe results."""
        selected = [results[tf].confidence for tf in timeframes if tf in results and results[tf] is not None]
        if not selected:
            return 0.0
        return sum(selected) / len(selected)
