"""Core decision-making orchestration.

This module combines the output from the decision context and capital
protection layers into a final research-only decision. It does not execute
orders or interact with a broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from core.capital_protection import CapitalProtectionDecision
from core.decision_context import DecisionContext
from core.multi_timeframe import MultiTimeframeDecision


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

    def evaluate(
        self,
        context: DecisionContext,
        capital_decision: CapitalProtectionDecision,
        multi_timeframe_decision: Optional[MultiTimeframeDecision] = None,
    ) -> DecisionResult:
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

        # Multi-timeframe evidence is optional but important for direction.
        if multi_timeframe_decision is not None:
            if not multi_timeframe_decision.allowed:
                blocking_reasons.extend(multi_timeframe_decision.blocking_reasons or ["Multi-timeframe decision blocked trading"])
                reasons.append("Multi-timeframe decision blocked trading")
            elif multi_timeframe_decision.bias == "WAIT":
                blocking_reasons.append("Multi-timeframe bias is WAIT")
                reasons.append("Multi-timeframe bias is WAIT")
            elif multi_timeframe_decision.bias == "NO_TRADE":
                blocking_reasons.append("Multi-timeframe bias is NO_TRADE")
                reasons.append("Multi-timeframe bias is NO_TRADE")

        # Confidence is expressed in a beginner-friendly 0-100 scale.
        confidence = self._normalize_confidence(context)
        if multi_timeframe_decision is not None:
            confidence = self._merge_confidence(confidence, multi_timeframe_decision.confidence)
        if confidence < 70.0:
            blocking_reasons.append("Confidence below threshold")
            reasons.append("Confidence below threshold")

        # Only allow a trade when all safety checks pass.
        if blocking_reasons:
            return DecisionResult(
                action="NO_TRADE",
                allowed=False,
                confidence=self._clamp_confidence(confidence),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        direction = self._get_direction(context)
        if multi_timeframe_decision is not None:
            if multi_timeframe_decision.bias == "BUY_BIAS":
                direction = "BUY"
            elif multi_timeframe_decision.bias == "SELL_BIAS":
                direction = "SELL"
            else:
                direction = "NO_TRADE"

        if direction == "BUY":
            return DecisionResult(
                action="BUY",
                allowed=True,
                confidence=self._clamp_confidence(confidence),
                reasons=["Safety checks passed and bullish bias detected"],
                blocking_reasons=[],
            )

        if direction == "SELL":
            return DecisionResult(
                action="SELL",
                allowed=True,
                confidence=self._clamp_confidence(confidence),
                reasons=["Safety checks passed and bearish bias detected"],
                blocking_reasons=[],
            )

        return DecisionResult(
            action="NO_TRADE",
            allowed=False,
            confidence=self._clamp_confidence(confidence),
            reasons=["No clear direction detected"],
            blocking_reasons=["No clear direction detected"],
        )

    def explain(self, result: DecisionResult) -> str:
        """Return a readable summary of the final decision."""
        lines = [f"Final action: {result.action}"]
        lines.append(f"Trade allowed: {result.allowed}")
        lines.append(f"Confidence: {result.confidence:.1f}")
        if result.reasons:
            lines.append("Reasons: " + "; ".join(result.reasons))
        if result.blocking_reasons:
            lines.append("Blocking reasons: " + "; ".join(result.blocking_reasons))
        return " | ".join(lines)

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

    def _merge_confidence(self, context_confidence: float, multi_timeframe_confidence: float) -> float:
        """Blend context confidence with multi-timeframe confidence."""
        return self._clamp_confidence((context_confidence + multi_timeframe_confidence) / 2.0)

    def _clamp_confidence(self, value: float) -> float:
        """Keep confidence inside a safe 0-100 range."""
        return max(0.0, min(100.0, value))

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
