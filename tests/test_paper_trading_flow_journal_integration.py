"""Integration tests for paper trading flow with the trade journal."""

import pandas as pd

from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from storage.trade_journal import TradeJournal


def make_candles(bias: str = "bullish", rows: int = 60):
    """Create simple candle data for journal integration tests."""
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


def test_executed_buy_trade_is_recorded_in_journal():
    """A BUY decision should create a journal entry."""
    journal = TradeJournal()
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
        journal,
    )

    assert result.journal_recorded
    assert result.journal_trade_id is not None
    assert len(journal.get_all_entries()) >= 1


def test_executed_sell_trade_is_recorded_in_journal():
    """A SELL decision should create a journal entry."""
    journal = TradeJournal()
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
        journal,
    )

    assert result.journal_recorded
    assert result.journal_trade_id is not None


def test_no_trade_decision_is_recorded_in_journal():
    """A NO_TRADE outcome should still be recorded in the journal."""
    journal = TradeJournal()
    flow = PaperTradingFlow()
    result = flow.run_single_timeframe(
        make_candles("neutral"),
        PaperTradingFlowConfig(),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
        journal,
    )

    assert result.journal_recorded
    assert result.journal_trade_id is not None


def test_capital_protection_block_is_recorded_in_journal():
    """A capital-protection block should be recorded as a blocked entry."""
    journal = TradeJournal()
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
        journal,
    )

    assert result.journal_recorded
    assert result.journal_trade_id is not None


def test_flow_still_works_when_journal_is_not_provided():
    """Without a journal, the flow should continue to work."""
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
    assert result.journal_recorded is False


def test_journal_trade_id_is_returned_when_entry_created():
    """The flow should return the journal trade ID for created entries."""
    journal = TradeJournal()
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
        journal,
    )

    assert result.journal_trade_id is not None
