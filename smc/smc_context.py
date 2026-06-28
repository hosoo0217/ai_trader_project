"""SMC context combiner (v1).

This module combines market structure, BOS/CHOCH, and liquidity sweep outputs
into one summarized SMC context for research and backtesting.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from smc.bos_choch import BOSCHOCHResult
from smc.liquidity_sweep import LiquiditySweepResult
from smc.market_structure import MarketStructureResult


@dataclass
class SMCContextResult:
    """Unified SMC context result used by higher-level decision layers."""

    bias: str
    confidence: float
    market_structure_bias: str
    latest_break_type: str | None
    latest_break_direction: str | None
    latest_sweep_type: str | None
    latest_sweep_direction: str | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class SMCContextConfig:
    """Configuration for SMC context combination behavior."""

    minimum_confidence: float = 60.0
    require_structure_alignment: bool = False
    require_liquidity_sweep: bool = False
    require_bos_or_choch: bool = False


class SMCContextCombiner:
    """Combine SMC module outputs into one summarized context."""

    def combine(
        self,
        market_structure_result: MarketStructureResult | None,
        bos_choch_result: BOSCHOCHResult | None,
        liquidity_sweep_result: LiquiditySweepResult | None,
        config: SMCContextConfig,
    ) -> SMCContextResult:
        """Combine SMC evidence into one context result."""
        market_structure_bias = self._extract_market_structure_bias(market_structure_result)
        latest_break_type = self._extract_latest_break_type(bos_choch_result)
        latest_break_direction = self._extract_latest_break_direction(bos_choch_result)
        latest_sweep_type = self._extract_latest_sweep_type(liquidity_sweep_result)
        latest_sweep_direction = self._extract_latest_sweep_direction(liquidity_sweep_result)

        bullish_evidence = 0
        bearish_evidence = 0
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if market_structure_bias == "BULLISH":
            bullish_evidence += 1
            reasons.append("Market structure is bullish")
        elif market_structure_bias == "BEARISH":
            bearish_evidence += 1
            reasons.append("Market structure is bearish")

        if latest_break_direction == "BULLISH":
            bullish_evidence += 1
            reasons.append("Latest BOS/CHOCH direction is bullish")
        elif latest_break_direction == "BEARISH":
            bearish_evidence += 1
            reasons.append("Latest BOS/CHOCH direction is bearish")

        if latest_sweep_direction == "BULLISH":
            bullish_evidence += 1
            reasons.append("Latest liquidity sweep direction is bullish")
        elif latest_sweep_direction == "BEARISH":
            bearish_evidence += 1
            reasons.append("Latest liquidity sweep direction is bearish")

        if bullish_evidence == 0 and bearish_evidence == 0:
            return SMCContextResult(
                bias="UNKNOWN",
                confidence=0.0,
                market_structure_bias=market_structure_bias,
                latest_break_type=latest_break_type,
                latest_break_direction=latest_break_direction,
                latest_sweep_type=latest_sweep_type,
                latest_sweep_direction=latest_sweep_direction,
                reasons=["No usable SMC evidence found"],
                blocking_reasons=["All SMC inputs were missing or not directional"],
            )

        if bullish_evidence > bearish_evidence:
            bias = "BULLISH"
        elif bearish_evidence > bullish_evidence:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"
            reasons.append("Bullish and bearish evidence are balanced")

        confidence = self._calculate_confidence(bias, bullish_evidence, bearish_evidence)

        if config.require_structure_alignment and bias in {"BULLISH", "BEARISH"}:
            if market_structure_bias in {"BULLISH", "BEARISH"} and market_structure_bias != bias:
                bias = "NEUTRAL"
                blocking_reasons.append("Structure alignment required but market structure conflicts with final bias")

        if config.require_liquidity_sweep and latest_sweep_type is None:
            bias = "NEUTRAL"
            blocking_reasons.append("Liquidity sweep evidence is required")

        if config.require_bos_or_choch and latest_break_type is None:
            bias = "NEUTRAL"
            blocking_reasons.append("BOS/CHOCH evidence is required")

        minimum_confidence = max(0.0, min(100.0, float(config.minimum_confidence)))
        if bias in {"BULLISH", "BEARISH"} and confidence < minimum_confidence:
            bias = "NEUTRAL"
            blocking_reasons.append(
                f"Confidence {confidence:.1f} is below minimum threshold {minimum_confidence:.1f}"
            )

        return SMCContextResult(
            bias=bias,
            confidence=confidence,
            market_structure_bias=market_structure_bias,
            latest_break_type=latest_break_type,
            latest_break_direction=latest_break_direction,
            latest_sweep_type=latest_sweep_type,
            latest_sweep_direction=latest_sweep_direction,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: SMCContextResult) -> str:
        """Return a readable explanation for combined SMC context."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            f"SMC context: {result.bias} | confidence: {result.confidence:.1f} | "
            f"market structure: {result.market_structure_bias} | "
            f"latest break: {result.latest_break_type or 'None'} {result.latest_break_direction or ''} | "
            f"latest sweep: {result.latest_sweep_type or 'None'} {result.latest_sweep_direction or ''} | "
            f"reasons: {reasons_text} | blocking reasons: {blocks_text}"
        )

    def _calculate_confidence(self, bias: str, bullish_evidence: int, bearish_evidence: int) -> float:
        """Compute a simple bounded confidence score from evidence counts."""
        aligned = max(bullish_evidence, bearish_evidence)
        conflict = min(bullish_evidence, bearish_evidence)

        if bias in {"BULLISH", "BEARISH"}:
            score = 35.0 + (aligned * 25.0) - (conflict * 15.0)
        elif bias == "NEUTRAL":
            # Neutral means mixed evidence; confidence should stay modest.
            score = 40.0 - ((bullish_evidence + bearish_evidence) * 5.0)
        else:
            score = 0.0

        return max(0.0, min(100.0, float(score)))

    def _extract_market_structure_bias(self, result: MarketStructureResult | None) -> str:
        """Safely read market structure bias."""
        if result is None:
            return "UNKNOWN"
        value = str(getattr(result, "structure_bias", "UNKNOWN") or "UNKNOWN").upper()
        if value in {"BULLISH", "BEARISH", "NEUTRAL", "UNKNOWN"}:
            return value
        return "UNKNOWN"

    def _extract_latest_break_type(self, result: BOSCHOCHResult | None) -> str | None:
        """Safely read latest break type."""
        latest = getattr(result, "latest_break", None) if result is not None else None
        value = getattr(latest, "break_type", None)
        return str(value).upper() if value is not None else None

    def _extract_latest_break_direction(self, result: BOSCHOCHResult | None) -> str | None:
        """Safely read latest break direction."""
        latest = getattr(result, "latest_break", None) if result is not None else None
        value = getattr(latest, "direction", None)
        if value is None:
            return None
        direction = str(value).upper()
        if direction in {"BULLISH", "BEARISH"}:
            return direction
        return None

    def _extract_latest_sweep_type(self, result: LiquiditySweepResult | None) -> str | None:
        """Safely read latest sweep type."""
        latest = getattr(result, "latest_sweep", None) if result is not None else None
        value = getattr(latest, "sweep_type", None)
        return str(value).upper() if value is not None else None

    def _extract_latest_sweep_direction(self, result: LiquiditySweepResult | None) -> str | None:
        """Safely read latest sweep direction."""
        latest = getattr(result, "latest_sweep", None) if result is not None else None
        value = getattr(latest, "direction", None)
        if value is None:
            return None
        direction = str(value).upper()
        if direction in {"BULLISH", "BEARISH"}:
            return direction
        return None
