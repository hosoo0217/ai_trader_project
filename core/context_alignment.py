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


@dataclass
class ContextAlignmentResult:
    """Result of SMC/CRT alignment validation."""

    allowed: bool
    status: str
    aligned_bias: str | None
    confidence_adjustment: float
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ContextAlignmentGate:
    """Validate alignment between SMC context and CRT context."""

    def evaluate(
        self,
        smc_result: Any,
        crt_result: Any,
        config: ContextAlignmentConfig,
    ) -> ContextAlignmentResult:
        """Evaluate SMC/CRT alignment with safe fallback behavior."""
        if not config.enabled or not config.require_smc_crt_alignment:
            return ContextAlignmentResult(
                allowed=True,
                status="FILTER_DISABLED",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["Context alignment gate disabled"],
                blocking_reasons=[],
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
            )

        if smc_bias == "UNKNOWN":
            return ContextAlignmentResult(
                allowed=False,
                status="UNKNOWN_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["SMC context is UNKNOWN"],
                blocking_reasons=["SMC context is UNKNOWN"],
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
            )

        if smc_bias == "NEUTRAL":
            return ContextAlignmentResult(
                allowed=False,
                status="NEUTRAL_WAIT",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["SMC bias is NEUTRAL"],
                blocking_reasons=["SMC bias is NEUTRAL"],
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
                )
            return ContextAlignmentResult(
                allowed=False,
                status="UNKNOWN_BLOCKED",
                aligned_bias=None,
                confidence_adjustment=-5.0,
                reasons=["CRT context is UNKNOWN"],
                blocking_reasons=["CRT context is UNKNOWN and not allowed"],
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
                )
            return ContextAlignmentResult(
                allowed=False,
                status="NEUTRAL_WAIT",
                aligned_bias=None,
                confidence_adjustment=0.0,
                reasons=["CRT context is NEUTRAL"],
                blocking_reasons=["CRT neutral context is not allowed"],
            )

        if smc_bias == "BULLISH" and crt_bias == "BULLISH":
            return ContextAlignmentResult(
                allowed=True,
                status="ALIGNED_BULLISH",
                aligned_bias="BULLISH",
                confidence_adjustment=10.0,
                reasons=["SMC and CRT are aligned bullish"],
                blocking_reasons=[],
            )

        if smc_bias == "BEARISH" and crt_bias == "BEARISH":
            return ContextAlignmentResult(
                allowed=True,
                status="ALIGNED_BEARISH",
                aligned_bias="BEARISH",
                confidence_adjustment=10.0,
                reasons=["SMC and CRT are aligned bearish"],
                blocking_reasons=[],
            )

        return ContextAlignmentResult(
            allowed=False,
            status="CONFLICT_BLOCKED",
            aligned_bias=None,
            confidence_adjustment=-30.0,
            reasons=["SMC and CRT contexts conflict"],
            blocking_reasons=[f"SMC bias {smc_bias} conflicts with CRT bias {crt_bias}"],
        )

    def explain(self, result: ContextAlignmentResult) -> str:
        """Return a readable summary of alignment gate output."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            f"Context alignment: {result.status} | allowed: {result.allowed} | "
            f"aligned bias: {result.aligned_bias or 'None'} | "
            f"confidence adjustment: {result.confidence_adjustment:.1f} | "
            f"reasons: {reasons_text} | blocking reasons: {blocks_text}"
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
