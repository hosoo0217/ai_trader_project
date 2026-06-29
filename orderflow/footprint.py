"""Footprint data models for research and backtesting.

These classes only describe and summarize historical bid/ask volume data.
They do not connect to live feeds, brokers, Sierra Chart, or any exchange.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


def _safe_volume(volume: float) -> float:
    """Convert invalid negative volume into zero for safe calculations."""
    return max(0.0, float(volume))


@dataclass
class FootprintLevel:
    """Bid and ask volume traded at one price level."""

    price: float
    bid_volume: float
    ask_volume: float

    def delta(self) -> float:
        """Return ask volume minus bid volume."""
        return _safe_volume(self.ask_volume) - _safe_volume(self.bid_volume)

    def total_volume(self) -> float:
        """Return the combined safe bid and ask volume."""
        return _safe_volume(self.bid_volume) + _safe_volume(self.ask_volume)

    def imbalance_ratio(self) -> float:
        """Return ask volume divided by bid volume.

        A value above 1.0 means ask volume is larger than bid volume.
        If bid volume is zero and ask volume exists, the ratio is infinite.
        """
        bid_volume = _safe_volume(self.bid_volume)
        ask_volume = _safe_volume(self.ask_volume)
        if bid_volume == 0.0:
            return float("inf") if ask_volume > 0.0 else 0.0
        return ask_volume / bid_volume


@dataclass
class FootprintCandle:
    """OHLC candle enriched with bid/ask volume at each price level."""

    time: object | None
    open: float
    high: float
    low: float
    close: float
    levels: list[FootprintLevel] = field(default_factory=list)
    source_format: str = "PRICE_LEVEL_FOOTPRINT"
    source_note: str | None = None
    reported_volume: float | None = None
    reported_delta: float | None = None

    def total_bid_volume(self) -> float:
        """Return total safe bid volume across all price levels."""
        return sum(_safe_volume(level.bid_volume) for level in self.levels)

    def total_ask_volume(self) -> float:
        """Return total safe ask volume across all price levels."""
        return sum(_safe_volume(level.ask_volume) for level in self.levels)

    def total_volume(self) -> float:
        """Return total safe bid plus ask volume across the candle."""
        return self.total_bid_volume() + self.total_ask_volume()

    def delta(self) -> float:
        """Return candle-level ask volume minus bid volume."""
        return self.total_ask_volume() - self.total_bid_volume()

    def is_buy_delta(self) -> bool:
        """Return True when aggressive buy-side volume is larger."""
        return self.delta() > 0.0

    def is_sell_delta(self) -> bool:
        """Return True when aggressive sell-side volume is larger."""
        return self.delta() < 0.0


@dataclass
class FootprintSummary:
    """Summary of one footprint candle."""

    total_bid_volume: float
    total_ask_volume: float
    total_volume: float
    delta: float
    max_bid_level: Optional[float]
    max_ask_level: Optional[float]
    point_of_control: Optional[float]
    reasons: list[str] = field(default_factory=list)


class FootprintAnalyzer:
    """Create simple summaries from footprint candle data."""

    def summarize(self, candle: FootprintCandle | None) -> FootprintSummary:
        """Summarize one footprint candle safely."""
        if candle is None:
            return FootprintSummary(
                total_bid_volume=0.0,
                total_ask_volume=0.0,
                total_volume=0.0,
                delta=0.0,
                max_bid_level=None,
                max_ask_level=None,
                point_of_control=None,
                reasons=["No footprint candle provided"],
            )

        if not candle.levels:
            return FootprintSummary(
                total_bid_volume=0.0,
                total_ask_volume=0.0,
                total_volume=0.0,
                delta=0.0,
                max_bid_level=None,
                max_ask_level=None,
                point_of_control=None,
                reasons=["No footprint levels available"],
            )

        reasons: list[str] = []
        if any(level.bid_volume < 0.0 or level.ask_volume < 0.0 for level in candle.levels):
            reasons.append("Negative volume was treated as zero")

        max_bid = max(candle.levels, key=lambda level: _safe_volume(level.bid_volume))
        max_ask = max(candle.levels, key=lambda level: _safe_volume(level.ask_volume))
        point_of_control = max(candle.levels, key=lambda level: level.total_volume())
        total_bid_volume = candle.total_bid_volume()
        total_ask_volume = candle.total_ask_volume()
        total_volume = total_bid_volume + total_ask_volume
        delta = total_ask_volume - total_bid_volume

        if delta > 0.0:
            reasons.append("Buy delta: ask volume is greater than bid volume")
        elif delta < 0.0:
            reasons.append("Sell delta: bid volume is greater than ask volume")
        else:
            reasons.append("Neutral delta: bid and ask volume are balanced")

        return FootprintSummary(
            total_bid_volume=total_bid_volume,
            total_ask_volume=total_ask_volume,
            total_volume=total_volume,
            delta=delta,
            max_bid_level=float(max_bid.price),
            max_ask_level=float(max_ask.price),
            point_of_control=float(point_of_control.price),
            reasons=reasons,
        )

    def explain(self, summary: FootprintSummary) -> str:
        """Return a readable footprint summary."""
        if summary.point_of_control is None:
            return "Footprint summary: no price levels available."

        return (
            "Footprint summary: "
            f"total_volume={summary.total_volume:.2f}, "
            f"bid_volume={summary.total_bid_volume:.2f}, "
            f"ask_volume={summary.total_ask_volume:.2f}, "
            f"delta={summary.delta:.2f}, "
            f"POC={summary.point_of_control:.2f}."
        )
