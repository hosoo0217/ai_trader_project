"""Order flow imbalance analyzer for research and backtesting.

This module analyzes FootprintCandle price levels to detect ask/bid imbalances.
It is offline research logic and does not connect to live systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow.footprint import FootprintCandle


@dataclass
class ImbalanceConfig:
    """Configuration for imbalance detection thresholds."""

    imbalance_ratio_threshold: float = 3.0
    min_volume: float = 10.0


@dataclass
class ImbalanceLevel:
    """Detected imbalance at one price level."""

    price: float
    imbalance_type: str
    bid_volume: float
    ask_volume: float
    ratio: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class ImbalanceResult:
    """Output of imbalance analysis for one footprint candle."""

    imbalances: list[ImbalanceLevel] = field(default_factory=list)
    ask_imbalances: int = 0
    bid_imbalances: int = 0
    bias: str = "UNKNOWN"
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class ImbalanceAnalyzer:
    """Detect ask-side and bid-side volume imbalances."""

    def analyze(self, candle: FootprintCandle | None, config: ImbalanceConfig) -> ImbalanceResult:
        """Analyze one footprint candle and return imbalance summary."""
        if candle is None:
            return ImbalanceResult(
                imbalances=[],
                ask_imbalances=0,
                bid_imbalances=0,
                bias="UNKNOWN",
                reasons=["No footprint candle provided"],
                blocking_reasons=["No footprint candle provided"],
            )

        levels = getattr(candle, "levels", None)
        if levels is None or len(levels) == 0:
            return ImbalanceResult(
                imbalances=[],
                ask_imbalances=0,
                bid_imbalances=0,
                bias="UNKNOWN",
                reasons=["No footprint levels available"],
                blocking_reasons=["No footprint levels available"],
            )

        ratio_threshold = max(1.0, float(config.imbalance_ratio_threshold))
        min_volume = max(0.0, float(config.min_volume))
        imbalance_levels: list[ImbalanceLevel] = []
        ask_count = 0
        bid_count = 0

        for level in levels:
            if level is None:
                continue

            price_value = self._safe_float(getattr(level, "price", 0.0), default=0.0)
            bid_volume = self._safe_volume(getattr(level, "bid_volume", 0.0))
            ask_volume = self._safe_volume(getattr(level, "ask_volume", 0.0))
            total_volume = bid_volume + ask_volume

            if total_volume < min_volume or total_volume <= 0.0:
                continue

            ask_condition = False
            bid_condition = False
            ask_ratio = 0.0
            bid_ratio = 0.0
            ask_reasons: list[str] = []
            bid_reasons: list[str] = []

            if bid_volume == 0.0 and ask_volume >= min_volume:
                ask_condition = True
                ask_ratio = float("inf")
                ask_reasons.append("Bid volume is zero with strong ask volume")
            elif bid_volume > 0.0:
                ask_ratio = ask_volume / bid_volume
                if ask_ratio >= ratio_threshold:
                    ask_condition = True
                    ask_reasons.append(
                        f"Ask/Bid ratio {ask_ratio:.2f} is above threshold {ratio_threshold:.2f}"
                    )

            if ask_volume == 0.0 and bid_volume >= min_volume:
                bid_condition = True
                bid_ratio = float("inf")
                bid_reasons.append("Ask volume is zero with strong bid volume")
            elif ask_volume > 0.0:
                bid_ratio = bid_volume / ask_volume
                if bid_ratio >= ratio_threshold:
                    bid_condition = True
                    bid_reasons.append(
                        f"Bid/Ask ratio {bid_ratio:.2f} is above threshold {ratio_threshold:.2f}"
                    )

            if ask_condition and (not bid_condition or ask_ratio >= bid_ratio):
                ask_count += 1
                imbalance_levels.append(
                    ImbalanceLevel(
                        price=price_value,
                        imbalance_type="ASK_IMBALANCE",
                        bid_volume=bid_volume,
                        ask_volume=ask_volume,
                        ratio=ask_ratio,
                        reasons=ask_reasons or ["Ask-side imbalance detected"],
                    )
                )
            elif bid_condition:
                bid_count += 1
                imbalance_levels.append(
                    ImbalanceLevel(
                        price=price_value,
                        imbalance_type="BID_IMBALANCE",
                        bid_volume=bid_volume,
                        ask_volume=ask_volume,
                        ratio=bid_ratio,
                        reasons=bid_reasons or ["Bid-side imbalance detected"],
                    )
                )

        if ask_count > bid_count:
            bias = "BULLISH"
            reasons = ["More ask imbalances than bid imbalances"]
        elif bid_count > ask_count:
            bias = "BEARISH"
            reasons = ["More bid imbalances than ask imbalances"]
        else:
            bias = "NEUTRAL"
            reasons = ["Ask and bid imbalance counts are equal"]

        reasons.append(f"Detected ask imbalances: {ask_count}")
        reasons.append(f"Detected bid imbalances: {bid_count}")

        return ImbalanceResult(
            imbalances=imbalance_levels,
            ask_imbalances=ask_count,
            bid_imbalances=bid_count,
            bias=bias,
            reasons=reasons,
            blocking_reasons=[],
        )

    def explain(self, result: ImbalanceResult) -> str:
        """Return a readable imbalance analysis summary."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Order flow imbalance summary: "
            f"bias={result.bias}, "
            f"ask_imbalances={result.ask_imbalances}, "
            f"bid_imbalances={result.bid_imbalances}, "
            f"levels={len(result.imbalances)}, "
            f"reasons={reasons_text}, "
            f"blocking_reasons={blocks_text}."
        )

    def _safe_float(self, value: object, default: float = 0.0) -> float:
        """Safely convert a value to float."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def _safe_volume(self, value: object) -> float:
        """Convert invalid/negative volume into zero safely."""
        safe = self._safe_float(value, default=0.0)
        return max(0.0, safe)
