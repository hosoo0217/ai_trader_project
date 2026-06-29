"""Pipeline from strategy improvement suggestions to human approval requests.

This module is a safe connector only. It does not connect to live data,
brokers, Sierra Chart, CME, OpenAI, or any external API. It does not create
orders, generate trade signals, or automatically change strategy rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ai.human_approval import HumanApprovalConfig, HumanApprovalRequest, HumanApprovalWorkflow

if TYPE_CHECKING:
    from ai.strategy_improvement import StrategyImprovementResult, StrategyImprovementSuggestion


REQUESTS_CREATED = "REQUESTS_CREATED"
NO_SUGGESTIONS = "NO_SUGGESTIONS"
SKIPPED = "SKIPPED"
UNKNOWN = "UNKNOWN"


@dataclass
class StrategyApprovalPipelineConfig:
    """Settings for turning improvement suggestions into approval requests."""

    create_requests_for_all_suggestions: bool = True
    require_human_approval: bool = True
    allow_auto_apply: bool = False
    include_low_priority_suggestions: bool = True


@dataclass
class StrategyApprovalPipelineResult:
    """Result from creating pending approval requests."""

    created_requests: list[HumanApprovalRequest] = field(default_factory=list)
    skipped_suggestions: list = field(default_factory=list)
    total_suggestions: int = 0
    pending_requests: int = 0
    status: str = UNKNOWN
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class StrategyApprovalPipeline:
    """Create approval requests from safe strategy improvement suggestions."""

    def __init__(self, workflow: HumanApprovalWorkflow | None = None) -> None:
        self.workflow = workflow or HumanApprovalWorkflow()

    def create_requests(
        self,
        improvement_result: "StrategyImprovementResult | None",
        config: StrategyApprovalPipelineConfig,
    ) -> StrategyApprovalPipelineResult:
        """Create pending human approval requests without applying changes."""
        reasons = [
            "Strategy approval pipeline creates approval requests only",
            "Human approval is required before any future strategy change",
            "No strategy rules are changed automatically",
        ]
        blocking_reasons: list[str] = []

        if improvement_result is None:
            blocking_reasons.append("Strategy improvement result was not provided")
            return StrategyApprovalPipelineResult(
                status=UNKNOWN,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        suggestions = self._safe_suggestions(improvement_result)
        total_suggestions = len(suggestions)
        if total_suggestions == 0:
            return StrategyApprovalPipelineResult(
                created_requests=[],
                skipped_suggestions=[],
                total_suggestions=0,
                pending_requests=0,
                status=NO_SUGGESTIONS,
                reasons=reasons + ["No strategy improvement suggestions were available"],
                blocking_reasons=[],
            )

        if not bool(getattr(config, "create_requests_for_all_suggestions", True)):
            blocking_reasons.append("Approval request creation was disabled by pipeline config")
            return StrategyApprovalPipelineResult(
                created_requests=[],
                skipped_suggestions=suggestions,
                total_suggestions=total_suggestions,
                pending_requests=0,
                status=SKIPPED,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        approval_config = HumanApprovalConfig(
            require_human_approval=bool(getattr(config, "require_human_approval", True)),
            allow_auto_apply=False,
            approval_log_enabled=True,
        )

        created_requests: list[HumanApprovalRequest] = []
        skipped_suggestions: list[StrategyImprovementSuggestion] = []
        for suggestion in suggestions:
            priority = str(getattr(suggestion, "priority", UNKNOWN) or UNKNOWN).upper()
            if priority == "LOW" and not bool(getattr(config, "include_low_priority_suggestions", True)):
                skipped_suggestions.append(suggestion)
                blocking_reasons.append("Skipped LOW priority suggestion by pipeline config")
                continue

            request = self.workflow.create_request(suggestion, approval_config)
            created_requests.append(request)

        pending_requests = sum(1 for request in created_requests if request.status == "PENDING")
        if created_requests:
            status = REQUESTS_CREATED
        elif skipped_suggestions:
            status = SKIPPED
        else:
            status = UNKNOWN
            blocking_reasons.append("No approval requests could be created")

        return StrategyApprovalPipelineResult(
            created_requests=created_requests,
            skipped_suggestions=skipped_suggestions,
            total_suggestions=total_suggestions,
            pending_requests=pending_requests,
            status=status,
            reasons=self._dedupe(reasons),
            blocking_reasons=self._dedupe(blocking_reasons),
        )

    def explain(self, result: StrategyApprovalPipelineResult | None) -> str:
        """Return a beginner-readable explanation of the pipeline result."""
        if result is None:
            return (
                "Strategy approval pipeline status: UNKNOWN. "
                "No pipeline result was provided, so no approval requests were created."
            )

        reasons = "; ".join(result.reasons) if result.reasons else "None"
        blocking = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Strategy approval pipeline status: "
            f"{result.status}. "
            f"total_suggestions={result.total_suggestions}, "
            f"created_requests={len(result.created_requests)}, "
            f"pending_requests={result.pending_requests}, "
            f"skipped_suggestions={len(result.skipped_suggestions)}. "
            "Suggestions become PENDING human approval requests only; "
            "the pipeline does not apply strategy changes or create trades. "
            f"reasons={reasons}. "
            f"blocking_reasons={blocking}."
        )

    def _safe_suggestions(self, improvement_result: object) -> list:
        suggestions = getattr(improvement_result, "suggestions", [])
        if isinstance(suggestions, list):
            return suggestions
        if isinstance(suggestions, tuple):
            return list(suggestions)
        return []

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
