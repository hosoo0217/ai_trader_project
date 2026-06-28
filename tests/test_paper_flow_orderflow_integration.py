"""Integration tests for optional Order Flow context inside PaperTradingFlow."""

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
from orderflow.orderflow_context import OrderFlowContextResult
from risk.risk_engine import RiskEngineConfig
from smc.smc_context import SMCContextResult
from storage.decision_trace import DecisionTracer


def _make_candles(rows: int = 120, step: float = 3.0) -> pd.DataFrame:
    """Create clear directional candles for paper-flow tests."""
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


def _mock_smc_result(bias: str) -> SMCContextResult:
    return SMCContextResult(
        bias=bias,
        confidence=80.0,
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


def _orderflow(bias: str, confidence: float = 80.0) -> OrderFlowContextResult:
    return OrderFlowContextResult(
        bias=bias,
        confidence=confidence,
        delta_direction="BUYING_PRESSURE" if bias == "BULLISH" else "SELLING_PRESSURE" if bias == "BEARISH" else "NEUTRAL",
        imbalance_bias=bias,
        absorption_bias=bias,
        final_cvd=100.0 if bias == "BULLISH" else -100.0 if bias == "BEARISH" else 0.0,
        reasons=[f"Mocked {bias} Order Flow context"],
        blocking_reasons=[],
    )


def _run_flow(
    smc_bias: str,
    crt_bias: str,
    candle_step: float,
    orderflow_context_result: OrderFlowContextResult | None = None,
    tracer: DecisionTracer | None = None,
):
    with (
        patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=_mock_smc_result(smc_bias)),
        patch("core.paper_trading_flow.CRTEngine.analyze", return_value=_mock_crt_result(crt_bias)),
    ):
        return PaperTradingFlow().run_single_timeframe(
            candles=_make_candles(step=candle_step),
            flow_config=PaperTradingFlowConfig(),
            market_config=MarketAnalyzerConfig(),
            mtf_config=MultiTimeframeConfig(minimum_confidence=0.0),
            capital_config=CapitalProtectionConfig(),
            capital_state=CapitalProtectionState(),
            broker_config=PaperBrokerConfig(),
            broker_state=PaperBrokerState(),
            journal=None,
            risk_config=RiskEngineConfig(),
            session_config=SessionFilterConfig(enabled=False),
            current_time=datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
            volatility_config=VolatilityFilterConfig(min_atr=0.1, max_atr=100.0),
            spread_config=SpreadFilterConfig(max_spread=3.0),
            current_spread=1.0,
            tracer=tracer,
            alignment_config=ContextAlignmentConfig(enabled=True),
            orderflow_context_result=orderflow_context_result,
        )


def test_paper_flow_still_works_without_orderflow_context() -> None:
    result = _run_flow("BULLISH", "BULLISH", candle_step=3.0)

    assert result.completed is True
    assert result.alignment_allowed is True
    assert result.orderflow_checked is True
    assert result.orderflow_bias == "UNKNOWN"
    assert "Order Flow context not provided" in result.orderflow_reasons


def test_paper_flow_includes_bullish_orderflow_context_when_provided() -> None:
    result = _run_flow("BULLISH", "BULLISH", candle_step=3.0, orderflow_context_result=_orderflow("BULLISH"))

    assert result.alignment_allowed is True
    assert result.aligned_bias == "BULLISH"
    assert result.orderflow_bias == "BULLISH"
    assert result.orderflow_confidence == 80.0
    assert any("Order Flow confirms BULLISH alignment" in item for item in result.alignment_reasons)


def test_paper_flow_includes_bearish_orderflow_context_when_provided() -> None:
    result = _run_flow("BEARISH", "BEARISH", candle_step=-3.0, orderflow_context_result=_orderflow("BEARISH"))

    assert result.alignment_allowed is True
    assert result.aligned_bias == "BEARISH"
    assert result.orderflow_bias == "BEARISH"
    assert result.orderflow_confidence == 80.0


def test_smc_crt_bullish_with_missing_orderflow_still_works() -> None:
    result = _run_flow("BULLISH", "BULLISH", candle_step=3.0)

    assert result.alignment_allowed is True
    assert result.aligned_bias == "BULLISH"


def test_smc_crt_bearish_with_missing_orderflow_still_works() -> None:
    result = _run_flow("BEARISH", "BEARISH", candle_step=-3.0)

    assert result.alignment_allowed is True
    assert result.aligned_bias == "BEARISH"


def test_orderflow_conflict_blocks_alignment() -> None:
    result = _run_flow("BULLISH", "BULLISH", candle_step=3.0, orderflow_context_result=_orderflow("BEARISH"))

    assert result.trade_executed is False
    assert result.alignment_allowed is False
    assert result.alignment_status == "CONFLICT_BLOCKED"
    assert "Order Flow bias BEARISH conflicts with BULLISH alignment" in result.alignment_blocking_reasons


def test_decision_trace_includes_orderflow_fields_or_reasons() -> None:
    tracer = DecisionTracer()
    result = _run_flow("BULLISH", "BULLISH", candle_step=3.0, orderflow_context_result=_orderflow("BULLISH"), tracer=tracer)

    assert result.trace_explanation is not None
    assert "ORDER_FLOW_CONTEXT" in result.trace_explanation
    assert "orderflow_bias=BULLISH" in result.trace_explanation
    assert "orderflow_confidence=80.0" in result.trace_explanation
