"""Full trading session reports for paper/demo/backtest runs.

This module is reporting only. It does not connect to live data, brokers,
Sierra Chart, CME, OpenAI, or any external API, and it never creates trade
signals or real orders.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any
from uuid import uuid4


@dataclass
class TradingSessionReport:
    """Beginner-readable summary of one paper/demo/backtest session."""

    session_id: str
    mode: str
    scenario: str | None
    profile: str | None
    final_action: str
    trade_executed: bool
    market_bias: str | None
    smc_bias: str | None
    crt_bias: str | None
    orderflow_bias: str | None
    safety_status: str | None
    safety_passed: bool
    blocked_reasons: list[str] = field(default_factory=list)
    journal_summary: dict = field(default_factory=dict)
    performance_summary: dict = field(default_factory=dict)
    ai_coach_summary: str | None = None
    decision_trace_id: str | None = None
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class TradingSessionReportGenerator:
    """Create reporting summaries from paper trading flow results."""

    def generate_from_flow_result(
        self,
        flow_result: object | None,
        mode: str | None = None,
        scenario: str | None = None,
        profile: str | None = None,
    ) -> TradingSessionReport:
        """Extract a safe report from a PaperTradingFlowResult-like object."""
        if flow_result is None:
            return TradingSessionReport(
                session_id=str(uuid4()),
                mode=mode or "UNKNOWN",
                scenario=scenario,
                profile=profile,
                final_action="UNKNOWN",
                trade_executed=False,
                market_bias="UNKNOWN",
                smc_bias=None,
                crt_bias=None,
                orderflow_bias=None,
                safety_status=None,
                safety_passed=False,
                blocked_reasons=["No flow result provided"],
                journal_summary={},
                performance_summary={},
                ai_coach_summary=None,
                decision_trace_id=None,
                reasons=["No flow result provided"],
                warnings=["Session report was generated without a flow result"],
            )

        final_action = str(self._get(flow_result, "decision_action", "UNKNOWN") or "UNKNOWN")
        trade_executed = bool(self._get(flow_result, "trade_executed", False))
        safety_passed = bool(self._get(flow_result, "safety_allowed", False))
        blocked_reasons = self._blocked_reasons(flow_result)
        reasons = self._safe_list(self._get(flow_result, "reasons", []))
        warnings: list[str] = []

        if not trade_executed and not blocked_reasons:
            blocked_reasons = ["Trade was not executed"]
        if self._get(flow_result, "orderflow_bias", None) is None:
            warnings.append("Order Flow bias was not available")
        if self._get(flow_result, "smc_bias", None) is None:
            warnings.append("SMC bias was not available")
        if self._get(flow_result, "crt_bias", None) is None:
            warnings.append("CRT bias was not available")

        trace_id = self._get(flow_result, "trace_id", None)
        session_id = str(trace_id or self._get(flow_result, "session_id", None) or uuid4())

        return TradingSessionReport(
            session_id=session_id,
            mode=mode or str(self._get(flow_result, "mode", "UNKNOWN") or "UNKNOWN"),
            scenario=scenario if scenario is not None else self._optional_str(self._get(flow_result, "scenario", None)),
            profile=profile if profile is not None else self._optional_str(self._get(flow_result, "profile", None)),
            final_action=final_action,
            trade_executed=trade_executed,
            market_bias=self._optional_str(self._get(flow_result, "market_bias", "UNKNOWN")),
            smc_bias=self._optional_str(self._get(flow_result, "smc_bias", None)),
            crt_bias=self._optional_str(self._get(flow_result, "crt_bias", None)),
            orderflow_bias=self._optional_str(self._get(flow_result, "orderflow_bias", None)),
            safety_status=self._optional_str(self._get(flow_result, "safety_status", None)),
            safety_passed=safety_passed,
            blocked_reasons=blocked_reasons,
            journal_summary=self._journal_summary(flow_result),
            performance_summary=self._performance_summary(flow_result),
            ai_coach_summary=self._ai_coach_summary(flow_result),
            decision_trace_id=self._optional_str(trace_id),
            reasons=reasons or ["Session report generated"],
            warnings=self._dedupe(warnings),
        )

    def explain(self, report: TradingSessionReport) -> str:
        """Return a readable one-line explanation of a session report."""
        blocked_text = "; ".join(report.blocked_reasons) if report.blocked_reasons else "None"
        reasons_text = "; ".join(report.reasons) if report.reasons else "None"
        warnings_text = "; ".join(report.warnings) if report.warnings else "None"
        return (
            "Trading session report: "
            f"mode={report.mode}, "
            f"scenario={report.scenario}, "
            f"profile={report.profile}, "
            f"final_action={report.final_action}, "
            f"trade_executed={report.trade_executed}, "
            f"market_bias={report.market_bias}, "
            f"smc_bias={report.smc_bias}, "
            f"crt_bias={report.crt_bias}, "
            f"orderflow_bias={report.orderflow_bias}, "
            f"safety_status={report.safety_status}, "
            f"safety_passed={report.safety_passed}, "
            f"trace_id={report.decision_trace_id or 'N/A'}, "
            f"blocked_reasons={blocked_text}, "
            f"warnings={warnings_text}, "
            f"reasons={reasons_text}."
        )

    def _blocked_reasons(self, flow_result: object) -> list[str]:
        """Collect the main reasons a session did not allow a trade."""
        names = [
            "safety_blocking_reasons",
            "risk_blocking_reasons",
            "session_blocking_reasons",
            "news_blocking_reasons",
            "volatility_blocking_reasons",
            "spread_blocking_reasons",
            "smc_blocking_reasons",
            "crt_blocking_reasons",
            "orderflow_blocking_reasons",
            "alignment_blocking_reasons",
            "blocking_reasons",
        ]
        values: list[str] = []
        for name in names:
            values.extend(self._safe_list(self._get(flow_result, name, [])))
        return self._dedupe(values)

    def _journal_summary(self, flow_result: object) -> dict:
        """Return journal summary data if the caller attached it."""
        summary = self._get(flow_result, "journal_summary", None)
        if isinstance(summary, dict):
            return dict(summary)

        journal = self._get(flow_result, "journal", None)
        if journal is not None and hasattr(journal, "summarize"):
            try:
                return dict(journal.summarize())
            except Exception:
                return {}

        return {}

    def _performance_summary(self, flow_result: object) -> dict:
        """Return performance summary data if available."""
        summary = self._get(flow_result, "performance_summary", None)
        if isinstance(summary, dict):
            return dict(summary)

        performance = self._get(flow_result, "performance_report", None)
        if performance is None:
            performance = self._get(flow_result, "performance", None)
        if is_dataclass(performance):
            return dict(asdict(performance))
        if isinstance(performance, dict):
            return dict(performance)
        return {}

    def _ai_coach_summary(self, flow_result: object) -> str | None:
        """Extract a short AI Coach summary when one was attached by the caller."""
        for name in ["ai_coach_summary", "coach_summary", "ai_review_summary"]:
            value = self._get(flow_result, name, None)
            if value:
                return str(value)

        review = self._get(flow_result, "ai_review", None)
        if review is not None:
            summary = self._get(review, "summary", None)
            if summary:
                return str(summary)
        return None

    def _get(self, obj: object, name: str, default: Any = None) -> Any:
        """Read attributes or dictionary keys without crashing."""
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def _optional_str(self, value: object) -> str | None:
        if value is None:
            return None
        return str(value)

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
