"""Simple rolling-window backtest runner for paper trading flow.

This module repeatedly runs the paper trading flow on candle windows and
collects high-level backtest metrics. It is simulation-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from analysis.news_filter import NewsFilterConfig
from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from orderflow.orderflow_context import OrderFlowContextResult
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
    session_checked: bool = False
    session_allowed: bool = False
    active_session: str | None = None
    session_status: str | None = None
    session_reasons: list[str] = field(default_factory=list)
    session_blocking_reasons: list[str] = field(default_factory=list)
    news_checked: bool = False
    news_allowed: bool = False
    news_status: str | None = None
    active_news_event: str | None = None
    news_reasons: list[str] = field(default_factory=list)
    news_blocking_reasons: list[str] = field(default_factory=list)
    volatility_checked: bool = False
    volatility_allowed: bool = False
    volatility_status: str | None = None
    atr: float | None = None
    last_candle_range: float | None = None
    volatility_reasons: list[str] = field(default_factory=list)
    volatility_blocking_reasons: list[str] = field(default_factory=list)
    spread_checked: bool = False
    spread_allowed: bool = False
    spread_status: str | None = None
    spread: float | None = None
    spread_reasons: list[str] = field(default_factory=list)
    spread_blocking_reasons: list[str] = field(default_factory=list)


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
        session_config: Optional[SessionFilterConfig] = None,
        session_time_fallback: Optional[datetime] = None,
        news_config: Optional[NewsFilterConfig] = None,
        volatility_config: Optional[VolatilityFilterConfig] = None,
        spread_config: Optional[SpreadFilterConfig] = None,
        current_spread: Optional[float] = None,
        orderflow_context_result: Optional[OrderFlowContextResult] = None,
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
        last_flow_result = None
        time_parse_fallback_used = False

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
            window_current_time = self._resolve_window_time(window, session_time_fallback)
            if window_current_time is None:
                time_parse_fallback_used = True
                window_current_time = datetime.now(timezone.utc)

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
                session_config,
                window_current_time,
                news_config,
                volatility_config,
                spread_config,
                current_spread,
                orderflow_context_result=orderflow_context_result,
            )
            last_flow_result = flow_result

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
        if time_parse_fallback_used:
            reasons.append("Session time parse fallback to current UTC was used")
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
            session_checked=bool(getattr(last_flow_result, "session_checked", False)),
            session_allowed=bool(getattr(last_flow_result, "session_allowed", False)),
            active_session=getattr(last_flow_result, "active_session", None),
            session_status=getattr(last_flow_result, "session_status", None),
            session_reasons=list(getattr(last_flow_result, "session_reasons", [])),
            session_blocking_reasons=list(getattr(last_flow_result, "session_blocking_reasons", [])),
            news_checked=bool(getattr(last_flow_result, "news_checked", False)),
            news_allowed=bool(getattr(last_flow_result, "news_allowed", False)),
            news_status=getattr(last_flow_result, "news_status", None),
            active_news_event=getattr(last_flow_result, "active_news_event", None),
            news_reasons=list(getattr(last_flow_result, "news_reasons", [])),
            news_blocking_reasons=list(getattr(last_flow_result, "news_blocking_reasons", [])),
            volatility_checked=bool(getattr(last_flow_result, "volatility_checked", False)),
            volatility_allowed=bool(getattr(last_flow_result, "volatility_allowed", False)),
            volatility_status=getattr(last_flow_result, "volatility_status", None),
            atr=getattr(last_flow_result, "atr", None),
            last_candle_range=getattr(last_flow_result, "last_candle_range", None),
            volatility_reasons=list(getattr(last_flow_result, "volatility_reasons", [])),
            volatility_blocking_reasons=list(getattr(last_flow_result, "volatility_blocking_reasons", [])),
            spread_checked=bool(getattr(last_flow_result, "spread_checked", False)),
            spread_allowed=bool(getattr(last_flow_result, "spread_allowed", False)),
            spread_status=getattr(last_flow_result, "spread_status", None),
            spread=getattr(last_flow_result, "spread", None),
            spread_reasons=list(getattr(last_flow_result, "spread_reasons", [])),
            spread_blocking_reasons=list(getattr(last_flow_result, "spread_blocking_reasons", [])),
        )

    def _resolve_window_time(
        self,
        window: pd.DataFrame,
        session_time_fallback: Optional[datetime],
    ) -> Optional[datetime]:
        """Resolve session time from the last candle in a window.

        Returns a timezone-aware UTC datetime when possible.
        """
        if "time" in window.columns and not window.empty:
            parsed = pd.to_datetime(window["time"].iloc[-1], errors="coerce", utc=True)
            if not pd.isna(parsed):
                return parsed.to_pydatetime()

        if session_time_fallback is not None:
            if session_time_fallback.tzinfo is None:
                return session_time_fallback.replace(tzinfo=timezone.utc)
            return session_time_fallback.astimezone(timezone.utc)

        return None

    def explain(self, result: BacktestResult) -> str:
        """Return a readable summary of the backtest result."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "No reasons"
        return (
            f"Backtest status: {result.status} | iterations: {result.total_iterations} | "
            f"executed: {result.trades_executed} | blocked: {result.trades_blocked} | "
            f"final balance: {result.final_balance:.2f} | total pnl: {result.total_pnl:.2f} | "
            f"reasons: {reasons_text}"
        )
