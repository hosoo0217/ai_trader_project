"""Core decision-making orchestration.

This module combines the output from the decision context and capital
protection layers into a final research-only decision. It does not execute
orders or interact with a broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from core.capital_protection import CapitalProtectionDecision
from core.decision_context import DecisionContext


@dataclass
class DecisionResult:
    """Simple outcome returned by the decision engine."""

    action: str = "NO_TRADE"
    allowed: bool = False
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)


class DecisionEngine:
    """Combine safety checks and directional context into one decision."""

    def evaluate(self, context: DecisionContext, capital_decision: CapitalProtectionDecision) -> DecisionResult:
        """Return a safe action for a given context and protection decision."""
        blocking_reasons: List[str] = []
        reasons: List[str] = []

        # Capital protection has highest authority.
        if capital_decision is not None and not capital_decision.allowed:
            blocking_reasons.extend(capital_decision.reasons or ["Capital protection blocked trading"])
            reasons.append("Capital protection blocked trading")

        # DecisionContext provides the validation helper we should reuse.
        if context is not None and not context.is_trade_allowed():
            context_reasons = context.explain_blocking_reasons()
            blocking_reasons.extend([f"DecisionContext: {reason}" for reason in context_reasons])
            reasons.append("DecisionContext blocked trading")

        # Confidence is expressed in a beginner-friendly 0-100 scale.
        confidence = self._normalize_confidence(context)
        if confidence < 70.0:
            blocking_reasons.append("Confidence below threshold")
            reasons.append("Confidence below threshold")

        # Only allow a trade when all safety checks pass.
        if blocking_reasons:
            return DecisionResult(
                action="NO_TRADE",
                allowed=False,
                confidence=confidence,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        direction = self._get_direction(context)
        if direction == "BUY":
            return DecisionResult(
                action="BUY",
                allowed=True,
                confidence=confidence,
                reasons=["Safety checks passed and bullish bias detected"],
                blocking_reasons=[],
            )

        if direction == "SELL":
            return DecisionResult(
                action="SELL",
                allowed=True,
                confidence=confidence,
                reasons=["Safety checks passed and bearish bias detected"],
                blocking_reasons=[],
            )

        return DecisionResult(
            action="NO_TRADE",
            allowed=False,
            confidence=confidence,
            reasons=["No clear direction detected"],
            blocking_reasons=["No clear direction detected"],
        )

    def explain(self, result: DecisionResult) -> str:
        """Return a simple human-readable summary of a decision result."""
        if result.allowed:
            return f"{result.action} with confidence {result.confidence:.1f}."

        if result.blocking_reasons:
            return f"{result.action} because: " + "; ".join(result.blocking_reasons)

        return f"{result.action} for unknown reasons."

    def _normalize_confidence(self, context: DecisionContext | None) -> float:
        """Convert the context confidence to a 0-100 scale if needed."""
        if context is None:
            return 0.0

        raw_confidence = getattr(getattr(context, "crt", None), "confidence", 0.0)
        if raw_confidence is None:
            return 0.0

        if raw_confidence <= 1.0:
            return float(raw_confidence * 100.0)

        return float(raw_confidence)

    def _get_direction(self, context: DecisionContext | None) -> str:
        """Infer a simple directional bias from the context."""
        if context is None:
            return "NO_TRADE"

        bias = getattr(getattr(context, "smc", None), "bias", 0)
        if bias > 0:
            return "BUY"
        if bias < 0:
            return "SELL"

        trend = getattr(getattr(context, "market", None), "trend", 0)
        if trend > 0:
            return "BUY"
        if trend < 0:
            return "SELL"

        return "NO_TRADE"
