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

        alignment_allowed = bool(getattr(context, "alignment_allowed", True))
        alignment_status = getattr(context, "alignment_status", None)
        aligned_bias = str(getattr(context, "aligned_bias", "") or "").upper() or None
        alignment_adjustment = float(getattr(context, "alignment_confidence_adjustment", 0.0) or 0.0)
        alignment_reasons = list(getattr(context, "alignment_reasons", []))
        alignment_blocking_reasons = list(getattr(context, "alignment_blocking_reasons", []))

        if not alignment_allowed:
            return DecisionResult(
                action="NO_TRADE",
                allowed=False,
                confidence=self._clamp_confidence(confidence),
                reasons=[*reasons, "Context alignment gate blocked trading"],
                blocking_reasons=[
                    *blocking_reasons,
                    f"Context alignment status: {alignment_status or 'UNKNOWN'}",
                    *[f"ALIGNMENT: {item}" for item in alignment_blocking_reasons],
                ],
            )

        if direction == "NO_TRADE" and aligned_bias == "BULLISH":
            direction = "BUY"
            reasons.append("Alignment bias supports BUY context")
        elif direction == "NO_TRADE" and aligned_bias == "BEARISH":
            direction = "SELL"
            reasons.append("Alignment bias supports SELL context")

        if alignment_adjustment != 0.0:
            confidence = self._clamp_confidence(confidence + alignment_adjustment)
            reasons.append(f"Alignment confidence adjustment applied: {alignment_adjustment:+.1f}")

        if alignment_reasons:
            reasons.extend([f"ALIGNMENT: {item}" for item in alignment_reasons])

        smc_context = getattr(context, "smc", None)
        smc_bias = str(getattr(smc_context, "smc_bias", "UNKNOWN") or "UNKNOWN").upper()
        smc_confidence = float(getattr(smc_context, "smc_confidence", 0.0) or 0.0)
        smc_reasons = list(getattr(smc_context, "smc_reasons", []))
        smc_blocking_reasons = list(getattr(smc_context, "smc_blocking_reasons", []))
        crt_context = getattr(context, "crt", None)
        crt_bias = str(getattr(crt_context, "crt_bias", "UNKNOWN") or "UNKNOWN").upper()
        crt_signal_type = getattr(crt_context, "crt_signal_type", None)
        crt_reasons = list(getattr(crt_context, "crt_reasons", []))
        crt_blocking_reasons = list(getattr(crt_context, "crt_blocking_reasons", []))

        if smc_bias == "UNKNOWN":
            reasons.append("SMC context is UNKNOWN")
        elif smc_bias == "NEUTRAL":
            reasons.append("SMC context is NEUTRAL")

        if direction == "BUY" and smc_bias == "BULLISH":
            confidence = self._clamp_confidence(confidence + 5.0)
            reasons.append("SMC bias supports BUY direction")
        elif direction == "SELL" and smc_bias == "BEARISH":
            confidence = self._clamp_confidence(confidence + 5.0)
            reasons.append("SMC bias supports SELL direction")
        elif direction in {"BUY", "SELL"} and smc_bias in {"BULLISH", "BEARISH"}:
            smc_conflict = (direction == "BUY" and smc_bias == "BEARISH") or (direction == "SELL" and smc_bias == "BULLISH")
            if smc_conflict and smc_confidence >= 60.0:
                return DecisionResult(
                    action="NO_TRADE",
                    allowed=False,
                    confidence=self._clamp_confidence(confidence),
                    reasons=[*reasons, "SMC conflict blocked trade"],
                    blocking_reasons=[
                        *blocking_reasons,
                        "Strong SMC conflict with final direction",
                        *[f"SMC: {item}" for item in smc_blocking_reasons],
                    ],
                )
            if smc_conflict:
                confidence = self._clamp_confidence(confidence - 10.0)
                reasons.append("SMC conflict reduced confidence")

        if smc_reasons:
            reasons.extend([f"SMC: {item}" for item in smc_reasons])

        if crt_bias == "UNKNOWN":
            reasons.append("CRT context is UNKNOWN")
        elif crt_bias == "NEUTRAL":
            reasons.append("CRT context is NEUTRAL")

        if direction == "BUY" and crt_bias == "BULLISH":
            confidence = self._clamp_confidence(confidence + 5.0)
            reasons.append("CRT bias supports BUY direction")
        elif direction == "SELL" and crt_bias == "BEARISH":
            confidence = self._clamp_confidence(confidence + 5.0)
            reasons.append("CRT bias supports SELL direction")
        elif direction in {"BUY", "SELL"} and crt_bias in {"BULLISH", "BEARISH"}:
            crt_conflict = (direction == "BUY" and crt_bias == "BEARISH") or (direction == "SELL" and crt_bias == "BULLISH")
            strong_crt_conflict = bool(crt_blocking_reasons) and crt_signal_type in {"HIGH_MANIPULATION", "LOW_MANIPULATION"}
            if crt_conflict and strong_crt_conflict:
                return DecisionResult(
                    action="NO_TRADE",
                    allowed=False,
                    confidence=self._clamp_confidence(confidence),
                    reasons=[*reasons, "CRT conflict blocked trade"],
                    blocking_reasons=[
                        *blocking_reasons,
                        f"Strong CRT conflict with final direction ({crt_signal_type or 'NO_SIGNAL'})",
                        *[f"CRT: {item}" for item in crt_blocking_reasons],
                    ],
                )
            if crt_conflict:
                confidence = self._clamp_confidence(confidence - 5.0)
                reasons.append("CRT conflict reduced confidence")

        if crt_reasons:
            reasons.extend([f"CRT: {item}" for item in crt_reasons])

        if direction == "BUY":
            return DecisionResult(
                action="BUY",
                allowed=True,
                confidence=self._clamp_confidence(confidence),
                reasons=["Safety checks passed and bullish bias detected", *reasons],
                blocking_reasons=[],
            )

        if direction == "SELL":
            return DecisionResult(
                action="SELL",
                allowed=True,
                confidence=self._clamp_confidence(confidence),
                reasons=["Safety checks passed and bearish bias detected", *reasons],
                blocking_reasons=[],
            )

        return DecisionResult(
            action="NO_TRADE",
            allowed=False,
            confidence=self._clamp_confidence(confidence),
            reasons=[*reasons, "No clear direction detected"],
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
