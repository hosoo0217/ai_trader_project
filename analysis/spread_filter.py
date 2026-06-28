"""Spread-based safety filter for paper trading and backtesting.

This module blocks trading when spread is unknown, invalid, or too high.
It is research-only and does not connect to brokers or external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SpreadFilterConfig:
    """Configuration for simple spread safety checks."""

    enabled: bool = True
    max_spread: float = 3.0
    block_if_spread_unknown: bool = True


@dataclass
class SpreadFilterResult:
    """Outcome of one spread filter evaluation."""

    allowed: bool
    status: str
    spread: float | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class SpreadFilter:
    """Evaluate whether current spread is safe enough for trading."""

    def evaluate(self, spread: float | None, config: SpreadFilterConfig) -> SpreadFilterResult:
        """Return a safe allow/block decision from spread value."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if not config.enabled:
            return SpreadFilterResult(
                allowed=True,
                status="FILTER_DISABLED",
                spread=spread,
                reasons=["Spread filter disabled"],
                blocking_reasons=[],
            )

        if spread is None:
            if config.block_if_spread_unknown:
                blocking_reasons.append("Spread is unknown")
                return SpreadFilterResult(
                    allowed=False,
                    status="SPREAD_UNKNOWN",
                    spread=None,
                    reasons=reasons,
                    blocking_reasons=blocking_reasons,
                )

            reasons.append("Spread is unknown but allowed by configuration")
            return SpreadFilterResult(
                allowed=True,
                status="SPREAD_UNKNOWN",
                spread=None,
                reasons=reasons,
                blocking_reasons=[],
            )

        if spread < 0:
            blocking_reasons.append("Spread cannot be negative")
            return SpreadFilterResult(
                allowed=False,
                status="INVALID_SPREAD",
                spread=spread,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        if spread > config.max_spread:
            blocking_reasons.append("Spread is above maximum threshold")
            return SpreadFilterResult(
                allowed=False,
                status="SPREAD_TOO_HIGH",
                spread=spread,
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        reasons.append("Spread is within configured range")
        return SpreadFilterResult(
            allowed=True,
            status="SPREAD_ALLOWED",
            spread=spread,
            reasons=reasons,
            blocking_reasons=[],
        )

    def explain(self, result: SpreadFilterResult) -> str:
        """Return a readable explanation for logs and console output."""
        spread_text = f"{result.spread:.4f}" if result.spread is not None else "None"
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"

        return (
            f"Spread filter status: {result.status} | "
            f"allowed: {result.allowed} | "
            f"spread: {spread_text} | "
            f"reasons: {reasons_text} | "
            f"blocking reasons: {blocks_text}"
        )
