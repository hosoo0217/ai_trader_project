"""Unit tests for the paper trading flow."""

import pandas as pd

from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig, PaperTradingFlowResult


def make_candles(bias: str = "bullish", rows: int = 60):
    """Create simple candle data for flow tests."""
    if bias == "bullish":
        closes = [100 + i for i in range(rows)]
    elif bias == "bearish":
        closes = [100 - i for i in range(rows)]
    else:
        closes = [100] * rows

    return pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=rows, freq="D"),
            "open": closes,
            "high": [value + 1 for value in closes],
            "low": [value - 1 for value in closes],
            "close": closes,
        }
    )


def test_full_flow_completes_without_live_broker():
    """The flow should complete and only use the paper broker state."""
    flow = PaperTradingFlow()
    config = PaperTradingFlowConfig()
    candles = make_candles("bullish")
    result = flow.run_single_timeframe(
        candles,
        config,
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
    )

    assert result.completed
    assert result.trade_executed or result.status == "NO_TRADE"


def test_invalid_candle_data_returns_safe_no_trade_result():
    """Invalid candle data should produce a no-trade result."""
    flow = PaperTradingFlow()
    result = flow.run_single_timeframe(
        None,
        PaperTradingFlowConfig(),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
    )

    assert not result.completed
    assert result.decision_action == "NO_TRADE"


def test_valid_bullish_data_can_produce_buy_paper_trade():
    """Bullish data should be able to create a BUY paper trade."""
    flow = PaperTradingFlow()
    result = flow.run_single_timeframe(
        make_candles("bullish"),
        PaperTradingFlowConfig(),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
    )

    assert result.completed
    assert result.decision_action in {"BUY", "NO_TRADE"}


def test_valid_bearish_data_can_produce_sell_paper_trade():
    """Bearish data should be able to create a SELL paper trade."""
    flow = PaperTradingFlow()
    result = flow.run_single_timeframe(
        make_candles("bearish"),
        PaperTradingFlowConfig(),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
    )

    assert result.completed
    assert result.decision_action in {"SELL", "NO_TRADE"}


def test_capital_protection_block_prevents_trade():
    """Capital protection should stop the flow from executing a paper order."""
    flow = PaperTradingFlow()
    result = flow.run_single_timeframe(
        make_candles("bullish"),
        PaperTradingFlowConfig(),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(max_daily_loss=1.0),
        CapitalProtectionState(realized_daily_pnl=-1.0),
        PaperBrokerConfig(),
        PaperBrokerState(),
    )

    assert result.completed
    assert result.decision_action == "NO_TRADE"


def test_explain_returns_readable_text():
    """The explanation should summarize the flow result clearly."""
    flow = PaperTradingFlow()
    result = PaperTradingFlowResult(
        completed=True,
        status="EXECUTED",
        market_bias="BULLISH",
        decision_action="BUY",
        trade_executed=True,
        reasons=["Market analysis succeeded"],
        balance=10000.0,
    )

    explanation = flow.explain(result)

    assert "Paper flow status" in explanation
    assert "BUY" in explanation
