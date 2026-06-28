"""Export Order Flow replay reports for later study.

This module is reporting/export only. It does not connect to brokers, live
feeds, Sierra Chart, CME, OpenAI, or any external API, and it never creates
trade signals.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any

from ai.orderflow_replay_coach import OrderFlowReplayCoachReview
from orderflow.replay import OrderFlowReplayResult
from orderflow.replay_report import OrderFlowReplayReport


@dataclass
class OrderFlowReplayExportConfig:
    """Configuration for saving replay study reports."""

    output_dir: str = "reports"
    text_filename: str = "orderflow_replay_report.txt"
    json_filename: str = "orderflow_replay_report.json"
    include_steps: bool = True


@dataclass
class OrderFlowReplayExportResult:
    """Result returned after attempting to export replay reports."""

    exported: bool
    text_path: str | None
    json_path: str | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class OrderFlowReplayExporter:
    """Save replay output as readable text and structured JSON."""

    def export_text(
        self,
        replay_result: OrderFlowReplayResult | None,
        report: OrderFlowReplayReport | None,
        coach_review: OrderFlowReplayCoachReview | None,
        config: OrderFlowReplayExportConfig,
    ) -> str | None:
        """Write a beginner-readable text report and return its path."""
        try:
            output_dir = self._ensure_output_dir(config)
            path = output_dir / config.text_filename
            path.write_text(
                self._build_text(replay_result, report, coach_review, config),
                encoding="utf-8",
            )
            return str(path)
        except OSError:
            return None

    def export_json(
        self,
        replay_result: OrderFlowReplayResult | None,
        report: OrderFlowReplayReport | None,
        coach_review: OrderFlowReplayCoachReview | None,
        config: OrderFlowReplayExportConfig,
    ) -> str | None:
        """Write a structured JSON report and return its path."""
        try:
            output_dir = self._ensure_output_dir(config)
            path = output_dir / config.json_filename
            payload = self._build_json_payload(replay_result, report, coach_review, config)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return str(path)
        except (OSError, TypeError, ValueError):
            return None

    def export_all(
        self,
        replay_result: OrderFlowReplayResult | None,
        report: OrderFlowReplayReport | None,
        coach_review: OrderFlowReplayCoachReview | None,
        config: OrderFlowReplayExportConfig,
    ) -> OrderFlowReplayExportResult:
        """Export both text and JSON files safely."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        text_path = self.export_text(replay_result, report, coach_review, config)
        if text_path:
            reasons.append(f"Text report exported to {text_path}")
        else:
            blocking_reasons.append("Text report export failed")

        json_path = self.export_json(replay_result, report, coach_review, config)
        if json_path:
            reasons.append(f"JSON report exported to {json_path}")
        else:
            blocking_reasons.append("JSON report export failed")

        return OrderFlowReplayExportResult(
            exported=text_path is not None and json_path is not None,
            text_path=text_path,
            json_path=json_path,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: OrderFlowReplayExportResult) -> str:
        """Return a short readable export summary."""
        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocks = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Order Flow replay export: "
            f"exported={result.exported}, "
            f"text_path={result.text_path}, "
            f"json_path={result.json_path}, "
            f"reasons={reasons}, "
            f"blocking_reasons={blocks}."
        )

    def _ensure_output_dir(self, config: OrderFlowReplayExportConfig) -> Path:
        """Create the output folder if it does not already exist."""
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _build_text(
        self,
        replay_result: OrderFlowReplayResult | None,
        report: OrderFlowReplayReport | None,
        coach_review: OrderFlowReplayCoachReview | None,
        config: OrderFlowReplayExportConfig,
    ) -> str:
        """Build the text report in simple sections."""
        lines: list[str] = []
        replay_summary = self._replay_summary(replay_result)
        report_data = self._report_summary(report)
        coach_data = self._coach_summary(coach_review)

        lines.extend(
            [
                "Order Flow Replay Summary",
                f"- Passed: {replay_summary['passed']}",
                f"- Data quality status: {replay_summary['data_quality_status']}",
                f"- Steps: {replay_summary['step_count']}",
                f"- Final bias: {replay_summary['final_bias']}",
                f"- Final confidence: {replay_summary['final_confidence']}",
                f"- Final CVD: {replay_summary['final_cvd']}",
                f"- Reasons: {self._join_list(replay_summary['reasons'])}",
                f"- Blocking reasons: {self._join_list(replay_summary['blocking_reasons'])}",
                "",
                "Order Flow Replay Report",
                f"- Total steps: {report_data['total_steps']}",
                f"- Bullish steps: {report_data['bullish_steps']}",
                f"- Bearish steps: {report_data['bearish_steps']}",
                f"- Neutral steps: {report_data['neutral_steps']}",
                f"- Unknown steps: {report_data['unknown_steps']}",
                f"- Dominant bias: {report_data['dominant_bias']}",
                f"- Average confidence: {report_data['average_confidence']}",
                f"- Max confidence: {report_data['max_confidence']}",
                f"- Min confidence: {report_data['min_confidence']}",
                f"- Final bias: {report_data['final_bias']}",
                f"- Final confidence: {report_data['final_confidence']}",
                f"- Final CVD: {report_data['final_cvd']}",
                f"- Warnings: {self._join_list(report_data['warnings'])}",
                f"- Reasons: {self._join_list(report_data['reasons'])}",
                "",
                "AI Coach Order Flow Replay Review",
                f"- Status: {coach_data['status']}",
                f"- Grade: {coach_data['grade']}",
                f"- Summary: {coach_data['summary']}",
                f"- Market read: {coach_data['market_read']}",
                f"- Strengths: {self._join_list(coach_data['strengths'])}",
                f"- Risks: {self._join_list(coach_data['risks'])}",
                f"- Lessons: {self._join_list(coach_data['lessons'])}",
                f"- Next steps: {self._join_list(coach_data['next_steps'])}",
                f"- Warnings: {self._join_list(coach_data['warnings'])}",
                f"- Reasons: {self._join_list(coach_data['reasons'])}",
                "",
                "Warnings",
                f"- {self._join_list(self._collect_warnings(report, coach_review))}",
                "",
                "Blocking reasons",
                f"- {self._join_list(self._collect_blocking_reasons(replay_result))}",
            ]
        )

        if config.include_steps:
            lines.extend(["", "Replay Steps"])
            steps = self._replay_steps(replay_result)
            if not steps:
                lines.append("- No replay steps available")
            for step in steps:
                lines.extend(
                    [
                        f"- Index: {step['index']}",
                        f"  Time: {step['time']}",
                        f"  Candle delta: {step['candle_delta']}",
                        f"  Cumulative delta: {step['cumulative_delta']}",
                        f"  Delta direction: {step['delta_direction']}",
                        f"  Imbalance bias: {step['imbalance_bias']}",
                        f"  Absorption bias: {step['absorption_bias']}",
                        f"  Order Flow bias: {step['orderflow_bias']}",
                        f"  Confidence: {step['orderflow_confidence']}",
                    ]
                )

        return "\n".join(lines) + "\n"

    def _build_json_payload(
        self,
        replay_result: OrderFlowReplayResult | None,
        report: OrderFlowReplayReport | None,
        coach_review: OrderFlowReplayCoachReview | None,
        config: OrderFlowReplayExportConfig,
    ) -> dict[str, Any]:
        """Build a JSON-safe payload for tools and future reports."""
        return {
            "replay_result": self._replay_summary(replay_result),
            "replay_steps": self._replay_steps(replay_result) if config.include_steps else [],
            "replay_report": self._report_summary(report),
            "coach_review": self._coach_summary(coach_review),
            "warnings": self._collect_warnings(report, coach_review),
            "blocking_reasons": self._collect_blocking_reasons(replay_result),
        }

    def _replay_summary(self, replay_result: OrderFlowReplayResult | None) -> dict[str, Any]:
        if replay_result is None:
            return {
                "passed": False,
                "data_quality_status": None,
                "step_count": 0,
                "final_bias": "UNKNOWN",
                "final_confidence": 0.0,
                "final_cvd": 0.0,
                "reasons": ["No replay result provided"],
                "blocking_reasons": [],
            }
        return {
            "passed": bool(getattr(replay_result, "passed", False)),
            "data_quality_status": getattr(replay_result, "data_quality_status", None),
            "step_count": len(getattr(replay_result, "steps", []) or []),
            "final_bias": str(getattr(replay_result, "final_bias", "UNKNOWN") or "UNKNOWN"),
            "final_confidence": self._safe_float(getattr(replay_result, "final_confidence", 0.0)),
            "final_cvd": self._safe_float(getattr(replay_result, "final_cvd", 0.0)),
            "reasons": list(getattr(replay_result, "reasons", []) or []),
            "blocking_reasons": list(getattr(replay_result, "blocking_reasons", []) or []),
        }

    def _replay_steps(self, replay_result: OrderFlowReplayResult | None) -> list[dict[str, Any]]:
        steps = list(getattr(replay_result, "steps", []) or []) if replay_result is not None else []
        return [self._safe_dataclass_dict(step) for step in steps]

    def _report_summary(self, report: OrderFlowReplayReport | None) -> dict[str, Any]:
        if report is None:
            return {
                "total_steps": 0,
                "bullish_steps": 0,
                "bearish_steps": 0,
                "neutral_steps": 0,
                "unknown_steps": 0,
                "average_confidence": 0.0,
                "max_confidence": 0.0,
                "min_confidence": 0.0,
                "final_bias": "UNKNOWN",
                "final_confidence": 0.0,
                "final_cvd": 0.0,
                "dominant_bias": "UNKNOWN",
                "reasons": ["No replay report provided"],
                "warnings": [],
            }
        return self._safe_dataclass_dict(report)

    def _coach_summary(self, coach_review: OrderFlowReplayCoachReview | None) -> dict[str, Any]:
        if coach_review is None:
            return {
                "status": "NO_USABLE_ORDERFLOW",
                "grade": "F",
                "summary": "No AI Coach review provided.",
                "market_read": "Order Flow could not be reviewed.",
                "strengths": [],
                "risks": [],
                "lessons": [],
                "next_steps": [],
                "warnings": [],
                "reasons": ["No AI Coach review provided"],
            }
        return self._safe_dataclass_dict(coach_review)

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
        """Keep JSON export safe when times or custom objects appear."""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if is_dataclass(value):
            return self._safe_dataclass_dict(value)
        return str(value)

    def _collect_warnings(
        self,
        report: OrderFlowReplayReport | None,
        coach_review: OrderFlowReplayCoachReview | None,
    ) -> list[str]:
        warnings: list[str] = []
        warnings.extend(list(getattr(report, "warnings", []) or []) if report is not None else [])
        warnings.extend(list(getattr(coach_review, "warnings", []) or []) if coach_review is not None else [])
        return self._dedupe(warnings)

    def _collect_blocking_reasons(self, replay_result: OrderFlowReplayResult | None) -> list[str]:
        if replay_result is None:
            return []
        return list(getattr(replay_result, "blocking_reasons", []) or [])

    def _join_list(self, values: Any) -> str:
        if not values:
            return "None"
        if isinstance(values, list):
            return "; ".join(str(value) for value in values) if values else "None"
        return str(values)

    def _safe_float(self, value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
