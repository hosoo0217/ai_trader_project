"""JSON-backed history for full trading session reports.

This module is reporting/history only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API, and it never creates
trade signals.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any

from storage.session_report import TradingSessionReport


@dataclass
class SessionHistoryConfig:
    """Configuration for session history storage."""

    output_dir: str = "reports"
    history_filename: str = "session_history.json"


@dataclass
class SessionHistorySummary:
    """Summary of many saved trading session reports."""

    total_sessions: int
    executed_sessions: int
    blocked_sessions: int
    bullish_sessions: int
    bearish_sessions: int
    neutral_sessions: int
    unknown_sessions: int
    common_blocking_reasons: dict
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SessionHistoryStore:
    """Append and summarize TradingSessionReport records in JSON."""

    def load_history(self, config: SessionHistoryConfig) -> list[dict]:
        """Load history from disk without crashing on missing or invalid files."""
        path = self._history_path(config)
        if not path.exists():
            self._ensure_output_dir(config)
            path.write_text("[]", encoding="utf-8")
            return []

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(raw, list):
            return []

        return [item for item in raw if isinstance(item, dict)]

    def append_report(self, report: TradingSessionReport | dict | None, config: SessionHistoryConfig) -> bool:
        """Append one report to the JSON history file."""
        try:
            history = self.load_history(config)
            history.append(self._report_dict(report))
            path = self._history_path(config)
            path.write_text(json.dumps(history, indent=2), encoding="utf-8")
            return True
        except (OSError, TypeError, ValueError):
            return False

    def summarize(self, history: list[dict] | object) -> SessionHistorySummary:
        """Summarize saved session reports."""
        if not isinstance(history, list):
            return SessionHistorySummary(
                total_sessions=0,
                executed_sessions=0,
                blocked_sessions=0,
                bullish_sessions=0,
                bearish_sessions=0,
                neutral_sessions=0,
                unknown_sessions=0,
                common_blocking_reasons={},
                reasons=["No valid session history available"],
                warnings=["Session history was not a list"],
            )

        reports = [item for item in history if isinstance(item, dict)]
        executed_sessions = 0
        blocked_sessions = 0
        bias_counts = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0, "UNKNOWN": 0}
        blocking_counts: dict[str, int] = {}

        for report in reports:
            if bool(report.get("trade_executed", False)):
                executed_sessions += 1
            else:
                blocked_sessions += 1

            bias = self._resolve_bias(report)
            bias_counts[bias] += 1

            for reason in self._safe_list(report.get("blocked_reasons", [])):
                blocking_counts[reason] = blocking_counts.get(reason, 0) + 1

        return SessionHistorySummary(
            total_sessions=len(reports),
            executed_sessions=executed_sessions,
            blocked_sessions=blocked_sessions,
            bullish_sessions=bias_counts["BULLISH"],
            bearish_sessions=bias_counts["BEARISH"],
            neutral_sessions=bias_counts["NEUTRAL"],
            unknown_sessions=bias_counts["UNKNOWN"],
            common_blocking_reasons=blocking_counts,
            reasons=[f"Summarized {len(reports)} session report(s)"],
            warnings=[],
        )

    def explain(self, summary: SessionHistorySummary) -> str:
        """Return a readable one-line history summary."""
        blocks = (
            "; ".join(f"{reason}={count}" for reason, count in summary.common_blocking_reasons.items())
            if summary.common_blocking_reasons
            else "None"
        )
        warnings = "; ".join(summary.warnings) if summary.warnings else "None"
        return (
            "Session history summary: "
            f"total_sessions={summary.total_sessions}, "
            f"executed={summary.executed_sessions}, "
            f"blocked={summary.blocked_sessions}, "
            f"bullish={summary.bullish_sessions}, "
            f"bearish={summary.bearish_sessions}, "
            f"neutral={summary.neutral_sessions}, "
            f"unknown={summary.unknown_sessions}, "
            f"common_blocking_reasons={blocks}, "
            f"warnings={warnings}."
        )

    def _ensure_output_dir(self, config: SessionHistoryConfig) -> Path:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _history_path(self, config: SessionHistoryConfig) -> Path:
        return self._ensure_output_dir(config) / config.history_filename

    def _report_dict(self, report: TradingSessionReport | dict | None) -> dict[str, Any]:
        """Convert reports to JSON-safe dictionaries."""
        if report is None:
            return {
                "session_id": "UNKNOWN",
                "mode": "UNKNOWN",
                "scenario": None,
                "profile": None,
                "final_action": "UNKNOWN",
                "trade_executed": False,
                "market_bias": "UNKNOWN",
                "blocked_reasons": ["No session report provided"],
                "reasons": ["No session report provided"],
                "warnings": ["Missing report appended to history"],
            }
        if is_dataclass(report):
            raw = asdict(report)
        elif isinstance(report, dict):
            raw = dict(report)
        else:
            raw = {"session_id": "UNKNOWN", "trade_executed": False, "market_bias": "UNKNOWN"}
        return {str(key): self._json_safe(value) for key, value in raw.items()}

    def _json_safe(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if is_dataclass(value):
            return self._report_dict(value)
        return str(value)

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
