"""Combine order flow analyzers into one research context.

This module summarizes Delta/CVD, imbalance, and absorption outputs.
It does not connect to live data, brokers, Sierra Chart, CME, or external APIs.
It also does not generate trade signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow.absorption import AbsorptionResult
from orderflow.delta_cvd import DeltaCVDResult
from orderflow.imbalance import ImbalanceResult


@dataclass
class OrderFlowContextConfig:
    """Configuration for combining order flow evidence."""

    minimum_confidence: float = 50.0
    require_delta_alignment: bool = False
    require_imbalance_alignment: bool = False
    require_absorption_confirmation: bool = False


@dataclass
class OrderFlowContextResult:
    """Unified order flow context for future decision making."""

    bias: str
    confidence: float
    delta_direction: str | None
    imbalance_bias: str | None
    absorption_bias: str | None
    final_cvd: float | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class OrderFlowContextCombiner:
    """Combine order flow evidence into a single context summary."""

    def combine(
        self,
        delta_cvd_result: DeltaCVDResult | None,
        imbalance_result: ImbalanceResult | None,
        absorption_result: AbsorptionResult | None,
        config: OrderFlowContextConfig,
    ) -> OrderFlowContextResult:
        """Combine available order flow results without producing trades."""
        delta_direction = self._safe_attr(delta_cvd_result, "latest_direction")
        imbalance_bias = self._safe_attr(imbalance_result, "bias")
        absorption_bias = self._safe_attr(absorption_result, "bias")
        final_cvd = self._safe_float_or_none(self._safe_attr(delta_cvd_result, "final_cvd"))
        reasons: list[str] = []
        blocking_reasons: list[str] = []
        bullish_evidence = 0
        bearish_evidence = 0

        delta_bias = self._bias_from_delta(delta_direction)
        if delta_bias == "BULLISH":
            bullish_evidence += 1
            reasons.append("Delta/CVD shows buying pressure")
        elif delta_bias == "BEARISH":
            bearish_evidence += 1
            reasons.append("Delta/CVD shows selling pressure")
        elif delta_cvd_result is not None:
            reasons.append("Delta/CVD is neutral")

        if imbalance_bias == "BULLISH":
            bullish_evidence += 1
            reasons.append("Imbalance is bullish")
        elif imbalance_bias == "BEARISH":
            bearish_evidence += 1
            reasons.append("Imbalance is bearish")
        elif imbalance_result is not None:
            reasons.append("Imbalance is neutral or unknown")

        if absorption_bias == "BULLISH":
            bullish_evidence += 1
            reasons.append("Absorption is bullish")
        elif absorption_bias == "BEARISH":
            bearish_evidence += 1
            reasons.append("Absorption is bearish")
        elif absorption_result is not None:
            reasons.append("Absorption is neutral or unknown")

        total_directional_evidence = bullish_evidence + bearish_evidence
        any_input_provided = any(result is not None for result in [delta_cvd_result, imbalance_result, absorption_result])
        if total_directional_evidence == 0:
            if not any_input_provided:
                return OrderFlowContextResult(
                    bias="UNKNOWN",
                    confidence=0.0,
                    delta_direction=delta_direction,
                    imbalance_bias=imbalance_bias,
                    absorption_bias=absorption_bias,
                    final_cvd=final_cvd,
                    reasons=["No order flow inputs provided"],
                    blocking_reasons=["No usable order flow evidence"],
                )

            return OrderFlowContextResult(
                bias="NEUTRAL",
                confidence=0.0,
                delta_direction=delta_direction,
                imbalance_bias=imbalance_bias,
                absorption_bias=absorption_bias,
                final_cvd=final_cvd,
                reasons=reasons or ["No directional order flow evidence"],
                blocking_reasons=[],
            )

        if bullish_evidence > bearish_evidence:
            bias = "BULLISH"
        elif bearish_evidence > bullish_evidence:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"
            reasons.append("Bullish and bearish order flow evidence are balanced")

        confidence = self._calculate_confidence(bullish_evidence, bearish_evidence)

        if bias in {"BULLISH", "BEARISH"}:
            self._apply_alignment_requirements(
                bias=bias,
                delta_bias=delta_bias,
                imbalance_bias=imbalance_bias,
                absorption_bias=absorption_bias,
                config=config,
                blocking_reasons=blocking_reasons,
            )

            minimum_confidence = self._clamp(float(config.minimum_confidence))
            if confidence < minimum_confidence:
                blocking_reasons.append(
                    f"Confidence {confidence:.1f} is below minimum {minimum_confidence:.1f}"
                )

        if blocking_reasons:
            reasons.append("Order flow context was neutralized by configuration requirements")
            bias = "NEUTRAL"

        return OrderFlowContextResult(
            bias=bias,
            confidence=confidence,
            delta_direction=delta_direction,
            imbalance_bias=imbalance_bias,
            absorption_bias=absorption_bias,
            final_cvd=final_cvd,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: OrderFlowContextResult) -> str:
        """Return a readable order flow context summary."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Order flow context summary: "
            f"bias={result.bias}, "
            f"confidence={result.confidence:.1f}, "
            f"delta_direction={result.delta_direction}, "
            f"imbalance_bias={result.imbalance_bias}, "
            f"absorption_bias={result.absorption_bias}, "
            f"final_cvd={result.final_cvd}, "
            f"reasons={reasons_text}, "
            f"blocking_reasons={blocks_text}."
        )

    def _bias_from_delta(self, delta_direction: str | None) -> str:
        """Convert Delta/CVD direction into the shared bias language."""
        if delta_direction == "BUYING_PRESSURE":
            return "BULLISH"
        if delta_direction == "SELLING_PRESSURE":
            return "BEARISH"
        return "NEUTRAL"

    def _calculate_confidence(self, bullish_evidence: int, bearish_evidence: int) -> float:
        """Calculate a simple confidence score from aligned and conflicting evidence."""
        aligned_evidence = max(bullish_evidence, bearish_evidence)
        conflicting_evidence = min(bullish_evidence, bearish_evidence)
        confidence = (aligned_evidence * 30.0) - (conflicting_evidence * 20.0)
        if aligned_evidence >= 2:
            confidence += 10.0
        return self._clamp(confidence)

    def _apply_alignment_requirements(
        self,
        bias: str,
        delta_bias: str,
        imbalance_bias: str | None,
        absorption_bias: str | None,
        config: OrderFlowContextConfig,
        blocking_reasons: list[str],
    ) -> None:
        """Add blocking reasons when required sources do not support the bias."""
        if config.require_delta_alignment and delta_bias not in {bias, "NEUTRAL"}:
            blocking_reasons.append("Delta direction conflicts with final order flow bias")

        if config.require_imbalance_alignment and imbalance_bias not in {bias, "NEUTRAL"}:
            blocking_reasons.append("Imbalance bias conflicts with final order flow bias")

        if config.require_absorption_confirmation and absorption_bias != bias:
            blocking_reasons.append("Absorption does not confirm final order flow bias")

    def _safe_attr(self, value: object, name: str) -> object | None:
        """Read an attribute safely from optional analyzer results."""
        if value is None:
            return None
        return getattr(value, name, None)

    def _safe_float_or_none(self, value: object | None) -> float | None:
        """Convert a value to float, returning None if it is missing or invalid."""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _clamp(self, value: float) -> float:
        """Keep confidence inside a safe 0-100 range."""
        return max(0.0, min(100.0, value))
