"""
Decision context data models for trading decisions.

This module defines simple dataclasses that aggregate the market state,
structure-based SMC signals, CRT engine flags, orderflow cues, and risk
considerations into a single `DecisionContext` object.

The classes are intentionally lightweight and designed for unit testing and
algorithmic decision-making logic. They do NOT perform any broker execution
or live trading operations.

Beginner-friendly comments are included to explain fields and helper methods.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class MarketContext:
    """Holds basic market data relevant to decisions.

    Attributes:
        price: current mid/last price for the instrument
        volatility: simple measure of recent volatility (e.g., ATR or stddev)
        trend: simplified trend score where -1 = down, 0 = flat, 1 = up
    """

    price: float = 0.0
    volatility: float = 0.0
    trend: int = 0


@dataclass
class SMCContext:
    """Simplified SMC (Smart Money Concepts) context.

    Attributes:
        order_blocks_hit: whether price is near an order block
        liquidity_structure_clear: whether the expected liquidity structure is present
        bias: bias from SMC analysis (-1, 0, 1)
    """

    order_blocks_hit: bool = False
    liquidity_structure_clear: bool = False
    bias: int = 0
    smc_bias: str = "UNKNOWN"
    smc_confidence: float = 0.0
    smc_reasons: List[str] = field(default_factory=list)
    smc_blocking_reasons: List[str] = field(default_factory=list)


@dataclass
class CRTContext:
    """CRT engine context flags.

    Attributes:
        confirmed: True when the CRT engine confirms a trade setup
        confidence: float in [0,1] indicating confidence level
    """

    confirmed: bool = False
    confidence: float = 0.0
    crt_bias: str = "UNKNOWN"
    crt_signal_type: str | None = None
    crt_reasons: List[str] = field(default_factory=list)
    crt_blocking_reasons: List[str] = field(default_factory=list)


@dataclass
class OrderFlowContext:
    """Order flow signals and simple volume/imbalance stats.

    Attributes:
        buying_pressure: positive means buyers dominating, negative for sellers
        recent_fills: simplified recent fill imbalance measure
    """

    buying_pressure: float = 0.0
    recent_fills: float = 0.0
    orderflow_bias: str = "UNKNOWN"
    orderflow_confidence: float = 0.0
    orderflow_reasons: List[str] = field(default_factory=list)
    orderflow_blocking_reasons: List[str] = field(default_factory=list)


@dataclass
class RiskContext:
    """Risk settings and calculated allowances.

    Attributes:
        max_risk_per_trade: fraction of equity allowed to risk per trade (0-1)
        equity: current account equity (for sizing)
        stop_distance: suggested stop distance in price units
    """

    max_risk_per_trade: float = 0.01
    equity: float = 10000.0
    stop_distance: float = 0.0


@dataclass
class DecisionContext:
    """Aggregates all contexts into a single decision-making object.

    Helper methods:
        is_trade_allowed(): returns True if no blocking reasons exist
        explain_blocking_reasons(): returns a list of strings explaining blocks

    Defaults are conservative: by default trading is NOT allowed until
    specific signals (e.g., CRT confirmed) are present.
    """

    market: MarketContext = field(default_factory=MarketContext)
    smc: SMCContext = field(default_factory=SMCContext)
    crt: CRTContext = field(default_factory=CRTContext)
    orderflow: OrderFlowContext = field(default_factory=OrderFlowContext)
    risk: RiskContext = field(default_factory=RiskContext)

    # Additional flags
    trading_halted: bool = False
    max_concurrent_trades: int = 1
    open_trades_count: int = 0
    alignment_allowed: bool = True
    alignment_status: str | None = None
    aligned_bias: str | None = None
    alignment_confidence_adjustment: float = 0.0
    alignment_reasons: List[str] = field(default_factory=list)
    alignment_blocking_reasons: List[str] = field(default_factory=list)

    def is_trade_allowed(self) -> bool:
        """Determine whether a new trade is allowed.

        This method checks several conservative, beginner-friendly rules:
        - Trading is halted globally: no trades allowed.
        - CRT must confirm a setup with non-trivial confidence (>0.5).
        - Risk sizing must allow at least a minimal position (equity > 0).
        - Do not exceed max concurrent trades.

        These are simple examples and should be adapted to real strategies.
        """

        reasons = self.explain_blocking_reasons()
        return len(reasons) == 0

    def explain_blocking_reasons(self) -> List[str]:
        """Return human-readable reasons why trading is blocked.

        Useful for logging and for beginner developers to understand
        why the context prevents trading.
        """

        reasons: List[str] = []

        if self.trading_halted:
            reasons.append("Global trading halted")

        # CRT confirmation required by default
        if not self.crt.confirmed:
            reasons.append("CRT not confirmed")
        else:
            # If confirmed, require some confidence threshold
            if self.crt.confidence <= 0.5:
                reasons.append("CRT confidence too low")

        # Risk: equity must be positive and max risk reasonable
        if self.risk.equity <= 0:
            reasons.append("Non-positive equity")
        if not (0.0 <= self.risk.max_risk_per_trade <= 1.0):
            reasons.append("Invalid max_risk_per_trade value")

        # Concurrency limit
        if self.open_trades_count >= self.max_concurrent_trades:
            reasons.append("Max concurrent trades reached")

        # Market conditions: avoid trading when volatility is zero (no data)
        if self.market.volatility <= 0.0:
            reasons.append("Insufficient market volatility/data")

        return reasons
