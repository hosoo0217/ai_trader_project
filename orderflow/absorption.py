"""Order flow absorption analyzer for research and backtesting.

This module analyzes historical FootprintCandle data only.
It does not connect to live feeds, brokers, Sierra Chart, CME, or external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow.footprint import FootprintCandle


@dataclass
class AbsorptionConfig:
    """Configuration for simple absorption detection."""

    high_volume_threshold: float = 100.0
    small_body_ratio_threshold: float = 0.35
    close_near_high_ratio: float = 0.25
    close_near_low_ratio: float = 0.25


@dataclass
class AbsorptionSignal:
    """Detected absorption signal for one footprint candle."""

    signal_type: str
    direction: str
    total_volume: float
    delta: float
    candle_body: float
    candle_range: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class AbsorptionResult:
    """Output from absorption analysis."""

    signal: AbsorptionSignal | None
    bias: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class AbsorptionAnalyzer:
    """Detect simple buy/sell absorption from footprint candle data."""

    def analyze(self, candle: FootprintCandle | None, config: AbsorptionConfig) -> AbsorptionResult:
        """Analyze one footprint candle and return absorption context."""
        if candle is None:
            return self._neutral_result(
                total_volume=0.0,
                delta=0.0,
                candle_body=0.0,
                candle_range=0.0,
                reasons=["No footprint candle provided"],
                blocking_reasons=["No footprint candle provided"],
            )

        levels = getattr(candle, "levels", None)
        candle_body = abs(self._safe_float(getattr(candle, "close", 0.0)) - self._safe_float(getattr(candle, "open", 0.0)))
        candle_range = self._safe_float(getattr(candle, "high", 0.0)) - self._safe_float(getattr(candle, "low", 0.0))

        if levels is None or len(levels) == 0:
            return self._neutral_result(
                total_volume=0.0,
                delta=0.0,
                candle_body=candle_body,
                candle_range=max(0.0, candle_range),
                reasons=["No footprint levels available"],
                blocking_reasons=["No footprint levels available"],
            )

        total_volume = self._safe_total_volume(candle)
        delta = self._safe_delta(candle)
        high_volume_threshold = max(0.0, float(config.high_volume_threshold))
        small_body_threshold = max(0.0, float(config.small_body_ratio_threshold))
        near_high_ratio = max(0.0, float(config.close_near_high_ratio))
        near_low_ratio = max(0.0, float(config.close_near_low_ratio))
        reasons: list[str] = []

        if any(
            self._safe_float(getattr(level, "bid_volume", 0.0)) < 0.0
            or self._safe_float(getattr(level, "ask_volume", 0.0)) < 0.0
            for level in levels
        ):
            reasons.append("Negative volume was treated as zero")

        if candle_range <= 0.0:
            return self._neutral_result(
                total_volume=total_volume,
                delta=delta,
                candle_body=candle_body,
                candle_range=max(0.0, candle_range),
                reasons=[*reasons, "Candle range is zero"],
                blocking_reasons=["Candle range is zero"],
            )

        body_ratio = candle_body / candle_range
        high_volume = total_volume >= high_volume_threshold
        small_body = body_ratio <= small_body_threshold
        large_positive_delta = delta >= high_volume_threshold
        large_negative_delta = delta <= -high_volume_threshold
        close_value = self._safe_float(getattr(candle, "close", 0.0))
        high_value = self._safe_float(getattr(candle, "high", 0.0))
        low_value = self._safe_float(getattr(candle, "low", 0.0))
        fails_near_high = ((high_value - close_value) / candle_range) > near_high_ratio
        fails_near_low = ((close_value - low_value) / candle_range) > near_low_ratio

        if large_positive_delta and high_volume and small_body and fails_near_high:
            signal_reasons = [
                *reasons,
                "Large positive delta with high volume",
                "Small candle body relative to range",
                "Candle failed to close near high",
                "Aggressive buyers may be absorbed by sellers",
            ]
            return AbsorptionResult(
                signal=AbsorptionSignal(
                    signal_type="SELL_ABSORPTION",
                    direction="BEARISH",
                    total_volume=total_volume,
                    delta=delta,
                    candle_body=candle_body,
                    candle_range=candle_range,
                    reasons=signal_reasons,
                ),
                bias="BEARISH",
                reasons=signal_reasons,
                blocking_reasons=[],
            )

        if large_negative_delta and high_volume and small_body and fails_near_low:
            signal_reasons = [
                *reasons,
                "Large negative delta with high volume",
                "Small candle body relative to range",
                "Candle failed to close near low",
                "Aggressive sellers may be absorbed by buyers",
            ]
            return AbsorptionResult(
                signal=AbsorptionSignal(
                    signal_type="BUY_ABSORPTION",
                    direction="BULLISH",
                    total_volume=total_volume,
                    delta=delta,
                    candle_body=candle_body,
                    candle_range=candle_range,
                    reasons=signal_reasons,
                ),
                bias="BULLISH",
                reasons=signal_reasons,
                blocking_reasons=[],
            )

        return self._neutral_result(
            total_volume=total_volume,
            delta=delta,
            candle_body=candle_body,
            candle_range=candle_range,
            reasons=[*reasons, "No absorption pattern detected"],
            blocking_reasons=[],
        )

    def explain(self, result: AbsorptionResult) -> str:
        """Return a readable absorption analysis summary."""
        if result.signal is None:
            reasons_text = "; ".join(result.reasons) if result.reasons else "None"
            return f"Order flow absorption summary: bias={result.bias}, signal=NO_ABSORPTION, reasons={reasons_text}."

        return (
            "Order flow absorption summary: "
            f"bias={result.bias}, "
            f"signal={result.signal.signal_type}, "
            f"direction={result.signal.direction}, "
            f"total_volume={result.signal.total_volume:.2f}, "
            f"delta={result.signal.delta:.2f}."
        )

    def _neutral_result(
        self,
        total_volume: float,
        delta: float,
        candle_body: float,
        candle_range: float,
        reasons: list[str],
        blocking_reasons: list[str],
    ) -> AbsorptionResult:
        """Build a standard neutral no-absorption result."""
        return AbsorptionResult(
            signal=AbsorptionSignal(
                signal_type="NO_ABSORPTION",
                direction="NEUTRAL",
                total_volume=total_volume,
                delta=delta,
                candle_body=candle_body,
                candle_range=candle_range,
                reasons=list(reasons),
            ),
            bias="NEUTRAL",
            reasons=list(reasons),
            blocking_reasons=list(blocking_reasons),
        )

    def _safe_float(self, value: object, default: float = 0.0) -> float:
        """Safely convert a value to float."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def _safe_total_volume(self, candle: FootprintCandle) -> float:
        """Return total footprint volume without allowing bad data to crash."""
        try:
            return float(candle.total_volume())
        except Exception:
            return 0.0

    def _safe_delta(self, candle: FootprintCandle) -> float:
        """Return candle delta without allowing bad data to crash."""
        try:
            return float(candle.delta())
        except Exception:
            return 0.0
