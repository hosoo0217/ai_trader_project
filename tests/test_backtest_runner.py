"""Unit tests for BacktestRunner."""

from pathlib import Path

import pandas as pd

from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.backtest_runner import BacktestConfig, BacktestResult, BacktestRunner
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlowConfig, PaperTradingFlowResult
from risk.risk_engine import RiskEngineConfig
from storage.trade_journal import TradeJournal


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_sample(file_name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / file_name)


def run_backtest(candles: pd.DataFrame, config: BacktestConfig, journal: TradeJournal | None = None) -> BacktestResult:
    runner = BacktestRunner()
    return runner.run(
        candles,
        config,
        PaperTradingFlowConfig(simulate_exit=True),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
        RiskEngineConfig(),
        journal,
    )


def test_backtest_runs_on_bullish_sample_without_crashing() -> None:
    result = run_backtest(
        load_sample("bullish_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=5),
    )

    assert result.completed is True
    assert result.total_iterations >= 1


def test_backtest_runs_on_bearish_sample_without_crashing() -> None:
    result = run_backtest(
        load_sample("bearish_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=5),
    )

    assert result.completed is True
    assert result.total_iterations >= 1


def test_weak_or_small_data_does_not_crash() -> None:
    result = run_backtest(
        load_sample("weak_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=5),
    )

    assert result.completed is True
    assert result.total_iterations == 0


def test_journal_receives_entries() -> None:
    journal = TradeJournal()
    run_backtest(
        load_sample("bullish_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=5),
        journal,
    )

    assert len(journal.get_all_entries()) >= 1


def test_result_includes_total_iterations() -> None:
    result = run_backtest(
        load_sample("bullish_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=5),
    )

    assert isinstance(result.total_iterations, int)


def test_max_iterations_limits_run() -> None:
    result = run_backtest(
        load_sample("bullish_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=1, max_iterations=2),
    )

    assert result.total_iterations == 2


def test_max_iterations_three_can_run_when_enough_candles_exist() -> None:
    result = run_backtest(
        load_sample("bullish_sample_xauusd.csv"),
        BacktestConfig(window_size=60, step_size=1, max_iterations=3),
    )

    assert result.total_iterations == 3


def test_explain_returns_readable_text() -> None:
    runner = BacktestRunner()
    text = runner.explain(
        BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=2,
            trades_executed=1,
            trades_blocked=1,
            final_balance=10000.0,
            total_pnl=5.0,
            reasons=["Backtest completed"],
        )
    )

    assert "Backtest status" in text
    assert "iterations" in text
    assert "total pnl" in text


def test_backtest_passes_post_entry_candles_to_exit_simulation(monkeypatch) -> None:
    captured_exit_candles = []

    class CapturingFlow:
        def run_single_timeframe(self, candles, *args, **kwargs):
            captured_exit_candles.append(kwargs.get("exit_simulation_candles"))
            return PaperTradingFlowResult(
                completed=True,
                status="BLOCKED",
                trade_executed=False,
                reasons=["test flow result"],
            )

    monkeypatch.setattr("core.backtest_runner.PaperTradingFlow", CapturingFlow)

    candles = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=65, freq="min"),
            "open": [100.0 + index for index in range(65)],
            "high": [101.0 + index for index in range(65)],
            "low": [99.0 + index for index in range(65)],
            "close": [100.0 + index for index in range(65)],
        }
    )

    result = run_backtest(
        candles,
        BacktestConfig(window_size=60, step_size=1, max_iterations=1),
    )

    assert result.completed is True
    assert len(captured_exit_candles) == 1
    assert captured_exit_candles[0] is not None
    assert list(captured_exit_candles[0].index) == [60, 61, 62, 63, 64]
