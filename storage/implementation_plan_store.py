"""JSON-backed storage for future implementation plans.

This module stores planning records only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, edit config, or modify strategy rules.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any


@dataclass
class ImplementationPlanStoreConfig:
    """Configuration for implementation plan storage."""

    output_dir: str = "reports"
    plans_filename: str = "implementation_plans.json"


@dataclass
class ImplementationPlanStoreResult:
    """Result of saving one implementation plan record."""

    saved: bool
    plans_path: str | None
    total_plans: int
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ImplementationPlanStore:
    """Append and load future implementation plan records in JSON."""

    def load_plans(self, config: ImplementationPlanStoreConfig) -> list[dict]:
        """Load plans without crashing on missing or invalid files."""
        path = self._plans_path(config)
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

    def append_plan(
        self,
        plan: object | None,
        config: ImplementationPlanStoreConfig,
    ) -> ImplementationPlanStoreResult:
        """Append one plan record without implementing any change."""
        path = self._plans_path(config)
        reasons = [
            "Implementation plan stored for future human-reviewed work",
            "Store records plans only and does not change strategy rules",
        ]
        blocking_reasons: list[str] = []

        if plan is None:
            blocking_reasons.append("Implementation plan was not provided")

        try:
            plans = self.load_plans(config)
            plans.append(self._plan_dict(plan, blocking_reasons))
            path.write_text(json.dumps(plans, indent=2), encoding="utf-8")
            return ImplementationPlanStoreResult(
                saved=True,
                plans_path=str(path),
                total_plans=len(plans),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
        except (OSError, TypeError, ValueError) as exc:
            blocking_reasons.append(f"Could not save implementation plan: {exc}")
            return ImplementationPlanStoreResult(
                saved=False,
                plans_path=str(path),
                total_plans=0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

    def explain(self, result: ImplementationPlanStoreResult | None) -> str:
        """Return a beginner-readable explanation of the storage result."""
        if result is None:
            return (
                "Implementation plan store: saved=False, plans_path=None, "
                "total_plans=0, blocking_reasons=No store result was provided."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Implementation plan store: "
            f"saved={result.saved}, "
            f"plans_path={result.plans_path or 'None'}, "
            f"total_plans={result.total_plans}. "
            "Stored plans are for future human-reviewed work only; no strategy rule is changed. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _ensure_output_dir(self, config: ImplementationPlanStoreConfig) -> Path:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _plans_path(self, config: ImplementationPlanStoreConfig) -> Path:
        return self._ensure_output_dir(config) / config.plans_filename

    def _plan_dict(self, plan: object | None, extra_blocking_reasons: list[str]) -> dict[str, Any]:
        return {
            "plan_id": self._text(self._get(plan, "plan_id", None), "UNKNOWN"),
            "source_proposal_id": self._optional_text(self._get(plan, "source_proposal_id", None)),
            "title": self._text(self._get(plan, "title", None), "UNKNOWN"),
            "category": self._text(self._get(plan, "category", None), "UNKNOWN"),
            "priority": self._text(self._get(plan, "priority", None), "UNKNOWN"),
            "objective": self._text(self._get(plan, "objective", None), "UNKNOWN"),
            "proposed_steps": self._safe_list(self._get(plan, "proposed_steps", [])),
            "required_tests": self._safe_list(self._get(plan, "required_tests", [])),
            "risk_checks": self._safe_list(self._get(plan, "risk_checks", [])),
            "rollback_plan": self._text(self._get(plan, "rollback_plan", None), "UNKNOWN"),
            "status": self._text(self._get(plan, "status", None), "UNKNOWN"),
            "human_final_approval_required": True,
            "auto_implementation_allowed": False,
            "reasons": self._safe_list(self._get(plan, "reasons", [])),
            "blocking_reasons": self._dedupe(
                self._safe_list(self._get(plan, "blocking_reasons", []))
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
