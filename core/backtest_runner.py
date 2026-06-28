"""Simple rolling-window backtest runner for paper trading flow.

This module repeatedly runs the paper trading flow on candle windows and
collects high-level backtest metrics. It is simulation-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Optional

import pandas as pd

from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.performance_report import PerformanceReporter
from storage.trade_journal import TradeJournal


@dataclass
class BacktestConfig:
    """Configuration for rolling-window backtests."""

    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    window_size: int = 60
    step_size: int = 5
    max_iterations: int | None = None


@dataclass
class BacktestResult:
    """High-level output from a backtest run."""

    completed: bool
    status: str
    total_iterations: int
    trades_executed: int
    trades_blocked: int
    final_balance: float
    total_pnl: float
    reasons: list[str] = field(default_factory=list)


class BacktestRunner:
    """Run the paper trading flow over candle windows for research only."""

    def run(
        self,
        candles: Optional[pd.DataFrame],
        backtest_config: BacktestConfig,
        flow_config: PaperTradingFlowConfig,
        market_config: MarketAnalyzerConfig,
        mtf_config: MultiTimeframeConfig,
        capital_config: CapitalProtectionConfig,
        capital_state: CapitalProtectionState,
        broker_config: PaperBrokerConfig,
        broker_state: PaperBrokerState,
        risk_config: RiskEngineConfig,
        journal: Optional[TradeJournal],
    ) -> BacktestResult:
        """Execute rolling-window paper-flow runs and aggregate simple metrics."""
        if candles is None or not isinstance(candles, pd.DataFrame):
            return BacktestResult(
                completed=True,
                status="NO_DATA",
                total_iterations=0,
                trades_executed=0,
                trades_blocked=0,
                final_balance=float(broker_state.balance),
                total_pnl=0.0,
                reasons=["Invalid candle data"],
            )

        if backtest_config.window_size <= 0 or backtest_config.step_size <= 0:
            return BacktestResult(
                completed=True,
                status="INVALID_CONFIG",
                total_iterations=0,
                trades_executed=0,
                trades_blocked=0,
                final_balance=float(broker_state.balance),
                total_pnl=0.0,
                reasons=["Window size and step size must be positive"],
            )

        if len(candles) < backtest_config.window_size:
            return BacktestResult(
                completed=True,
                status="NO_ITERATIONS",
                total_iterations=0,
                trades_executed=0,
                trades_blocked=0,
                final_balance=float(broker_state.balance),
                total_pnl=0.0,
                reasons=["Not enough candles for one full backtest window"],
            )

        target_journal = journal if journal is not None else TradeJournal()
        flow = PaperTradingFlow()
        iterations = 0
        executed = 0
        blocked = 0

        effective_flow_config = replace(
            flow_config,
            symbol=backtest_config.symbol,
            timeframe=backtest_config.timeframe,
        )

        max_start = len(candles) - backtest_config.window_size
        for start in range(0, max_start + 1, backtest_config.step_size):
            if backtest_config.max_iterations is not None and iterations >= backtest_config.max_iterations:
                break

            window = candles.iloc[start : start + backtest_config.window_size].copy()
            flow_result = flow.run_single_timeframe(
                window,
                effective_flow_config,
                market_config,
                mtf_config,
                capital_config,
                capital_state,
                broker_config,
                broker_state,
                target_journal,
                risk_config,
            )

            iterations += 1
            if flow_result.trade_executed:
                executed += 1
            else:
                blocked += 1

        performance = PerformanceReporter().generate_report(target_journal)
        reasons = [
            "Backtest completed",
            f"Journal entries: {performance.total_trades}",
        ]
        if backtest_config.max_iterations is not None and iterations >= backtest_config.max_iterations:
            reasons.append("Stopped at max_iterations")

        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=iterations,
            trades_executed=executed,
            trades_blocked=blocked,
            final_balance=float(broker_state.balance),
            total_pnl=float(performance.total_pnl),
            reasons=reasons,
        )

    def explain(self, result: BacktestResult) -> str:
        """Return a readable summary of the backtest result."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "No reasons"
        return (
            f"Backtest status: {result.status} | iterations: {result.total_iterations} | "
            f"executed: {result.trades_executed} | blocked: {result.trades_blocked} | "
            f"final balance: {result.final_balance:.2f} | total pnl: {result.total_pnl:.2f} | "
            f"reasons: {reasons_text}"
        )
