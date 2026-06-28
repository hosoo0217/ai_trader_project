"""Volatility-based safety filter for paper trading and backtesting.

This module blocks trading when volatility is abnormally low or high.
It is research-only and does not connect to brokers or external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class VolatilityFilterConfig:
    """Configuration for simple ATR-based volatility checks."""

    enabled: bool = True
    atr_period: int = 14
    min_atr: float = 0.1
    max_atr: float = 100.0
    max_last_candle_range_multiplier: float = 3.0


@dataclass
class VolatilityFilterResult:
    """Outcome of one volatility filter evaluation."""

    allowed: bool
    status: str
    atr: float | None
    last_candle_range: float | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class VolatilityFilter:
    """Evaluate whether current volatility is safe enough for trading."""

    def evaluate(self, candles: pd.DataFrame | None, config: VolatilityFilterConfig) -> VolatilityFilterResult:
        """Return a safe allow/block decision from candle volatility."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if not isinstance(candles, pd.DataFrame):
            return VolatilityFilterResult(
                allowed=False,
                status="INVALID_DATA",
                atr=None,
                last_candle_range=None,
                reasons=["Candles are missing or invalid"],
                blocking_reasons=["Candles are missing or invalid"],
            )

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return VolatilityFilterResult(
                allowed=False,
                status="INVALID_DATA",
                atr=None,
                last_candle_range=None,
                reasons=["Missing required candle columns"],
                blocking_reasons=["Missing required candle columns"],
            )

        if not config.enabled:
            return VolatilityFilterResult(
                allowed=True,
                status="FILTER_DISABLED",
                atr=None,
                last_candle_range=None,
                reasons=["Volatility filter disabled"],
                blocking_reasons=[],
            )

        if config.atr_period <= 0:
            return VolatilityFilterResult(
                allowed=False,
                status="INVALID_DATA",
                atr=None,
                last_candle_range=None,
                reasons=["ATR period must be positive"],
                blocking_reasons=["ATR period must be positive"],
            )

        if len(candles) < config.atr_period + 1:
            return VolatilityFilterResult(
                allowed=False,
                status="NOT_ENOUGH_DATA",
                atr=None,
                last_candle_range=None,
                reasons=["Not enough candles for ATR calculation"],
                blocking_reasons=["Not enough candles for ATR calculation"],
            )

        working = candles.copy()
        for column in ["high", "low", "close"]:
            working[column] = pd.to_numeric(working[column], errors="coerce")

        if working[["high", "low", "close"]].isna().any().any():
            return VolatilityFilterResult(
                allowed=False,
                status="INVALID_DATA",
                atr=None,
                last_candle_range=None,
                reasons=["Candle price values contain invalid numbers"],
                blocking_reasons=["Candle price values contain invalid numbers"],
            )

        previous_close = working["close"].shift(1)
        tr_high_low = (working["high"] - working["low"]).abs()
        tr_high_prev_close = (working["high"] - previous_close).abs()
        tr_low_prev_close = (working["low"] - previous_close).abs()

        true_range = pd.concat([tr_high_low, tr_high_prev_close, tr_low_prev_close], axis=1).max(axis=1)
        atr_value = float(true_range.tail(config.atr_period).mean())

        last_candle_range = float((working["high"].iloc[-1] - working["low"].iloc[-1]))

        if atr_value < config.min_atr:
            blocking_reasons.append("ATR is below minimum threshold")
            return VolatilityFilterResult(
                allowed=False,
                status="VOLATILITY_TOO_LOW",
                atr=atr_value,
                last_candle_range=last_candle_range,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        if atr_value > config.max_atr:
            blocking_reasons.append("ATR is above maximum threshold")
            return VolatilityFilterResult(
                allowed=False,
                status="VOLATILITY_TOO_HIGH",
                atr=atr_value,
                last_candle_range=last_candle_range,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        max_allowed_last_range = atr_value * config.max_last_candle_range_multiplier
        if last_candle_range > max_allowed_last_range:
            blocking_reasons.append("Last candle range is abnormally large")
            return VolatilityFilterResult(
                allowed=False,
                status="ABNORMAL_LAST_CANDLE",
                atr=atr_value,
                last_candle_range=last_candle_range,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        reasons.append("Volatility is within configured range")
        return VolatilityFilterResult(
            allowed=True,
            status="VOLATILITY_ALLOWED",
            atr=atr_value,
            last_candle_range=last_candle_range,
            reasons=reasons,
            blocking_reasons=[],
        )

    def explain(self, result: VolatilityFilterResult) -> str:
        """Return a readable explanation for logs and console output."""
        atr_text = f"{result.atr:.4f}" if result.atr is not None else "None"
        range_text = f"{result.last_candle_range:.4f}" if result.last_candle_range is not None else "None"
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"

        return (
            f"Volatility filter status: {result.status} | "
            f"allowed: {result.allowed} | "
            f"atr: {atr_text} | "
            f"last candle range: {range_text} | "
            f"reasons: {reasons_text} | "
            f"blocking reasons: {blocks_text}"
        )
