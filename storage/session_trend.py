"""Performance trend analysis for saved trading session history.

This module is reporting/analysis only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API, and it never creates
trade signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SessionTrendConfig:
    """Configuration for session-history trend analysis."""

    min_sessions_for_trend: int = 3
    include_blocking_reason_counts: bool = True


@dataclass
class SessionTrendResult:
    """Trend result calculated from saved session reports."""

    total_sessions: int
    executed_sessions: int
    blocked_sessions: int
    execution_rate: float
    block_rate: float
    bullish_sessions: int
    bearish_sessions: int
    neutral_sessions: int
    unknown_sessions: int
    most_common_blocking_reason: str | None
    blocking_reason_counts: dict
    trend_status: str
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SessionTrendAnalyzer:
    """Analyze trends from a list of saved session report dictionaries."""

    def analyze(self, history: list[dict] | object, config: SessionTrendConfig) -> SessionTrendResult:
        """Analyze session history safely without generating trade signals."""
        if not isinstance(history, list):
            return self._empty_result(
                reasons=["No valid session history available"],
                warnings=["Session history was not a list"],
            )

        reports = [item for item in history if isinstance(item, dict)]
        invalid_count = len(history) - len(reports)

        executed_sessions = 0
        blocked_sessions = 0
        bias_counts = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0, "UNKNOWN": 0}
        blocking_reason_counts: dict[str, int] = {}

        for report in reports:
            if bool(report.get("trade_executed", False)):
                executed_sessions += 1
            else:
                blocked_sessions += 1

            bias = self._resolve_bias(report)
            bias_counts[bias] += 1

            for reason in self._safe_list(report.get("blocked_reasons", [])):
                blocking_reason_counts[reason] = blocking_reason_counts.get(reason, 0) + 1

        total_sessions = len(reports)
        execution_rate = (executed_sessions / total_sessions * 100.0) if total_sessions else 0.0
        block_rate = (blocked_sessions / total_sessions * 100.0) if total_sessions else 0.0
        trend_status = self._trend_status(total_sessions, execution_rate, block_rate, config)
        reasons = [f"Analyzed {total_sessions} session report(s)"]
        warnings = []
        if invalid_count:
            warnings.append(f"Ignored {invalid_count} invalid history item(s)")

        return SessionTrendResult(
            total_sessions=total_sessions,
            executed_sessions=executed_sessions,
            blocked_sessions=blocked_sessions,
            execution_rate=float(execution_rate),
            block_rate=float(block_rate),
            bullish_sessions=bias_counts["BULLISH"],
            bearish_sessions=bias_counts["BEARISH"],
            neutral_sessions=bias_counts["NEUTRAL"],
            unknown_sessions=bias_counts["UNKNOWN"],
            most_common_blocking_reason=self._most_common_blocking_reason(blocking_reason_counts),
            blocking_reason_counts=blocking_reason_counts if config.include_blocking_reason_counts else {},
            trend_status=trend_status,
            reasons=reasons,
            warnings=warnings,
        )

    def explain(self, result: SessionTrendResult) -> str:
        """Return a beginner-readable trend explanation."""
        common_reason = result.most_common_blocking_reason or "None"
        warnings = "; ".join(result.warnings) if result.warnings else "None"
        return (
            "Session trend: "
            f"status={result.trend_status}, "
            f"total_sessions={result.total_sessions}, "
            f"executed={result.executed_sessions}, "
            f"blocked={result.blocked_sessions}, "
            f"execution_rate={result.execution_rate:.1f}%, "
            f"block_rate={result.block_rate:.1f}%, "
            f"bullish={result.bullish_sessions}, "
            f"bearish={result.bearish_sessions}, "
            f"neutral={result.neutral_sessions}, "
            f"unknown={result.unknown_sessions}, "
            f"most_common_blocking_reason={common_reason}, "
            f"warnings={warnings}."
        )

    def _empty_result(self, reasons: list[str], warnings: list[str]) -> SessionTrendResult:
        """Build a safe empty trend result."""
        return SessionTrendResult(
            total_sessions=0,
            executed_sessions=0,
            blocked_sessions=0,
            execution_rate=0.0,
            block_rate=0.0,
            bullish_sessions=0,
            bearish_sessions=0,
            neutral_sessions=0,
            unknown_sessions=0,
            most_common_blocking_reason=None,
            blocking_reason_counts={},
            trend_status="NOT_ENOUGH_DATA",
            reasons=list(reasons),
            warnings=list(warnings),
        )

    def _trend_status(
        self,
        total_sessions: int,
        execution_rate: float,
        block_rate: float,
        config: SessionTrendConfig,
    ) -> str:
        """Resolve a simple status from execution/block rates."""
        if total_sessions < max(0, int(config.min_sessions_for_trend)):
            return "NOT_ENOUGH_DATA"
        if block_rate >= 70.0:
            return "MOSTLY_BLOCKED"
        if execution_rate >= 70.0:
            return "MOSTLY_EXECUTED"
        if total_sessions > 0:
            return "MIXED"
        return "UNKNOWN"

    def _resolve_bias(self, report: dict) -> str:
        raw_bias = report.get("market_bias") or report.get("final_bias") or report.get("final_action") or "UNKNOWN"
        bias = str(raw_bias or "UNKNOWN").upper()
        if bias in {"BUY", "BUYING", "LONG"}:
            return "BULLISH"
        if bias in {"SELL", "SELLING", "SHORT"}:
            return "BEARISH"
        if bias not in {"BULLISH", "BEARISH", "NEUTRAL"}:
            return "UNKNOWN"
        return bias

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

    def _most_common_blocking_reason(self, counts: dict[str, int]) -> str | None:
        if not counts:
            return None

        highest = max(counts.values())
        winners = [reason for reason, count in counts.items() if count == highest]
        if len(winners) != 1:
            return sorted(winners)[0] if winners else None
        return winners[0]
