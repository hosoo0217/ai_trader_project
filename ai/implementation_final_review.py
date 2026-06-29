"""Final human review for implementation plans.

This module records final review decisions only. It does not connect to live
data, brokers, Sierra Chart, CME, OpenAI, or any external API. It does not
create orders, generate trade signals, write code changes, or automatically
implement strategy rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


APPROVE_FOR_WORK = "APPROVE_FOR_WORK"
REJECT = "REJECT"
NEEDS_BACKTEST = "NEEDS_BACKTEST"
NEEDS_MORE_REVIEW = "NEEDS_MORE_REVIEW"
UNKNOWN = "UNKNOWN"

APPROVED_FOR_FUTURE_WORK = "APPROVED_FOR_FUTURE_WORK"
REJECTED = "REJECTED"


@dataclass
class ImplementationFinalReviewConfig:
    """Safety settings for final implementation plan review."""

    require_human_final_approval: bool = True
    require_backtest_evidence: bool = True
    allow_auto_implementation: bool = False


@dataclass
class ImplementationFinalReviewDecision:
    """One final review decision for an implementation plan."""

    plan_id: str | None
    decision: str
    reviewed_by: str | None
    reviewed_at: str | None
    notes: str | None
    approved_for_implementation_work: bool
    implementation_allowed_now: bool
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class ImplementationFinalReviewResult:
    """Result of final review for an implementation plan."""

    plan_id: str | None
    decision: ImplementationFinalReviewDecision | None
    status: str
    approved_for_work: bool
    implementation_allowed_now: bool
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ImplementationFinalReviewWorkflow:
    """Review implementation plans without implementing anything."""

    def review(
        self,
        plan: object | None,
        decision: str,
        config: ImplementationFinalReviewConfig,
        reviewed_by: str | None = None,
        notes: str | None = None,
    ) -> ImplementationFinalReviewResult:
        """Record a final human review decision safely."""
        _ = config
        reasons = [
            "Final implementation review records a human decision only",
            "Implementation must remain separate, reviewed, tested, and committed manually",
        ]
        blocking_reasons: list[str] = []
        normalized = self._normalize_decision(decision)

        if plan is None:
            blocking_reasons.append("Implementation plan was not provided")
            review_decision = ImplementationFinalReviewDecision(
                plan_id=None,
                decision=normalized,
                reviewed_by=reviewed_by,
                reviewed_at=self._now(),
                notes=notes,
                approved_for_implementation_work=False,
                implementation_allowed_now=False,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
            return ImplementationFinalReviewResult(
                plan_id=None,
                decision=review_decision,
                status=UNKNOWN,
                approved_for_work=False,
                implementation_allowed_now=False,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        plan_id = self._optional_text(self._get(plan, "plan_id", None))
        approved_for_work = False
        status = UNKNOWN

        if normalized == APPROVE_FOR_WORK:
            approved_for_work = True
            status = APPROVED_FOR_FUTURE_WORK
            reasons.append("Plan approved for future human-reviewed implementation work only")
            reasons.append("Approval does not allow immediate or automatic implementation")
        elif normalized == REJECT:
            status = REJECTED
            blocking_reasons.append("Reviewer rejected this implementation plan")
        elif normalized == NEEDS_BACKTEST:
            status = NEEDS_BACKTEST
            blocking_reasons.append("Backtest evidence is required before this plan can move forward")
        elif normalized == NEEDS_MORE_REVIEW:
            status = NEEDS_MORE_REVIEW
            blocking_reasons.append("More human review is required before this plan can move forward")
        else:
            normalized = UNKNOWN
            status = UNKNOWN
            blocking_reasons.append("Final review decision value was unknown")

        review_decision = ImplementationFinalReviewDecision(
            plan_id=plan_id,
            decision=normalized,
            reviewed_by=reviewed_by,
            reviewed_at=self._now(),
            notes=notes,
            approved_for_implementation_work=approved_for_work,
            implementation_allowed_now=False,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )
        return ImplementationFinalReviewResult(
            plan_id=plan_id,
            decision=review_decision,
            status=status,
            approved_for_work=approved_for_work,
            implementation_allowed_now=False,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: ImplementationFinalReviewResult | None) -> str:
        """Return a beginner-readable final review explanation."""
        if result is None:
            return (
                "Implementation final review status: UNKNOWN. "
                "No review result was provided, so implementation is not allowed now."
            )

        decision = result.decision.decision if result.decision is not None else UNKNOWN
        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Implementation final review status: "
            f"{result.status}. "
            f"plan_id={result.plan_id or 'None'}, "
            f"decision={decision}, "
            f"approved_for_work={result.approved_for_work}, "
            f"implementation_allowed_now={result.implementation_allowed_now}. "
            "Final review approves future human-reviewed work only; no strategy rule was changed "
            "and no trade signal was created. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _normalize_decision(self, decision: object) -> str:
        value = str(decision or UNKNOWN).strip().upper()
        if value in {APPROVE_FOR_WORK, REJECT, NEEDS_BACKTEST, NEEDS_MORE_REVIEW}:
            return value
        return UNKNOWN

    def _get(self, obj: object, name: str, default: object = None) -> object:
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def _optional_text(self, value: object) -> str | None:
        if value is None:
            return None
        return str(value)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
