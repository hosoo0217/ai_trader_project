"""Export full trading session reports for later study.

This module is reporting/export only. It does not connect to brokers, live
feeds, Sierra Chart, CME, OpenAI, or any external API, and it never creates
trade signals.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any

from storage.session_report import TradingSessionReport


@dataclass
class SessionReportExportConfig:
    """Configuration for saving full trading session reports."""

    output_dir: str = "reports"
    text_filename: str = "trading_session_report.txt"
    json_filename: str = "trading_session_report.json"


@dataclass
class SessionReportExportResult:
    """Result returned after attempting to export a session report."""

    exported: bool
    text_path: str | None
    json_path: str | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class SessionReportExporter:
    """Save full trading session reports as text and JSON."""

    def export_text(
        self,
        report: TradingSessionReport | None,
        config: SessionReportExportConfig,
    ) -> str | None:
        """Write a beginner-readable text report and return its path."""
        try:
            output_dir = self._ensure_output_dir(config)
            path = output_dir / config.text_filename
            path.write_text(self._build_text(report), encoding="utf-8")
            return str(path)
        except OSError:
            return None

    def export_json(
        self,
        report: TradingSessionReport | None,
        config: SessionReportExportConfig,
    ) -> str | None:
        """Write a structured JSON report and return its path."""
        try:
            output_dir = self._ensure_output_dir(config)
            path = output_dir / config.json_filename
            path.write_text(json.dumps(self._report_dict(report), indent=2), encoding="utf-8")
            return str(path)
        except (OSError, TypeError, ValueError):
            return None

    def export_all(
        self,
        report: TradingSessionReport | None,
        config: SessionReportExportConfig,
    ) -> SessionReportExportResult:
        """Export both text and JSON files safely."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        text_path = self.export_text(report, config)
        if text_path:
            reasons.append(f"Text session report exported to {text_path}")
        else:
            blocking_reasons.append("Text session report export failed")

        json_path = self.export_json(report, config)
        if json_path:
            reasons.append(f"JSON session report exported to {json_path}")
        else:
            blocking_reasons.append("JSON session report export failed")

        return SessionReportExportResult(
            exported=text_path is not None and json_path is not None,
            text_path=text_path,
            json_path=json_path,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: SessionReportExportResult) -> str:
        """Return a short readable export summary."""
        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocks = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Trading session report export: "
            f"exported={result.exported}, "
            f"text_path={result.text_path}, "
            f"json_path={result.json_path}, "
            f"reasons={reasons}, "
            f"blocking_reasons={blocks}."
        )

    def _ensure_output_dir(self, config: SessionReportExportConfig) -> Path:
        """Create the output folder if it does not already exist."""
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _build_text(self, report: TradingSessionReport | None) -> str:
        """Build the text report in clear sections."""
        data = self._report_dict(report)
        lines = [
            "Full Trading Session Report",
            "",
            "Session Info",
            f"- Session ID: {data['session_id']}",
            f"- Mode: {data['mode']}",
            f"- Scenario: {data['scenario'] or 'N/A'}",
            f"- Profile: {data['profile'] or 'N/A'}",
            "",
            "Decision Summary",
            f"- Final action: {data['final_action']}",
            f"- Trade executed: {data['trade_executed']}",
            "",
            "Market Context",
            f"- Market bias: {data['market_bias'] or 'UNKNOWN'}",
            "",
            "SMC / CRT / Order Flow",
            f"- SMC bias: {data['smc_bias'] or 'N/A'}",
            f"- CRT bias: {data['crt_bias'] or 'N/A'}",
            f"- Order Flow bias: {data['orderflow_bias'] or 'N/A'}",
            "",
            "Safety Gate",
            f"- Safety status: {data['safety_status'] or 'N/A'}",
            f"- Safety passed: {data['safety_passed']}",
            "",
            "Blocked Reasons",
            f"- {self._join_list(data['blocked_reasons'])}",
            "",
            "Journal Summary",
            f"- {self._format_dict(data['journal_summary'])}",
            "",
            "Performance Summary",
            f"- {self._format_dict(data['performance_summary'])}",
            "",
            "AI Coach Summary",
            f"- {data['ai_coach_summary'] or 'N/A'}",
            "",
            "Decision Trace",
            f"- Decision trace ID: {data['decision_trace_id'] or 'N/A'}",
            "",
            "Warnings",
            f"- {self._join_list(data['warnings'])}",
            "",
            "Reasons",
            f"- {self._join_list(data['reasons'])}",
        ]
        return "\n".join(lines) + "\n"

    def _report_dict(self, report: TradingSessionReport | None) -> dict[str, Any]:
        """Return a JSON-safe report dictionary."""
        if report is None:
            return {
                "session_id": "UNKNOWN",
                "mode": "UNKNOWN",
                "scenario": None,
                "profile": None,
                "final_action": "UNKNOWN",
                "trade_executed": False,
                "market_bias": "UNKNOWN",
                "smc_bias": None,
                "crt_bias": None,
                "orderflow_bias": None,
                "safety_status": None,
                "safety_passed": False,
                "blocked_reasons": ["No session report provided"],
                "journal_summary": {},
                "performance_summary": {},
                "ai_coach_summary": None,
                "decision_trace_id": None,
                "reasons": ["No session report provided"],
                "warnings": ["Export created from missing session report"],
            }
        return self._safe_dataclass_dict(report)

    def _safe_dataclass_dict(self, value: Any) -> dict[str, Any]:
        """Convert dataclasses to plain JSON-safe dictionaries."""
        if is_dataclass(value):
            raw = asdict(value)
        elif isinstance(value, dict):
            raw = value
        else:
            raw = {}
        return {str(key): self._json_safe(item) for key, item in raw.items()}

    def _json_safe(self, value: Any) -> Any:
        """Keep JSON export safe when custom objects appear."""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if is_dataclass(value):
            return self._safe_dataclass_dict(value)
        return str(value)

    def _join_list(self, values: Any) -> str:
        if not values:
            return "None"
        if isinstance(values, list):
            return "; ".join(str(value) for value in values) if values else "None"
        return str(values)

    def _format_dict(self, value: Any) -> str:
        if not value:
            return "None"
        if isinstance(value, dict):
            return "; ".join(f"{key}={item}" for key, item in value.items())
        return str(value)
