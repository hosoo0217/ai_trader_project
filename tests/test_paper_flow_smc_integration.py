"""Integration tests for SMC context inside PaperTradingFlow."""

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
from risk.risk_engine import RiskEngineConfig
from smc.smc_context import SMCContextResult
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


def test_smc_analysis_runs_without_crashing() -> None:
    result = _run_flow(_make_candles(step=2.0))

    assert result.completed is True
    assert result.smc_checked is True


def test_bullish_smc_context_can_support_buy_decision() -> None:
    result = _run_flow(_make_candles(step=3.0))

    assert result.decision_action in {"BUY", "NO_TRADE"}
    assert result.smc_bias in {"BULLISH", "NEUTRAL", "UNKNOWN"}


def test_bearish_smc_context_can_support_sell_decision() -> None:
    result = _run_flow(_make_candles(step=-3.0))

    assert result.decision_action in {"SELL", "NO_TRADE"}
    assert result.smc_bias in {"BEARISH", "NEUTRAL", "UNKNOWN"}


def test_conflicting_smc_context_blocks_safely() -> None:
    mocked_conflict = SMCContextResult(
        bias="BEARISH",
        confidence=90.0,
        market_structure_bias="BEARISH",
        latest_break_type="BOS",
        latest_break_direction="BEARISH",
        latest_sweep_type="HIGH_SWEEP",
        latest_sweep_direction="BEARISH",
        reasons=["Mocked bearish context"],
        blocking_reasons=["Mocked strong bearish evidence"],
    )

    with patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=mocked_conflict):
        result = _run_flow(_make_candles(step=3.0))

    assert result.decision_action == "NO_TRADE"
    assert result.trade_executed is False


def test_unknown_smc_does_not_crash() -> None:
    mocked_unknown = SMCContextResult(
        bias="UNKNOWN",
        confidence=0.0,
        market_structure_bias="UNKNOWN",
        latest_break_type=None,
        latest_break_direction=None,
        latest_sweep_type=None,
        latest_sweep_direction=None,
        reasons=["No usable SMC evidence found"],
        blocking_reasons=["All SMC inputs were missing or not directional"],
    )

    with patch("core.paper_trading_flow.SMCContextCombiner.combine", return_value=mocked_unknown):
        result = _run_flow(_make_candles(step=2.0))

    assert result.completed is True
    assert result.smc_bias == "UNKNOWN"


def test_smc_reasons_appear_in_flow_result() -> None:
    result = _run_flow(_make_candles(step=2.0))

    assert isinstance(result.smc_reasons, list)
    assert len(result.smc_reasons) > 0


def test_smc_trace_steps_are_added_when_tracer_is_provided() -> None:
    tracer = DecisionTracer()
    result = _run_flow(_make_candles(step=2.0), tracer=tracer)

    assert result.trace_explanation is not None
    assert "SMC_MARKET_STRUCTURE" in result.trace_explanation
    assert "SMC_BOS_CHOCH" in result.trace_explanation
    assert "SMC_LIQUIDITY_SWEEP" in result.trace_explanation
    assert "SMC_CONTEXT" in result.trace_explanation
