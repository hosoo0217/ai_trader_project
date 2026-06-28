"""Sierra Chart footprint CSV importer for research and backtesting.

This module only loads historical CSV files from disk and maps rows into
FootprintCandle objects. It does not connect to Sierra Chart live feeds,
brokers, or exchanges.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from orderflow.footprint import FootprintCandle, FootprintLevel


@dataclass
class SierraChartImportConfig:
    """Column mapping for Sierra Chart-style footprint CSV exports."""

    time_column: str = "time"
    open_column: str = "open"
    high_column: str = "high"
    low_column: str = "low"
    close_column: str = "close"
    price_column: str = "price"
    bid_volume_column: str = "bid_volume"
    ask_volume_column: str = "ask_volume"


class SierraChartImporter:
    """Convert CSV/DataFrame rows into FootprintCandle objects."""

    def load_csv(self, path: str, config: SierraChartImportConfig) -> list[FootprintCandle]:
        """Load a footprint CSV file and map rows into footprint candles safely."""
        try:
            dataframe = pd.read_csv(path)
        except Exception:
            return []
        return self.from_dataframe(dataframe, config)

    def from_dataframe(self, dataframe: pd.DataFrame, config: SierraChartImportConfig) -> list[FootprintCandle]:
        """Convert a DataFrame with Sierra Chart-style columns into candles."""
        if dataframe is None or not isinstance(dataframe, pd.DataFrame):
            return []
        if dataframe.empty:
            return []

        required_columns = [
            config.time_column,
            config.open_column,
            config.high_column,
            config.low_column,
            config.close_column,
            config.price_column,
            config.bid_volume_column,
            config.ask_volume_column,
        ]
        if not set(required_columns).issubset(dataframe.columns):
            return []

        candles: list[FootprintCandle] = []

        grouped = dataframe.groupby(config.time_column, sort=False, dropna=False)
        for group_time, group in grouped:
            open_values = pd.to_numeric(group[config.open_column], errors="coerce")
            high_values = pd.to_numeric(group[config.high_column], errors="coerce")
            low_values = pd.to_numeric(group[config.low_column], errors="coerce")
            close_values = pd.to_numeric(group[config.close_column], errors="coerce")

            first_open = self._first_valid(open_values)
            max_high = self._safe_max(high_values)
            min_low = self._safe_min(low_values)
            last_close = self._last_valid(close_values)
            if first_open is None or max_high is None or min_low is None or last_close is None:
                # Skip malformed candle groups rather than crashing import.
                continue

            price_values = pd.to_numeric(group[config.price_column], errors="coerce")
            bid_values = pd.to_numeric(group[config.bid_volume_column], errors="coerce")
            ask_values = pd.to_numeric(group[config.ask_volume_column], errors="coerce")

            levels: list[FootprintLevel] = []
            for index in range(len(group)):
                price = price_values.iloc[index]
                if pd.isna(price):
                    continue

                bid_raw = bid_values.iloc[index]
                ask_raw = ask_values.iloc[index]
                bid = 0.0 if pd.isna(bid_raw) else max(0.0, float(bid_raw))
                ask = 0.0 if pd.isna(ask_raw) else max(0.0, float(ask_raw))

                levels.append(
                    FootprintLevel(
                        price=float(price),
                        bid_volume=bid,
                        ask_volume=ask,
                    )
                )

            candles.append(
                FootprintCandle(
                    time=group_time,
                    open=float(first_open),
                    high=float(max_high),
                    low=float(min_low),
                    close=float(last_close),
                    levels=levels,
                )
            )

        return candles

    def explain_import(self, candles: list[FootprintCandle]) -> str:
        """Return a readable summary of imported footprint candles."""
        if not candles:
            return "Sierra footprint import: no candles imported."

        total_levels = sum(len(candle.levels) for candle in candles)
        first_time = candles[0].time
        last_time = candles[-1].time
        return (
            "Sierra footprint import: "
            f"candles={len(candles)}, "
            f"levels={total_levels}, "
            f"time_range={first_time} -> {last_time}."
        )

    def _first_valid(self, values: pd.Series) -> float | None:
        """Return first valid numeric value from a series."""
        valid = values.dropna()
        if valid.empty:
            return None
        return float(valid.iloc[0])

    def _last_valid(self, values: pd.Series) -> float | None:
        """Return last valid numeric value from a series."""
        valid = values.dropna()
        if valid.empty:
            return None
        return float(valid.iloc[-1])

    def _safe_max(self, values: pd.Series) -> float | None:
        """Return max numeric value when available."""
        valid = values.dropna()
        if valid.empty:
            return None
        return float(valid.max())

    def _safe_min(self, values: pd.Series) -> float | None:
        """Return min numeric value when available."""
        valid = values.dropna()
        if valid.empty:
            return None
        return float(valid.min())
