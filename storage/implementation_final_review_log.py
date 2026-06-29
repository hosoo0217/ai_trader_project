"""JSON-backed log for implementation final review decisions.

This module records final review decisions only. It does not connect to live
data, brokers, Sierra Chart, CME, OpenAI, or any external API. It does not
create orders, generate trade signals, edit config, or change strategy rules.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any


@dataclass
class ImplementationFinalReviewLogConfig:
    """Configuration for the implementation final review log."""

    output_dir: str = "reports"
    log_filename: str = "implementation_final_reviews.json"


@dataclass
class ImplementationFinalReviewLogResult:
    """Result of saving one final review record."""

    saved: bool
    log_path: str | None
    total_records: int
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ImplementationFinalReviewLogStore:
    """Append and load implementation final review records in JSON."""

    def load_log(self, config: ImplementationFinalReviewLogConfig) -> list[dict]:
        """Load final review records without crashing on missing or invalid files."""
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

    def append_review(
        self,
        plan: object | None,
        final_review_result: object | None,
        config: ImplementationFinalReviewLogConfig,
    ) -> ImplementationFinalReviewLogResult:
        """Append one final review record without applying strategy changes."""
        path = self._log_path(config)
        reasons = [
            "Implementation final review recorded for audit and future review",
            "Final review log records decisions only and does not change strategy rules",
        ]
        blocking_reasons: list[str] = []

        if plan is None:
            blocking_reasons.append("Implementation plan was not provided")
        if final_review_result is None:
            blocking_reasons.append("Implementation final review result was not provided")

        try:
            records = self.load_log(config)
            records.append(self._review_record(plan, final_review_result, blocking_reasons))
            path.write_text(json.dumps(records, indent=2), encoding="utf-8")
            return ImplementationFinalReviewLogResult(
                saved=True,
                log_path=str(path),
                total_records=len(records),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
        except (OSError, TypeError, ValueError) as exc:
            blocking_reasons.append(f"Could not save implementation final review log: {exc}")
            return ImplementationFinalReviewLogResult(
                saved=False,
                log_path=str(path),
                total_records=0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

    def explain(self, result: ImplementationFinalReviewLogResult | None) -> str:
        """Return a beginner-readable explanation of the final review log result."""
        if result is None:
            return (
                "Implementation final review log: saved=False, log_path=None, "
                "total_records=0, blocking_reasons=No final review log result was provided."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Implementation final review log: "
            f"saved={result.saved}, "
            f"log_path={result.log_path or 'None'}, "
            f"total_records={result.total_records}. "
            "APPROVE_FOR_WORK remains future human-reviewed work only; no strategy rule is changed. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _ensure_output_dir(self, config: ImplementationFinalReviewLogConfig) -> Path:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _log_path(self, config: ImplementationFinalReviewLogConfig) -> Path:
        return self._ensure_output_dir(config) / config.log_filename

    def _review_record(
        self,
        plan: object | None,
        final_review_result: object | None,
        extra_blocking_reasons: list[str],
    ) -> dict[str, Any]:
        decision = self._get(final_review_result, "decision", None)
        return {
            "plan_id": self._optional_text(
                self._get(plan, "plan_id", None)
                or self._get(final_review_result, "plan_id", None)
                or self._get(decision, "plan_id", None)
            ),
            "source_proposal_id": self._optional_text(self._get(plan, "source_proposal_id", None)),
            "title": self._text(self._get(plan, "title", None), "UNKNOWN"),
            "category": self._text(self._get(plan, "category", None), "UNKNOWN"),
            "priority": self._text(self._get(plan, "priority", None), "UNKNOWN"),
            "final_review_decision": self._text(self._get(decision, "decision", None), "UNKNOWN"),
            "final_review_status": self._text(self._get(final_review_result, "status", None), "UNKNOWN"),
            "approved_for_work": bool(self._get(final_review_result, "approved_for_work", False)),
            "implementation_allowed_now": False,
            "reviewed_by": self._optional_text(self._get(decision, "reviewed_by", None)),
            "reviewed_at": self._optional_text(self._get(decision, "reviewed_at", None)),
            "notes": self._optional_text(self._get(decision, "notes", None)),
            "human_final_approval_required": True,
            "auto_implementation_allowed": False,
            "reasons": self._safe_list(self._get(final_review_result, "reasons", [])),
            "blocking_reasons": self._dedupe(
                self._safe_list(self._get(final_review_result, "blocking_reasons", []))
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
