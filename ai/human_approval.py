"""Human approval workflow for strategy improvement suggestions.

This module records review decisions only. It does not connect to brokers,
Sierra Chart, CME, OpenAI, or any external API. It does not create orders,
generate trade signals, or automatically change strategy rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from ai.strategy_improvement import StrategyImprovementSuggestion


PENDING = "PENDING"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
NEEDS_REVIEW = "NEEDS_REVIEW"
UNKNOWN = "UNKNOWN"

APPROVE = "APPROVE"
REJECT = "REJECT"


@dataclass
class HumanApprovalConfig:
    """Safety settings for human approval review."""

    require_human_approval: bool = True
    allow_auto_apply: bool = False
    approval_log_enabled: bool = True


@dataclass
class HumanApprovalRequest:
    """A strategy suggestion waiting for human review."""

    request_id: str
    suggestion_category: str
    suggestion_priority: str
    suggestion_text: str
    reason: str
    risk: str
    created_at: str | None
    status: str
    human_approval_required: bool


@dataclass
class HumanApprovalDecision:
    """A human decision about one approval request."""

    request_id: str
    decision: str
    decided_by: str | None
    decided_at: str | None
    notes: str | None
    allowed_to_apply: bool
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class HumanApprovalResult:
    """Combined request and decision outcome."""

    request: HumanApprovalRequest | None
    decision: HumanApprovalDecision | None
    approved: bool
    allowed_to_apply: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class HumanApprovalWorkflow:
    """Create and decide safe human approval requests."""

    def create_request(
        self,
        suggestion: StrategyImprovementSuggestion | None,
        config: HumanApprovalConfig,
    ) -> HumanApprovalRequest:
        """Convert a strategy suggestion into a pending review request."""
        _ = config
        category = self._get_text(suggestion, "category", UNKNOWN)
        priority = self._get_text(suggestion, "priority", UNKNOWN)
        suggestion_text = self._get_text(
            suggestion,
            "suggestion",
            "No strategy improvement suggestion was provided.",
        )
        reason = self._get_text(suggestion, "reason", "No suggestion reason was provided.")
        risk = self._get_text(suggestion, "risk", "No suggestion risk was provided.")

        return HumanApprovalRequest(
            request_id=self._request_id(category),
            suggestion_category=category,
            suggestion_priority=priority,
            suggestion_text=suggestion_text,
            reason=reason,
            risk=risk,
            created_at=self._now(),
            status=PENDING,
            human_approval_required=True,
        )

    def decide(
        self,
        request: HumanApprovalRequest | None,
        decision: str,
        config: HumanApprovalConfig,
        decided_by: str | None = None,
        notes: str | None = None,
    ) -> HumanApprovalResult:
        """Record a human decision without changing strategy behavior."""
        reasons = [
            "Human approval workflow records review decisions only",
            "approval does not automatically change strategy rules",
        ]
        blocking_reasons: list[str] = []

        if request is None:
            blocking_reasons.append("Approval request was not provided")
            approval_decision = HumanApprovalDecision(
                request_id=UNKNOWN,
                decision=self._normalize_decision(decision),
                decided_by=decided_by,
                decided_at=self._now(),
                notes=notes,
                allowed_to_apply=False,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )
            return HumanApprovalResult(
                request=None,
                decision=approval_decision,
                approved=False,
                allowed_to_apply=False,
                status=UNKNOWN,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        normalized = self._normalize_decision(decision)
        approved = False
        allowed_to_apply = False
        status = NEEDS_REVIEW

        if normalized == APPROVE:
            approved = True
            status = APPROVED
            require_human_approval = bool(getattr(config, "require_human_approval", True))
            allow_auto_apply = bool(getattr(config, "allow_auto_apply", False))
            if require_human_approval and not allow_auto_apply:
                allowed_to_apply = True
                reasons.append("A human approved this future reviewed change proposal")
            else:
                blocking_reasons.append("Approval config does not permit this request to be applied")
        elif normalized == REJECT:
            status = REJECTED
            blocking_reasons.append("Human rejected this strategy improvement suggestion")
        elif normalized == NEEDS_REVIEW:
            status = NEEDS_REVIEW
            blocking_reasons.append("Human marked this suggestion as needing more review")
        else:
            normalized = UNKNOWN
            status = UNKNOWN
            blocking_reasons.append("Decision value was unknown")

        approval_decision = HumanApprovalDecision(
            request_id=request.request_id,
            decision=normalized,
            decided_by=decided_by,
            decided_at=self._now(),
            notes=notes,
            allowed_to_apply=allowed_to_apply,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

        request.status = status
        return HumanApprovalResult(
            request=request,
            decision=approval_decision,
            approved=approved,
            allowed_to_apply=allowed_to_apply,
            status=status,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: HumanApprovalResult | None) -> str:
        """Return a beginner-readable approval summary."""
        if result is None:
            return (
                "Human approval status: UNKNOWN. "
                "No approval result was provided, so no strategy change is allowed."
            )

        request_id = result.request.request_id if result.request else UNKNOWN
        decision = result.decision.decision if result.decision else UNKNOWN
        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Human approval status: "
            f"{result.status}. "
            f"request_id={request_id}, "
            f"decision={decision}, "
            f"approved={result.approved}, "
            f"allowed_to_apply={result.allowed_to_apply}. "
            "Approval is permission for a future reviewed strategy change proposal only; "
            "this workflow does not automatically change rules or create trades. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _request_id(self, category: str) -> str:
        """Create a readable identifier from safe text and a short UUID."""
        safe_category = "".join(
            char.lower() if char.isalnum() else "-" for char in str(category or UNKNOWN)
        ).strip("-")
        safe_category = safe_category or "unknown"
        return f"approval-{safe_category}-{uuid4().hex[:8]}"

    def _normalize_decision(self, decision: object) -> str:
        value = str(decision or UNKNOWN).strip().upper()
        if value in {APPROVE, REJECT, NEEDS_REVIEW}:
            return value
        return UNKNOWN

    def _get_text(self, obj: object, name: str, default: str) -> str:
        if obj is None:
            return default
        value = getattr(obj, name, default)
        if value is None:
            return default
        return str(value)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
