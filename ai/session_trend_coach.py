"""Rule-based AI Coach review for session history trends.

This module is education/reporting only. It does not call OpenAI APIs, connect
to brokers, connect to live data, or create trade signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from storage.session_trend import SessionTrendResult


@dataclass
class SessionTrendCoachConfig:
    """Configuration for session trend coaching."""

    high_block_rate_threshold: float = 70.0
    high_execution_rate_threshold: float = 70.0
    min_sessions_for_confident_review: int = 5


@dataclass
class SessionTrendCoachReview:
    """Beginner-friendly review of session history trend results."""

    status: str
    grade: str
    summary: str
    trend_read: str
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    lessons: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class SessionTrendCoach:
    """Explain session trend results in simple educational language."""

    def review(
        self,
        trend_result: SessionTrendResult | None,
        config: SessionTrendCoachConfig,
    ) -> SessionTrendCoachReview:
        """Review a session trend without generating trade instructions."""
        if trend_result is None:
            return SessionTrendCoachReview(
                status="UNKNOWN",
                grade="F",
                summary="No usable session trend data was available to review.",
                trend_read="Session trend is unknown because no trend result was provided.",
                strengths=[],
                risks=["No session trend context is available"],
                lessons=self._base_lessons(),
                next_steps=["Save more paper/demo/backtest session reports, then review the trend again."],
                warnings=["Session trend result is missing"],
                reasons=["No session trend result provided"],
            )

        status, trend_read = self._status_and_read(trend_result)
        strengths: list[str] = []
        risks: list[str] = []
        warnings = list(trend_result.warnings)
        reasons = list(trend_result.reasons)
        lessons = self._base_lessons()
        next_steps = [
            "Save more session reports to improve review quality.",
            "Compare trend behavior with SMC, CRT, Order Flow, risk, session, news, and spread filters.",
        ]

        if trend_result.total_sessions < int(config.min_sessions_for_confident_review):
            warnings.append("More saved sessions are needed for a confident review")
            risks.append("Small history sample can make the trend unreliable")

        if trend_result.block_rate >= float(config.high_block_rate_threshold):
            risks.append("Many sessions are being blocked")
            warnings.append("High block rate means common blocking reasons should be reviewed")
            if trend_result.most_common_blocking_reason:
                next_steps.append(f"Review repeated blocker: {trend_result.most_common_blocking_reason}.")

        if trend_result.execution_rate >= float(config.high_execution_rate_threshold):
            strengths.append("Many sessions are passing filters")
            warnings.append("High execution rate alone does not prove profitability")

        if trend_result.most_common_blocking_reason:
            risks.append(f"Most common blocking reason: {trend_result.most_common_blocking_reason}")

        if status == "MOSTLY_BLOCKED":
            lessons.append("Blocked trades are useful because they can protect capital.")
        elif status == "MOSTLY_EXECUTED":
            lessons.append("Execution rate must be reviewed alongside risk, PnL, and drawdown.")
        elif status == "MIXED_TREND":
            lessons.append("Mixed behavior can be normal while the rules are still being tested.")

        grade = self._grade(status, trend_result, config)
        summary = (
            f"Session trend review: status {status}, "
            f"execution rate {trend_result.execution_rate:.1f}%, "
            f"block rate {trend_result.block_rate:.1f}%, grade {grade}."
        )

        return SessionTrendCoachReview(
            status=status,
            grade=grade,
            summary=summary,
            trend_read=trend_read,
            strengths=self._dedupe(strengths),
            risks=self._dedupe(risks),
            lessons=self._dedupe(lessons),
            next_steps=self._dedupe(next_steps),
            warnings=self._dedupe(warnings),
            reasons=reasons,
        )

    def explain(self, review: SessionTrendCoachReview) -> str:
        """Return a readable coach explanation."""
        lines = [
            f"Status: {review.status}",
            f"Grade: {review.grade}",
            f"Summary: {review.summary}",
            f"Trend read: {review.trend_read}",
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

    def _status_and_read(self, trend_result: SessionTrendResult) -> tuple[str, str]:
        """Map trend status into coach status and plain-language read."""
        trend_status = str(trend_result.trend_status or "UNKNOWN")
        common = trend_result.most_common_blocking_reason

        if trend_status == "NOT_ENOUGH_DATA":
            return (
                "NOT_ENOUGH_DATA",
                "More saved sessions are needed before the trend can be reviewed with confidence.",
            )
        if trend_status == "MOSTLY_BLOCKED":
            detail = f" The most common blocker is {common}." if common else ""
            return (
                "MOSTLY_BLOCKED",
                "The system is being conservative because most sessions are blocked." + detail,
            )
        if trend_status == "MOSTLY_EXECUTED":
            return (
                "MOSTLY_EXECUTED",
                "More setups are passing filters, but execution rate alone does not mean profitability.",
            )
        if trend_status == "MIXED":
            return (
                "MIXED_TREND",
                "The system has mixed behavior, with both executed and blocked sessions present.",
            )
        return ("UNKNOWN", "Session trend status is unknown.")

    def _grade(self, status: str, trend_result: SessionTrendResult, config: SessionTrendCoachConfig) -> str:
        """Assign a simple educational grade."""
        if status == "UNKNOWN":
            return "F"
        if status == "NOT_ENOUGH_DATA":
            return "D" if trend_result.total_sessions > 0 else "F"
        if trend_result.total_sessions < int(config.min_sessions_for_confident_review):
            return "C"
        if status == "MOSTLY_EXECUTED":
            return "B"
        if status == "MOSTLY_BLOCKED":
            return "C"
        if status == "MIXED_TREND":
            return "C"
        return "F"

    def _base_lessons(self) -> list[str]:
        """Reusable reminders that keep the review educational."""
        return [
            "This is not a trade signal.",
            "SMC, CRT, Order Flow, risk, session, news, and spread filters still matter.",
            "More history improves review quality.",
        ]

    def _dedupe(self, values: list[str]) -> list[str]:
        """Keep output stable and easy to read."""
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
