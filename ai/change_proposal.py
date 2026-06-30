"""Safe change proposals from approved human approval decisions.

This module creates proposal records only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, or automatically change strategy rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


PROPOSED = "PROPOSED"
BLOCKED = "BLOCKED"
NEEDS_REVIEW = "NEEDS_REVIEW"
UNKNOWN = "UNKNOWN"

PROPOSAL_CREATED = "PROPOSAL_CREATED"
NO_APPROVED_DECISION = "NO_APPROVED_DECISION"


@dataclass
class ChangeProposalConfig:
    """Safety settings for creating future change proposals."""

    require_approved_decision: bool = True
    allow_auto_implementation: bool = False
    require_final_review: bool = True


@dataclass
class ChangeProposal:
    """A human-reviewed proposal for future strategy research work."""

    proposal_id: str
    source_request_id: str | None
    category: str
    priority: str
    title: str
    description: str
    reason: str
    risk: str
    proposed_change: str
    status: str
    human_review_required: bool
    auto_implementation_allowed: bool
    implementation_allowed: bool = False
    doc_path: str | None = None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class ChangeProposalResult:
    """Result of trying to create a change proposal."""

    proposal: ChangeProposal | None
    created: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ChangeProposalEngine:
    """Convert approved human approval records into safe proposals."""

    def create_from_approval_record(
        self,
        approval_record: dict | object | None,
        config: ChangeProposalConfig,
    ) -> ChangeProposalResult:
        """Create a proposal only from an approved decision record."""
        reasons = [
            "Change proposals are planning records only",
            "Final human review is required before implementation",
            "No strategy rules are changed automatically",
        ]
        blocking_reasons: list[str] = []

        if approval_record is None:
            blocking_reasons.append("Approval record was not provided")
            return ChangeProposalResult(
                proposal=None,
                created=False,
                status=UNKNOWN,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        approved = bool(self._get(approval_record, "approved", False))
        if bool(getattr(config, "require_approved_decision", True)) and not approved:
            reasons.append("Only approved human approval decisions can become change proposals")
            return ChangeProposalResult(
                proposal=None,
                created=False,
                status=NO_APPROVED_DECISION,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        source_request_id = self._optional_text(self._get(approval_record, "request_id", None))
        category = self._text(self._get(approval_record, "suggestion_category", None), UNKNOWN)
        priority = self._text(self._get(approval_record, "suggestion_priority", None), UNKNOWN)
        description = self._text(
            self._get(approval_record, "suggestion_text", None),
            "No suggestion text was available for this proposal.",
        )
        record_reasons = self._safe_list(self._get(approval_record, "reasons", []))
        record_blocking_reasons = self._safe_list(self._get(approval_record, "blocking_reasons", []))
        reason = self._first_text(record_reasons, "Approved human decision was recorded for future review.")
        risk = self._text(
            self._get(approval_record, "risk", None),
            "Risk must be reviewed again before any implementation.",
        )

        proposal = ChangeProposal(
            proposal_id=self._proposal_id(category),
            source_request_id=source_request_id,
            category=category,
            priority=priority,
            title=f"Review proposed {category} change",
            description=description,
            reason=reason,
            risk=risk,
            proposed_change=(
                "Prepare a human-reviewed change proposal from this approved research note. "
                "Do not implement code or strategy rules until final review is complete."
            ),
            status=PROPOSED,
            human_review_required=True,
            auto_implementation_allowed=False,
            reasons=self._dedupe(reasons + record_reasons),
            blocking_reasons=self._dedupe(record_blocking_reasons),
        )

        return ChangeProposalResult(
            proposal=proposal,
            created=True,
            status=PROPOSAL_CREATED,
            reasons=proposal.reasons,
            blocking_reasons=proposal.blocking_reasons,
        )

    def explain(self, result: ChangeProposalResult | None) -> str:
        """Return a beginner-readable explanation of the proposal result."""
        if result is None:
            return (
                "Change proposal status: UNKNOWN. "
                "No result was provided, so no proposal was created."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        if result.proposal is None:
            return (
                "Change proposal status: "
                f"{result.status}. "
                f"created={result.created}. "
                "No strategy rule was changed and no trade was created. "
                f"reasons={reasons}. "
                f"blocking_reasons={blocking}."
            )

        proposal = result.proposal
        return (
            "Change proposal status: "
            f"{result.status}. "
            f"proposal_id={proposal.proposal_id}, "
            f"source_request_id={proposal.source_request_id or 'None'}, "
            f"category={proposal.category}, "
            f"priority={proposal.priority}, "
            f"proposal_status={proposal.status}, "
            f"human_review_required={proposal.human_review_required}, "
            f"auto_implementation_allowed={proposal.auto_implementation_allowed}. "
            "This is a proposal only; no strategy rule was changed and final human review is required. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _proposal_id(self, category: str) -> str:
        safe_category = "".join(
            char.lower() if char.isalnum() else "-" for char in str(category or UNKNOWN)
        ).strip("-")
        safe_category = safe_category or "unknown"
        return f"proposal-{safe_category}-{uuid4().hex[:8]}"

    def _get(self, obj: dict | object, name: str, default: object = None) -> object:
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

    def _first_text(self, values: list[str], default: str) -> str:
        for value in values:
            if value:
                return value
        return default

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
