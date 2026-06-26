from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd


def load_candles(csv_path: str | Path) -> List[dict]:
    """Load candle data from a CSV file.

    The CSV is expected to contain these columns:
    - time
    - open
    - high
    - low
    - close
    """
    path = Path(csv_path)
    df = pd.read_csv(path)

    # Keep the column names simple and beginner friendly.
    required_columns = {"time", "open", "high", "low", "close"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.loc[:, ["time", "open", "high", "low", "close"]].copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"]).reset_index(drop=True)

    # Convert numeric columns to float values.
    for column in ["open", "high", "low", "close"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)

    return df.to_dict(orient="records")
