"""Simple paper broker for safe in-memory trading simulation.

This module does not connect to any real broker or exchange. It only stores
positions and balance in memory so tests and backtests can simulate order
flow without risking real money.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4


@dataclass
class PaperBrokerConfig:
    """Configuration for the paper broker."""

    starting_balance: float = 10000.0
    allow_buy: bool = True
    allow_sell: bool = True
    max_open_positions: int = 1


@dataclass
class PaperPosition:
    """A single simulated open or closed position."""

    position_id: str
    symbol: str
    side: str
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    volume: float
    status: str = "OPEN"
    reason: str = ""


@dataclass
class PaperBrokerState:
    """Runtime state for the paper broker."""

    balance: float = 10000.0
    open_positions: List[PaperPosition] = field(default_factory=list)
    closed_positions: List[PaperPosition] = field(default_factory=list)


@dataclass
class PaperOrderResult:
    """Result of an order attempt."""

    accepted: bool
    status: str
    reason: str
    position: Optional[PaperPosition] = None


class PaperBroker:
    """In-memory broker used for paper trading and tests."""

    def create_default_state(self, config: PaperBrokerConfig) -> PaperBrokerState:
        """Create a fresh state with the configured starting balance."""
        return PaperBrokerState(balance=config.starting_balance)

    def place_market_order(
        self,
        config: PaperBrokerConfig,
        state: PaperBrokerState,
        symbol: str,
        side: str,
        price: float,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        reason: str = "",
    ) -> PaperOrderResult:
        """Open a new paper position if the order is valid."""
        if not config.allow_buy and side.upper() == "BUY":
            return PaperOrderResult(False, "REJECTED", "Buying is disabled")
        if not config.allow_sell and side.upper() == "SELL":
            return PaperOrderResult(False, "REJECTED", "Selling is disabled")
        if side.upper() not in {"BUY", "SELL"}:
            return PaperOrderResult(False, "REJECTED", "Unknown side")
        if price <= 0:
            return PaperOrderResult(False, "REJECTED", "Price must be positive")
        if volume <= 0:
            return PaperOrderResult(False, "REJECTED", "Volume must be positive")
        if len(state.open_positions) >= config.max_open_positions:
            return PaperOrderResult(False, "REJECTED", "Maximum open positions reached")

        position = PaperPosition(
            position_id=str(uuid4()),
            symbol=symbol,
            side=side.upper(),
            entry_price=float(price),
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume=float(volume),
            status="OPEN",
            reason=reason,
        )
        state.open_positions.append(position)
        return PaperOrderResult(True, "OPENED", "Order accepted", position)

    def close_position(
        self,
        state: PaperBrokerState,
        position_id: str,
        exit_price: float,
        reason: str = "",
    ) -> PaperOrderResult:
        """Close an existing position and update the simulated balance."""
        if exit_price <= 0:
            return PaperOrderResult(False, "REJECTED", "Exit price must be positive")

        for index, position in enumerate(state.open_positions):
            if position.position_id == position_id:
                if position.side == "BUY":
                    pnl = (exit_price - position.entry_price) * position.volume
                elif position.side == "SELL":
                    pnl = (position.entry_price - exit_price) * position.volume
                else:
                    pnl = 0.0

                state.balance += pnl
                position.status = "CLOSED"
                position.reason = reason or position.reason
                state.open_positions.pop(index)
                state.closed_positions.append(position)
                return PaperOrderResult(True, "CLOSED", "Position closed", position)

        return PaperOrderResult(False, "REJECTED", "Position not found")

    def get_open_positions(self, state: PaperBrokerState) -> List[PaperPosition]:
        """Return only currently open paper positions."""
        return [position for position in state.open_positions if position.status == "OPEN"]

    def get_balance(self, state: PaperBrokerState) -> float:
        """Return the current simulated balance."""
        return float(state.balance)
