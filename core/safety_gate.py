"""Unified pre-trade safety gate for paper trading and backtesting.

This module combines multiple safety checks into one final allow or block
decision before any trade can continue. It is research-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from analysis.news_filter import NewsFilterResult
from analysis.session_filter import SessionFilterResult
from analysis.spread_filter import SpreadFilterResult
from analysis.volatility_filter import VolatilityFilterResult
from core.capital_protection import CapitalProtectionDecision


@dataclass
class SafetyGateDecision:
    """Final decision from the pre-trade safety gate."""

    allowed: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)


class SafetyGate:
    """Combine safety checks and return one clear pre-trade decision."""

    def evaluate(
        self,
        session_result: SessionFilterResult | None = None,
        news_result: NewsFilterResult | None = None,
        volatility_result: VolatilityFilterResult | None = None,
        spread_result: SpreadFilterResult | None = None,
        capital_decision: CapitalProtectionDecision | None = None,
    ) -> SafetyGateDecision:
        """Evaluate provided checks and produce one safe gate decision."""
        checks: list[tuple[str, object]] = []
        if session_result is not None:
            checks.append(("SESSION", session_result))
        if news_result is not None:
            checks.append(("NEWS", news_result))
        if volatility_result is not None:
            checks.append(("VOLATILITY", volatility_result))
        if spread_result is not None:
            checks.append(("SPREAD", spread_result))
        if capital_decision is not None:
            checks.append(("CAPITAL_PROTECTION", capital_decision))

        if not checks:
            return SafetyGateDecision(
                allowed=False,
                status="NO_CHECKS_PROVIDED",
                reasons=["No safety checks were provided"],
                blocking_reasons=["No safety checks were provided"],
                passed_checks=[],
                failed_checks=[],
            )

        reasons: list[str] = []
        blocking_reasons: list[str] = []
        passed_checks: list[str] = []
        failed_checks: list[str] = []

        for check_name, check_result in checks:
            check_allowed = bool(getattr(check_result, "allowed", False))
            check_reasons = list(getattr(check_result, "reasons", []))
            check_blocks = list(getattr(check_result, "blocking_reasons", []))

            reasons.extend([f"{check_name}: {reason}" for reason in check_reasons])

            if check_allowed:
                passed_checks.append(check_name)
                continue

            failed_checks.append(check_name)
            if check_blocks:
                blocking_reasons.extend([f"{check_name}: {reason}" for reason in check_blocks])
            elif check_reasons:
                blocking_reasons.extend([f"{check_name}: {reason}" for reason in check_reasons])
            else:
                blocking_reasons.append(f"{check_name}: Check blocked trading")

        # Capital protection has highest authority and must force block when failed.
        capital_blocked = "CAPITAL_PROTECTION" in failed_checks
        blocked = bool(failed_checks) or capital_blocked

        if blocked:
            return SafetyGateDecision(
                allowed=False,
                status="SAFETY_BLOCKED",
                reasons=reasons,
                blocking_reasons=blocking_reasons,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
            )

        return SafetyGateDecision(
            allowed=True,
            status="SAFETY_PASSED",
            reasons=reasons,
            blocking_reasons=[],
            passed_checks=passed_checks,
            failed_checks=[],
        )

    def explain(self, decision: SafetyGateDecision) -> str:
        """Return a readable explanation for logs and console output."""
        passed_text = ", ".join(decision.passed_checks) if decision.passed_checks else "None"
        failed_text = ", ".join(decision.failed_checks) if decision.failed_checks else "None"
        blocks_text = "; ".join(decision.blocking_reasons) if decision.blocking_reasons else "None"

        if decision.allowed:
            recommendation = "Safety passed. Trade may continue to risk validation."
        else:
            recommendation = "Safety blocked. Do not trade."

        return (
            f"Safety status: {decision.status} | "
            f"allowed: {decision.allowed} | "
            f"passed checks: {passed_text} | "
            f"failed checks: {failed_text} | "
            f"blocking reasons: {blocks_text} | "
            f"recommendation: {recommendation}"
        )
