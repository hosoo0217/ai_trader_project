"""SMC Break of Structure (BOS) and CHOCH analyzer (v1).

This module uses swing levels from market structure analysis and checks whether
price breaks those levels. It is for research/backtesting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from smc.market_structure import MarketStructureResult, SwingPoint


@dataclass
class StructureBreak:
    """A detected structure break event."""

    index: int
    time: object | None
    price: float
    break_type: str
    direction: str
    broken_level: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class BOSCHOCHConfig:
    """Configuration for BOS/CHOCH detection."""

    require_close_break: bool = True
    buffer: float = 0.0


@dataclass
class BOSCHOCHResult:
    """Result of BOS/CHOCH analysis."""

    latest_break: StructureBreak | None = None
    breaks: list[StructureBreak] = field(default_factory=list)
    bias: str = "UNKNOWN"
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class BOSCHOCHAnalyzer:
    """Detect basic BOS and CHOCH from swing highs/lows."""

    def analyze(
        self,
        candles: pd.DataFrame,
        market_structure_result: MarketStructureResult | None,
        config: BOSCHOCHConfig,
    ) -> BOSCHOCHResult:
        """Analyze candles and return detected BOS/CHOCH breaks."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return BOSCHOCHResult(
                bias="UNKNOWN",
                reasons=["No candle data provided"],
                blocking_reasons=["No candle data provided"],
            )

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return BOSCHOCHResult(
                bias="UNKNOWN",
                reasons=["Missing required OHLC columns"],
                blocking_reasons=["Missing required OHLC columns"],
            )

        if market_structure_result is None:
            return BOSCHOCHResult(
                bias="UNKNOWN",
                reasons=["Missing market structure result"],
                blocking_reasons=["Missing market structure result"],
            )

        if market_structure_result.last_swing_high is None or market_structure_result.last_swing_low is None:
            return BOSCHOCHResult(
                bias="UNKNOWN",
                reasons=["Missing swing highs or swing lows"],
                blocking_reasons=["Market structure result has no usable swing levels"],
            )

        if not market_structure_result.swing_highs or not market_structure_result.swing_lows:
            return BOSCHOCHResult(
                bias="UNKNOWN",
                reasons=["Missing swing lists in market structure"],
                blocking_reasons=["Market structure result has no swing lists"],
            )

        close_values = pd.to_numeric(candles["close"], errors="coerce")
        high_values = pd.to_numeric(candles["high"], errors="coerce")
        low_values = pd.to_numeric(candles["low"], errors="coerce")
        if close_values.isna().all() or high_values.isna().all() or low_values.isna().all():
            return BOSCHOCHResult(
                bias="UNKNOWN",
                reasons=["OHLC values are invalid"],
                blocking_reasons=["OHLC values are invalid"],
            )

        effective_buffer = max(0.0, float(config.buffer))
        last_swing_high = market_structure_result.last_swing_high
        last_swing_low = market_structure_result.last_swing_low

        breaks: list[StructureBreak] = []
        current_bias = str(market_structure_result.structure_bias or "UNKNOWN").upper()

        for index in range(len(candles)):
            bullish_break = self._is_bullish_break(
                index,
                last_swing_high,
                close_values,
                high_values,
                config,
                effective_buffer,
            )
            if bullish_break:
                break_price = float(close_values.iloc[index]) if config.require_close_break else float(high_values.iloc[index])
                break_type = "BOS" if current_bias == "BULLISH" else "CHOCH"
                breaks.append(
                    StructureBreak(
                        index=index,
                        time=candles["time"].iloc[index],
                        price=break_price,
                        break_type=break_type,
                        direction="BULLISH",
                        broken_level=float(last_swing_high.price),
                        reasons=[
                            f"Price broke above swing high {last_swing_high.price:.4f}",
                            f"Break confirmed by {'close' if config.require_close_break else 'wick'}",
                        ],
                    )
                )
                current_bias = "BULLISH"

            bearish_break = self._is_bearish_break(
                index,
                last_swing_low,
                close_values,
                low_values,
                config,
                effective_buffer,
            )
            if bearish_break:
                break_price = float(close_values.iloc[index]) if config.require_close_break else float(low_values.iloc[index])
                break_type = "BOS" if current_bias == "BEARISH" else "CHOCH"
                breaks.append(
                    StructureBreak(
                        index=index,
                        time=candles["time"].iloc[index],
                        price=break_price,
                        break_type=break_type,
                        direction="BEARISH",
                        broken_level=float(last_swing_low.price),
                        reasons=[
                            f"Price broke below swing low {last_swing_low.price:.4f}",
                            f"Break confirmed by {'close' if config.require_close_break else 'wick'}",
                        ],
                    )
                )
                current_bias = "BEARISH"

        if not breaks:
            return BOSCHOCHResult(
                latest_break=None,
                breaks=[],
                bias="NEUTRAL",
                reasons=["No BOS or CHOCH break found"],
                blocking_reasons=[],
            )

        latest_break = breaks[-1]
        return BOSCHOCHResult(
            latest_break=latest_break,
            breaks=breaks,
            bias=latest_break.direction,
            reasons=[f"Detected {len(breaks)} structure break(s)", f"Latest break type: {latest_break.break_type}"],
            blocking_reasons=[],
        )

    def explain(self, result: BOSCHOCHResult) -> str:
        """Return a readable summary of BOS/CHOCH analysis."""
        if result.latest_break is None:
            reasons_text = "; ".join(result.reasons) if result.reasons else "None"
            blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
            return (
                f"SMC BOS/CHOCH: {result.bias} | breaks: 0 | "
                f"reasons: {reasons_text} | blocking reasons: {blocks_text}"
            )

        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        latest_reasons = "; ".join(result.latest_break.reasons) if result.latest_break.reasons else "None"
        return (
            f"SMC BOS/CHOCH: {result.bias} | breaks: {len(result.breaks)} | "
            f"latest: {result.latest_break.break_type} {result.latest_break.direction} at {result.latest_break.price:.4f} | "
            f"latest reasons: {latest_reasons} | reasons: {reasons_text}"
        )

    def _is_bullish_break(
        self,
        index: int,
        last_swing_high: SwingPoint,
        close_values: pd.Series,
        high_values: pd.Series,
        config: BOSCHOCHConfig,
        buffer_value: float,
    ) -> bool:
        """Check bullish break condition against last swing high."""
        if index <= int(last_swing_high.index):
            return False

        break_level = float(last_swing_high.price) + buffer_value
        if config.require_close_break:
            close_value = close_values.iloc[index]
            if pd.isna(close_value):
                return False
            return bool(float(close_value) > break_level)

        high_value = high_values.iloc[index]
        if pd.isna(high_value):
            return False
        return bool(float(high_value) > break_level)

    def _is_bearish_break(
        self,
        index: int,
        last_swing_low: SwingPoint,
        close_values: pd.Series,
        low_values: pd.Series,
        config: BOSCHOCHConfig,
        buffer_value: float,
    ) -> bool:
        """Check bearish break condition against last swing low."""
        if index <= int(last_swing_low.index):
            return False

        break_level = float(last_swing_low.price) - buffer_value
        if config.require_close_break:
            close_value = close_values.iloc[index]
            if pd.isna(close_value):
                return False
            return bool(float(close_value) < break_level)

        low_value = low_values.iloc[index]
        if pd.isna(low_value):
            return False
        return bool(float(low_value) < break_level)
