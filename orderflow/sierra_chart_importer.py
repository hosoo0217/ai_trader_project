"""Sierra Chart footprint CSV importer for research and backtesting.

This module only loads historical CSV files from disk and maps rows into
FootprintCandle objects. It does not connect to Sierra Chart live feeds,
brokers, or exchanges.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from orderflow.footprint import FootprintCandle, FootprintLevel


@dataclass
class SierraChartImportConfig:
    """Column mapping for Sierra Chart-style footprint CSV exports."""

    date_column: str = "Date"
    time_column: str = "time"
    open_column: str = "open"
    high_column: str = "high"
    low_column: str = "low"
    close_column: str = "close"
    volume_column: str = "Volume"
    delta_column: str = "Delta"
    price_column: str = "price"
    bid_volume_column: str = "bid_volume"
    ask_volume_column: str = "ask_volume"
    date_aliases: list[str] = field(default_factory=lambda: ["date", "Date"])
    time_aliases: list[str] = field(default_factory=lambda: ["time", "datetime", "date_time", "timestamp", "Date Time", "DateTime"])
    open_aliases: list[str] = field(default_factory=lambda: ["open", "Open"])
    high_aliases: list[str] = field(default_factory=lambda: ["high", "High"])
    low_aliases: list[str] = field(default_factory=lambda: ["low", "Low"])
    close_aliases: list[str] = field(default_factory=lambda: ["close", "Close", "last", "Last"])
    volume_aliases: list[str] = field(default_factory=lambda: ["volume", "Volume"])
    delta_aliases: list[str] = field(default_factory=lambda: ["delta", "Delta"])
    price_aliases: list[str] = field(default_factory=lambda: ["price", "Price", "level", "Level"])
    bid_volume_aliases: list[str] = field(
        default_factory=lambda: ["bid_volume", "Bid Volume", "BidVolume", "bid", "Bid", "bid_vol"]
    )
    ask_volume_aliases: list[str] = field(
        default_factory=lambda: ["ask_volume", "Ask Volume", "AskVolume", "ask", "Ask", "ask_vol"]
    )


def normalize_column_name(name: object) -> str:
    """Normalize headers by ignoring case, spaces, and underscores."""
    base_name = str(name).strip()
    if "." in base_name:
        prefix, suffix = base_name.rsplit(".", 1)
        if suffix.isdigit():
            base_name = prefix
    return base_name.lower().replace(" ", "").replace("_", "")


def resolve_column(dataframe_columns: object, aliases: list[str]) -> str | None:
    """Find the first DataFrame column matching one of the aliases safely."""
    try:
        columns = list(dataframe_columns)
    except TypeError:
        return None

    for alias in aliases:
        normalized_alias = normalize_column_name(alias)
        for column in columns:
            if normalize_column_name(column) == normalized_alias:
                return str(column)
    return None


def build_resolved_column_map(dataframe: pd.DataFrame, config: SierraChartImportConfig) -> dict[str, str]:
    """Resolve DataFrame columns into the normalized footprint field names."""
    if dataframe is None or not isinstance(dataframe, pd.DataFrame):
        return {}

    alias_map = {
        "date": [config.date_column, *config.date_aliases],
        "time": [config.time_column, *config.time_aliases],
        "open": [config.open_column, *config.open_aliases],
        "high": [config.high_column, *config.high_aliases],
        "low": [config.low_column, *config.low_aliases],
        "close": [config.close_column, *config.close_aliases],
        "volume": [config.volume_column, *config.volume_aliases],
        "delta": [config.delta_column, *config.delta_aliases],
        "price": [config.price_column, *config.price_aliases],
        "bid_volume": [config.bid_volume_column, *config.bid_volume_aliases],
        "ask_volume": [config.ask_volume_column, *config.ask_volume_aliases],
    }

    resolved: dict[str, str] = {}
    for field_name, aliases in alias_map.items():
        column = resolve_column(dataframe.columns, aliases)
        if column is not None:
            resolved[field_name] = column
    return resolved


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

        column_map = build_resolved_column_map(dataframe, config)
        if self._is_bar_summary_column_map(column_map):
            return self._from_bar_summary_dataframe(dataframe, column_map)

        required_fields = {"time", "open", "high", "low", "close", "price", "bid_volume", "ask_volume"}
        if not required_fields.issubset(column_map):
            return []

        candles: list[FootprintCandle] = []

        grouped = dataframe.groupby(column_map["time"], sort=False, dropna=False)
        for group_time, group in grouped:
            open_values = pd.to_numeric(self._series_from_column(group, column_map["open"]), errors="coerce")
            high_values = pd.to_numeric(self._series_from_column(group, column_map["high"]), errors="coerce")
            low_values = pd.to_numeric(self._series_from_column(group, column_map["low"]), errors="coerce")
            close_values = pd.to_numeric(self._series_from_column(group, column_map["close"]), errors="coerce")

            first_open = self._first_valid(open_values)
            max_high = self._safe_max(high_values)
            min_low = self._safe_min(low_values)
            last_close = self._last_valid(close_values)
            if first_open is None or max_high is None or min_low is None or last_close is None:
                # Skip malformed candle groups rather than crashing import.
                continue

            price_values = pd.to_numeric(self._series_from_column(group, column_map["price"]), errors="coerce")
            bid_values = pd.to_numeric(self._series_from_column(group, column_map["bid_volume"]), errors="coerce")
            ask_values = pd.to_numeric(self._series_from_column(group, column_map["ask_volume"]), errors="coerce")

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
        source_formats = {str(getattr(candle, "source_format", "PRICE_LEVEL_FOOTPRINT")) for candle in candles}
        source_text = "BAR_SUMMARY" if source_formats == {"BAR_SUMMARY"} else "PRICE_LEVEL_FOOTPRINT"
        note = ""
        if "BAR_SUMMARY" in source_formats:
            note = " BAR_SUMMARY uses one synthetic close-price level per bar; it is not full price-level footprint data."
        return (
            "Sierra footprint import: "
            f"source={source_text}, "
            f"candles={len(candles)}, "
            f"levels={total_levels}, "
            f"time_range={first_time} -> {last_time}."
            f"{note}"
        )

    def _is_bar_summary_column_map(self, column_map: dict[str, str]) -> bool:
        """Return True for Sierra Chart bar/study summary exports."""
        required_fields = {"date", "time", "open", "high", "low", "close", "bid_volume", "ask_volume"}
        return required_fields.issubset(column_map) and "price" not in column_map

    def _from_bar_summary_dataframe(
        self,
        dataframe: pd.DataFrame,
        column_map: dict[str, str],
    ) -> list[FootprintCandle]:
        """Convert Sierra bar summary rows into synthetic one-level candles."""
        candles: list[FootprintCandle] = []

        open_values = pd.to_numeric(self._series_from_column(dataframe, column_map["open"]), errors="coerce")
        high_values = pd.to_numeric(self._series_from_column(dataframe, column_map["high"]), errors="coerce")
        low_values = pd.to_numeric(self._series_from_column(dataframe, column_map["low"]), errors="coerce")
        close_values = pd.to_numeric(self._series_from_column(dataframe, column_map["close"]), errors="coerce")
        bid_values = pd.to_numeric(self._series_from_column(dataframe, column_map["bid_volume"]), errors="coerce")
        ask_values = pd.to_numeric(self._series_from_column(dataframe, column_map["ask_volume"]), errors="coerce")
        date_values = self._series_from_column(dataframe, column_map["date"])
        time_values = self._series_from_column(dataframe, column_map["time"])
        volume_values = (
            pd.to_numeric(self._series_from_column(dataframe, column_map["volume"]), errors="coerce")
            if "volume" in column_map
            else None
        )
        delta_values = (
            pd.to_numeric(self._series_from_column(dataframe, column_map["delta"]), errors="coerce")
            if "delta" in column_map
            else None
        )

        for index in range(len(dataframe)):
            open_price = open_values.iloc[index]
            high_price = high_values.iloc[index]
            low_price = low_values.iloc[index]
            close_price = close_values.iloc[index]
            if any(pd.isna(value) for value in [open_price, high_price, low_price, close_price]):
                continue

            bid_raw = bid_values.iloc[index]
            ask_raw = ask_values.iloc[index]
            bid = 0.0 if pd.isna(bid_raw) else max(0.0, float(bid_raw))
            ask = 0.0 if pd.isna(ask_raw) else max(0.0, float(ask_raw))
            reported_volume = self._optional_float(volume_values.iloc[index]) if volume_values is not None else None
            reported_delta = self._optional_float(delta_values.iloc[index]) if delta_values is not None else None

            candles.append(
                FootprintCandle(
                    time=self._join_date_time(date_values.iloc[index], time_values.iloc[index]),
                    open=float(open_price),
                    high=float(high_price),
                    low=float(low_price),
                    close=float(close_price),
                    levels=[
                        FootprintLevel(
                            price=float(close_price),
                            bid_volume=bid,
                            ask_volume=ask,
                        )
                    ],
                    source_format="BAR_SUMMARY",
                    source_note=(
                        "Sierra Chart bar summary export: one synthetic close-price level was created; "
                        "this is not full price-level footprint data."
                    ),
                    reported_volume=reported_volume,
                    reported_delta=reported_delta,
                )
            )

        return candles

    def _series_from_column(self, dataframe: pd.DataFrame, column: str) -> pd.Series:
        """Return a Series for a column, using the first duplicate safely."""
        values = dataframe[column]
        if isinstance(values, pd.DataFrame):
            return values.iloc[:, 0]
        return values

    def _join_date_time(self, date_value: object, time_value: object) -> str:
        """Join Sierra Date and Time fields into a stable timestamp string."""
        date_text = "" if pd.isna(date_value) else str(date_value).strip()
        time_text = "" if pd.isna(time_value) else str(time_value).strip()
        return f"{date_text} {time_text}".strip()

    def _optional_float(self, value: object) -> float | None:
        """Convert optional numeric metadata safely."""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

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
