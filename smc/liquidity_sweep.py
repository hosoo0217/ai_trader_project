"""SMC liquidity sweep analyzer (v1).

This module detects simple liquidity sweeps around previous swing highs/lows.
It is for research and backtesting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from smc.market_structure import MarketStructureResult, SwingPoint


@dataclass
class LiquiditySweep:
    """One detected liquidity sweep event."""

    index: int
    time: object | None
    sweep_type: str
    direction: str
    swept_level: float
    sweep_price: float
    close_price: float
    confirmed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class LiquiditySweepConfig:
    """Configuration for liquidity sweep detection."""

    lookback_swings: int = 5
    require_close_back_inside: bool = True
    buffer: float = 0.0


@dataclass
class LiquiditySweepResult:
    """Result of liquidity sweep analysis."""

    latest_sweep: LiquiditySweep | None = None
    sweeps: list[LiquiditySweep] = field(default_factory=list)
    bias: str = "UNKNOWN"
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class LiquiditySweepAnalyzer:
    """Detect high and low liquidity sweeps from market structure swings."""

    def analyze(
        self,
        candles: pd.DataFrame,
        market_structure_result: MarketStructureResult | None,
        config: LiquiditySweepConfig,
    ) -> LiquiditySweepResult:
        """Analyze candles and return detected liquidity sweeps."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return LiquiditySweepResult(
                bias="UNKNOWN",
                reasons=["No candle data provided"],
                blocking_reasons=["No candle data provided"],
            )

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return LiquiditySweepResult(
                bias="UNKNOWN",
                reasons=["Missing required OHLC columns"],
                blocking_reasons=["Missing required OHLC columns"],
            )

        if market_structure_result is None:
            return LiquiditySweepResult(
                bias="UNKNOWN",
                reasons=["Missing market structure result"],
                blocking_reasons=["Missing market structure result"],
            )

        if not market_structure_result.swing_highs or not market_structure_result.swing_lows:
            return LiquiditySweepResult(
                bias="UNKNOWN",
                reasons=["Missing swing highs or swing lows"],
                blocking_reasons=["Market structure result has no usable swing lists"],
            )

        close_values = pd.to_numeric(candles["close"], errors="coerce")
        high_values = pd.to_numeric(candles["high"], errors="coerce")
        low_values = pd.to_numeric(candles["low"], errors="coerce")
        if close_values.isna().all() or high_values.isna().all() or low_values.isna().all():
            return LiquiditySweepResult(
                bias="UNKNOWN",
                reasons=["OHLC values are invalid"],
                blocking_reasons=["OHLC values are invalid"],
            )

        lookback_count = max(1, int(config.lookback_swings))
        recent_high_swings = market_structure_result.swing_highs[-lookback_count:]
        recent_low_swings = market_structure_result.swing_lows[-lookback_count:]
        buffer_value = max(0.0, float(config.buffer))

        sweeps: list[LiquiditySweep] = []

        for index in range(len(candles)):
            candle_high = high_values.iloc[index]
            candle_low = low_values.iloc[index]
            candle_close = close_values.iloc[index]

            if pd.isna(candle_high) or pd.isna(candle_low) or pd.isna(candle_close):
                continue

            for swing_high in recent_high_swings:
                if index <= int(swing_high.index):
                    continue

                high_break = float(candle_high) > (float(swing_high.price) + buffer_value)
                if not high_break:
                    continue

                close_back_inside = float(candle_close) < float(swing_high.price)
                confirmed = close_back_inside if config.require_close_back_inside else True

                if not confirmed:
                    continue

                sweep = LiquiditySweep(
                    index=index,
                    time=candles["time"].iloc[index],
                    sweep_type="HIGH_SWEEP",
                    direction="BEARISH",
                    swept_level=float(swing_high.price),
                    sweep_price=float(candle_high),
                    close_price=float(candle_close),
                    confirmed=confirmed,
                    reasons=[
                        f"Candle high swept swing high {float(swing_high.price):.4f}",
                        (
                            "Close returned below swept high"
                            if config.require_close_back_inside
                            else "Wick sweep accepted without close-back-inside"
                        ),
                    ],
                )
                sweeps.append(sweep)

            for swing_low in recent_low_swings:
                if index <= int(swing_low.index):
                    continue

                low_break = float(candle_low) < (float(swing_low.price) - buffer_value)
                if not low_break:
                    continue

                close_back_inside = float(candle_close) > float(swing_low.price)
                confirmed = close_back_inside if config.require_close_back_inside else True

                if not confirmed:
                    continue

                sweep = LiquiditySweep(
                    index=index,
                    time=candles["time"].iloc[index],
                    sweep_type="LOW_SWEEP",
                    direction="BULLISH",
                    swept_level=float(swing_low.price),
                    sweep_price=float(candle_low),
                    close_price=float(candle_close),
                    confirmed=confirmed,
                    reasons=[
                        f"Candle low swept swing low {float(swing_low.price):.4f}",
                        (
                            "Close returned above swept low"
                            if config.require_close_back_inside
                            else "Wick sweep accepted without close-back-inside"
                        ),
                    ],
                )
                sweeps.append(sweep)

        if not sweeps:
            return LiquiditySweepResult(
                latest_sweep=None,
                sweeps=[],
                bias="NEUTRAL",
                reasons=["No liquidity sweep found"],
                blocking_reasons=[],
            )

        latest_sweep = sweeps[-1]
        return LiquiditySweepResult(
            latest_sweep=latest_sweep,
            sweeps=sweeps,
            bias=latest_sweep.direction,
            reasons=[f"Detected {len(sweeps)} liquidity sweep(s)"],
            blocking_reasons=[],
        )

    def explain(self, result: LiquiditySweepResult) -> str:
        """Return a readable summary of liquidity sweep analysis."""
        if result.latest_sweep is None:
            reasons_text = "; ".join(result.reasons) if result.reasons else "None"
            blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
            return (
                f"SMC liquidity sweep: {result.bias} | sweeps: 0 | "
                f"reasons: {reasons_text} | blocking reasons: {blocks_text}"
            )

        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        latest_reasons = "; ".join(result.latest_sweep.reasons) if result.latest_sweep.reasons else "None"
        return (
            f"SMC liquidity sweep: {result.bias} | sweeps: {len(result.sweeps)} | "
            f"latest: {result.latest_sweep.sweep_type} {result.latest_sweep.direction} at {result.latest_sweep.sweep_price:.4f} | "
            f"latest reasons: {latest_reasons} | reasons: {reasons_text}"
        )
