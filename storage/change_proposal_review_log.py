"""JSON-backed log for change proposal review decisions.

This module records review decisions only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, or automatically implement strategy changes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any


@dataclass
class ChangeProposalReviewLogConfig:
    """Configuration for the change proposal review log."""

    output_dir: str = "reports"
    log_filename: str = "change_proposal_reviews.json"


@dataclass
class ChangeProposalReviewLogResult:
    """Result of saving one change proposal review record."""

    saved: bool
    log_path: str | None
    total_records: int
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ChangeProposalReviewLogStore:
    """Append and load change proposal review records in JSON."""

    def load_log(self, config: ChangeProposalReviewLogConfig) -> list[dict]:
        """Load review records without crashing on missing or invalid files."""
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
        proposal: object | None,
        review_result: object | None,
        config: ChangeProposalReviewLogConfig,
    ) -> ChangeProposalReviewLogResult:
        """Append one review record without applying strategy changes."""
        path = self._log_path(config)
        reasons = [
            "Change proposal review recorded for audit and future review",
            "Review log records decisions only and does not change strategy rules",
        ]
        blocking_reasons: list[str] = []

        if proposal is None:
            blocking_reasons.append("Change proposal was not provided")
        if review_result is None:
            blocking_reasons.append("Change proposal review result was not provided")

        try:
            records = self.load_log(config)
            records.append(self._review_record(proposal, review_result, blocking_reasons))
            path.write_text(json.dumps(records, indent=2), encoding="utf-8")
            return ChangeProposalReviewLogResult(
                saved=True,
                log_path=str(path),
                total_records=len(records),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
        except (OSError, TypeError, ValueError) as exc:
            blocking_reasons.append(f"Could not save change proposal review log: {exc}")
            return ChangeProposalReviewLogResult(
                saved=False,
                log_path=str(path),
                total_records=0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

    def explain(self, result: ChangeProposalReviewLogResult | None) -> str:
        """Return a beginner-readable explanation of the review log result."""
        if result is None:
            return (
                "Change proposal review log: saved=False, log_path=None, "
                "total_records=0, blocking_reasons=No review log result was provided."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Change proposal review log: "
            f"saved={result.saved}, "
            f"log_path={result.log_path or 'None'}, "
            f"total_records={result.total_records}. "
            "ACCEPT remains future work only; no strategy rule is changed. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _ensure_output_dir(self, config: ChangeProposalReviewLogConfig) -> Path:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _log_path(self, config: ChangeProposalReviewLogConfig) -> Path:
        return self._ensure_output_dir(config) / config.log_filename

    def _review_record(
        self,
        proposal: object | None,
        review_result: object | None,
        extra_blocking_reasons: list[str],
    ) -> dict[str, Any]:
        decision = self._get(review_result, "decision", None)
        return {
            "proposal_id": self._optional_text(
                self._get(proposal, "proposal_id", None)
                or self._get(review_result, "proposal_id", None)
                or self._get(decision, "proposal_id", None)
            ),
            "source_request_id": self._optional_text(self._get(proposal, "source_request_id", None)),
            "category": self._text(self._get(proposal, "category", None), "UNKNOWN"),
            "priority": self._text(self._get(proposal, "priority", None), "UNKNOWN"),
            "title": self._text(self._get(proposal, "title", None), "UNKNOWN"),
            "description": self._text(self._get(proposal, "description", None), "UNKNOWN"),
            "review_decision": self._text(self._get(decision, "decision", None), "UNKNOWN"),
            "review_status": self._text(self._get(review_result, "status", None), "UNKNOWN"),
            "accepted": bool(self._get(review_result, "accepted", False)),
            "implementation_allowed": bool(self._get(review_result, "implementation_allowed", False)),
            "reviewed_by": self._optional_text(self._get(decision, "reviewed_by", None)),
            "reviewed_at": self._optional_text(self._get(decision, "reviewed_at", None)),
            "notes": self._optional_text(self._get(decision, "notes", None)),
            "human_review_required": bool(self._get(proposal, "human_review_required", True)),
            "auto_implementation_allowed": bool(self._get(proposal, "auto_implementation_allowed", False)),
            "reasons": self._safe_list(self._get(review_result, "reasons", [])),
            "blocking_reasons": self._dedupe(
                self._safe_list(self._get(review_result, "blocking_reasons", []))
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
