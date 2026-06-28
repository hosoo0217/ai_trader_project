"""Integration tests for CRT context inside PaperTradingFlow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pandas as pd

from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from crt.crt_engine import CRTResult, CRTSignal
from risk.risk_engine import RiskEngineConfig
from storage.decision_trace import DecisionTracer


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


def _run_flow(candles: pd.DataFrame, tracer: DecisionTracer | None = None):
    return PaperTradingFlow().run_single_timeframe(
        candles=candles,
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(minimum_confidence=0.0),
        capital_config=CapitalProtectionConfig(),
        capital_state=CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=PaperBrokerState(),
        risk_config=RiskEngineConfig(),
        session_config=SessionFilterConfig(enabled=False),
        current_time=datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        volatility_config=VolatilityFilterConfig(min_atr=0.1, max_atr=100.0),
        spread_config=SpreadFilterConfig(max_spread=3.0),
        current_spread=1.0,
        tracer=tracer,
    )


def _mock_crt_result(bias: str, signal_type: str | None, reasons: list[str], blocks: list[str]) -> CRTResult:
    signal = None
    if signal_type is not None:
        signal = CRTSignal(
            index=1,
            time=datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc),
            signal_type=signal_type,
            direction=bias if bias in {"BULLISH", "BEARISH"} else "NEUTRAL",
            reference_high=101.0,
            reference_low=99.0,
            sweep_price=None,
            close_price=100.5,
            confirmed=True,
            reasons=["Mocked CRT signal"],
        )

    return CRTResult(
        bias=bias,
        latest_signal=signal,
        signals=[signal] if signal is not None else [],
        reasons=reasons,
        blocking_reasons=blocks,
    )


def test_crt_analysis_runs_without_crashing() -> None:
    result = _run_flow(_make_candles(step=2.0))

    assert result.completed is True
    assert result.crt_checked is True


def test_bullish_crt_context_can_support_buy_decision() -> None:
    mocked = _mock_crt_result(
        bias="BULLISH",
        signal_type="LOW_MANIPULATION",
        reasons=["Mocked bullish CRT context"],
        blocks=[],
    )
    with patch("core.paper_trading_flow.CRTEngine.analyze", return_value=mocked):
        result = _run_flow(_make_candles(step=3.0))

    assert result.decision_action == "BUY"
    assert result.crt_bias == "BULLISH"


def test_bearish_crt_context_can_support_sell_decision() -> None:
    mocked = _mock_crt_result(
        bias="BEARISH",
        signal_type="HIGH_MANIPULATION",
        reasons=["Mocked bearish CRT context"],
        blocks=[],
    )
    with patch("core.paper_trading_flow.CRTEngine.analyze", return_value=mocked):
        result = _run_flow(_make_candles(step=-3.0))

    assert result.decision_action == "SELL"
    assert result.crt_bias == "BEARISH"


def test_conflicting_crt_context_blocks_or_reduces_confidence_safely() -> None:
    mocked = _mock_crt_result(
        bias="BEARISH",
        signal_type="HIGH_MANIPULATION",
        reasons=["Mocked strong bearish context"],
        blocks=["Mocked bearish blocking reason"],
    )
    with patch("core.paper_trading_flow.CRTEngine.analyze", return_value=mocked):
        result = _run_flow(_make_candles(step=3.0))

    assert result.decision_action in {"NO_TRADE", "BUY"}
    if result.decision_action == "NO_TRADE":
        assert result.trade_executed is False
    else:
        assert any("CRT conflict reduced confidence" in reason for reason in result.reasons)


def test_unknown_crt_does_not_crash() -> None:
    mocked = _mock_crt_result(
        bias="UNKNOWN",
        signal_type=None,
        reasons=["No usable CRT evidence found"],
        blocks=["CRT data invalid"],
    )
    with patch("core.paper_trading_flow.CRTEngine.analyze", return_value=mocked):
        result = _run_flow(_make_candles(step=2.0))

    assert result.completed is True
    assert result.crt_bias == "UNKNOWN"


def test_crt_reasons_appear_in_flow_result() -> None:
    mocked = _mock_crt_result(
        bias="BULLISH",
        signal_type="BULLISH_EXPANSION",
        reasons=["Mocked CRT reason"],
        blocks=["Mocked CRT block"],
    )
    with patch("core.paper_trading_flow.CRTEngine.analyze", return_value=mocked):
        result = _run_flow(_make_candles(step=2.0))

    assert "Mocked CRT reason" in result.crt_reasons
    assert "Mocked CRT block" in result.crt_blocking_reasons


def test_crt_trace_steps_are_added_when_tracer_is_provided() -> None:
    tracer = DecisionTracer()

    result = _run_flow(_make_candles(step=2.0), tracer=tracer)

    assert result.trace_explanation is not None
    assert "CRT_ENGINE" in result.trace_explanation
    assert "CRT_CONTEXT" in result.trace_explanation
