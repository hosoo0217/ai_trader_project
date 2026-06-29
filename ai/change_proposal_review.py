"""Safe final review workflow for saved change proposals.

This module records review outcomes only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, or automatically implement strategy changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


ACCEPT = "ACCEPT"
REJECT = "REJECT"
NEEDS_MORE_DATA = "NEEDS_MORE_DATA"
NEEDS_BACKTEST = "NEEDS_BACKTEST"
UNKNOWN = "UNKNOWN"

ACCEPTED_FOR_FUTURE_WORK = "ACCEPTED_FOR_FUTURE_WORK"
REJECTED = "REJECTED"


@dataclass
class ChangeProposalReviewConfig:
    """Safety settings for reviewing a saved change proposal."""

    require_final_human_review: bool = True
    allow_auto_implementation: bool = False
    require_backtest_before_accept: bool = True


@dataclass
class ChangeProposalReviewDecision:
    """One review decision for a change proposal."""

    proposal_id: str | None
    decision: str
    reviewed_by: str | None
    reviewed_at: str | None
    notes: str | None
    accepted_for_future_work: bool
    implementation_allowed: bool
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class ChangeProposalReviewResult:
    """Result of reviewing a change proposal."""

    proposal_id: str | None
    decision: ChangeProposalReviewDecision | None
    status: str
    accepted: bool
    implementation_allowed: bool
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ChangeProposalReviewWorkflow:
    """Review saved proposals without implementing them."""

    def review(
        self,
        proposal: object | None,
        decision: str,
        config: ChangeProposalReviewConfig,
        reviewed_by: str | None = None,
        notes: str | None = None,
    ) -> ChangeProposalReviewResult:
        """Record a proposal review decision safely."""
        _ = config
        reasons = [
            "Change proposal review records review outcomes only",
            "Final implementation must remain separate and human-controlled",
        ]
        blocking_reasons: list[str] = []

        if proposal is None:
            blocking_reasons.append("Change proposal was not provided")
            review_decision = ChangeProposalReviewDecision(
                proposal_id=None,
                decision=self._normalize_decision(decision),
                reviewed_by=reviewed_by,
                reviewed_at=self._now(),
                notes=notes,
                accepted_for_future_work=False,
                implementation_allowed=False,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
            return ChangeProposalReviewResult(
                proposal_id=None,
                decision=review_decision,
                status=UNKNOWN,
                accepted=False,
                implementation_allowed=False,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        proposal_id = self._optional_text(self._get(proposal, "proposal_id", None))
        normalized = self._normalize_decision(decision)
        accepted = False
        status = UNKNOWN

        if normalized == ACCEPT:
            accepted = True
            status = ACCEPTED_FOR_FUTURE_WORK
            reasons.append("Proposal accepted for future reviewed work only")
            reasons.append("Acceptance does not allow automatic implementation")
        elif normalized == REJECT:
            status = REJECTED
            blocking_reasons.append("Reviewer rejected this change proposal")
        elif normalized == NEEDS_MORE_DATA:
            status = NEEDS_MORE_DATA
            blocking_reasons.append("More data is required before this proposal can move forward")
        elif normalized == NEEDS_BACKTEST:
            status = NEEDS_BACKTEST
            blocking_reasons.append("Backtesting is required before this proposal can move forward")
        else:
            normalized = UNKNOWN
            status = UNKNOWN
            blocking_reasons.append("Review decision value was unknown")

        review_decision = ChangeProposalReviewDecision(
            proposal_id=proposal_id,
            decision=normalized,
            reviewed_by=reviewed_by,
            reviewed_at=self._now(),
            notes=notes,
            accepted_for_future_work=accepted,
            implementation_allowed=False,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )
        return ChangeProposalReviewResult(
            proposal_id=proposal_id,
            decision=review_decision,
            status=status,
            accepted=accepted,
            implementation_allowed=False,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: ChangeProposalReviewResult | None) -> str:
        """Return a beginner-readable review explanation."""
        if result is None:
            return (
                "Change proposal review status: UNKNOWN. "
                "No review result was provided, so implementation is not allowed."
            )

        decision = result.decision.decision if result.decision is not None else UNKNOWN
        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Change proposal review status: "
            f"{result.status}. "
            f"proposal_id={result.proposal_id or 'None'}, "
            f"decision={decision}, "
            f"accepted={result.accepted}, "
            f"implementation_allowed={result.implementation_allowed}. "
            "Reviewing a proposal does not implement it; no strategy rule was changed. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _normalize_decision(self, decision: object) -> str:
        value = str(decision or UNKNOWN).strip().upper()
        if value in {ACCEPT, REJECT, NEEDS_MORE_DATA, NEEDS_BACKTEST}:
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
