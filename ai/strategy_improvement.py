"""Safe strategy improvement suggestions from session trend reviews.

This module is education/research/reporting only. It does not connect to live
data, brokers, Sierra Chart, CME, OpenAI, or any external API. It does not
change strategy rules, create orders, or generate trade signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai.session_trend_coach import SessionTrendCoachReview
from storage.session_trend import SessionTrendResult


@dataclass
class StrategyImprovementConfig:
    """Configuration for safe strategy improvement suggestions."""

    high_block_rate_threshold: float = 70.0
    low_execution_rate_threshold: float = 30.0
    require_human_approval: bool = True


@dataclass
class StrategyImprovementSuggestion:
    """One human-reviewed idea for improving strategy research."""

    category: str
    priority: str
    suggestion: str
    reason: str
    risk: str
    human_approval_required: bool


@dataclass
class StrategyImprovementResult:
    """Collection of safe strategy improvement suggestions."""

    status: str
    suggestions: list[StrategyImprovementSuggestion] = field(default_factory=list)
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class StrategyImprovementEngine:
    """Suggest research improvements from session trend and coach context."""

    def suggest(
        self,
        trend_result: SessionTrendResult | None,
        coach_review: SessionTrendCoachReview | None,
        config: StrategyImprovementConfig,
    ) -> StrategyImprovementResult:
        """Create safe suggestions without changing strategy behavior."""
        if trend_result is None:
            return StrategyImprovementResult(
                status="UNKNOWN",
                suggestions=[],
                summary="No usable session trend data was available for strategy suggestions.",
                warnings=["No trend data exists"],
                reasons=[
                    "Session trend result was not provided",
                    "Suggestions are research notes, not trade signals",
                    "Human approval is required before any strategy change",
                ],
            )

        suggestions: list[StrategyImprovementSuggestion] = []
        warnings = self._safe_list(getattr(trend_result, "warnings", []))
        reasons = self._safe_list(getattr(trend_result, "reasons", []))
        reasons.append("Suggestions are research notes, not trade signals")
        reasons.append("Human approval is required before any strategy change")

        if coach_review is None:
            warnings.append("AI Coach trend review was not provided; using trend data only")
        else:
            warnings.extend(self._safe_list(getattr(coach_review, "warnings", [])))
            reasons.extend(self._safe_list(getattr(coach_review, "reasons", [])))

        trend_status = str(getattr(trend_result, "trend_status", "UNKNOWN") or "UNKNOWN")
        block_rate = self._safe_float(getattr(trend_result, "block_rate", 0.0))
        execution_rate = self._safe_float(getattr(trend_result, "execution_rate", 0.0))
        common_blocker = self._common_blocker(trend_result)

        if trend_status == "NOT_ENOUGH_DATA":
            suggestions.append(
                self._suggestion(
                    category="BACKTESTING",
                    priority="MEDIUM",
                    suggestion="Save more session history before changing strategy rules.",
                    reason="There are not enough saved sessions to judge the strategy trend reliably.",
                    risk="Changing rules from a tiny sample can overfit the strategy to noise.",
                    config=config,
                )
            )

        if block_rate >= self._safe_float(config.high_block_rate_threshold):
            suggestions.append(
                self._suggestion(
                    category="BACKTESTING",
                    priority="HIGH",
                    suggestion="Review the most common blocking reasons before changing filters.",
                    reason=f"Block rate is high at {block_rate:.1f}%.",
                    risk="Loosening filters without review can let weak setups pass.",
                    config=config,
                )
            )
            suggestions.extend(self._blocking_reason_suggestions(common_blocker, config))

        high_execution_threshold = max(0.0, 100.0 - self._safe_float(config.low_execution_rate_threshold))
        if execution_rate >= high_execution_threshold:
            warnings.append("High execution rate does not automatically mean the strategy is profitable")
            suggestions.append(
                self._suggestion(
                    category="RISK_MANAGEMENT",
                    priority="MEDIUM",
                    suggestion="Check performance reports, drawdown, and risk metrics before trusting the pass rate.",
                    reason=f"Execution rate is high at {execution_rate:.1f}%.",
                    risk="A high pass rate can still lose money if risk control or trade quality is weak.",
                    config=config,
                )
            )

        suggestions = self._dedupe_suggestions(suggestions)
        warnings = self._dedupe(warnings)
        reasons = self._dedupe(reasons)

        if trend_status == "NOT_ENOUGH_DATA":
            status = "NOT_ENOUGH_DATA"
        elif suggestions:
            status = "HAS_SUGGESTIONS"
        else:
            status = "NO_SUGGESTIONS"

        summary = self._summary(status, len(suggestions))
        return StrategyImprovementResult(
            status=status,
            suggestions=suggestions,
            summary=summary,
            warnings=warnings,
            reasons=reasons,
        )

    def explain(self, result: StrategyImprovementResult | None) -> str:
        """Return a beginner-readable explanation of the suggestions."""
        if result is None:
            return (
                "Strategy improvement suggestions: status=UNKNOWN. "
                "No result was provided, so no suggestions can be reviewed."
            )

        lines = [
            f"Status: {result.status}",
            f"Summary: {result.summary}",
        ]

        if result.suggestions:
            lines.append("Suggestions:")
            for suggestion in result.suggestions:
                approval = "Yes" if suggestion.human_approval_required else "No"
                lines.append(
                    "- "
                    f"[{suggestion.priority}] {suggestion.category}: {suggestion.suggestion} "
                    f"Reason: {suggestion.reason} "
                    f"Risk: {suggestion.risk} "
                    f"Human approval required: {approval}."
                )

        if result.warnings:
            lines.append("Warnings: " + "; ".join(result.warnings))
        if result.reasons:
            lines.append("Reasons: " + "; ".join(result.reasons))

        return "\n".join(lines)

    def _blocking_reason_suggestions(
        self,
        common_blocker: str | None,
        config: StrategyImprovementConfig,
    ) -> list[StrategyImprovementSuggestion]:
        """Translate repeated blockers into specific research suggestions."""
        if not common_blocker:
            return []

        blocker = common_blocker.upper()
        suggestions: list[StrategyImprovementSuggestion] = []

        if "SESSION" in blocker:
            suggestions.append(
                self._suggestion(
                    category="SESSION_FILTER",
                    priority="MEDIUM",
                    suggestion="Review session filter settings and test weekday session samples.",
                    reason=f"Repeated blocker mentions session rules: {common_blocker}.",
                    risk="Changing session rules can expose the strategy to weaker market hours.",
                    config=config,
                )
            )
        if "SMC" in blocker:
            suggestions.append(
                self._suggestion(
                    category="SMC",
                    priority="MEDIUM",
                    suggestion="Review SMC sample data and swing detection quality.",
                    reason=f"Repeated blocker mentions SMC context: {common_blocker}.",
                    risk="Weak structure data can make market bias unreliable.",
                    config=config,
                )
            )
        if "ORDER_FLOW" in blocker or "ORDER FLOW" in blocker:
            suggestions.append(
                self._suggestion(
                    category="ORDER_FLOW",
                    priority="MEDIUM",
                    suggestion="Check footprint CSV data quality and order flow alignment settings.",
                    reason=f"Repeated blocker mentions Order Flow context: {common_blocker}.",
                    risk="Bad footprint data can make context confidence misleading.",
                    config=config,
                )
            )
        if "SPREAD" in blocker:
            suggestions.append(
                self._suggestion(
                    category="SPREAD_FILTER",
                    priority="MEDIUM",
                    suggestion="Review spread threshold settings against backtest conditions.",
                    reason=f"Repeated blocker mentions spread rules: {common_blocker}.",
                    risk="Loose spread limits can increase trading costs in simulation results.",
                    config=config,
                )
            )
        if "NEWS" in blocker:
            suggestions.append(
                self._suggestion(
                    category="NEWS_FILTER",
                    priority="MEDIUM",
                    suggestion="Review news filter timing around blocked sessions.",
                    reason=f"Repeated blocker mentions news rules: {common_blocker}.",
                    risk="Relaxing news rules can expose tests to unstable event windows.",
                    config=config,
                )
            )

        return suggestions

    def _suggestion(
        self,
        category: str,
        priority: str,
        suggestion: str,
        reason: str,
        risk: str,
        config: StrategyImprovementConfig,
    ) -> StrategyImprovementSuggestion:
        """Build a suggestion. Approval remains required for every idea."""
        return StrategyImprovementSuggestion(
            category=category,
            priority=priority,
            suggestion=suggestion,
            reason=reason,
            risk=risk,
            human_approval_required=True if config.require_human_approval else True,
        )

    def _common_blocker(self, trend_result: SessionTrendResult) -> str | None:
        """Find the most useful repeated blocking reason if one exists."""
        blocker = getattr(trend_result, "most_common_blocking_reason", None)
        if blocker:
            return str(blocker)

        counts = getattr(trend_result, "blocking_reason_counts", {})
        if not isinstance(counts, dict) or not counts:
            return None

        try:
            return str(max(counts, key=counts.get))
        except Exception:
            return None

    def _summary(self, status: str, suggestion_count: int) -> str:
        if status == "NOT_ENOUGH_DATA":
            return "More saved session history is needed before strategy changes are considered."
        if status == "HAS_SUGGESTIONS":
            return (
                f"Created {suggestion_count} research suggestion(s). "
                "Human approval is required before any strategy change."
            )
        if status == "NO_SUGGESTIONS":
            return "No strategy improvement suggestions were needed from the current trend."
        return "Strategy improvement status is unknown."

    def _safe_float(self, value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _safe_list(self, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, tuple):
            return [str(item) for item in value]
        if isinstance(value, set):
            return [str(item) for item in value]
        return [str(value)]

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _dedupe_suggestions(
        self,
        suggestions: list[StrategyImprovementSuggestion],
    ) -> list[StrategyImprovementSuggestion]:
        seen: set[tuple[str, str]] = set()
        result: list[StrategyImprovementSuggestion] = []
        for suggestion in suggestions:
            key = (suggestion.category, suggestion.suggestion)
            if key not in seen:
                seen.add(key)
                result.append(suggestion)
        return result
