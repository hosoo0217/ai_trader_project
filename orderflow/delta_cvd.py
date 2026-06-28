"""Order flow delta and cumulative delta analyzer for research/backtesting.

This module analyzes historical FootprintCandle objects only.
It does not connect to live feeds, brokers, Sierra Chart, or exchanges.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow.footprint import FootprintCandle


@dataclass
class DeltaCVDConfig:
    """Configuration for delta and cumulative delta analysis."""

    strong_delta_threshold: float = 100.0
    reset_cvd_each_session: bool = False


@dataclass
class DeltaCVDPoint:
    """Delta/CVD values for one footprint candle index."""

    index: int
    time: object | None
    delta: float
    cumulative_delta: float
    total_volume: float
    direction: str
    reasons: list[str] = field(default_factory=list)


@dataclass
class DeltaCVDResult:
    """Final result from delta/CVD analysis over many candles."""

    points: list[DeltaCVDPoint] = field(default_factory=list)
    final_cvd: float = 0.0
    latest_delta: float | None = None
    latest_direction: str = "NEUTRAL"
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class DeltaCVDAnalyzer:
    """Calculate candle delta and running cumulative delta (CVD)."""

    def analyze(self, candles: list[FootprintCandle] | None, config: DeltaCVDConfig) -> DeltaCVDResult:
        """Analyze footprint candles and return point-by-point delta/CVD."""
        if candles is None or len(candles) == 0:
            return DeltaCVDResult(
                points=[],
                final_cvd=0.0,
                latest_delta=None,
                latest_direction="NEUTRAL",
                reasons=["No footprint candles provided"],
                blocking_reasons=[],
            )

        threshold = max(0.0, float(config.strong_delta_threshold))
        points: list[DeltaCVDPoint] = []
        cumulative_delta = 0.0

        for index, candle in enumerate(candles):
            if candle is None:
                delta = 0.0
                total_volume = 0.0
                time_value = None
                point_reasons = ["Missing candle treated as neutral"]
            else:
                try:
                    delta = float(candle.delta())
                except Exception:
                    delta = 0.0
                try:
                    total_volume = float(candle.total_volume())
                except Exception:
                    total_volume = 0.0
                time_value = getattr(candle, "time", None)
                point_reasons = []

            cumulative_delta += delta
            direction = self._direction_from_delta(delta, threshold)

            if direction == "BUYING_PRESSURE":
                point_reasons.append("Delta is above strong threshold")
            elif direction == "SELLING_PRESSURE":
                point_reasons.append("Delta is below negative strong threshold")
            else:
                point_reasons.append("Delta is inside neutral threshold range")

            points.append(
                DeltaCVDPoint(
                    index=index,
                    time=time_value,
                    delta=delta,
                    cumulative_delta=cumulative_delta,
                    total_volume=total_volume,
                    direction=direction,
                    reasons=point_reasons,
                )
            )

        latest = points[-1]
        reasons = [f"Processed {len(points)} footprint candle(s)"]
        if latest.direction == "BUYING_PRESSURE":
            reasons.append("Latest delta indicates buying pressure")
        elif latest.direction == "SELLING_PRESSURE":
            reasons.append("Latest delta indicates selling pressure")
        else:
            reasons.append("Latest delta is neutral")

        return DeltaCVDResult(
            points=points,
            final_cvd=points[-1].cumulative_delta,
            latest_delta=latest.delta,
            latest_direction=latest.direction,
            reasons=reasons,
            blocking_reasons=[],
        )

    def explain(self, result: DeltaCVDResult) -> str:
        """Return a readable summary string for delta/CVD output."""
        if not result.points:
            reasons_text = "; ".join(result.reasons) if result.reasons else "None"
            return (
                "Delta/CVD summary: points=0, final_cvd=0.00, latest_delta=None, "
                f"latest_direction={result.latest_direction}, reasons={reasons_text}."
            )

        return (
            "Delta/CVD summary: "
            f"points={len(result.points)}, "
            f"final_cvd={result.final_cvd:.2f}, "
            f"latest_delta={result.latest_delta:.2f}, "
            f"latest_direction={result.latest_direction}."
        )

    def _direction_from_delta(self, delta: float, threshold: float) -> str:
        """Classify directional pressure from delta and threshold."""
        if delta > threshold:
            return "BUYING_PRESSURE"
        if delta < -threshold:
            return "SELLING_PRESSURE"
        return "NEUTRAL"
