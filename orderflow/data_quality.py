"""Data-quality checks for imported footprint Order Flow data.

This module validates already-loaded footprint candles for research and
backtesting. It does not connect to live data, brokers, Sierra Chart, CME, or
external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Iterable


@dataclass
class OrderFlowDataQualityConfig:
    """Configuration for footprint data-quality checks."""

    min_candles: int = 1
    min_levels_per_candle: int = 1
    allow_zero_volume_levels: bool = True
    max_invalid_level_ratio: float = 0.25


@dataclass
class OrderFlowDataQualityResult:
    """Result from checking footprint data quality."""

    passed: bool
    status: str
    candle_count: int
    total_levels: int
    invalid_levels: int
    invalid_level_ratio: float
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class OrderFlowDataQualityChecker:
    """Check whether imported footprint candles are safe enough to analyze."""

    def check(
        self,
        candles: Iterable[object] | None,
        config: OrderFlowDataQualityConfig,
    ) -> OrderFlowDataQualityResult:
        """Validate footprint candles without raising on malformed data."""
        if candles is None:
            return OrderFlowDataQualityResult(
                passed=False,
                status="INVALID",
                candle_count=0,
                total_levels=0,
                invalid_levels=0,
                invalid_level_ratio=0.0,
                reasons=["No candle object was provided"],
                blocking_reasons=["Order Flow data input is invalid"],
            )

        try:
            candle_list = list(candles)
        except TypeError:
            return OrderFlowDataQualityResult(
                passed=False,
                status="INVALID",
                candle_count=0,
                total_levels=0,
                invalid_levels=0,
                invalid_level_ratio=0.0,
                reasons=["Candle input is not iterable"],
                blocking_reasons=["Order Flow data input is invalid"],
            )

        candle_count = len(candle_list)
        if candle_count == 0:
            return OrderFlowDataQualityResult(
                passed=False,
                status="EMPTY",
                candle_count=0,
                total_levels=0,
                invalid_levels=0,
                invalid_level_ratio=0.0,
                reasons=["No footprint candles available"],
                blocking_reasons=["Order Flow data is empty"],
            )

        min_candles = max(0, int(config.min_candles))
        min_levels = max(0, int(config.min_levels_per_candle))
        max_invalid_ratio = self._clamp_ratio(config.max_invalid_level_ratio)
        total_levels = 0
        invalid_levels = 0
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if candle_count < min_candles:
            blocking_reasons.append(f"Candle count {candle_count} is below minimum {min_candles}")

        for candle_index, candle in enumerate(candle_list):
            levels = getattr(candle, "levels", None)
            if levels is None:
                blocking_reasons.append(f"Candle {candle_index} has no levels field")
                continue

            try:
                level_list = list(levels)
            except TypeError:
                blocking_reasons.append(f"Candle {candle_index} levels are not iterable")
                continue

            level_count = len(level_list)
            total_levels += level_count
            if level_count < min_levels:
                blocking_reasons.append(
                    f"Candle {candle_index} level count {level_count} is below minimum {min_levels}"
                )

            for level in level_list:
                if self._is_invalid_level(level, config.allow_zero_volume_levels):
                    invalid_levels += 1

        invalid_level_ratio = invalid_levels / total_levels if total_levels > 0 else 0.0
        if invalid_levels > 0:
            reasons.append(f"Invalid footprint levels detected: {invalid_levels}")

        if invalid_level_ratio > max_invalid_ratio:
            blocking_reasons.append(
                f"Invalid level ratio {invalid_level_ratio:.2f} is above maximum {max_invalid_ratio:.2f}"
            )

        if blocking_reasons:
            status = "FAILED"
            passed = False
            reasons.append("Order Flow data quality failed")
        elif invalid_levels > 0:
            status = "WARNING"
            passed = True
            reasons.append("Order Flow data quality passed with warnings")
        else:
            status = "PASSED"
            passed = True
            reasons.append("Order Flow data quality passed")

        return OrderFlowDataQualityResult(
            passed=passed,
            status=status,
            candle_count=candle_count,
            total_levels=total_levels,
            invalid_levels=invalid_levels,
            invalid_level_ratio=invalid_level_ratio,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: OrderFlowDataQualityResult) -> str:
        """Return a readable summary for CLI output or test diagnostics."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Order Flow data quality: "
            f"status={result.status}, "
            f"passed={result.passed}, "
            f"candles={result.candle_count}, "
            f"levels={result.total_levels}, "
            f"invalid_levels={result.invalid_levels}, "
            f"invalid_ratio={result.invalid_level_ratio:.2f}, "
            f"reasons={reasons_text}, "
            f"blocking_reasons={blocks_text}."
        )

    def _is_invalid_level(self, level: object, allow_zero_volume_levels: bool) -> bool:
        """Return True when one price level has unusable price or volume data."""
        price = self._safe_float_or_none(getattr(level, "price", None))
        bid_volume = self._safe_float_or_none(getattr(level, "bid_volume", None))
        ask_volume = self._safe_float_or_none(getattr(level, "ask_volume", None))

        if price is None or bid_volume is None or ask_volume is None:
            return True
        if bid_volume < 0.0 or ask_volume < 0.0:
            return True
        if not allow_zero_volume_levels and bid_volume == 0.0 and ask_volume == 0.0:
            return True
        return False

    def _safe_float_or_none(self, value: object) -> float | None:
        """Convert values to finite floats and reject None, NaN, or infinity."""
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if not isfinite(number):
            return None
        return number

    def _clamp_ratio(self, value: float) -> float:
        """Keep configured ratios inside the normal 0.0 to 1.0 range."""
        try:
            ratio = float(value)
        except (TypeError, ValueError):
            return 0.25
        return max(0.0, min(1.0, ratio))
