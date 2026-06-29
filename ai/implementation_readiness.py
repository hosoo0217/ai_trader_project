"""Readiness checklist for future implementation work.

This module checks whether an implementation plan appears ready for future
human-reviewed coding work. It does not connect to live data, brokers, Sierra
Chart, CME, OpenAI, or any external API. It does not create orders, generate
trade signals, write code changes, or automatically implement strategy rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


READY_FOR_HUMAN_WORK = "READY_FOR_HUMAN_WORK"
NOT_READY = "NOT_READY"
NEEDS_BACKTEST = "NEEDS_BACKTEST"
NEEDS_TESTS = "NEEDS_TESTS"
NEEDS_RISK_REVIEW = "NEEDS_RISK_REVIEW"
UNKNOWN = "UNKNOWN"


@dataclass
class ImplementationReadinessConfig:
    """Safety settings for implementation readiness checks."""

    require_final_review_approval: bool = True
    require_backtest_evidence: bool = True
    require_tests_defined: bool = True
    require_risk_checks: bool = True
    allow_live_trading_changes: bool = False


@dataclass
class ImplementationReadinessChecklist:
    """Checklist result for future human-reviewed implementation work."""

    plan_id: str | None
    ready: bool
    status: str
    checklist_items: dict[str, bool] = field(default_factory=dict)
    missing_items: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ImplementationReadinessChecker:
    """Check readiness without implementing anything."""

    def check(
        self,
        plan: object | None,
        final_review_record_or_result: object | None,
        config: ImplementationReadinessConfig,
    ) -> ImplementationReadinessChecklist:
        """Build a conservative readiness checklist."""
        reasons = [
            "Readiness checklist is for future human-reviewed work only",
            "Readiness does not implement strategy rules or code changes",
        ]
        warnings = [
            "READY_FOR_HUMAN_WORK is not permission for automatic implementation",
        ]
        blocking_reasons: list[str] = []
        missing_items: list[str] = []

        if plan is None:
            blocking_reasons.append("Implementation plan was not provided")
            return ImplementationReadinessChecklist(
                plan_id=None,
                ready=False,
                status=UNKNOWN,
                checklist_items=self._base_items(),
                missing_items=["plan"],
                warnings=warnings,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        plan_id = self._optional_text(self._get(plan, "plan_id", None))
        checklist_items = self._base_items()

        final_review_approved = self._final_review_approved(final_review_record_or_result)
        checklist_items["final_review_approved"] = final_review_approved
        if bool(getattr(config, "require_final_review_approval", True)) and not final_review_approved:
            missing_items.append("final_review_approved")
            blocking_reasons.append("Final review approval was not found")

        backtest_evidence = self._has_backtest_evidence(plan, final_review_record_or_result)
        checklist_items["backtest_evidence_required"] = backtest_evidence
        if bool(getattr(config, "require_backtest_evidence", True)) and not backtest_evidence:
            missing_items.append("backtest_evidence_required")
            blocking_reasons.append("Backtest evidence is required before readiness")

        tests_defined = bool(self._safe_list(self._get(plan, "required_tests", [])))
        checklist_items["required_tests_defined"] = tests_defined
        if bool(getattr(config, "require_tests_defined", True)) and not tests_defined:
            missing_items.append("required_tests_defined")
            blocking_reasons.append("Required tests are not defined")

        risk_checks_defined = bool(self._safe_list(self._get(plan, "risk_checks", [])))
        checklist_items["risk_checks_defined"] = risk_checks_defined
        if bool(getattr(config, "require_risk_checks", True)) and not risk_checks_defined:
            missing_items.append("risk_checks_defined")
            blocking_reasons.append("Risk checks are not defined")

        rollback_defined = bool(str(self._get(plan, "rollback_plan", "") or "").strip())
        checklist_items["rollback_plan_defined"] = rollback_defined
        if not rollback_defined:
            missing_items.append("rollback_plan_defined")
            blocking_reasons.append("Rollback plan is not defined")

        no_auto = not bool(self._get(plan, "auto_implementation_allowed", False))
        checklist_items["no_auto_implementation"] = no_auto
        if not no_auto:
            missing_items.append("no_auto_implementation")
            blocking_reasons.append("Automatic implementation must remain disabled")

        no_live_change = not bool(getattr(config, "allow_live_trading_changes", False))
        checklist_items["no_live_trading_change"] = no_live_change
        if not no_live_change:
            missing_items.append("no_live_trading_change")
            blocking_reasons.append("Live trading changes are not allowed by readiness checks")

        human_final_work = bool(self._get(plan, "human_final_approval_required", True))
        checklist_items["human_final_work_required"] = human_final_work
        if not human_final_work:
            missing_items.append("human_final_work_required")
            blocking_reasons.append("Human final work requirement must remain enabled")

        status = self._status_for_missing(missing_items)
        ready = status == READY_FOR_HUMAN_WORK
        return ImplementationReadinessChecklist(
            plan_id=plan_id,
            ready=ready,
            status=status,
            checklist_items=checklist_items,
            missing_items=self._dedupe(missing_items),
            warnings=warnings,
            reasons=reasons,
            blocking_reasons=self._dedupe(blocking_reasons),
        )

    def explain(self, checklist: ImplementationReadinessChecklist | None) -> str:
        """Return a beginner-readable readiness explanation."""
        if checklist is None:
            return (
                "Implementation readiness status: UNKNOWN. "
                "No checklist was provided, so readiness is false."
            )

        missing = "; ".join(checklist.missing_items) if checklist.missing_items else "None"
        blocking = "; ".join(checklist.blocking_reasons) if checklist.blocking_reasons else "None"
        return (
            "Implementation readiness status: "
            f"{checklist.status}. "
            f"plan_id={checklist.plan_id or 'None'}, "
            f"ready={checklist.ready}. "
            "Readiness is for future human-reviewed coding work only; no strategy rule was changed "
            "and no trade signal was created. "
            f"missing_items={missing}. "
            f"blocking_reasons={blocking}."
        )

    def _base_items(self) -> dict[str, bool]:
        return {
            "final_review_approved": False,
            "backtest_evidence_required": False,
            "required_tests_defined": False,
            "risk_checks_defined": False,
            "rollback_plan_defined": False,
            "no_auto_implementation": False,
            "no_live_trading_change": False,
            "human_final_work_required": False,
        }

    def _final_review_approved(self, review: object | None) -> bool:
        if review is None:
            return False

        decision_obj = self._get(review, "decision", None)
        decision = self._get(decision_obj, "decision", decision_obj)
        saved_decision = self._get(review, "final_review_decision", None)
        status = self._get(review, "status", None) or self._get(review, "final_review_status", None)
        approved = bool(
            self._get(review, "approved_for_work", False)
            or self._get(decision_obj, "approved_for_implementation_work", False)
        )
        return (
            approved
            or str(decision or saved_decision or "").upper() == "APPROVE_FOR_WORK"
            or str(status or "").upper() == "APPROVED_FOR_FUTURE_WORK"
        )

    def _has_backtest_evidence(self, plan: object, review: object | None) -> bool:
        explicit = (
            self._get(plan, "backtest_evidence", None)
            or self._get(plan, "backtest_evidence_present", None)
            or self._get(review, "backtest_evidence", None)
            or self._get(review, "backtest_evidence_present", None)
        )
        if bool(explicit):
            return True

        searchable = " ".join(
            self._safe_list(self._get(plan, "reasons", []))
            + self._safe_list(self._get(review, "reasons", []))
            + self._safe_list(self._get(review, "notes", []))
        ).lower()
        return "backtest evidence" in searchable or "backtest verified" in searchable

    def _status_for_missing(self, missing_items: list[str]) -> str:
        if not missing_items:
            return READY_FOR_HUMAN_WORK
        if "final_review_approved" in missing_items:
            return NOT_READY
        if "backtest_evidence_required" in missing_items:
            return NEEDS_BACKTEST
        if "required_tests_defined" in missing_items:
            return NEEDS_TESTS
        if "risk_checks_defined" in missing_items:
            return NEEDS_RISK_REVIEW
        return NOT_READY

    def _get(self, obj: object | None, name: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

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
        return [str(value)]

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
