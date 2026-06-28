"""Simple risk engine for paper trading and backtesting.

This module calculates a risk plan before placing a paper trade. It does not
connect to any live broker or external API.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RiskEngineConfig:
    """Configuration used to build one risk plan."""

    account_balance: float = 10000.0
    risk_per_trade_percent: float = 1.0
    reward_to_risk: float = 2.0
    default_stop_distance: float = 10.0
    min_volume: float = 0.01
    max_volume: float = 10.0
    point_value: float = 1.0


@dataclass
class RiskPlan:
    """A full risk and position-sizing plan for one potential trade."""

    allowed: bool
    side: str
    entry_price: float
    stop_loss: float | None
    take_profit: float | None
    risk_amount: float
    risk_per_unit: float
    volume: float
    reward_to_risk: float
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class RiskEngine:
    """Create simple, safe stop-loss/take-profit and position-size plans."""

    def create_plan(self, side: str, entry_price: float, config: RiskEngineConfig) -> RiskPlan:
        """Build a risk plan from side, entry price, and config."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []
        normalized_side = (side or "").upper()

        if normalized_side not in {"BUY", "SELL"}:
            blocking_reasons.append("Invalid side. Only BUY or SELL is allowed")

        if entry_price <= 0:
            blocking_reasons.append("Entry price must be positive")

        if config.account_balance <= 0:
            blocking_reasons.append("Account balance must be positive")

        if config.risk_per_trade_percent <= 0:
            blocking_reasons.append("Risk per trade percent must be positive")

        if config.default_stop_distance <= 0:
            blocking_reasons.append("Default stop distance must be positive")

        if config.reward_to_risk <= 0:
            blocking_reasons.append("Reward-to-risk must be positive")

        if config.min_volume <= 0:
            blocking_reasons.append("Minimum volume must be positive")

        if config.max_volume <= 0:
            blocking_reasons.append("Maximum volume must be positive")

        if config.min_volume > config.max_volume:
            blocking_reasons.append("Minimum volume cannot be greater than maximum volume")

        if config.point_value <= 0:
            blocking_reasons.append("Point value must be positive")

        if blocking_reasons:
            return RiskPlan(
                allowed=False,
                side=normalized_side,
                entry_price=float(entry_price),
                stop_loss=None,
                take_profit=None,
                risk_amount=0.0,
                risk_per_unit=0.0,
                volume=0.0,
                reward_to_risk=float(config.reward_to_risk),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        if normalized_side == "BUY":
            stop_loss = float(entry_price - config.default_stop_distance)
            take_profit = float(entry_price + (config.default_stop_distance * config.reward_to_risk))
            if stop_loss >= entry_price:
                blocking_reasons.append("BUY stop loss must be below entry price")
            if take_profit <= entry_price:
                blocking_reasons.append("BUY take profit must be above entry price")
        else:
            stop_loss = float(entry_price + config.default_stop_distance)
            take_profit = float(entry_price - (config.default_stop_distance * config.reward_to_risk))
            if stop_loss <= entry_price:
                blocking_reasons.append("SELL stop loss must be above entry price")
            if take_profit >= entry_price:
                blocking_reasons.append("SELL take profit must be below entry price")

        risk_amount = float(config.account_balance * config.risk_per_trade_percent / 100.0)
        risk_per_unit = float(abs(entry_price - stop_loss) * config.point_value)

        if risk_per_unit <= 0:
            blocking_reasons.append("Calculated risk per unit must be positive")
            return RiskPlan(
                allowed=False,
                side=normalized_side,
                entry_price=float(entry_price),
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                risk_per_unit=risk_per_unit,
                volume=0.0,
                reward_to_risk=float(config.reward_to_risk),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        raw_volume = float(risk_amount / risk_per_unit)
        if raw_volume <= 0:
            blocking_reasons.append("Calculated volume must be positive")
            return RiskPlan(
                allowed=False,
                side=normalized_side,
                entry_price=float(entry_price),
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                risk_per_unit=risk_per_unit,
                volume=0.0,
                reward_to_risk=float(config.reward_to_risk),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        volume = raw_volume
        if raw_volume < config.min_volume:
            volume = float(config.min_volume)
            reasons.append("Calculated volume is below minimum. Using min_volume")
        elif raw_volume > config.max_volume:
            volume = float(config.max_volume)
            reasons.append("Calculated volume is above maximum. Using max_volume")

        if blocking_reasons:
            return RiskPlan(
                allowed=False,
                side=normalized_side,
                entry_price=float(entry_price),
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                risk_per_unit=risk_per_unit,
                volume=volume,
                reward_to_risk=float(config.reward_to_risk),
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        reasons.append("Risk plan created")
        return RiskPlan(
            allowed=True,
            side=normalized_side,
            entry_price=float(entry_price),
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=risk_amount,
            risk_per_unit=risk_per_unit,
            volume=volume,
            reward_to_risk=float(config.reward_to_risk),
            reasons=reasons,
            blocking_reasons=[],
        )

    def explain(self, plan: RiskPlan) -> str:
        """Return a readable summary of the generated risk plan."""
        if not plan.allowed:
            block_text = "; ".join(plan.blocking_reasons) if plan.blocking_reasons else "No reason provided"
            return (
                f"Risk plan blocked | side={plan.side} | entry={plan.entry_price:.2f} | "
                f"blocking_reasons={block_text}"
            )

        reasons_text = "; ".join(plan.reasons) if plan.reasons else "No notes"
        return (
            f"Risk plan allowed | side={plan.side} | entry={plan.entry_price:.2f} | "
            f"SL={plan.stop_loss:.2f} | TP={plan.take_profit:.2f} | risk_amount={plan.risk_amount:.2f} | "
            f"risk_per_unit={plan.risk_per_unit:.2f} | volume={plan.volume:.4f} | notes={reasons_text}"
        )
