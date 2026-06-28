"""Unit tests for order flow context combiner."""

from __future__ import annotations

from orderflow.absorption import AbsorptionResult, AbsorptionSignal
from orderflow.delta_cvd import DeltaCVDResult
from orderflow.imbalance import ImbalanceResult
from orderflow.orderflow_context import OrderFlowContextCombiner, OrderFlowContextConfig


def _delta(direction: str, final_cvd: float = 0.0) -> DeltaCVDResult:
    return DeltaCVDResult(
        points=[],
        final_cvd=final_cvd,
        latest_delta=None,
        latest_direction=direction,
        reasons=[],
        blocking_reasons=[],
    )


def _imbalance(bias: str) -> ImbalanceResult:
    return ImbalanceResult(
        imbalances=[],
        ask_imbalances=0,
        bid_imbalances=0,
        bias=bias,
        reasons=[],
        blocking_reasons=[],
    )


def _absorption(bias: str) -> AbsorptionResult:
    signal_type = "NO_ABSORPTION"
    direction = "NEUTRAL"
    if bias == "BULLISH":
        signal_type = "BUY_ABSORPTION"
        direction = "BULLISH"
    elif bias == "BEARISH":
        signal_type = "SELL_ABSORPTION"
        direction = "BEARISH"

    return AbsorptionResult(
        signal=AbsorptionSignal(
            signal_type=signal_type,
            direction=direction,
            total_volume=100.0,
            delta=100.0,
            candle_body=1.0,
            candle_range=10.0,
            reasons=[],
        ),
        bias=bias,
        reasons=[],
        blocking_reasons=[],
    )


def test_bullish_context_from_aligned_bullish_evidence() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("BUYING_PRESSURE", final_cvd=150.0),
        _imbalance("BULLISH"),
        _absorption("BULLISH"),
        OrderFlowContextConfig(),
    )

    assert result.bias == "BULLISH"
    assert result.confidence > 50.0
    assert result.delta_direction == "BUYING_PRESSURE"
    assert result.imbalance_bias == "BULLISH"
    assert result.absorption_bias == "BULLISH"
    assert result.final_cvd == 150.0


def test_bearish_context_from_aligned_bearish_evidence() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("SELLING_PRESSURE", final_cvd=-200.0),
        _imbalance("BEARISH"),
        _absorption("BEARISH"),
        OrderFlowContextConfig(),
    )

    assert result.bias == "BEARISH"
    assert result.confidence > 50.0


def test_neutral_context_from_conflicting_evidence() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BEARISH"),
        None,
        OrderFlowContextConfig(),
    )

    assert result.bias == "NEUTRAL"
    assert "balanced" in " ".join(result.reasons)


def test_unknown_when_no_inputs_exist() -> None:
    result = OrderFlowContextCombiner().combine(
        None,
        None,
        None,
        OrderFlowContextConfig(),
    )

    assert result.bias == "UNKNOWN"
    assert result.confidence == 0.0
    assert "No usable order flow evidence" in result.blocking_reasons


def test_confidence_increases_with_aligned_evidence() -> None:
    combiner = OrderFlowContextCombiner()

    one_source = combiner.combine(
        _delta("BUYING_PRESSURE"),
        None,
        None,
        OrderFlowContextConfig(minimum_confidence=0.0),
    )
    three_sources = combiner.combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BULLISH"),
        _absorption("BULLISH"),
        OrderFlowContextConfig(minimum_confidence=0.0),
    )

    assert three_sources.confidence > one_source.confidence


def test_confidence_decreases_with_conflict() -> None:
    combiner = OrderFlowContextCombiner()

    aligned = combiner.combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BULLISH"),
        None,
        OrderFlowContextConfig(minimum_confidence=0.0),
    )
    conflicted = combiner.combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BULLISH"),
        _absorption("BEARISH"),
        OrderFlowContextConfig(minimum_confidence=0.0),
    )

    assert conflicted.confidence < aligned.confidence


def test_require_delta_alignment_blocks_conflict() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("SELLING_PRESSURE"),
        _imbalance("BULLISH"),
        _absorption("BULLISH"),
        OrderFlowContextConfig(require_delta_alignment=True),
    )

    assert result.bias == "NEUTRAL"
    assert "Delta direction conflicts with final order flow bias" in result.blocking_reasons


def test_require_imbalance_alignment_blocks_conflict() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BEARISH"),
        _absorption("BULLISH"),
        OrderFlowContextConfig(require_imbalance_alignment=True),
    )

    assert result.bias == "NEUTRAL"
    assert "Imbalance bias conflicts with final order flow bias" in result.blocking_reasons


def test_require_absorption_confirmation_blocks_when_absorption_missing() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BULLISH"),
        None,
        OrderFlowContextConfig(require_absorption_confirmation=True),
    )

    assert result.bias == "NEUTRAL"
    assert "Absorption does not confirm final order flow bias" in result.blocking_reasons


def test_explain_returns_readable_text() -> None:
    result = OrderFlowContextCombiner().combine(
        _delta("BUYING_PRESSURE"),
        _imbalance("BULLISH"),
        _absorption("BULLISH"),
        OrderFlowContextConfig(),
    )

    text = OrderFlowContextCombiner().explain(result)

    assert "Order flow context summary" in text
    assert "bias=BULLISH" in text
    assert "confidence=" in text
