"""Integration tests for RiskEngine usage inside paper trading flow."""

import pandas as pd

from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.exit_simulator import ExitSimulationConfig
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.trade_journal import TradeJournal


def make_candles(direction: str, rows: int = 60) -> pd.DataFrame:
    """Create deterministic bullish or bearish candles for flow integration tests."""
    if direction == "BUY":
        closes = [100.0 + index for index in range(rows)]
    elif direction == "SELL":
        closes = [200.0 - index for index in range(rows)]
    else:
        closes = [100.0 for _ in range(rows)]

    return pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=rows, freq="D"),
            "open": closes,
            "high": [value + 1.0 for value in closes],
            "low": [value - 1.0 for value in closes],
            "close": closes,
        }
    )


def run_flow(
    candles: pd.DataFrame,
    flow_config: PaperTradingFlowConfig,
    risk_config: RiskEngineConfig,
    journal: TradeJournal | None = None,
):
    """Run flow with risk config and defaults for integration assertions."""
    state = PaperBrokerState()
    result = PaperTradingFlow().run_single_timeframe(
        candles,
        flow_config,
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


def test_buy_flow_uses_risk_engine_sl_tp_volume() -> None:
    candles = make_candles("BUY")
    risk_config = RiskEngineConfig(
        account_balance=100.0,
        risk_per_trade_percent=1.0,
        default_stop_distance=1.0,
        reward_to_risk=1.0,
        min_volume=1.0,
        max_volume=1.0,
    )

    result, _state = run_flow(candles, PaperTradingFlowConfig(simulate_exit=False), risk_config)

    assert result.trade_executed is True
    assert result.risk_checked is True
    assert result.risk_allowed is True
    assert result.stop_loss == 158.0
    assert result.take_profit == 160.0
    assert result.volume == 1.0


def test_sell_flow_uses_risk_engine_sl_tp_volume() -> None:
    candles = make_candles("SELL")
    risk_config = RiskEngineConfig(
        account_balance=100.0,
        risk_per_trade_percent=1.0,
        default_stop_distance=1.0,
        reward_to_risk=1.0,
        min_volume=1.0,
        max_volume=1.0,
    )

    result, _state = run_flow(candles, PaperTradingFlowConfig(simulate_exit=False), risk_config)

    assert result.trade_executed is True
    assert result.risk_checked is True
    assert result.risk_allowed is True
    assert result.stop_loss == 142.0
    assert result.take_profit == 140.0
    assert result.volume == 1.0


def test_invalid_risk_config_blocks_trade() -> None:
    candles = make_candles("BUY")
    risk_config = RiskEngineConfig(risk_per_trade_percent=0.0)

    result, state = run_flow(candles, PaperTradingFlowConfig(simulate_exit=False), risk_config)

    assert result.trade_executed is False
    assert result.risk_checked is True
    assert result.risk_allowed is False
    assert result.status == "NO_TRADE"
    assert any("Risk per trade percent" in reason for reason in result.risk_blocking_reasons)
    assert len(state.open_positions) == 0


def test_risk_blocked_trade_is_recorded_in_journal() -> None:
    candles = make_candles("BUY")
    journal = TradeJournal()
    risk_config = RiskEngineConfig(risk_per_trade_percent=0.0)

    result, _state = run_flow(candles, PaperTradingFlowConfig(simulate_exit=False), risk_config, journal)

    assert result.journal_recorded is True
    entries = journal.get_all_entries()
    assert len(entries) == 1
    assert entries[0].executed is False
    assert entries[0].status == "BLOCKED"
    assert any("Risk per trade percent" in reason for reason in entries[0].blocking_reasons)


def test_executed_trade_journal_entry_includes_sl_tp_and_volume() -> None:
    candles = make_candles("BUY")
    journal = TradeJournal()
    risk_config = RiskEngineConfig(
        account_balance=100.0,
        risk_per_trade_percent=1.0,
        default_stop_distance=1.0,
        reward_to_risk=1.0,
        min_volume=1.0,
        max_volume=1.0,
    )

    result, _state = run_flow(candles, PaperTradingFlowConfig(simulate_exit=False), risk_config, journal)

    assert result.trade_executed is True
    entry = journal.get_all_entries()[0]
    assert entry.stop_loss == 158.0
    assert entry.take_profit == 160.0
    assert entry.volume == 1.0


def test_exit_simulator_uses_risk_generated_sl_tp() -> None:
    candles = make_candles("BUY")
    candles["high"] = 160.0
    candles["low"] = 159.0

    risk_config = RiskEngineConfig(
        account_balance=100.0,
        risk_per_trade_percent=1.0,
        default_stop_distance=1.0,
        reward_to_risk=1.0,
        min_volume=1.0,
        max_volume=1.0,
    )

    result, state = run_flow(
        candles,
        PaperTradingFlowConfig(simulate_exit=True, exit_simulation_config=ExitSimulationConfig(conservative_same_candle=True)),
        risk_config,
    )

    assert result.trade_executed is True
    assert result.exit_simulated is True
    assert result.exit_reason == "TAKE_PROFIT"
    assert result.exit_price == 160.0
    assert result.pnl == 1.0
    assert len(state.open_positions) == 0
