"""Capital protection engine for safe trading decisions.

This module provides simple, beginner-friendly risk controls that can be used
by the decision-making flow without performing any broker execution or live
trading. The rules are intentionally conservative and easy to understand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CapitalProtectionConfig:
    """Configuration for capital protection rules.

    Each setting represents a simple safety rule. The defaults are intentionally
    conservative so that the engine blocks trading until the user has provided
    a clear positive state.
    """

    max_daily_loss: float = 0.0
    daily_profit_target: float = 0.0
    max_consecutive_losses: int = 0
    max_open_positions: int = 0
    trading_enabled: bool = True
    manual_pause: bool = False


@dataclass
class CapitalProtectionState:
    """Runtime state used by the capital protection engine."""

    realized_daily_pnl: float = 0.0
    consecutive_losses: int = 0
    open_positions: int = 0
    emergency_stop: bool = False


@dataclass
class CapitalProtectionDecision:
    """Outcome of a capital protection evaluation."""

    allowed: bool = True
    status: str = "allowed"
    reasons: List[str] = field(default_factory=list)


class CapitalProtectionEngine:
    """Simple capital protection engine.

    The engine evaluates a set of protective rules in priority order. It does
    not execute orders or connect to a broker; it only returns a decision.
    """

    def evaluate(self, config: CapitalProtectionConfig, state: CapitalProtectionState) -> CapitalProtectionDecision:
        """Evaluate whether trading should be allowed.

        The rules are checked in the required priority order. The first blocking
        rules are the strongest and stop all trading immediately.
        """
        reasons: List[str] = []

        if state.emergency_stop:
            reasons.append("Emergency stop activated")
        elif not config.trading_enabled:
            reasons.append("Trading disabled")
        elif config.manual_pause:
            reasons.append("Manual pause active")
        elif state.realized_daily_pnl <= -abs(config.max_daily_loss) and config.max_daily_loss > 0:
            reasons.append("Daily loss limit reached")
        elif state.realized_daily_pnl >= abs(config.daily_profit_target) and config.daily_profit_target > 0:
            reasons.append("Daily profit target reached")
        elif state.consecutive_losses >= config.max_consecutive_losses and config.max_consecutive_losses > 0:
            reasons.append("Maximum consecutive losses reached")
        elif state.open_positions >= config.max_open_positions and config.max_open_positions > 0:
            reasons.append("Maximum open positions reached")

        if reasons:
            return CapitalProtectionDecision(allowed=False, status="blocked", reasons=reasons)

        return CapitalProtectionDecision(allowed=True, status="allowed", reasons=[])

    def should_stop_trading(self, config: CapitalProtectionConfig, state: CapitalProtectionState) -> bool:
        """Return True when trading should be blocked."""
        return not self.evaluate(config, state).allowed

    def explain_decision(self, decision: CapitalProtectionDecision) -> str:
        """Create a human-readable explanation for a decision."""
        if decision.allowed:
            return "Trading is allowed."

        if not decision.reasons:
            return "Trading is blocked for an unknown reason."

        return "Trading is blocked because: " + "; ".join(decision.reasons)
