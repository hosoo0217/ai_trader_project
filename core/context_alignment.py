"""SMC + CRT context alignment gate for research and backtesting.

This module validates whether SMC and CRT context agree before supporting
higher-level decision logic. It does not create trade signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextAlignmentConfig:
    """Configuration for context alignment checks."""

    enabled: bool = True
    require_smc_crt_alignment: bool = True
    allow_neutral_crt: bool = True
    allow_unknown_crt: bool = False
    minimum_smc_confidence: float = 50.0
    require_orderflow_alignment: bool = False
    minimum_confidence: float = 50.0


@dataclass
class ContextAlignmentResult:
    """Result of SMC/CRT alignment validation."""

    allowed: bool
    status: str
    aligned_bias: str | None
    confidence_adjustment: float
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    aligned: bool = False
    final_bias: str = "UNKNOWN"
    confidence: float = 0.0
    smc_bias: str | None = None
    crt_bias: str | None = None
    orderflow_bias: str | None = None


class ContextAlignmentGate:
    """Validate alignment between SMC context and CRT context."""

    def evaluate(
        self,
        smc_result: Any,
        crt_result: Any,
        config: ContextAlignmentConfig,
        orderflow_result: Any = None,
    ) -> ContextAlignmentResult:
        """Evaluate SMC/CRT alignment with safe fallback behavior."""
        orderflow_bias = self._read_bias(orderflow_result, "UNKNOWN")

        if not config.enabled or not config.require_smc_crt_alignment:
            return ContextAlignmentResult(
                allowed=True,
                status="FILTER_DISABLED",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["Context alignment gate disabled"],
                blocking_reasons=[],
                aligned=False,
                final_bias="UNKNOWN",
                confidence=0.0,
                smc_bias=self._read_bias(smc_result, "UNKNOWN"),
                crt_bias=self._read_bias(crt_result, "UNKNOWN"),
                orderflow_bias=orderflow_bias,
            )

        smc_bias = self._read_bias(smc_result, "UNKNOWN")
        smc_confidence = self._read_confidence(smc_result)

        if smc_result is None:
            return ContextAlignmentResult(
                allowed=False,
                status="UNKNOWN_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["SMC context is missing"],
                blocking_reasons=["SMC context is missing"],
                aligned=False,
                final_bias="UNKNOWN",
                confidence=0.0,
                smc_bias=None,
                crt_bias=self._read_bias(crt_result, "UNKNOWN"),
                orderflow_bias=orderflow_bias,
            )

        if smc_bias == "UNKNOWN":
            return ContextAlignmentResult(
                allowed=False,
                status="UNKNOWN_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["SMC context is UNKNOWN"],
                blocking_reasons=["SMC context is UNKNOWN"],
                aligned=False,
                final_bias="UNKNOWN",
                confidence=0.0,
                smc_bias=smc_bias,
                crt_bias=self._read_bias(crt_result, "UNKNOWN"),
                orderflow_bias=orderflow_bias,
            )

        min_smc_confidence = max(0.0, min(100.0, float(config.minimum_smc_confidence)))
        if smc_confidence < min_smc_confidence:
            return ContextAlignmentResult(
                allowed=False,
                status="UNKNOWN_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=[f"SMC confidence {smc_confidence:.1f} below minimum {min_smc_confidence:.1f}"],
                blocking_reasons=["SMC confidence below minimum threshold"],
                aligned=False,
                final_bias="UNKNOWN",
                confidence=0.0,
                smc_bias=smc_bias,
                crt_bias=self._read_bias(crt_result, "UNKNOWN"),
                orderflow_bias=orderflow_bias,
            )

        if smc_bias == "NEUTRAL":
            return ContextAlignmentResult(
                allowed=False,
                status="NEUTRAL_WAIT",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["SMC bias is NEUTRAL"],
                blocking_reasons=["SMC bias is NEUTRAL"],
                aligned=False,
                final_bias="UNKNOWN",
                confidence=0.0,
                smc_bias=smc_bias,
                crt_bias=self._read_bias(crt_result, "UNKNOWN"),
                orderflow_bias=orderflow_bias,
            )

        crt_bias = self._read_bias(crt_result, "UNKNOWN")

        if crt_result is None or crt_bias == "UNKNOWN":
            if config.allow_unknown_crt:
                return ContextAlignmentResult(
                    allowed=True,
                    status="NEUTRAL_WAIT",
                    aligned_bias=None,
                    confidence_adjustment=-5.0,
                    reasons=["CRT context is UNKNOWN but allowed by configuration"],
                    blocking_reasons=[],
                    aligned=False,
                    final_bias="NEUTRAL",
                    confidence=40.0,
                    smc_bias=smc_bias,
                    crt_bias=crt_bias,
                    orderflow_bias=orderflow_bias,
                )
            return ContextAlignmentResult(
                allowed=False,
                status="UNKNOWN_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=-5.0,
                reasons=["CRT context is UNKNOWN"],
                blocking_reasons=["CRT context is UNKNOWN and not allowed"],
                aligned=False,
                final_bias="UNKNOWN",
                confidence=0.0,
                smc_bias=smc_bias,
                crt_bias=crt_bias,
                orderflow_bias=orderflow_bias,
            )

        if crt_bias == "NEUTRAL":
            if config.allow_neutral_crt:
                return ContextAlignmentResult(
                    allowed=True,
                    status="NEUTRAL_WAIT",
                    aligned_bias=None,
                    confidence_adjustment=0.0,
                    reasons=["CRT context is NEUTRAL and allowed by configuration"],
                    blocking_reasons=[],
                    aligned=False,
                    final_bias="NEUTRAL",
                    confidence=40.0,
                    smc_bias=smc_bias,
                    crt_bias=crt_bias,
                    orderflow_bias=orderflow_bias,
                )
            return ContextAlignmentResult(
                allowed=False,
                status="NEUTRAL_WAIT",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["CRT context is NEUTRAL"],
                blocking_reasons=["CRT neutral context is not allowed"],
                aligned=False,
                final_bias="NEUTRAL",
                confidence=0.0,
                smc_bias=smc_bias,
                crt_bias=crt_bias,
                orderflow_bias=orderflow_bias,
            )

        if smc_bias == "BULLISH" and crt_bias == "BULLISH":
            return self._build_directional_result("BULLISH", smc_bias, crt_bias, orderflow_bias, config)

        if smc_bias == "BEARISH" and crt_bias == "BEARISH":
            return self._build_directional_result("BEARISH", smc_bias, crt_bias, orderflow_bias, config)

        return ContextAlignmentResult(
            allowed=False,
            status="CONFLICT_BLOCKED",
            aligned_bias=None,
            confidence_adjustment=-30.0,
            reasons=["SMC and CRT contexts conflict"],
            blocking_reasons=[f"SMC bias {smc_bias} conflicts with CRT bias {crt_bias}"],
            aligned=False,
            final_bias="NEUTRAL",
            confidence=0.0,
            smc_bias=smc_bias,
            crt_bias=crt_bias,
            orderflow_bias=orderflow_bias,
        )

    def explain(self, result: ContextAlignmentResult) -> str:
        """Return a readable summary of alignment gate output."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            f"Context alignment: {result.status} | allowed: {result.allowed} | "
            f"SMC bias: {result.smc_bias or 'None'} | "
            f"CRT bias: {result.crt_bias or 'None'} | "
            f"Order Flow bias: {result.orderflow_bias or 'None'} | "
            f"final bias: {result.final_bias} | "
            f"confidence: {result.confidence:.1f} | "
            f"aligned bias: {result.aligned_bias or 'None'} | "
            f"confidence adjustment: {result.confidence_adjustment:.1f} | "
            f"reasons: {reasons_text} | blocking reasons: {blocks_text}"
        )

    def _build_directional_result(
        self,
        final_bias: str,
        smc_bias: str,
        crt_bias: str,
        orderflow_bias: str,
        config: ContextAlignmentConfig,
    ) -> ContextAlignmentResult:
        """Build an aligned directional result, optionally checking order flow."""
        reasons = [f"SMC and CRT are aligned {final_bias.lower()}"]
        blocking_reasons: list[str] = []
        confidence = 70.0

        if orderflow_bias == final_bias:
            confidence = 90.0
            reasons.append(f"Order Flow confirms {final_bias} alignment")
        elif orderflow_bias in {"NEUTRAL", "UNKNOWN"}:
            reasons.append("Order Flow is neutral or unknown")
            if config.require_orderflow_alignment:
                blocking_reasons.append("Order Flow alignment is required but missing or neutral")
        else:
            blocking_reasons.append(f"Order Flow bias {orderflow_bias} conflicts with {final_bias} alignment")

        minimum_confidence = max(0.0, min(100.0, float(config.minimum_confidence)))
        if confidence < minimum_confidence:
            blocking_reasons.append(f"Alignment confidence {confidence:.1f} below minimum {minimum_confidence:.1f}")

        if blocking_reasons:
            return ContextAlignmentResult(
                allowed=False,
                status="CONFLICT_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=-30.0,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
                aligned=False,
                final_bias="NEUTRAL",
                confidence=max(0.0, min(100.0, confidence)),
                smc_bias=smc_bias,
                crt_bias=crt_bias,
                orderflow_bias=orderflow_bias,
            )

        status = "ALIGNED_BULLISH" if final_bias == "BULLISH" else "ALIGNED_BEARISH"
        confidence_adjustment = 15.0 if orderflow_bias == final_bias else 10.0
        return ContextAlignmentResult(
            allowed=True,
            status=status,
            aligned_bias=final_bias,
            confidence_adjustment=confidence_adjustment,
            reasons=reasons,
            blocking_reasons=[],
            aligned=True,
            final_bias=final_bias,
            confidence=max(0.0, min(100.0, confidence)),
            smc_bias=smc_bias,
            crt_bias=crt_bias,
            orderflow_bias=orderflow_bias,
        )

    def _read_bias(self, source: Any, default: str = "UNKNOWN") -> str:
        """Safely normalize a context bias string."""
        if source is None:
            return default

        value = str(getattr(source, "bias", default) or default).upper()
        if value in {"BULLISH", "BEARISH", "NEUTRAL", "UNKNOWN"}:
            return value
        return "UNKNOWN"

    def _read_confidence(self, source: Any) -> float:
        """Safely normalize confidence to 0-100."""
        if source is None:
            return 0.0

        raw = getattr(source, "confidence", 0.0)
        try:
            confidence = float(raw)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(100.0, confidence))
