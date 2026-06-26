from __future__ import annotations

from typing import List

from src.risk_manager import RiskManager
from src.strategy import generate_signals


def run_backtest(candles: List[dict]) -> dict:
    """Run a simple backtest over the provided candles.

    This project is intentionally beginner friendly and focuses on a
    backtest-only flow with no live broker integration.
    """
    signals = generate_signals(candles)
    risk_manager = RiskManager(risk_per_trade=0.01)

    equity = 10000.0
    trades = 0
    entry_price = None

    for signal in signals:
        if signal["action"] == "buy" and entry_price is None:
            entry_price = signal["close"]
            stop_loss = entry_price * 0.99
            position_size = risk_manager.position_size(entry_price, stop_loss)
            trades += 1
            equity = equity * (1 + position_size * 0.01)
        elif signal["action"] == "sell" and entry_price is not None:
            exit_price = signal["close"]
            equity = equity * (1 + (exit_price - entry_price) / entry_price * 0.1)
            entry_price = None

    return {
        "trades": trades,
        "final_equity": round(equity, 2),
        "signals": signals,
    }
