from __future__ import annotations


class RiskManager:
    """A very simple risk manager for beginner-friendly backtests."""

    def __init__(self, risk_per_trade: float = 0.01) -> None:
        self.risk_per_trade = risk_per_trade

    def position_size(self, entry_price: float, stop_loss: float) -> float:
        """Return a placeholder position size based on 1% risk."""
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit <= 0:
            return 0.0
        return self.risk_per_trade * entry_price / risk_per_unit
