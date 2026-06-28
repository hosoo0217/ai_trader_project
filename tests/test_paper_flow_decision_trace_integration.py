"""Integration tests for DecisionTracer + PaperTradingFlow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.decision_trace import DecisionTracer


def _make_candles(rows: int = 120, step: float = 2.0) -> pd.DataFrame:
    """Create deterministic candles with a clear trend for stable tests."""
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    price = 100.0
    data: list[dict[str, float | datetime]] = []

    for index in range(rows):
        open_price = price
        close = open_price + step
        high = close + 0.5
        low = open_price - 0.5
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


def _run_flow(
    candles: pd.DataFrame,
    tracer: DecisionTracer | None = None,
    spread_config: SpreadFilterConfig | None = None,
    current_spread: float | None = 1.0,
) -> object:
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
        spread_config=spread_config or SpreadFilterConfig(max_spread=3.0),
        current_spread=current_spread,
        tracer=tracer,
    )


def test_flow_creates_trace_when_tracer_is_provided() -> None:
    tracer = DecisionTracer()

    result = _run_flow(_make_candles(), tracer=tracer)

    assert result.trace_id is not None
    assert result.trace_explanation is not None
    assert "Decision trace ID:" in result.trace_explanation
    assert "MARKET_ANALYZER" in result.trace_explanation


def test_flow_works_without_tracer() -> None:
    result = _run_flow(_make_candles(), tracer=None)

    assert result.completed is True
    assert result.trace_id is None
    assert result.trace_explanation is None


def test_blocked_trade_still_creates_trace() -> None:
    tracer = DecisionTracer()

    result = _run_flow(
        _make_candles(),
        tracer=tracer,
        spread_config=SpreadFilterConfig(max_spread=2.0),
        current_spread=4.0,
    )

    assert result.decision_action == "NO_TRADE"
    assert result.trace_id is not None
    assert result.trace_explanation is not None
    assert "SAFETY_GATE" in result.trace_explanation


def test_executed_buy_trace_includes_decision_engine_and_paper_broker() -> None:
    tracer = DecisionTracer()

    result = _run_flow(_make_candles(step=3.0), tracer=tracer)

    assert result.trade_executed is True
    assert result.decision_action == "BUY"
    assert result.trace_explanation is not None
    assert "DECISION_ENGINE" in result.trace_explanation
    assert "PAPER_BROKER" in result.trace_explanation


def test_safety_blocked_trace_includes_safety_gate() -> None:
    tracer = DecisionTracer()

    result = _run_flow(
        _make_candles(),
        tracer=tracer,
        spread_config=SpreadFilterConfig(max_spread=1.0),
        current_spread=2.0,
    )

    assert result.safety_allowed is False
    assert result.trace_explanation is not None
    assert "SAFETY_GATE" in result.trace_explanation


def test_trace_explanation_is_readable() -> None:
    tracer = DecisionTracer()

    result = _run_flow(_make_candles(), tracer=tracer)

    assert result.trace_explanation is not None
    assert "Symbol:" in result.trace_explanation
    assert "Final action:" in result.trace_explanation
    assert "Steps:" in result.trace_explanation
