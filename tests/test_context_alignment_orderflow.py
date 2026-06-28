"""Unit tests for SMC + CRT + Order Flow alignment."""

from __future__ import annotations

from types import SimpleNamespace

from core.context_alignment import ContextAlignmentConfig, ContextAlignmentGate


def _source(bias: str, confidence: float = 80.0) -> SimpleNamespace:
    """Create a small context-like object for alignment tests."""
    return SimpleNamespace(bias=bias, confidence=confidence)


def test_bullish_alignment_with_all_sources_bullish() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BULLISH"),
        _source("BULLISH"),
        ContextAlignmentConfig(),
        orderflow_result=_source("BULLISH"),
    )

    assert result.aligned is True
    assert result.allowed is True
    assert result.final_bias == "BULLISH"
    assert result.smc_bias == "BULLISH"
    assert result.crt_bias == "BULLISH"
    assert result.orderflow_bias == "BULLISH"
    assert result.confidence >= 80.0


def test_bearish_alignment_with_all_sources_bearish() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BEARISH"),
        _source("BEARISH"),
        ContextAlignmentConfig(),
        orderflow_result=_source("BEARISH"),
    )

    assert result.aligned is True
    assert result.allowed is True
    assert result.final_bias == "BEARISH"
    assert result.confidence >= 80.0


def test_bullish_smc_crt_with_neutral_orderflow_passes_when_not_required() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BULLISH"),
        _source("BULLISH"),
        ContextAlignmentConfig(require_orderflow_alignment=False),
        orderflow_result=_source("NEUTRAL"),
    )

    assert result.aligned is True
    assert result.final_bias == "BULLISH"
    assert result.confidence >= 50.0


def test_bearish_smc_crt_with_unknown_orderflow_passes_when_not_required() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BEARISH"),
        _source("BEARISH"),
        ContextAlignmentConfig(require_orderflow_alignment=False),
        orderflow_result=_source("UNKNOWN"),
    )

    assert result.aligned is True
    assert result.final_bias == "BEARISH"
    assert result.confidence >= 50.0


def test_orderflow_conflict_blocks_alignment() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BULLISH"),
        _source("BULLISH"),
        ContextAlignmentConfig(),
        orderflow_result=_source("BEARISH"),
    )

    assert result.aligned is False
    assert result.allowed is False
    assert result.final_bias == "NEUTRAL"
    assert "Order Flow bias BEARISH conflicts with BULLISH alignment" in result.blocking_reasons


def test_require_orderflow_alignment_blocks_when_orderflow_missing() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BULLISH"),
        _source("BULLISH"),
        ContextAlignmentConfig(require_orderflow_alignment=True),
        orderflow_result=None,
    )

    assert result.aligned is False
    assert result.allowed is False
    assert result.final_bias == "NEUTRAL"
    assert "Order Flow alignment is required but missing or neutral" in result.blocking_reasons


def test_require_orderflow_alignment_passes_when_orderflow_matches() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BEARISH"),
        _source("BEARISH"),
        ContextAlignmentConfig(require_orderflow_alignment=True),
        orderflow_result=_source("BEARISH"),
    )

    assert result.aligned is True
    assert result.final_bias == "BEARISH"
    assert result.blocking_reasons == []


def test_no_useful_context_returns_unknown_and_not_aligned() -> None:
    result = ContextAlignmentGate().evaluate(
        None,
        _source("UNKNOWN"),
        ContextAlignmentConfig(),
        orderflow_result=_source("UNKNOWN"),
    )

    assert result.aligned is False
    assert result.final_bias == "UNKNOWN"
    assert result.confidence == 0.0


def test_confidence_stays_between_zero_and_one_hundred() -> None:
    result = ContextAlignmentGate().evaluate(
        _source("BULLISH"),
        _source("BULLISH"),
        ContextAlignmentConfig(minimum_confidence=0.0),
        orderflow_result=_source("BULLISH"),
    )

    assert 0.0 <= result.confidence <= 100.0


def test_explain_returns_readable_text() -> None:
    gate = ContextAlignmentGate()
    result = gate.evaluate(
        _source("BULLISH"),
        _source("BULLISH"),
        ContextAlignmentConfig(),
        orderflow_result=_source("BULLISH"),
    )

    text = gate.explain(result)

    assert "Context alignment" in text
    assert "SMC bias: BULLISH" in text
    assert "CRT bias: BULLISH" in text
    assert "Order Flow bias: BULLISH" in text
    assert "final bias: BULLISH" in text
