"""Basic Smart Money Concepts market structure analyzer (v1).

This module detects simple swing highs, swing lows, and a basic structure bias
from OHLC candles for research and backtesting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class SwingPoint:
    """A detected swing point on a candle index."""

    index: int
    time: object | None
    price: float
    kind: str


@dataclass
class MarketStructureConfig:
    """Configuration for swing detection and structure analysis."""

    swing_lookback: int = 2
    min_swing_distance: float = 0.0


@dataclass
class MarketStructureResult:
    """Result of market structure analysis."""

    structure_bias: str
    swing_highs: list[SwingPoint] = field(default_factory=list)
    swing_lows: list[SwingPoint] = field(default_factory=list)
    last_swing_high: SwingPoint | None = None
    last_swing_low: SwingPoint | None = None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class MarketStructureAnalyzer:
    """Detect swing highs/lows and infer simple structure bias."""

    def analyze(self, candles: pd.DataFrame, config: MarketStructureConfig) -> MarketStructureResult:
        """Analyze OHLC candles and return a simple structure interpretation."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return MarketStructureResult(
                structure_bias="UNKNOWN",
                reasons=["No candle data provided"],
                blocking_reasons=["No candle data provided"],
            )

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return MarketStructureResult(
                structure_bias="UNKNOWN",
                reasons=["Missing required OHLC columns"],
                blocking_reasons=["Missing required OHLC columns"],
            )

        if config.swing_lookback <= 0:
            return MarketStructureResult(
                structure_bias="UNKNOWN",
                reasons=["Invalid swing_lookback configuration"],
                blocking_reasons=["swing_lookback must be greater than zero"],
            )

        minimum_candles = (config.swing_lookback * 2) + 1
        if len(candles) < minimum_candles:
            return MarketStructureResult(
                structure_bias="UNKNOWN",
                reasons=["Not enough candles for swing analysis"],
                blocking_reasons=["Not enough candles for configured swing_lookback"],
            )

        swing_highs = self.find_swing_highs(candles, config)
        swing_lows = self.find_swing_lows(candles, config)

        last_swing_high = swing_highs[-1] if swing_highs else None
        last_swing_low = swing_lows[-1] if swing_lows else None

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return MarketStructureResult(
                structure_bias="UNKNOWN",
                swing_highs=swing_highs,
                swing_lows=swing_lows,
                last_swing_high=last_swing_high,
                last_swing_low=last_swing_low,
                reasons=["Not enough swing points to determine structure"],
                blocking_reasons=["Need at least two swing highs and two swing lows"],
            )

        previous_high = swing_highs[-2]
        latest_high = swing_highs[-1]
        previous_low = swing_lows[-2]
        latest_low = swing_lows[-1]

        higher_high = latest_high.price > previous_high.price
        lower_high = latest_high.price < previous_high.price
        higher_low = latest_low.price > previous_low.price
        lower_low = latest_low.price < previous_low.price

        if higher_high and higher_low:
            return MarketStructureResult(
                structure_bias="BULLISH",
                swing_highs=swing_highs,
                swing_lows=swing_lows,
                last_swing_high=latest_high,
                last_swing_low=latest_low,
                reasons=["Latest swing high and swing low are both higher"],
                blocking_reasons=[],
            )

        if lower_high and lower_low:
            return MarketStructureResult(
                structure_bias="BEARISH",
                swing_highs=swing_highs,
                swing_lows=swing_lows,
                last_swing_high=latest_high,
                last_swing_low=latest_low,
                reasons=["Latest swing high and swing low are both lower"],
                blocking_reasons=[],
            )

        return MarketStructureResult(
            structure_bias="NEUTRAL",
            swing_highs=swing_highs,
            swing_lows=swing_lows,
            last_swing_high=latest_high,
            last_swing_low=latest_low,
            reasons=["Swing highs and lows are mixed"],
            blocking_reasons=[],
        )

    def find_swing_highs(self, candles: pd.DataFrame, config: MarketStructureConfig) -> list[SwingPoint]:
        """Find swing highs using left/right lookback comparison."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return []
        if "high" not in candles.columns:
            return []
        if config.swing_lookback <= 0:
            return []

        high_values = pd.to_numeric(candles["high"], errors="coerce")
        if high_values.isna().all():
            return []

        swings: list[SwingPoint] = []
        lookback = config.swing_lookback
        minimum_distance = max(0.0, float(config.min_swing_distance))

        for index in range(lookback, len(candles) - lookback):
            current_high = high_values.iloc[index]
            if pd.isna(current_high):
                continue

            left_values = high_values.iloc[index - lookback : index]
            right_values = high_values.iloc[index + 1 : index + lookback + 1]
            if left_values.isna().any() or right_values.isna().any():
                continue

            if bool((current_high > left_values).all() and (current_high > right_values).all()):
                swing = SwingPoint(
                    index=index,
                    time=candles["time"].iloc[index] if "time" in candles.columns else None,
                    price=float(current_high),
                    kind="SWING_HIGH",
                )
                if swings and abs(swing.price - swings[-1].price) < minimum_distance:
                    continue
                swings.append(swing)

        return swings

    def find_swing_lows(self, candles: pd.DataFrame, config: MarketStructureConfig) -> list[SwingPoint]:
        """Find swing lows using left/right lookback comparison."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return []
        if "low" not in candles.columns:
            return []
        if config.swing_lookback <= 0:
            return []

        low_values = pd.to_numeric(candles["low"], errors="coerce")
        if low_values.isna().all():
            return []

        swings: list[SwingPoint] = []
        lookback = config.swing_lookback
        minimum_distance = max(0.0, float(config.min_swing_distance))

        for index in range(lookback, len(candles) - lookback):
            current_low = low_values.iloc[index]
            if pd.isna(current_low):
                continue

            left_values = low_values.iloc[index - lookback : index]
            right_values = low_values.iloc[index + 1 : index + lookback + 1]
            if left_values.isna().any() or right_values.isna().any():
                continue

            if bool((current_low < left_values).all() and (current_low < right_values).all()):
                swing = SwingPoint(
                    index=index,
                    time=candles["time"].iloc[index] if "time" in candles.columns else None,
                    price=float(current_low),
                    kind="SWING_LOW",
                )
                if swings and abs(swing.price - swings[-1].price) < minimum_distance:
                    continue
                swings.append(swing)

        return swings

    def explain(self, result: MarketStructureResult) -> str:
        """Return a readable summary of market structure analysis."""
        last_high_text = f"{result.last_swing_high.price:.4f}" if result.last_swing_high is not None else "None"
        last_low_text = f"{result.last_swing_low.price:.4f}" if result.last_swing_low is not None else "None"
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"

        return (
            f"SMC market structure: {result.structure_bias} | "
            f"swing highs: {len(result.swing_highs)} | "
            f"swing lows: {len(result.swing_lows)} | "
            f"last swing high: {last_high_text} | "
            f"last swing low: {last_low_text} | "
            f"reasons: {reasons_text} | "
            f"blocking reasons: {blocks_text}"
        )
