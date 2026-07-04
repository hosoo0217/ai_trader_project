"""Simple rolling-window backtest runner for paper trading flow.

This module repeatedly runs the paper trading flow on candle windows and
collects high-level backtest metrics. It is simulation-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Optional

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
from storage.decision_trace import DecisionTracer
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
    iteration_traces: list["BacktestIterationTrace"] = field(default_factory=list)


@dataclass
class BacktestIterationTrace:
    """Research-only diagnostic details for one rolling backtest iteration."""

    iteration_index: int
    window_start: int
    window_end: int
    final_action: str
    final_allowed: bool
    trade_executed: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    trace_id: str | None = None
    trace_explanation: str | None = None
    trace_steps: list[dict[str, Any]] = field(default_factory=list)
    decision_engine_status: str | None = None
    decision_engine_reasons: list[str] = field(default_factory=list)
    decision_engine_blocking_reasons: list[str] = field(default_factory=list)
    smc_status: str | None = None
    smc_reasons: list[str] = field(default_factory=list)
    smc_blocking_reasons: list[str] = field(default_factory=list)
    crt_status: str | None = None
    crt_reasons: list[str] = field(default_factory=list)
    crt_blocking_reasons: list[str] = field(default_factory=list)
    multi_timeframe_status: str | None = None
    multi_timeframe_reasons: list[str] = field(default_factory=list)
    multi_timeframe_blocking_reasons: list[str] = field(default_factory=list)
    orderflow_status: str | None = None
    orderflow_reasons: list[str] = field(default_factory=list)
    orderflow_blocking_reasons: list[str] = field(default_factory=list)
    safety_status: str | None = None
    safety_reasons: list[str] = field(default_factory=list)
    safety_blocking_reasons: list[str] = field(default_factory=list)
    risk_status: str | None = None
    risk_reasons: list[str] = field(default_factory=list)
    risk_blocking_reasons: list[str] = field(default_factory=list)
    trade_manager_status: str | None = None
    trade_manager_reasons: list[str] = field(default_factory=list)
    trade_manager_blocking_reasons: list[str] = field(default_factory=list)
    exit_simulator_status: str | None = None
    exit_simulator_reasons: list[str] = field(default_factory=list)
    exit_simulator_blocking_reasons: list[str] = field(default_factory=list)
    simulated_pnl: float | None = None
    outcome: str | None = None


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
        collect_iteration_traces: bool = False,
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
        iteration_traces: list[BacktestIterationTrace] = []

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
            exit_simulation_candles = candles.iloc[start + backtest_config.window_size :].copy()
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
                DecisionTracer() if collect_iteration_traces else None,
                orderflow_context_result=orderflow_context_result,
                exit_simulation_candles=exit_simulation_candles,
            )
            last_flow_result = flow_result

            iterations += 1
            if flow_result.trade_executed:
                executed += 1
            else:
                blocked += 1

            if collect_iteration_traces:
                iteration_traces.append(
                    self._build_iteration_trace(
                        iteration_index=iterations,
                        window_start=start,
                        window_end=start + backtest_config.window_size - 1,
                        flow_result=flow_result,
                    )
                )

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
            iteration_traces=iteration_traces,
        )

    def _build_iteration_trace(
        self,
        iteration_index: int,
        window_start: int,
        window_end: int,
        flow_result,
    ) -> BacktestIterationTrace:
        """Convert one paper-flow result into a stable diagnostic record."""
        trace_steps = [
            {
                "step_name": step.step_name,
                "status": step.status,
                "allowed": bool(step.allowed),
                "reasons": list(step.reasons),
                "blocking_reasons": list(step.blocking_reasons),
            }
            for step in getattr(flow_result, "trace_steps", [])
        ]

        def step_values(step_name: str) -> tuple[str | None, list[str], list[str]]:
            for step in trace_steps:
                if step["step_name"] == step_name:
                    return (
                        str(step["status"]),
                        list(step["reasons"]),
                        list(step["blocking_reasons"]),
                    )
            return None, [], []

        decision_status, decision_reasons, decision_blocks = step_values("DECISION_ENGINE")
        mtf_status, mtf_reasons, mtf_blocks = step_values("MULTI_TIMEFRAME")
        smc_status, _, _ = step_values("SMC_CONTEXT")
        crt_status, _, _ = step_values("CRT_CONTEXT")
        orderflow_status, _, _ = step_values("ORDER_FLOW_CONTEXT")
        risk_status, risk_reasons, risk_blocks = step_values("RISK_ENGINE")
        trade_status, trade_reasons, trade_blocks = step_values("TRADE_MANAGER")
        exit_status, exit_reasons, exit_blocks = step_values("EXIT_SIMULATOR")

        blocking_reasons = list(getattr(flow_result, "session_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "news_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "volatility_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "spread_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "safety_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "risk_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "smc_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "crt_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "orderflow_blocking_reasons", []))
        blocking_reasons.extend(getattr(flow_result, "alignment_blocking_reasons", []))
        for step in trace_steps:
            blocking_reasons.extend(step["blocking_reasons"])

        pnl = getattr(flow_result, "pnl", None)
        outcome = None
        if pnl is not None:
            if float(pnl) > 0:
                outcome = "WIN"
            elif float(pnl) < 0:
                outcome = "LOSS"
            else:
                outcome = "BREAKEVEN"

        return BacktestIterationTrace(
            iteration_index=iteration_index,
            window_start=window_start,
            window_end=window_end,
            final_action=str(getattr(flow_result, "decision_action", "NO_TRADE")),
            final_allowed=bool(getattr(flow_result, "trade_executed", False)),
            trade_executed=bool(getattr(flow_result, "trade_executed", False)),
            status=str(getattr(flow_result, "status", "UNKNOWN")),
            reasons=list(getattr(flow_result, "reasons", [])),
            blocking_reasons=list(dict.fromkeys(blocking_reasons)),
            trace_id=getattr(flow_result, "trace_id", None),
            trace_explanation=getattr(flow_result, "trace_explanation", None),
            trace_steps=trace_steps,
            decision_engine_status=decision_status,
            decision_engine_reasons=decision_reasons,
            decision_engine_blocking_reasons=decision_blocks,
            smc_status=smc_status or getattr(flow_result, "smc_bias", None),
            smc_reasons=list(getattr(flow_result, "smc_reasons", [])),
            smc_blocking_reasons=list(getattr(flow_result, "smc_blocking_reasons", [])),
            crt_status=crt_status or getattr(flow_result, "crt_bias", None),
            crt_reasons=list(getattr(flow_result, "crt_reasons", [])),
            crt_blocking_reasons=list(getattr(flow_result, "crt_blocking_reasons", [])),
            multi_timeframe_status=mtf_status,
            multi_timeframe_reasons=mtf_reasons,
            multi_timeframe_blocking_reasons=mtf_blocks,
            orderflow_status=orderflow_status or getattr(flow_result, "orderflow_bias", None),
            orderflow_reasons=list(getattr(flow_result, "orderflow_reasons", [])),
            orderflow_blocking_reasons=list(getattr(flow_result, "orderflow_blocking_reasons", [])),
            safety_status=getattr(flow_result, "safety_status", None),
            safety_reasons=list(getattr(flow_result, "safety_reasons", [])),
            safety_blocking_reasons=list(getattr(flow_result, "safety_blocking_reasons", [])),
            risk_status=risk_status or ("ALLOWED" if bool(getattr(flow_result, "risk_allowed", False)) else "BLOCKED"),
            risk_reasons=risk_reasons or list(getattr(flow_result, "risk_reasons", [])),
            risk_blocking_reasons=risk_blocks or list(getattr(flow_result, "risk_blocking_reasons", [])),
            trade_manager_status=trade_status,
            trade_manager_reasons=trade_reasons,
            trade_manager_blocking_reasons=trade_blocks,
            exit_simulator_status=exit_status,
            exit_simulator_reasons=exit_reasons,
            exit_simulator_blocking_reasons=exit_blocks,
            simulated_pnl=float(pnl) if pnl is not None else None,
            outcome=outcome,
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
