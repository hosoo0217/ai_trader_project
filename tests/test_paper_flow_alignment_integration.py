"""Integration tests for ContextAlignmentGate inside PaperTradingFlow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pandas as pd

from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.context_alignment import ContextAlignmentConfig
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from crt.crt_engine import CRTResult
from risk.risk_engine import RiskEngineConfig
from smc.smc_context import SMCContextResult
from storage.decision_trace import DecisionTracer
from storage.trade_journal import TradeJournal


def _make_candles(rows: int = 120, step: float = 2.0) -> pd.DataFrame:
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    price = 100.0
    data: list[dict[str, float | datetime]] = []

    for index in range(rows):
        open_price = price
        close = open_price + step
        high = max(open_price, close) + 0.5
        low = min(open_price, close) - 0.5
        data.append(
            {
                "time": start + timedelta(minutes=index),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
            }
        )
        price = close

    return pd.DataFrame(data)


def _mock_smc_result(bias: str, confidence: float = 80.0) -> SMCContextResult:
    return SMCContextResult(
        bias=bias,
        confidence=confidence,
        market_structure_bias=bias,
        latest_break_type="BOS",
        latest_break_direction=bias,
        latest_sweep_type="LOW_SWEEP" if bias == "BULLISH" else "HIGH_SWEEP",
        latest_sweep_direction=bias,
        reasons=[f"Mocked {bias} SMC context"],
        blocking_reasons=[],
    )


def _mock_crt_result(bias: str) -> CRTResult:
    return CRTResult(
        bias=bias,
        reasons=[f"Mocked {bias} CRT context"],
        blocking_reasons=[],
    )


def _run_flow(candles: pd.DataFrame, tracer: DecisionTracer | None = None, journal: TradeJournal | None = None):
    return PaperTradingFlow().run_single_timeframe(
        candles=candles,
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(minimum_confidence=0.0),
        capital_config=CapitalProtectionConfig(),
        capital_state=CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=PaperBrokerState(),
        journal=journal,
        risk_config=RiskEngineConfig(),
        session_config=SessionFilterConfig(enabled=False),
        current_time=datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        volatility_config=VolatilityFilterConfig(min_atr=0.1, max_atr=100.0),
        spread_config=SpreadFilterConfig(max_spread=3.0),
        current_spread=1.0,
        tracer=tracer,
        alignment_config=ContextAlignmentConfig(enabled=True),
    )


def test_bullish_smc_and_bullish_crt_allows_flow_to_continue() -> None:
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BULLISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BULLISH")),
    ):
        result = _run_flow(_make_candles(step=3.0))

    assert result.alignment_checked is True
    assert result.alignment_allowed is True
    assert result.alignment_status == "ALIGNED_BULLISH"
    assert result.aligned_bias == "BULLISH"


def test_bearish_smc_and_bearish_crt_allows_flow_to_continue() -> None:
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BEARISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BEARISH")),
    ):
        result = _run_flow(_make_candles(step=-3.0))

    assert result.alignment_checked is True
    assert result.alignment_allowed is True
    assert result.alignment_status == "ALIGNED_BEARISH"
    assert result.aligned_bias == "BEARISH"


def test_bullish_smc_and_bearish_crt_blocks_trade() -> None:
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BULLISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BEARISH")),
    ):
        result = _run_flow(_make_candles(step=3.0))

    assert result.decision_action == "NO_TRADE"
    assert result.trade_executed is False
    assert result.alignment_allowed is False
    assert result.alignment_status == "CONFLICT_BLOCKED"


def test_bearish_smc_and_bullish_crt_blocks_trade() -> None:
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BEARISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BULLISH")),
    ):
        result = _run_flow(_make_candles(step=-3.0))

    assert result.decision_action == "NO_TRADE"
    assert result.trade_executed is False
    assert result.alignment_allowed is False
    assert result.alignment_status == "CONFLICT_BLOCKED"


def test_alignment_blocked_trade_is_recorded_in_journal() -> None:
    journal = TradeJournal()
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BULLISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BEARISH")),
    ):
        result = _run_flow(_make_candles(step=3.0), journal=journal)

    entries = journal.get_all_entries()
    assert result.journal_recorded is True
    assert len(entries) == 1
    assert entries[0].status == "BLOCKED"
    assert any("SMC bias BULLISH conflicts with CRT bias BEARISH" in item for item in entries[0].blocking_reasons)


def test_alignment_blocked_trade_does_not_execute_paper_order() -> None:
    tracer = DecisionTracer()
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BULLISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BEARISH")),
    ):
        result = _run_flow(_make_candles(step=3.0), tracer=tracer)

    assert result.trade_executed is False
    assert result.trace_explanation is not None
    assert "RISK_ENGINE" not in result.trace_explanation
    assert "PAPER_BROKER" not in result.trace_explanation


def test_decision_trace_includes_context_alignment_step() -> None:
    tracer = DecisionTracer()
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result("BULLISH")),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result("BULLISH")),
    ):
        result = _run_flow(_make_candles(step=3.0), tracer=tracer)

    assert result.trace_explanation is not None
    assert "CONTEXT_ALIGNMENT" in result.trace_explanation
