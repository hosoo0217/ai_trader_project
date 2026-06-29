"""Safe implementation plans from accepted proposal reviews.

This module creates planning records only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, write strategy changes, or automatically
implement anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


PLANNED = "PLANNED"
BLOCKED = "BLOCKED"
NEEDS_BACKTEST = "NEEDS_BACKTEST"
NEEDS_REVIEW = "NEEDS_REVIEW"
UNKNOWN = "UNKNOWN"

PLAN_CREATED = "PLAN_CREATED"
NO_ACCEPTED_REVIEW = "NO_ACCEPTED_REVIEW"


@dataclass
class ImplementationPlanConfig:
    """Safety settings for future implementation planning."""

    require_accepted_review: bool = True
    require_backtest_before_implementation: bool = True
    allow_auto_implementation: bool = False
    require_human_final_approval: bool = True


@dataclass
class ImplementationPlan:
    """A planning record for future human-reviewed implementation work."""

    plan_id: str
    source_proposal_id: str | None
    title: str
    category: str
    priority: str
    objective: str
    proposed_steps: list[str] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    risk_checks: list[str] = field(default_factory=list)
    rollback_plan: str = ""
    status: str = PLANNED
    human_final_approval_required: bool = True
    auto_implementation_allowed: bool = False
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class ImplementationPlanResult:
    """Result of trying to create an implementation plan."""

    plan: ImplementationPlan | None
    created: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ImplementationPlanWorkflow:
    """Create future implementation plans without implementing changes."""

    def create_from_review(
        self,
        proposal: object | None,
        review_record_or_result: object | None,
        config: ImplementationPlanConfig,
    ) -> ImplementationPlanResult:
        """Create a plan only from an accepted proposal review."""
        reasons = [
            "Implementation plans are planning records only",
            "Actual code or rule changes must be separate human-reviewed work",
            "Final human approval is required before implementation",
        ]
        blocking_reasons: list[str] = []

        if proposal is None:
            blocking_reasons.append("Change proposal was not provided")
            return ImplementationPlanResult(
                plan=None,
                created=False,
                status=UNKNOWN,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
        if review_record_or_result is None:
            blocking_reasons.append("Change proposal review was not provided")
            return ImplementationPlanResult(
                plan=None,
                created=False,
                status=UNKNOWN,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        review_decision = self._review_decision(review_record_or_result)
        review_status = self._review_status(review_record_or_result)
        accepted = self._accepted(review_record_or_result, review_decision, review_status)

        if review_decision == NEEDS_BACKTEST or review_status == NEEDS_BACKTEST:
            reasons.append("More backtesting is required before implementation planning")
            blocking_reasons.append("Review requires backtesting before this proposal can move forward")
            return ImplementationPlanResult(
                plan=None,
                created=False,
                status=NEEDS_BACKTEST,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        if bool(getattr(config, "require_accepted_review", True)) and not accepted:
            reasons.append("Only accepted proposal reviews can become implementation plans")
            return ImplementationPlanResult(
                plan=None,
                created=False,
                status=NO_ACCEPTED_REVIEW,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        source_proposal_id = self._optional_text(self._get(proposal, "proposal_id", None))
        category = self._text(self._get(proposal, "category", None), UNKNOWN)
        priority = self._text(self._get(proposal, "priority", None), UNKNOWN)
        title = self._text(self._get(proposal, "title", None), "Review accepted change proposal")
        objective = self._text(
            self._get(proposal, "description", None),
            "Plan future human-reviewed implementation work for this accepted proposal.",
        )

        plan = ImplementationPlan(
            plan_id=self._plan_id(category),
            source_proposal_id=source_proposal_id,
            title=f"Implementation plan for {title}",
            category=category,
            priority=priority,
            objective=objective,
            proposed_steps=[
                "Review current strategy logic",
                "Define exact rule change",
                "Add unit tests",
                "Run backtest",
                "Review risk impact",
                "Require final human approval before implementation",
            ],
            required_tests=[
                "unit tests",
                "regression tests",
                "backtest comparison",
                "safety gate tests",
            ],
            risk_checks=[
                "drawdown check",
                "capital protection check",
                "session/news/spread filter check",
                "no live trading confirmation",
            ],
            rollback_plan=(
                "Revert code change, restore previous config, rerun tests, "
                "and do not use in live trading until validated."
            ),
            status=PLANNED,
            human_final_approval_required=True,
            auto_implementation_allowed=False,
            reasons=self._dedupe(reasons + self._safe_list(self._get(review_record_or_result, "reasons", []))),
            blocking_reasons=self._dedupe(
                blocking_reasons + self._safe_list(self._get(review_record_or_result, "blocking_reasons", []))
            ),
        )
        return ImplementationPlanResult(
            plan=plan,
            created=True,
            status=PLAN_CREATED,
            reasons=plan.reasons,
            blocking_reasons=plan.blocking_reasons,
        )

    def explain(self, result: ImplementationPlanResult | None) -> str:
        """Return a beginner-readable explanation of the plan result."""
        if result is None:
            return (
                "Implementation plan status: UNKNOWN. "
                "No result was provided, so no plan was created."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        if result.plan is None:
            return (
                "Implementation plan status: "
                f"{result.status}. "
                f"created={result.created}. "
                "No strategy rule was changed and no trade signal was created. "
                f"reasons={reasons}. "
                f"blocking_reasons={blocking}."
            )

        plan = result.plan
        return (
            "Implementation plan status: "
            f"{result.status}. "
            f"plan_id={plan.plan_id}, "
            f"source_proposal_id={plan.source_proposal_id or 'None'}, "
            f"plan_status={plan.status}, "
            f"human_final_approval_required={plan.human_final_approval_required}, "
            f"auto_implementation_allowed={plan.auto_implementation_allowed}. "
            "This is planning only; no strategy rule was changed and no trade signal was created. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _review_decision(self, review: object) -> str:
        decision = self._get(review, "review_decision", None)
        if decision is None:
            decision_obj = self._get(review, "decision", None)
            decision = self._get(decision_obj, "decision", decision_obj)
        return str(decision or UNKNOWN).upper()

    def _review_status(self, review: object) -> str:
        status = self._get(review, "review_status", None)
        if status is None:
            status = self._get(review, "status", None)
        return str(status or UNKNOWN).upper()

    def _accepted(self, review: object, decision: str, status: str) -> bool:
        accepted = bool(self._get(review, "accepted", False))
        return accepted or decision == "ACCEPT" or status == "ACCEPTED_FOR_FUTURE_WORK"

    def _plan_id(self, category: str) -> str:
        safe_category = "".join(
            char.lower() if char.isalnum() else "-" for char in str(category or UNKNOWN)
        ).strip("-")
        safe_category = safe_category or "unknown"
        return f"plan-{safe_category}-{uuid4().hex[:8]}"

    def _get(self, obj: object | None, name: str, default: object = None) -> object:
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
        return [str(value)]

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
