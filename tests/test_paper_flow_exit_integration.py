"""Integration tests for paper flow exit simulation."""

import pandas as pd

from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.trade_journal import TradeJournal


def make_flow_candles(direction: str, exit_kind: str | None = None) -> pd.DataFrame:
    """Create candles that produce a decision and optional SL/TP exit."""
    rows = 60
    if direction == "BUY":
        closes = [100.0 + index for index in range(rows)]
        highs = [200.0 for _ in closes]
        lows = [159.0 for _ in closes]
        if exit_kind == "SL":
            highs = [159.5 for _ in closes]
            lows[-1] = 158.0
    elif direction == "SELL":
        closes = [200.0 - index for index in range(rows)]
        highs = [141.5 for _ in closes]
        lows = [100.0 for _ in closes]
        if exit_kind == "SL":
            highs[-1] = 142.0
            lows = [140.5 for _ in closes]
    else:
        closes = [100.0 for _ in range(rows)]
        highs = [101.0 for _ in closes]
        lows = [99.0 for _ in closes]

    return pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=rows, freq="D"),
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
        }
    )


def run_flow(candles: pd.DataFrame, config: PaperTradingFlowConfig, journal: TradeJournal | None = None):
    """Run the paper flow with permissive test defaults."""
    state = PaperBrokerState()
    risk_config = RiskEngineConfig(
        account_balance=100.0,
        risk_per_trade_percent=1.0,
        reward_to_risk=1.0,
        default_stop_distance=1.0,
        min_volume=1.0,
        max_volume=1.0,
        point_value=1.0,
    )
    result = PaperTradingFlow().run_single_timeframe(
        candles,
        config,
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        state,
        journal,
        risk_config,
        SessionFilterConfig(enabled=False),
        spread_config=SpreadFilterConfig(max_spread=3.0),
        current_spread=1.0,
    )
    return result, state


def test_buy_trade_can_be_opened_and_closed_by_tp() -> None:
    result, state = run_flow(
        make_flow_candles("BUY", "TP"),
        PaperTradingFlowConfig(stop_loss=50.0, take_profit=160.0, simulate_exit=True),
    )

    assert result.trade_executed is True
    assert result.exit_simulated is True
    assert result.exit_reason == "TAKE_PROFIT"
    assert result.exit_price == 160.0
    assert result.pnl == 1.0
    assert len(state.open_positions) == 0
    assert len(state.closed_positions) == 1


def test_buy_trade_can_be_opened_and_closed_by_sl() -> None:
    result, state = run_flow(
        make_flow_candles("BUY", "SL"),
        PaperTradingFlowConfig(stop_loss=158.0, take_profit=500.0, simulate_exit=True),
    )

    assert result.trade_executed is True
    assert result.exit_reason == "STOP_LOSS"
    assert result.exit_price == 158.0
    assert result.pnl == -1.0
    assert len(state.open_positions) == 0


def test_sell_trade_can_be_opened_and_closed_by_tp() -> None:
    result, state = run_flow(
        make_flow_candles("SELL", "TP"),
        PaperTradingFlowConfig(stop_loss=500.0, take_profit=140.0, simulate_exit=True),
    )

    assert result.trade_executed is True
    assert result.exit_reason == "TAKE_PROFIT"
    assert result.exit_price == 140.0
    assert result.pnl == 1.0
    assert len(state.open_positions) == 0


def test_sell_trade_can_be_opened_and_closed_by_sl() -> None:
    result, state = run_flow(
        make_flow_candles("SELL", "SL"),
        PaperTradingFlowConfig(stop_loss=142.0, take_profit=50.0, simulate_exit=True),
    )

    assert result.trade_executed is True
    assert result.exit_reason == "STOP_LOSS"
    assert result.exit_price == 142.0
    assert result.pnl == -1.0
    assert len(state.open_positions) == 0


def test_no_trade_does_not_run_exit_simulation() -> None:
    result, state = run_flow(
        make_flow_candles("NONE"),
        PaperTradingFlowConfig(stop_loss=95.0, take_profit=105.0, simulate_exit=True),
    )

    assert result.trade_executed is False
    assert result.exit_simulated is False
    assert result.exit_reason is None
    assert len(state.open_positions) == 0


def test_journal_records_pnl_when_trade_is_closed() -> None:
    journal = TradeJournal()
    result, _state = run_flow(
        make_flow_candles("BUY", "TP"),
        PaperTradingFlowConfig(stop_loss=50.0, take_profit=160.0, simulate_exit=True),
        journal,
    )

    entries = journal.get_all_entries()
    summary = journal.summarize()

    assert result.journal_recorded is True
    assert entries[0].status == "CLOSED"
    assert entries[0].exit_reason == "TAKE_PROFIT"
    assert entries[0].pnl == 1.0
    assert summary["total_pnl"] == 1.0
    assert summary["wins"] == 1


def test_flow_result_includes_exit_reason_and_pnl() -> None:
    result, _state = run_flow(
        make_flow_candles("SELL", "TP"),
        PaperTradingFlowConfig(stop_loss=500.0, take_profit=140.0, simulate_exit=True),
    )

    assert result.exit_reason == "TAKE_PROFIT"
    assert result.pnl == 1.0
    assert "Exit simulation: TAKE_PROFIT" in result.reasons
