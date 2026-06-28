"""Rule-based AI Coach review for Order Flow replay reports.

This module is educational/reporting only. It does not call OpenAI APIs, connect
to brokers, connect to live data, or create trade signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow.replay_report import OrderFlowReplayReport


@dataclass
class OrderFlowReplayCoachConfig:
    """Configuration for replay-report coaching."""

    high_confidence_threshold: float = 70.0
    low_confidence_threshold: float = 40.0
    require_warning_on_low_confidence: bool = True


@dataclass
class OrderFlowReplayCoachReview:
    """Beginner-friendly review of an Order Flow replay report."""

    status: str
    grade: str
    summary: str
    market_read: str
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    lessons: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class OrderFlowReplayCoach:
    """Explain replay reports in simple educational language."""

    def review(
        self,
        report: OrderFlowReplayReport | None,
        config: OrderFlowReplayCoachConfig,
    ) -> OrderFlowReplayCoachReview:
        """Review a replay report without generating trade instructions."""
        if report is None or getattr(report, "total_steps", 0) <= 0:
            warnings = list(getattr(report, "warnings", [])) if report is not None else ["Replay report is missing"]
            return OrderFlowReplayCoachReview(
                status="NO_USABLE_ORDERFLOW",
                grade="F",
                summary="No usable Order Flow replay data was available to review.",
                market_read="Order Flow is unclear because there were no replay steps to evaluate.",
                strengths=[],
                risks=["No replay context is available"],
                lessons=["Start with a clean footprint CSV that passes data quality checks."],
                next_steps=["Check CSV columns, footprint levels, and data quality before reviewing Order Flow."],
                warnings=warnings,
                reasons=list(getattr(report, "reasons", [])) if report is not None else ["No replay report provided"],
            )

        dominant_bias = str(report.dominant_bias or "UNKNOWN")
        warnings = list(report.warnings)
        risks: list[str] = []
        strengths: list[str] = []
        lessons = [
            "Order Flow is context, not a trade signal.",
            "SMC, CRT, risk, session, spread, and news filters still matter.",
        ]
        next_steps = [
            "Compare this Order Flow read with SMC and CRT context.",
            "Review risk, session, spread, and news filters before trusting any setup.",
        ]
        reasons = list(report.reasons)

        if warnings:
            risks.extend(warnings)

        if report.average_confidence < float(config.low_confidence_threshold):
            risks.append("Average Order Flow confidence is low")
            if config.require_warning_on_low_confidence:
                warnings.append("Low average confidence means this replay should be treated cautiously")
        elif report.average_confidence >= float(config.high_confidence_threshold):
            strengths.append("Average Order Flow confidence is strong")
        else:
            strengths.append("Average Order Flow confidence is acceptable")

        mixed = self._has_mixed_steps(report)
        if mixed:
            risks.append("Replay contains mixed or conflicting Order Flow steps")

        if dominant_bias == "BULLISH":
            status = "STRONG_ORDERFLOW" if report.average_confidence >= config.high_confidence_threshold and not mixed else "WEAK_ORDERFLOW"
            market_read = (
                "Buyers were more aggressive during this replay. "
                f"Bullish steps={report.bullish_steps}, final CVD={report.final_cvd:.2f}."
            )
            strengths.append("Order Flow supports bullish context")
        elif dominant_bias == "BEARISH":
            status = "STRONG_ORDERFLOW" if report.average_confidence >= config.high_confidence_threshold and not mixed else "WEAK_ORDERFLOW"
            market_read = (
                "Sellers were more aggressive during this replay. "
                f"Bearish steps={report.bearish_steps}, final CVD={report.final_cvd:.2f}."
            )
            strengths.append("Order Flow supports bearish context")
        elif dominant_bias in {"NEUTRAL", "UNKNOWN"}:
            status = "MIXED_ORDERFLOW"
            market_read = "Order Flow was unclear or mixed. No dominant directional read was strong enough."
            risks.append("Dominant Order Flow bias is neutral or unknown")
        else:
            status = "MIXED_ORDERFLOW"
            market_read = "Order Flow was unclear or mixed."
            risks.append("Dominant Order Flow bias is not recognized")

        if warnings and report.total_steps == 0:
            status = "FAILED_REPLAY"
        elif report.warnings and report.total_steps > 0:
            risks.append("Replay report contains warnings")

        grade = self._grade(status, report, config, mixed)
        summary = (
            f"Order Flow replay review: dominant bias {dominant_bias}, "
            f"average confidence {report.average_confidence:.1f}, grade {grade}."
        )

        return OrderFlowReplayCoachReview(
            status=status,
            grade=grade,
            summary=summary,
            market_read=market_read,
            strengths=self._dedupe(strengths),
            risks=self._dedupe(risks),
            lessons=lessons,
            next_steps=next_steps,
            warnings=self._dedupe(warnings),
            reasons=reasons,
        )

    def explain(self, review: OrderFlowReplayCoachReview) -> str:
        """Return a readable coach explanation."""
        lines = [
            f"Status: {review.status}",
            f"Grade: {review.grade}",
            f"Summary: {review.summary}",
            f"Market read: {review.market_read}",
        ]
        if review.strengths:
            lines.append("Strengths: " + "; ".join(review.strengths))
        if review.risks:
            lines.append("Risks: " + "; ".join(review.risks))
        if review.warnings:
            lines.append("Warnings: " + "; ".join(review.warnings))
        if review.lessons:
            lines.append("Lessons: " + "; ".join(review.lessons))
        if review.next_steps:
            lines.append("Next steps: " + "; ".join(review.next_steps))
        return "\n".join(lines)

    def _grade(
        self,
        status: str,
        report: OrderFlowReplayReport,
        config: OrderFlowReplayCoachConfig,
        mixed: bool,
    ) -> str:
        """Assign a simple educational grade."""
        if status in {"NO_USABLE_ORDERFLOW", "FAILED_REPLAY"}:
            return "F"
        if report.average_confidence < float(config.low_confidence_threshold):
            return "D"
        if mixed or status == "MIXED_ORDERFLOW":
            return "C"
        if report.average_confidence >= float(config.high_confidence_threshold):
            return "A"
        return "B"

    def _has_mixed_steps(self, report: OrderFlowReplayReport) -> bool:
        """Return True when replay has more than one directional or unclear bucket."""
        active_buckets = 0
        for count in [report.bullish_steps, report.bearish_steps, report.neutral_steps, report.unknown_steps]:
            if count > 0:
                active_buckets += 1
        return active_buckets > 1

    def _dedupe(self, values: list[str]) -> list[str]:
        """Keep output stable and easy to read."""
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
