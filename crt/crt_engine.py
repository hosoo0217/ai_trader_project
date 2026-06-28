"""Candle Range Theory (CRT) engine v1.

This module detects simple reference-range manipulation and expansion patterns
from OHLC candles for research and backtesting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class CRTRange:
    """Reference candle range used for CRT comparisons."""

    reference_index: int
    reference_time: object | None
    high: float
    low: float
    open: float
    close: float


@dataclass
class CRTSignal:
    """Single CRT signal detected at one candle."""

    index: int
    time: object | None
    signal_type: str
    direction: str
    reference_high: float
    reference_low: float
    sweep_price: float | None
    close_price: float
    confirmed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class CRTConfig:
    """Configuration for CRT reference and confirmation behavior."""

    reference_candle_offset: int = 1
    require_close_back_inside: bool = True
    require_expansion_close: bool = True
    buffer: float = 0.0


@dataclass
class CRTResult:
    """Final result from CRT analysis."""

    bias: str
    latest_signal: CRTSignal | None = None
    signals: list[CRTSignal] = field(default_factory=list)
    reference_range: CRTRange | None = None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class CRTEngine:
    """Detect simple CRT manipulation and expansion context."""

    def analyze(self, candles: pd.DataFrame, config: CRTConfig) -> CRTResult:
        """Analyze OHLC candles and return CRT context."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return CRTResult(
                bias="UNKNOWN",
                reasons=["No candle data provided"],
                blocking_reasons=["No candle data provided"],
            )

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            return CRTResult(
                bias="UNKNOWN",
                reasons=["Missing required OHLC columns"],
                blocking_reasons=["Missing required OHLC columns"],
            )

        offset = int(config.reference_candle_offset)
        if offset <= 0:
            return CRTResult(
                bias="UNKNOWN",
                reasons=["Invalid reference candle offset"],
                blocking_reasons=["reference_candle_offset must be greater than zero"],
            )

        if len(candles) <= offset:
            return CRTResult(
                bias="UNKNOWN",
                reasons=["Not enough candles for CRT analysis"],
                blocking_reasons=["Not enough candles for configured reference offset"],
            )

        open_values = pd.to_numeric(candles["open"], errors="coerce")
        high_values = pd.to_numeric(candles["high"], errors="coerce")
        low_values = pd.to_numeric(candles["low"], errors="coerce")
        close_values = pd.to_numeric(candles["close"], errors="coerce")

        if open_values.isna().all() or high_values.isna().all() or low_values.isna().all() or close_values.isna().all():
            return CRTResult(
                bias="UNKNOWN",
                reasons=["OHLC values are invalid"],
                blocking_reasons=["OHLC values are invalid"],
            )

        buffer_value = max(0.0, float(config.buffer))
        signals: list[CRTSignal] = []
        reference_range: CRTRange | None = None

        for index in range(offset, len(candles)):
            reference_index = index - offset

            ref_open = open_values.iloc[reference_index]
            ref_high = high_values.iloc[reference_index]
            ref_low = low_values.iloc[reference_index]
            ref_close = close_values.iloc[reference_index]
            current_high = high_values.iloc[index]
            current_low = low_values.iloc[index]
            current_close = close_values.iloc[index]

            if pd.isna(ref_open) or pd.isna(ref_high) or pd.isna(ref_low) or pd.isna(ref_close):
                continue
            if pd.isna(current_high) or pd.isna(current_low) or pd.isna(current_close):
                continue

            reference_range = CRTRange(
                reference_index=reference_index,
                reference_time=candles["time"].iloc[reference_index],
                high=float(ref_high),
                low=float(ref_low),
                open=float(ref_open),
                close=float(ref_close),
            )

            low_manipulation_break = float(current_low) < (float(ref_low) - buffer_value)
            if low_manipulation_break:
                close_inside = float(current_close) > float(ref_low)
                confirmed = close_inside if config.require_close_back_inside else True
                if confirmed:
                    signals.append(
                        CRTSignal(
                            index=index,
                            time=candles["time"].iloc[index],
                            signal_type="LOW_MANIPULATION",
                            direction="BULLISH",
                            reference_high=float(ref_high),
                            reference_low=float(ref_low),
                            sweep_price=float(current_low),
                            close_price=float(current_close),
                            confirmed=True,
                            reasons=[
                                f"Low swept below reference low {float(ref_low):.4f}",
                                (
                                    "Close returned above reference low"
                                    if config.require_close_back_inside
                                    else "Close-back-inside not required"
                                ),
                            ],
                        )
                    )

            high_manipulation_break = float(current_high) > (float(ref_high) + buffer_value)
            if high_manipulation_break:
                close_inside = float(current_close) < float(ref_high)
                confirmed = close_inside if config.require_close_back_inside else True
                if confirmed:
                    signals.append(
                        CRTSignal(
                            index=index,
                            time=candles["time"].iloc[index],
                            signal_type="HIGH_MANIPULATION",
                            direction="BEARISH",
                            reference_high=float(ref_high),
                            reference_low=float(ref_low),
                            sweep_price=float(current_high),
                            close_price=float(current_close),
                            confirmed=True,
                            reasons=[
                                f"High swept above reference high {float(ref_high):.4f}",
                                (
                                    "Close returned below reference high"
                                    if config.require_close_back_inside
                                    else "Close-back-inside not required"
                                ),
                            ],
                        )
                    )

            if config.require_expansion_close:
                bullish_expansion = float(current_close) > (float(ref_high) + buffer_value)
                bearish_expansion = float(current_close) < (float(ref_low) - buffer_value)
            else:
                bullish_expansion = float(current_high) > (float(ref_high) + buffer_value)
                bearish_expansion = float(current_low) < (float(ref_low) - buffer_value)

            if bullish_expansion:
                signals.append(
                    CRTSignal(
                        index=index,
                        time=candles["time"].iloc[index],
                        signal_type="BULLISH_EXPANSION",
                        direction="BULLISH",
                        reference_high=float(ref_high),
                        reference_low=float(ref_low),
                        sweep_price=None,
                        close_price=float(current_close),
                        confirmed=True,
                        reasons=["Price expanded above reference high"],
                    )
                )

            if bearish_expansion:
                signals.append(
                    CRTSignal(
                        index=index,
                        time=candles["time"].iloc[index],
                        signal_type="BEARISH_EXPANSION",
                        direction="BEARISH",
                        reference_high=float(ref_high),
                        reference_low=float(ref_low),
                        sweep_price=None,
                        close_price=float(current_close),
                        confirmed=True,
                        reasons=["Price expanded below reference low"],
                    )
                )

        if not signals:
            return CRTResult(
                bias="NEUTRAL",
                latest_signal=None,
                signals=[],
                reference_range=reference_range,
                reasons=["No CRT signal found"],
                blocking_reasons=[],
            )

        latest_signal = signals[-1]
        signal_to_bias = {
            "LOW_MANIPULATION": "BULLISH",
            "HIGH_MANIPULATION": "BEARISH",
            "BULLISH_EXPANSION": "BULLISH",
            "BEARISH_EXPANSION": "BEARISH",
        }
        bias = signal_to_bias.get(latest_signal.signal_type, "NEUTRAL")

        return CRTResult(
            bias=bias,
            latest_signal=latest_signal,
            signals=signals,
            reference_range=reference_range,
            reasons=[f"Detected {len(signals)} CRT signal(s)", f"Latest signal: {latest_signal.signal_type}"],
            blocking_reasons=[],
        )

    def explain(self, result: CRTResult) -> str:
        """Return a readable CRT analysis summary."""
        if result.latest_signal is None:
            reasons_text = "; ".join(result.reasons) if result.reasons else "None"
            blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
            return (
                f"CRT context: {result.bias} | signals: 0 | "
                f"reasons: {reasons_text} | blocking reasons: {blocks_text}"
            )

        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        latest_reasons = "; ".join(result.latest_signal.reasons) if result.latest_signal.reasons else "None"
        return (
            f"CRT context: {result.bias} | signals: {len(result.signals)} | "
            f"latest: {result.latest_signal.signal_type} {result.latest_signal.direction} | "
            f"close: {result.latest_signal.close_price:.4f} | "
            f"latest reasons: {latest_reasons} | reasons: {reasons_text}"
        )
