"""Unit tests for SMC + CRT context alignment gate."""

from __future__ import annotations

from core.context_alignment import ContextAlignmentConfig, ContextAlignmentGate
from crt.crt_engine import CRTResult
from smc.smc_context import SMCContextResult


def _smc(bias: str, confidence: float = 70.0) -> SMCContextResult:
    return SMCContextResult(
        bias=bias,
        confidence=confidence,
        market_structure_bias=bias,
        latest_break_type="BOS",
        latest_break_direction=bias,
        latest_sweep_type="LOW_SWEEP" if bias == "BULLISH" else "HIGH_SWEEP",
        latest_sweep_direction=bias,
        reasons=["Mocked SMC context"],
        blocking_reasons=[],
    )


def _crt(bias: str) -> CRTResult:
    return CRTResult(bias=bias, reasons=["Mocked CRT context"], blocking_reasons=[])


def test_bullish_smc_and_bullish_crt_passes() -> None:
    result = ContextAlignmentGate().evaluate(_smc("BULLISH"), _crt("BULLISH"), ContextAlignmentConfig())

    assert result.allowed is True
    assert result.status == "ALIGNED_BULLISH"
    assert result.aligned_bias == "BULLISH"
    assert result.confidence_adjustment == 10.0


def test_bearish_smc_and_bearish_crt_passes() -> None:
    result = ContextAlignmentGate().evaluate(_smc("BEARISH"), _crt("BEARISH"), ContextAlignmentConfig())

    assert result.allowed is True
    assert result.status == "ALIGNED_BEARISH"
    assert result.aligned_bias == "BEARISH"
    assert result.confidence_adjustment == 10.0


def test_bullish_smc_and_bearish_crt_blocks() -> None:
    result = ContextAlignmentGate().evaluate(_smc("BULLISH"), _crt("BEARISH"), ContextAlignmentConfig())

    assert result.allowed is False
    assert result.status == "CONFLICT_BLOCKED"
    assert result.confidence_adjustment == -30.0


def test_bearish_smc_and_bullish_crt_blocks() -> None:
    result = ContextAlignmentGate().evaluate(_smc("BEARISH"), _crt("BULLISH"), ContextAlignmentConfig())

    assert result.allowed is False
    assert result.status == "CONFLICT_BLOCKED"
    assert result.confidence_adjustment == -30.0


def test_neutral_crt_allowed_when_configured() -> None:
    result = ContextAlignmentGate().evaluate(
        _smc("BULLISH"),
        _crt("NEUTRAL"),
        ContextAlignmentConfig(allow_neutral_crt=True),
    )

    assert result.allowed is True
    assert result.status == "NEUTRAL_WAIT"
    assert result.confidence_adjustment == 0.0


def test_unknown_crt_blocked_by_default() -> None:
    result = ContextAlignmentGate().evaluate(_smc("BULLISH"), _crt("UNKNOWN"), ContextAlignmentConfig())

    assert result.allowed is False
    assert result.status == "UNKNOWN_BLOCKED"
    assert result.confidence_adjustment == -5.0


def test_low_smc_confidence_blocks() -> None:
    result = ContextAlignmentGate().evaluate(
        _smc("BULLISH", confidence=20.0),
        _crt("BULLISH"),
        ContextAlignmentConfig(minimum_smc_confidence=50.0),
    )

    assert result.allowed is False
    assert result.status == "UNKNOWN_BLOCKED"


def test_disabled_gate_allows() -> None:
    result = ContextAlignmentGate().evaluate(
        _smc("BULLISH"),
        _crt("BEARISH"),
        ContextAlignmentConfig(enabled=False),
    )

    assert result.allowed is True
    assert result.status == "FILTER_DISABLED"
    assert "Context alignment gate disabled" in result.reasons


def test_explain_returns_readable_text() -> None:
    gate = ContextAlignmentGate()
    result = gate.evaluate(_smc("BULLISH"), _crt("BULLISH"), ContextAlignmentConfig())
    text = gate.explain(result)

    assert "Context alignment" in text
    assert "ALIGNED_BULLISH" in text
    assert "confidence adjustment" in text
