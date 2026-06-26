from __future__ import annotations

from typing import List

import pandas as pd


def generate_signals(candles: List[dict]) -> List[dict]:
    """Create simple EMA crossover signals for the candle list.

    Rules:
    - BUY when EMA20 > EMA50
    - SELL when EMA20 < EMA50
    - Otherwise hold
    """
    if not candles:
        return []

    df = pd.DataFrame(candles)
    df = df.sort_values("time").reset_index(drop=True)

    # Calculate EMAs from the close price.
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    signals: List[dict] = []
    for _, row in df.iterrows():
        if row["ema20"] > row["ema50"]:
            action = "buy"
        elif row["ema20"] < row["ema50"]:
            action = "sell"
        else:
            action = "hold"

        signals.append(
            {
                "time": row["time"],
                "close": row["close"],
                "ema20": row["ema20"],
                "ema50": row["ema50"],
                "action": action,
            }
        )

    return signals
