"""Simple candle-based exit simulation for paper trades.

This module evaluates whether an open paper position should be closed by a
stop loss, take profit, or the final candle. It is research-only and never
connects to a live broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

from broker.paper_broker import PaperPosition


@dataclass
class ExitSimulationConfig:
    """Configuration for simple exit simulation rules."""

    conservative_same_candle: bool = True
    close_at_final_candle: bool = False


@dataclass
class ExitSimulationResult:
    """Outcome of a single exit simulation."""

    exited: bool
    exit_reason: str
    exit_price: Optional[float]
    pnl: Optional[float]
    candle_index: Optional[int]
    reasons: List[str] = field(default_factory=list)


class ExitSimulator:
    """Evaluate whether a paper position should exit based on OHLC candles."""

    def simulate_exit(
        self,
        position: Optional[PaperPosition],
        candles: Optional[pd.DataFrame],
        config: ExitSimulationConfig,
        point_value: float = 1.0,
    ) -> ExitSimulationResult:
        """Check a position against candle data and return a simple exit result."""
        if position is None:
            return ExitSimulationResult(False, "INVALID_POSITION", None, None, None, ["No position provided"])

        if not self._is_valid_position(position):
            return ExitSimulationResult(False, "INVALID_POSITION", None, None, None, ["Position is invalid"])

        if candles is None or not isinstance(candles, pd.DataFrame):
            return ExitSimulationResult(False, "INVALID_CANDLES", None, None, None, ["No candle data provided"])

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return ExitSimulationResult(False, "INVALID_CANDLES", None, None, None, ["Missing required candle columns"])

        if candles.empty:
            return ExitSimulationResult(False, "INVALID_CANDLES", None, None, None, ["No candles available"])

        if not position.stop_loss and not position.take_profit:
            if config.close_at_final_candle:
                last_close = float(candles["close"].iloc[-1])
                return ExitSimulationResult(True, "FINAL_CANDLE", last_close, self._calculate_pnl(position, last_close, point_value), len(candles) - 1, ["Closed at final candle"])
            return ExitSimulationResult(False, "STILL_OPEN", None, None, None, ["No stop loss or take profit set"])

        for index, row in candles.iterrows():
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])

            if position.side == "BUY":
                stop_hit = low <= (position.stop_loss or float("inf"))
                take_hit = high >= (position.take_profit or float("inf"))
            elif position.side == "SELL":
                stop_hit = high >= (position.stop_loss or float("inf"))
                take_hit = low <= (position.take_profit or float("inf"))
            else:
                return ExitSimulationResult(False, "INVALID_POSITION", None, None, None, ["Unknown position side"])

            if stop_hit and take_hit:
                if config.conservative_same_candle:
                    exit_price = self._stop_loss_price(position)
                    exit_reason = "STOP_LOSS"
                else:
                    exit_price = self._take_profit_price(position)
                    exit_reason = "TAKE_PROFIT"
            elif stop_hit:
                exit_price = self._stop_loss_price(position)
                exit_reason = "STOP_LOSS"
            elif take_hit:
                exit_price = self._take_profit_price(position)
                exit_reason = "TAKE_PROFIT"
            else:
                continue

            pnl = self._calculate_pnl(position, exit_price, point_value)
            return ExitSimulationResult(True, exit_reason, exit_price, pnl, index, [f"Exited at candle {index}"])

        if config.close_at_final_candle:
            last_close = float(candles["close"].iloc[-1])
            return ExitSimulationResult(True, "FINAL_CANDLE", last_close, self._calculate_pnl(position, last_close, point_value), len(candles) - 1, ["Closed at final candle"])

        return ExitSimulationResult(False, "STILL_OPEN", None, None, None, ["No exit condition reached"])

    def explain(self, result: ExitSimulationResult) -> str:
        """Return a readable explanation of an exit simulation result."""
        if result.exit_reason == "INVALID_CANDLES":
            return "Exit simulation: invalid candle data."
        if result.exit_reason == "INVALID_POSITION":
            return "Exit simulation: invalid position."
        if result.exit_reason == "STILL_OPEN":
            return "Exit simulation: position remains open."

        if result.exited:
            return (
                f"Exit simulation: {result.exit_reason} at candle {result.candle_index}. "
                f"Exit price={result.exit_price:.2f}, PnL={result.pnl:.2f}."
            )
        return "Exit simulation: no exit condition was reached."

    def _is_valid_position(self, position: PaperPosition) -> bool:
        """Basic validation for a paper position."""
        return bool(position.position_id and position.side in {"BUY", "SELL"} and position.entry_price > 0 and position.volume > 0)

    def _calculate_pnl(
        self,
        position: PaperPosition,
        exit_price: float,
        point_value: float = 1.0,
    ) -> float:
        """Calculate monetary PnL using price distance, volume, and point value."""
        if position.side == "BUY":
            return (exit_price - position.entry_price) * position.volume * float(point_value)
        if position.side == "SELL":
            return (position.entry_price - exit_price) * position.volume * float(point_value)
        return 0.0

    def _stop_loss_price(self, position: PaperPosition) -> float:
        """Return the stop-loss price for the position."""
        if position.stop_loss is None:
            return float(position.entry_price)
        return float(position.stop_loss)

    def _take_profit_price(self, position: PaperPosition) -> float:
        """Return the take-profit price for the position."""
        if position.take_profit is None:
            return float(position.entry_price)
        return float(position.take_profit)
