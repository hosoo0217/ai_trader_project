"""Simple report generation for Order Flow replay results.

This module summarizes replay output for research/backtesting reports only.
It does not connect to live data, brokers, Sierra Chart, CME, or create trades.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow.replay import OrderFlowReplayResult


@dataclass
class OrderFlowReplayReport:
    """Summary statistics for an Order Flow replay result."""

    total_steps: int
    bullish_steps: int
    bearish_steps: int
    neutral_steps: int
    unknown_steps: int
    average_confidence: float
    max_confidence: float
    min_confidence: float
    final_bias: str
    final_confidence: float
    final_cvd: float
    dominant_bias: str
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class OrderFlowReplayReportGenerator:
    """Create readable summary reports from replay results."""

    def generate(self, replay_result: OrderFlowReplayResult | None) -> OrderFlowReplayReport:
        """Generate a replay report without producing trade signals."""
        if replay_result is None:
            return self._empty_report(
                reasons=["No replay result provided"],
                warnings=["Replay result is missing"],
            )

        steps = list(getattr(replay_result, "steps", []) or [])
        if not steps:
            warnings = []
            if not getattr(replay_result, "passed", False):
                warnings.extend(list(getattr(replay_result, "blocking_reasons", [])))
                if not warnings:
                    warnings.append("Replay failed without step data")

            return self._empty_report(
                reasons=list(getattr(replay_result, "reasons", [])) or ["Replay result has no steps"],
                warnings=warnings,
                final_bias=str(getattr(replay_result, "final_bias", "UNKNOWN") or "UNKNOWN"),
                final_confidence=self._safe_float(getattr(replay_result, "final_confidence", 0.0)),
                final_cvd=self._safe_float(getattr(replay_result, "final_cvd", 0.0)),
            )

        counts = {
            "BULLISH": 0,
            "BEARISH": 0,
            "NEUTRAL": 0,
            "UNKNOWN": 0,
        }
        confidences: list[float] = []

        for step in steps:
            bias = str(getattr(step, "orderflow_bias", "UNKNOWN") or "UNKNOWN")
            if bias not in counts:
                bias = "UNKNOWN"
            counts[bias] += 1
            confidences.append(self._safe_float(getattr(step, "orderflow_confidence", 0.0)))

        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        warnings = []
        if not getattr(replay_result, "passed", False):
            warnings.extend(list(getattr(replay_result, "blocking_reasons", [])))
            if not warnings:
                warnings.append("Replay result did not pass")

        return OrderFlowReplayReport(
            total_steps=len(steps),
            bullish_steps=counts["BULLISH"],
            bearish_steps=counts["BEARISH"],
            neutral_steps=counts["NEUTRAL"],
            unknown_steps=counts["UNKNOWN"],
            average_confidence=average_confidence,
            max_confidence=max(confidences) if confidences else 0.0,
            min_confidence=min(confidences) if confidences else 0.0,
            final_bias=str(getattr(replay_result, "final_bias", "UNKNOWN") or "UNKNOWN"),
            final_confidence=self._safe_float(getattr(replay_result, "final_confidence", 0.0)),
            final_cvd=self._safe_float(getattr(replay_result, "final_cvd", 0.0)),
            dominant_bias=self._dominant_bias(counts),
            reasons=list(getattr(replay_result, "reasons", [])) or ["Replay report generated"],
            warnings=warnings,
        )

    def explain(self, report: OrderFlowReplayReport) -> str:
        """Return a readable one-line replay report summary."""
        reasons_text = "; ".join(report.reasons) if report.reasons else "None"
        warnings_text = "; ".join(report.warnings) if report.warnings else "None"
        return (
            "Order Flow replay report: "
            f"steps={report.total_steps}, "
            f"bullish={report.bullish_steps}, "
            f"bearish={report.bearish_steps}, "
            f"neutral={report.neutral_steps}, "
            f"unknown={report.unknown_steps}, "
            f"dominant_bias={report.dominant_bias}, "
            f"average_confidence={report.average_confidence:.1f}, "
            f"final_bias={report.final_bias}, "
            f"final_cvd={report.final_cvd:.2f}, "
            f"warnings={warnings_text}, "
            f"reasons={reasons_text}."
        )

    def _empty_report(
        self,
        reasons: list[str],
        warnings: list[str],
        final_bias: str = "UNKNOWN",
        final_confidence: float = 0.0,
        final_cvd: float = 0.0,
    ) -> OrderFlowReplayReport:
        """Build a safe empty report for missing or failed replay results."""
        return OrderFlowReplayReport(
            total_steps=0,
            bullish_steps=0,
            bearish_steps=0,
            neutral_steps=0,
            unknown_steps=0,
            average_confidence=0.0,
            max_confidence=0.0,
            min_confidence=0.0,
            final_bias=final_bias,
            final_confidence=final_confidence,
            final_cvd=final_cvd,
            dominant_bias="UNKNOWN",
            reasons=list(reasons),
            warnings=list(warnings),
        )

    def _dominant_bias(self, counts: dict[str, int]) -> str:
        """Return the bias with the most steps, UNKNOWN on ties or no steps."""
        highest_count = max(counts.values()) if counts else 0
        if highest_count <= 0:
            return "UNKNOWN"

        winners = [bias for bias, count in counts.items() if count == highest_count]
        if len(winners) != 1:
            return "UNKNOWN"
        return winners[0]

    def _safe_float(self, value: object) -> float:
        """Convert values to float safely for report calculations."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
