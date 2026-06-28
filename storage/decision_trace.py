"""Structured decision trace for paper trading and backtesting.

This module records a readable audit trail of important decision steps.
It is research-only and does not connect to live systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class DecisionTraceStep:
    """One decision step in the trading flow audit trail."""

    step_name: str
    status: str
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class DecisionTrace:
    """Full audit trail for one decision flow."""

    trace_id: str
    symbol: str
    final_action: str
    final_allowed: bool
    steps: list[DecisionTraceStep] = field(default_factory=list)


class DecisionTracer:
    """Create and manage structured decision traces."""

    def create_trace(
        self,
        symbol: str,
        final_action: str = "NO_TRADE",
        final_allowed: bool = False,
    ) -> DecisionTrace:
        """Create an empty trace with a unique trace ID."""
        return DecisionTrace(
            trace_id=str(uuid4()),
            symbol=symbol,
            final_action=final_action,
            final_allowed=final_allowed,
            steps=[],
        )

    def add_step(
        self,
        trace: DecisionTrace,
        step_name: str,
        status: str,
        allowed: bool,
        reasons: list[str] | None = None,
        blocking_reasons: list[str] | None = None,
    ) -> None:
        """Append one step to the decision trace."""
        trace.steps.append(
            DecisionTraceStep(
                step_name=step_name,
                status=status,
                allowed=bool(allowed),
                reasons=list(reasons) if reasons is not None else [],
                blocking_reasons=list(blocking_reasons) if blocking_reasons is not None else [],
            )
        )

    def get_blocking_steps(self, trace: DecisionTrace) -> list[DecisionTraceStep]:
        """Return only steps that blocked trading."""
        return [step for step in trace.steps if not step.allowed]

    def explain_trace(self, trace: DecisionTrace) -> str:
        """Return a readable explanation of the full decision trace."""
        lines: list[str] = [
            f"Decision trace ID: {trace.trace_id}",
            f"Symbol: {trace.symbol}",
            f"Final action: {trace.final_action}",
            f"Final allowed: {trace.final_allowed}",
        ]

        if not trace.steps:
            lines.append("Steps: None")
            lines.append("Blocking reasons: None")
            return " | ".join(lines)

        step_parts: list[str] = []
        all_blocking_reasons: list[str] = []

        for index, step in enumerate(trace.steps, start=1):
            reasons_text = "; ".join(step.reasons) if step.reasons else "None"
            blocks_text = "; ".join(step.blocking_reasons) if step.blocking_reasons else "None"
            step_parts.append(
                f"{index}. {step.step_name} [{step.status}] allowed={step.allowed} reasons={reasons_text} blocking={blocks_text}"
            )
            all_blocking_reasons.extend(step.blocking_reasons)

        blocking_text = "; ".join(all_blocking_reasons) if all_blocking_reasons else "None"
        lines.append("Steps: " + " || ".join(step_parts))
        lines.append("Blocking reasons: " + blocking_text)

        return " | ".join(lines)
