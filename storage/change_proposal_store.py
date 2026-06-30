"""JSON-backed storage for approved change proposals.

This module stores proposal records only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, or automatically change strategy rules.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any


@dataclass
class ChangeProposalStoreConfig:
    """Configuration for change proposal storage."""

    output_dir: str = "reports"
    proposals_filename: str = "change_proposals.json"


@dataclass
class ChangeProposalStoreResult:
    """Result of saving one change proposal record."""

    saved: bool
    proposals_path: str | None
    total_proposals: int
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ChangeProposalStore:
    """Append and load future change proposal records in JSON."""

    def load_proposals(self, config: ChangeProposalStoreConfig) -> list[dict]:
        """Load proposals without crashing on missing or invalid files."""
        path = self._proposals_path(config)
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

    def append_proposal(
        self,
        proposal: object | None,
        config: ChangeProposalStoreConfig,
    ) -> ChangeProposalStoreResult:
        """Append one proposal record without applying strategy changes."""
        path = self._proposals_path(config)
        reasons = [
            "Change proposal stored for future human review",
            "Store records proposals only and does not change strategy rules",
        ]
        blocking_reasons: list[str] = []

        if proposal is None:
            blocking_reasons.append("Change proposal was not provided")

        try:
            proposals = self.load_proposals(config)
            proposals.append(self._proposal_dict(proposal, blocking_reasons))
            path.write_text(json.dumps(proposals, indent=2), encoding="utf-8")
            return ChangeProposalStoreResult(
                saved=True,
                proposals_path=str(path),
                total_proposals=len(proposals),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
        except (OSError, TypeError, ValueError) as exc:
            blocking_reasons.append(f"Could not save change proposal: {exc}")
            return ChangeProposalStoreResult(
                saved=False,
                proposals_path=str(path),
                total_proposals=0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

    def explain(self, result: ChangeProposalStoreResult | None) -> str:
        """Return a beginner-readable explanation of the storage result."""
        if result is None:
            return (
                "Change proposal store: saved=False, proposals_path=None, "
                "total_proposals=0, blocking_reasons=No store result was provided."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Change proposal store: "
            f"saved={result.saved}, "
            f"proposals_path={result.proposals_path or 'None'}, "
            f"total_proposals={result.total_proposals}. "
            "Stored proposals require final human review; no strategy rule is changed. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _ensure_output_dir(self, config: ChangeProposalStoreConfig) -> Path:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _proposals_path(self, config: ChangeProposalStoreConfig) -> Path:
        return self._ensure_output_dir(config) / config.proposals_filename

    def _proposal_dict(self, proposal: object | None, extra_blocking_reasons: list[str]) -> dict[str, Any]:
        return {
            "proposal_id": self._text(self._get(proposal, "proposal_id", None), "UNKNOWN"),
            "source_request_id": self._optional_text(self._get(proposal, "source_request_id", None)),
            "category": self._text(self._get(proposal, "category", None), "UNKNOWN"),
            "priority": self._text(self._get(proposal, "priority", None), "UNKNOWN"),
            "title": self._text(self._get(proposal, "title", None), "UNKNOWN"),
            "description": self._text(self._get(proposal, "description", None), "UNKNOWN"),
            "reason": self._text(self._get(proposal, "reason", None), "UNKNOWN"),
            "risk": self._text(self._get(proposal, "risk", None), "UNKNOWN"),
            "proposed_change": self._text(self._get(proposal, "proposed_change", None), "UNKNOWN"),
            "status": self._text(self._get(proposal, "status", None), "UNKNOWN"),
            "human_review_required": bool(self._get(proposal, "human_review_required", True)),
            "auto_implementation_allowed": bool(self._get(proposal, "auto_implementation_allowed", False)),
            "implementation_allowed": bool(self._get(proposal, "implementation_allowed", False)),
            "doc_path": self._optional_text(self._get(proposal, "doc_path", None)),
            "reasons": self._safe_list(self._get(proposal, "reasons", [])),
            "blocking_reasons": self._dedupe(
                self._safe_list(self._get(proposal, "blocking_reasons", []))
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
