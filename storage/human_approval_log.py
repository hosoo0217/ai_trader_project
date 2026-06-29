"""JSON-backed log for human approval decisions.

This module is audit/reporting only. It does not connect to live data, brokers,
Sierra Chart, CME, OpenAI, or any external API. It does not create orders,
generate trade signals, or automatically change strategy rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, is_dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class HumanApprovalLogConfig:
    """Configuration for the human approval decision log."""

    output_dir: str = "reports"
    log_filename: str = "human_approval_log.json"


@dataclass
class HumanApprovalLogResult:
    """Result of saving one human approval decision record."""

    saved: bool
    log_path: str | None
    total_records: int
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class HumanApprovalLogStore:
    """Append and load human approval decision records in JSON."""

    def load_log(self, config: HumanApprovalLogConfig) -> list[dict]:
        """Load approval records without crashing on missing or invalid files."""
        path = self._log_path(config)
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
            return []

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(raw, list):
            return []

        return [item for item in raw if isinstance(item, dict)]

    def append_decision(
        self,
        request: object | None,
        decision_result: object | None,
        config: HumanApprovalLogConfig,
    ) -> HumanApprovalLogResult:
        """Append one decision record without applying any strategy change."""
        path = self._log_path(config)
        reasons = [
            "Human approval decision recorded for audit and review",
            "Log records decisions only and does not change strategy rules",
        ]
        blocking_reasons: list[str] = []

        if request is None:
            blocking_reasons.append("Approval request was not provided")
        if decision_result is None:
            blocking_reasons.append("Approval decision result was not provided")

        try:
            records = self.load_log(config)
            records.append(self._record_dict(request, decision_result, blocking_reasons))
            path.write_text(json.dumps(records, indent=2), encoding="utf-8")
            return HumanApprovalLogResult(
                saved=True,
                log_path=str(path),
                total_records=len(records),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
        except (OSError, TypeError, ValueError) as exc:
            blocking_reasons.append(f"Could not save human approval decision log: {exc}")
            return HumanApprovalLogResult(
                saved=False,
                log_path=str(path),
                total_records=0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

    def explain(self, result: HumanApprovalLogResult | None) -> str:
        """Return a beginner-readable explanation of the log result."""
        if result is None:
            return (
                "Human approval decision log: saved=False, log_path=None, "
                "total_records=0, blocking_reasons=No log result was provided."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Human approval decision log: "
            f"saved={result.saved}, "
            f"log_path={result.log_path or 'None'}, "
            f"total_records={result.total_records}. "
            "This log records human decisions only; no strategy rule is changed. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _ensure_output_dir(self, config: HumanApprovalLogConfig) -> Path:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _log_path(self, config: HumanApprovalLogConfig) -> Path:
        return self._ensure_output_dir(config) / config.log_filename

    def _record_dict(
        self,
        request: object | None,
        decision_result: object | None,
        extra_blocking_reasons: list[str],
    ) -> dict[str, Any]:
        decision = self._get(decision_result, "decision", None)
        return {
            "request_id": self._text(
                self._get(request, "request_id", None)
                or self._get(decision, "request_id", None)
                or self._get(decision_result, "request_id", None),
                "UNKNOWN",
            ),
            "suggestion_category": self._text(self._get(request, "suggestion_category", None), "UNKNOWN"),
            "suggestion_priority": self._text(self._get(request, "suggestion_priority", None), "UNKNOWN"),
            "suggestion_text": self._text(self._get(request, "suggestion_text", None), "UNKNOWN"),
            "request_status": self._text(
                self._get(request, "status", None) or self._get(decision_result, "status", None),
                "UNKNOWN",
            ),
            "decision": self._text(self._get(decision, "decision", None), "UNKNOWN"),
            "approved": bool(self._get(decision_result, "approved", False)),
            "allowed_to_apply": bool(self._get(decision_result, "allowed_to_apply", False)),
            "decided_by": self._optional_text(self._get(decision, "decided_by", None)),
            "decided_at": self._optional_text(self._get(decision, "decided_at", None)),
            "notes": self._optional_text(self._get(decision, "notes", None)),
            "reasons": self._safe_list(self._get(decision_result, "reasons", [])),
            "blocking_reasons": self._dedupe(
                self._safe_list(self._get(decision_result, "blocking_reasons", []))
                + list(extra_blocking_reasons)
            ),
        }

    def _get(self, obj: object | None, name: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def _text(self, value: object, default: str) -> str:
        if value is None:
            return default
        return str(value)

    def _optional_text(self, value: object) -> str | None:
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
        if is_dataclass(value):
            return [str(asdict(value))]
        return [str(value)]

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
