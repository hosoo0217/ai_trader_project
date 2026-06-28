from __future__ import annotations

from smc.bos_choch import BOSCHOCHResult, StructureBreak
from smc.liquidity_sweep import LiquiditySweep, LiquiditySweepResult
from smc.market_structure import MarketStructureResult
from smc.smc_context import SMCContextCombiner, SMCContextConfig


def _market_structure(bias: str) -> MarketStructureResult:
    return MarketStructureResult(structure_bias=bias)


def _bos_choch(direction: str, break_type: str = "BOS") -> BOSCHOCHResult:
    latest_break = StructureBreak(
        index=10,
        time=None,
        price=100.0,
        break_type=break_type,
        direction=direction,
        broken_level=99.0,
        reasons=["fixture"],
    )
    return BOSCHOCHResult(latest_break=latest_break, breaks=[latest_break], bias=direction)


def _liquidity(direction: str, sweep_type: str) -> LiquiditySweepResult:
    latest_sweep = LiquiditySweep(
        index=10,
        time=None,
        sweep_type=sweep_type,
        direction=direction,
        swept_level=100.0,
        sweep_price=101.0,
        close_price=99.5,
        confirmed=True,
        reasons=["fixture"],
    )
    return LiquiditySweepResult(latest_sweep=latest_sweep, sweeps=[latest_sweep], bias=direction)


def test_bullish_smc_context_from_aligned_bullish_evidence() -> None:
    result = SMCContextCombiner().combine(
        _market_structure("BULLISH"),
        _bos_choch("BULLISH", "BOS"),
        _liquidity("BULLISH", "LOW_SWEEP"),
        SMCContextConfig(),
    )

    assert result.bias == "BULLISH"
    assert result.confidence >= 60.0


def test_bearish_smc_context_from_aligned_bearish_evidence() -> None:
    result = SMCContextCombiner().combine(
        _market_structure("BEARISH"),
        _bos_choch("BEARISH", "BOS"),
        _liquidity("BEARISH", "HIGH_SWEEP"),
        SMCContextConfig(),
    )

    assert result.bias == "BEARISH"
    assert result.confidence >= 60.0


def test_neutral_context_from_conflicting_evidence() -> None:
    result = SMCContextCombiner().combine(
        _market_structure("BULLISH"),
        _bos_choch("BEARISH", "CHOCH"),
        None,
        SMCContextConfig(minimum_confidence=0.0),
    )

    assert result.bias == "NEUTRAL"


def test_unknown_when_no_inputs_exist() -> None:
    result = SMCContextCombiner().combine(None, None, None, SMCContextConfig())

    assert result.bias == "UNKNOWN"
    assert result.confidence == 0.0


def test_confidence_increases_with_aligned_evidence() -> None:
    combiner = SMCContextCombiner()

    low_evidence = combiner.combine(
        _market_structure("BULLISH"),
        None,
        None,
        SMCContextConfig(minimum_confidence=0.0),
    )

    high_evidence = combiner.combine(
        _market_structure("BULLISH"),
        _bos_choch("BULLISH", "BOS"),
        _liquidity("BULLISH", "LOW_SWEEP"),
        SMCContextConfig(minimum_confidence=0.0),
    )

    assert high_evidence.confidence > low_evidence.confidence


def test_confidence_decreases_with_conflict() -> None:
    combiner = SMCContextCombiner()

    aligned = combiner.combine(
        _market_structure("BULLISH"),
        _bos_choch("BULLISH", "BOS"),
        None,
        SMCContextConfig(minimum_confidence=0.0),
    )

    conflicting = combiner.combine(
        _market_structure("BULLISH"),
        _bos_choch("BULLISH", "BOS"),
        _liquidity("BEARISH", "HIGH_SWEEP"),
        SMCContextConfig(minimum_confidence=0.0),
    )

    assert conflicting.confidence < aligned.confidence


def test_require_liquidity_sweep_blocks_when_no_sweep_exists() -> None:
    result = SMCContextCombiner().combine(
        _market_structure("BULLISH"),
        _bos_choch("BULLISH", "BOS"),
        None,
        SMCContextConfig(minimum_confidence=0.0, require_liquidity_sweep=True),
    )

    assert result.bias == "NEUTRAL"
    assert any("Liquidity sweep evidence is required" in text for text in result.blocking_reasons)


def test_require_bos_or_choch_blocks_when_no_break_exists() -> None:
    result = SMCContextCombiner().combine(
        _market_structure("BULLISH"),
        None,
        _liquidity("BULLISH", "LOW_SWEEP"),
        SMCContextConfig(minimum_confidence=0.0, require_bos_or_choch=True),
    )

    assert result.bias == "NEUTRAL"
    assert any("BOS/CHOCH evidence is required" in text for text in result.blocking_reasons)


def test_explain_returns_readable_text() -> None:
    result = SMCContextCombiner().combine(
        _market_structure("BULLISH"),
        _bos_choch("BULLISH", "BOS"),
        _liquidity("BULLISH", "LOW_SWEEP"),
        SMCContextConfig(),
    )

    text = SMCContextCombiner().explain(result)

    assert "SMC context" in text
    assert "confidence" in text
