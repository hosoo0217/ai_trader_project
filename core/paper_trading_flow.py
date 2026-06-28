"""Full paper trading pipeline for research and backtesting.

This module wires together the market analyzer, multi-timeframe combiner,
capital protection, decision engine, and paper broker into one safe flow.
It only simulates orders in memory and never connects to a live broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

import pandas as pd

from analysis.news_filter import NewsFilter, NewsFilterConfig
from analysis.session_filter import SessionFilter, SessionFilterConfig
from analysis.spread_filter import SpreadFilter, SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilter, VolatilityFilterConfig
from broker.paper_broker import PaperBroker, PaperBrokerConfig, PaperBrokerState
from crt.crt_engine import CRTConfig, CRTEngine, CRTResult
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionEngine, CapitalProtectionState
from core.context_alignment import ContextAlignmentConfig, ContextAlignmentGate, ContextAlignmentResult
from core.decision_context import DecisionContext, MarketContext, SMCContext, CRTContext, OrderFlowContext, RiskContext
from core.decision_engine import DecisionEngine, DecisionResult
from core.exit_simulator import ExitSimulationConfig, ExitSimulator
from core.market_analyzer import MarketAnalysisResult, MarketAnalyzer, MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeBiasCombiner, MultiTimeframeConfig, MultiTimeframeDecision
from core.safety_gate import SafetyGate
from core.trade_manager import TradeManager, TradeRequest
from risk.risk_engine import RiskEngine, RiskEngineConfig
from smc.bos_choch import BOSCHOCHAnalyzer, BOSCHOCHConfig
from smc.liquidity_sweep import LiquiditySweepAnalyzer, LiquiditySweepConfig
from smc.market_structure import MarketStructureAnalyzer, MarketStructureConfig
from smc.smc_context import SMCContextCombiner, SMCContextConfig, SMCContextResult
from storage.decision_trace import DecisionTrace, DecisionTracer
from storage.trade_journal import TradeJournal, TradeJournalEntry


@dataclass
class PaperTradingFlowConfig:
    """Configuration for the paper trading flow."""

    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    default_volume: float = 1.0
    default_price_column: str = "close"
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    simulate_exit: bool = False
    exit_simulation_config: ExitSimulationConfig = field(default_factory=ExitSimulationConfig)


@dataclass
class PaperTradingFlowResult:
    """Result of a full paper trading flow run."""

    completed: bool = False
    status: str = "REJECTED"
    market_bias: str = "UNKNOWN"
    decision_action: str = "NO_TRADE"
    trade_executed: bool = False
    reasons: List[str] = field(default_factory=list)
    balance: Optional[float] = None
    journal_recorded: bool = False
    journal_trade_id: Optional[str] = None
    session_checked: bool = False
    session_allowed: bool = False
    active_session: Optional[str] = None
    session_status: Optional[str] = None
    session_reasons: List[str] = field(default_factory=list)
    session_blocking_reasons: List[str] = field(default_factory=list)
    news_checked: bool = False
    news_allowed: bool = False
    news_status: Optional[str] = None
    active_news_event: Optional[str] = None
    news_reasons: List[str] = field(default_factory=list)
    news_blocking_reasons: List[str] = field(default_factory=list)
    volatility_checked: bool = False
    volatility_allowed: bool = False
    volatility_status: Optional[str] = None
    atr: Optional[float] = None
    last_candle_range: Optional[float] = None
    volatility_reasons: List[str] = field(default_factory=list)
    volatility_blocking_reasons: List[str] = field(default_factory=list)
    spread_checked: bool = False
    spread_allowed: bool = False
    spread_status: Optional[str] = None
    spread: Optional[float] = None
    spread_reasons: List[str] = field(default_factory=list)
    spread_blocking_reasons: List[str] = field(default_factory=list)
    safety_checked: bool = False
    safety_allowed: bool = False
    safety_status: Optional[str] = None
    safety_reasons: List[str] = field(default_factory=list)
    safety_blocking_reasons: List[str] = field(default_factory=list)
    safety_passed_checks: List[str] = field(default_factory=list)
    safety_failed_checks: List[str] = field(default_factory=list)
    risk_checked: bool = False
    risk_allowed: bool = False
    risk_reasons: List[str] = field(default_factory=list)
    risk_blocking_reasons: List[str] = field(default_factory=list)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    volume: Optional[float] = None
    exit_simulated: bool = False
    exit_reason: Optional[str] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    trace_id: Optional[str] = None
    trace_explanation: Optional[str] = None
    smc_checked: bool = False
    smc_bias: Optional[str] = None
    smc_confidence: Optional[float] = None
    smc_reasons: List[str] = field(default_factory=list)
    smc_blocking_reasons: List[str] = field(default_factory=list)
    crt_checked: bool = False
    crt_bias: str | None = None
    crt_signal_type: str | None = None
    crt_reasons: List[str] = field(default_factory=list)
    crt_blocking_reasons: List[str] = field(default_factory=list)
    alignment_checked: bool = False
    alignment_allowed: bool = False
    alignment_status: str | None = None
    aligned_bias: str | None = None
    confidence_adjustment: float = 0.0
    alignment_reasons: List[str] = field(default_factory=list)
    alignment_blocking_reasons: List[str] = field(default_factory=list)


class PaperTradingFlow:
    """Run a safe paper-trading flow from candles to simulated orders."""

    def run_single_timeframe(
        self,
        candles: Optional[pd.DataFrame],
        flow_config: PaperTradingFlowConfig,
        market_config: MarketAnalyzerConfig,
        mtf_config: MultiTimeframeConfig,
        capital_config: CapitalProtectionConfig,
        capital_state: CapitalProtectionState,
        broker_config: PaperBrokerConfig,
        broker_state: PaperBrokerState,
        journal: Optional[TradeJournal] = None,
        risk_config: Optional[RiskEngineConfig] = None,
        session_config: Optional[SessionFilterConfig] = None,
        current_time: Optional[datetime] = None,
        news_config: Optional[NewsFilterConfig] = None,
        volatility_config: Optional[VolatilityFilterConfig] = None,
        spread_config: Optional[SpreadFilterConfig] = None,
        current_spread: Optional[float] = None,
        tracer: Optional[DecisionTracer] = None,
        smc_enabled: bool = True,
        smc_market_structure_config: Optional[MarketStructureConfig] = None,
        smc_bos_choch_config: Optional[BOSCHOCHConfig] = None,
        smc_liquidity_sweep_config: Optional[LiquiditySweepConfig] = None,
        smc_context_config: Optional[SMCContextConfig] = None,
        crt_enabled: bool = True,
        crt_config: Optional[CRTConfig] = None,
        alignment_config: Optional[ContextAlignmentConfig] = None,
    ) -> PaperTradingFlowResult:
        """Run the paper flow using a single candle dataset for all timeframes."""
        decision_trace = self._create_decision_trace(tracer, flow_config.symbol)
        if candles is None or not isinstance(candles, pd.DataFrame):
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=["Invalid candle data"],
                blocking_reasons=["Invalid candle data"],
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Invalid candle data decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Invalid candle data"],
                balance=None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                ),
                tracer,
                decision_trace,
            )

        required_columns = {"time", "open", "high", "low", "close"}
        if not required_columns.issubset(candles.columns):
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=["Missing required candle columns"],
                blocking_reasons=["Missing required candle columns"],
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Missing-column decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Missing required candle columns"],
                balance=None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                ),
                tracer,
                decision_trace,
            )

        # Temporary simplification for v1: reuse the same candle data for all requested
        # higher timeframes so the pipeline can be tested end-to-end before real multi-timeframe
        # data is introduced.
        timeframe_data = {
            "W1": candles,
            "D1": candles,
            "H4": candles,
            "H1": candles,
            "M15": candles,
            "M5": candles,
        }

        market_analyzer = MarketAnalyzer()
        market_results = market_analyzer.analyze_multi_timeframe(timeframe_data, market_config)
        if not market_results:
            self._trace_step(
                tracer,
                decision_trace,
                "MARKET_ANALYZER",
                "NO_RESULTS",
                False,
                reasons=["No market analysis results"],
                blocking_reasons=["No market analysis results"],
            )
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=["No market analysis results"],
                blocking_reasons=["No market analysis results"],
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["No-market-analysis decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["No market analysis results"],
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                ),
                tracer,
                decision_trace,
            )

        primary_result = market_results.get(flow_config.timeframe) or next(iter(market_results.values()))
        if primary_result.bias == "UNKNOWN":
            self._trace_step(
                tracer,
                decision_trace,
                "MARKET_ANALYZER",
                "UNKNOWN",
                False,
                reasons=["Market analysis returned UNKNOWN"],
                blocking_reasons=["Market analysis returned UNKNOWN"],
            )
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=["Market analysis returned UNKNOWN"],
                blocking_reasons=["Market analysis returned UNKNOWN"],
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Unknown-bias decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Market analysis returned UNKNOWN"],
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                ),
                tracer,
                decision_trace,
            )

        self._trace_step(
            tracer,
            decision_trace,
            "MARKET_ANALYZER",
            primary_result.bias,
            True,
            reasons=list(getattr(primary_result, "reasons", [])),
            blocking_reasons=list(getattr(primary_result, "blocking_reasons", [])),
        )

        mtf_combiner = MultiTimeframeBiasCombiner()
        mtf_decision = mtf_combiner.combine(market_results, mtf_config)
        self._trace_step(
            tracer,
            decision_trace,
            "MULTI_TIMEFRAME",
            mtf_decision.bias,
            bool(mtf_decision.allowed and mtf_decision.bias not in {"NO_TRADE", "WAIT"}),
            reasons=list(getattr(mtf_decision, "reasons", [])),
            blocking_reasons=list(getattr(mtf_decision, "blocking_reasons", [])),
        )
        if mtf_decision.bias in {"NO_TRADE", "WAIT"} or not mtf_decision.allowed:
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=["Multi-timeframe decision blocked trading"],
                blocking_reasons=["Multi-timeframe decision blocked trading"],
                confidence=mtf_decision.confidence,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Multi-timeframe blocked decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Multi-timeframe decision blocked trading"],
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                ),
                tracer,
                decision_trace,
            )

        smc_checked = False
        smc_context_result: Optional[SMCContextResult] = None
        smc_bias: Optional[str] = None
        smc_confidence: Optional[float] = None
        smc_reasons: List[str] = []
        smc_blocking_reasons: List[str] = []
        crt_checked = False
        crt_result: Optional[CRTResult] = None
        crt_bias: str | None = None
        crt_signal_type: str | None = None
        crt_reasons: List[str] = []
        crt_blocking_reasons: List[str] = []
        alignment_checked = False
        alignment_result: Optional[ContextAlignmentResult] = None
        alignment_allowed = False
        alignment_status: str | None = None
        aligned_bias: str | None = None
        confidence_adjustment = 0.0
        alignment_reasons: List[str] = []
        alignment_blocking_reasons: List[str] = []

        if smc_enabled:
            smc_checked = True
            market_structure_result = MarketStructureAnalyzer().analyze(
                candles,
                smc_market_structure_config or MarketStructureConfig(),
            )
            self._trace_step(
                tracer,
                decision_trace,
                "SMC_MARKET_STRUCTURE",
                market_structure_result.structure_bias,
                market_structure_result.structure_bias in {"BULLISH", "BEARISH", "NEUTRAL"},
                reasons=list(market_structure_result.reasons),
                blocking_reasons=list(market_structure_result.blocking_reasons),
            )

            bos_choch_result = BOSCHOCHAnalyzer().analyze(
                candles,
                market_structure_result,
                smc_bos_choch_config or BOSCHOCHConfig(),
            )
            self._trace_step(
                tracer,
                decision_trace,
                "SMC_BOS_CHOCH",
                bos_choch_result.bias,
                bos_choch_result.bias in {"BULLISH", "BEARISH", "NEUTRAL"},
                reasons=list(bos_choch_result.reasons),
                blocking_reasons=list(bos_choch_result.blocking_reasons),
            )

            liquidity_sweep_result = LiquiditySweepAnalyzer().analyze(
                candles,
                market_structure_result,
                smc_liquidity_sweep_config or LiquiditySweepConfig(),
            )
            self._trace_step(
                tracer,
                decision_trace,
                "SMC_LIQUIDITY_SWEEP",
                liquidity_sweep_result.bias,
                liquidity_sweep_result.bias in {"BULLISH", "BEARISH", "NEUTRAL"},
                reasons=list(liquidity_sweep_result.reasons),
                blocking_reasons=list(liquidity_sweep_result.blocking_reasons),
            )

            smc_context_result = SMCContextCombiner().combine(
                market_structure_result=market_structure_result,
                bos_choch_result=bos_choch_result,
                liquidity_sweep_result=liquidity_sweep_result,
                config=smc_context_config or SMCContextConfig(),
            )
            smc_bias = smc_context_result.bias
            smc_confidence = smc_context_result.confidence
            smc_reasons = list(smc_context_result.reasons)
            smc_blocking_reasons = list(smc_context_result.blocking_reasons)
            self._trace_step(
                tracer,
                decision_trace,
                "SMC_CONTEXT",
                smc_context_result.bias,
                smc_context_result.bias in {"BULLISH", "BEARISH", "NEUTRAL"},
                reasons=list(smc_context_result.reasons),
                blocking_reasons=list(smc_context_result.blocking_reasons),
            )

        if crt_enabled:
            crt_checked = True
            try:
                crt_result = CRTEngine().analyze(candles, crt_config or CRTConfig())
            except Exception as error:
                crt_result = CRTResult(
                    bias="UNKNOWN",
                    reasons=[f"CRT engine failed safely: {error}"],
                    blocking_reasons=["CRT engine failed safely"],
                )

            crt_bias = crt_result.bias
            crt_signal_type = getattr(getattr(crt_result, "latest_signal", None), "signal_type", None)
            crt_reasons = list(crt_result.reasons)
            crt_blocking_reasons = list(crt_result.blocking_reasons)

            self._trace_step(
                tracer,
                decision_trace,
                "CRT_ENGINE",
                crt_signal_type or crt_result.bias,
                crt_result.bias in {"BULLISH", "BEARISH", "NEUTRAL", "UNKNOWN"},
                reasons=list(crt_result.reasons),
                blocking_reasons=list(crt_result.blocking_reasons),
            )
            self._trace_step(
                tracer,
                decision_trace,
                "CRT_CONTEXT",
                crt_result.bias,
                crt_result.bias in {"BULLISH", "BEARISH", "NEUTRAL", "UNKNOWN"},
                reasons=list(crt_result.reasons),
                blocking_reasons=list(crt_result.blocking_reasons),
            )

        capital_engine = CapitalProtectionEngine()
        capital_decision = capital_engine.evaluate(capital_config, capital_state)
        self._trace_step(
            tracer,
            decision_trace,
            "CAPITAL_PROTECTION",
            capital_decision.status,
            bool(capital_decision.allowed),
            reasons=list(getattr(capital_decision, "reasons", [])),
            blocking_reasons=list(getattr(capital_decision, "reasons", [])) if not capital_decision.allowed else [],
        )

        effective_current_time = current_time if current_time is not None else datetime.now(timezone.utc)
        session_result = None
        news_result = None
        volatility_result = None
        spread_result = None

        if capital_decision.allowed:
            effective_session_config = session_config or SessionFilterConfig()
            session_result = SessionFilter().evaluate(effective_current_time, effective_session_config)
            self._trace_step(
                tracer,
                decision_trace,
                "SESSION_FILTER",
                str(getattr(session_result, "status", "UNKNOWN")),
                bool(getattr(session_result, "allowed", False)),
                reasons=list(getattr(session_result, "reasons", [])),
                blocking_reasons=list(getattr(session_result, "blocking_reasons", [])),
            )

        if session_result is not None and session_result.allowed:
            effective_news_config = news_config or NewsFilterConfig()
            news_result = NewsFilter().evaluate(effective_current_time, effective_news_config)
            self._trace_step(
                tracer,
                decision_trace,
                "NEWS_FILTER",
                str(getattr(news_result, "status", "UNKNOWN")),
                bool(getattr(news_result, "allowed", False)),
                reasons=list(getattr(news_result, "reasons", [])),
                blocking_reasons=list(getattr(news_result, "blocking_reasons", [])),
            )

        if news_result is not None and news_result.allowed:
            effective_volatility_config = volatility_config or VolatilityFilterConfig()
            volatility_result = VolatilityFilter().evaluate(candles, effective_volatility_config)
            self._trace_step(
                tracer,
                decision_trace,
                "VOLATILITY_FILTER",
                str(getattr(volatility_result, "status", "UNKNOWN")),
                bool(getattr(volatility_result, "allowed", False)),
                reasons=list(getattr(volatility_result, "reasons", [])),
                blocking_reasons=list(getattr(volatility_result, "blocking_reasons", [])),
            )

        if volatility_result is not None and volatility_result.allowed:
            effective_spread_config = spread_config or SpreadFilterConfig()
            spread_result = SpreadFilter().evaluate(current_spread, effective_spread_config)
            self._trace_step(
                tracer,
                decision_trace,
                "SPREAD_FILTER",
                str(getattr(spread_result, "status", "UNKNOWN")),
                bool(getattr(spread_result, "allowed", False)),
                reasons=list(getattr(spread_result, "reasons", [])),
                blocking_reasons=list(getattr(spread_result, "blocking_reasons", [])),
            )

        safety_decision = SafetyGate().evaluate(
            session_result=session_result,
            news_result=news_result,
            volatility_result=volatility_result,
            spread_result=spread_result,
            capital_decision=capital_decision,
        )
        self._trace_step(
            tracer,
            decision_trace,
            "SAFETY_GATE",
            safety_decision.status,
            bool(safety_decision.allowed),
            reasons=list(getattr(safety_decision, "reasons", [])),
            blocking_reasons=list(getattr(safety_decision, "blocking_reasons", [])),
        )

        if not safety_decision.allowed:
            safety_status_reasons: List[str] = []
            if "CAPITAL_PROTECTION" in safety_decision.failed_checks:
                safety_status_reasons.append(f"Capital protection status: {capital_decision.status}")
            if "SESSION" in safety_decision.failed_checks and session_result is not None:
                safety_status_reasons.append(f"Session status: {session_result.status}")
            if "NEWS" in safety_decision.failed_checks and news_result is not None:
                safety_status_reasons.append(f"News status: {news_result.status}")
            if "VOLATILITY" in safety_decision.failed_checks and volatility_result is not None:
                safety_status_reasons.append(f"Volatility status: {volatility_result.status}")
            if "SPREAD" in safety_decision.failed_checks and spread_result is not None:
                safety_status_reasons.append(f"Spread status: {spread_result.status}")

            blocked_reasons = [
                *safety_status_reasons,
                *list(safety_decision.reasons),
                *list(safety_decision.blocking_reasons),
            ]
            blocked_blocking_reasons = [
                *safety_status_reasons,
                *list(safety_decision.blocking_reasons),
            ]

            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=[
                    *blocked_reasons,
                    *[f"SMC: {item}" for item in smc_reasons],
                    *[f"CRT: {item}" for item in crt_reasons],
                ],
                blocking_reasons=[
                    *blocked_blocking_reasons,
                    *[f"SMC: {item}" for item in smc_blocking_reasons],
                    *[f"CRT: {item}" for item in crt_blocking_reasons],
                ],
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Safety blocked decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=blocked_reasons,
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                session_checked=session_result is not None,
                session_allowed=bool(getattr(session_result, "allowed", False)),
                active_session=getattr(session_result, "active_session", None),
                session_status=getattr(session_result, "status", None),
                session_reasons=list(getattr(session_result, "reasons", [])),
                session_blocking_reasons=list(getattr(session_result, "blocking_reasons", [])),
                news_checked=news_result is not None,
                news_allowed=bool(getattr(news_result, "allowed", False)),
                news_status=getattr(news_result, "status", None),
                active_news_event=getattr(news_result, "active_event", None),
                news_reasons=list(getattr(news_result, "reasons", [])),
                news_blocking_reasons=list(getattr(news_result, "blocking_reasons", [])),
                volatility_checked=volatility_result is not None,
                volatility_allowed=bool(getattr(volatility_result, "allowed", False)),
                volatility_status=getattr(volatility_result, "status", None),
                atr=getattr(volatility_result, "atr", None),
                last_candle_range=getattr(volatility_result, "last_candle_range", None),
                volatility_reasons=list(getattr(volatility_result, "reasons", [])),
                volatility_blocking_reasons=list(getattr(volatility_result, "blocking_reasons", [])),
                spread_checked=spread_result is not None,
                spread_allowed=bool(getattr(spread_result, "allowed", False)),
                spread_status=getattr(spread_result, "status", None),
                spread=getattr(spread_result, "spread", None),
                spread_reasons=list(getattr(spread_result, "reasons", [])),
                spread_blocking_reasons=list(getattr(spread_result, "blocking_reasons", [])),
                safety_checked=True,
                safety_allowed=False,
                safety_status=safety_decision.status,
                safety_reasons=list(safety_decision.reasons),
                safety_blocking_reasons=list(safety_decision.blocking_reasons),
                safety_passed_checks=list(safety_decision.passed_checks),
                safety_failed_checks=list(safety_decision.failed_checks),
                smc_checked=smc_checked,
                smc_bias=smc_bias,
                smc_confidence=smc_confidence,
                smc_reasons=list(smc_reasons),
                smc_blocking_reasons=list(smc_blocking_reasons),
                crt_checked=crt_checked,
                crt_bias=crt_bias,
                crt_signal_type=crt_signal_type,
                crt_reasons=list(crt_reasons),
                crt_blocking_reasons=list(crt_blocking_reasons),
                alignment_checked=alignment_checked,
                alignment_allowed=alignment_allowed,
                alignment_status=alignment_status,
                aligned_bias=aligned_bias,
                confidence_adjustment=confidence_adjustment,
                alignment_reasons=list(alignment_reasons),
                alignment_blocking_reasons=list(alignment_blocking_reasons),
                ),
                tracer,
                decision_trace,
            )

        # Alignment gate is a context-quality validator only. It never executes trades.
        alignment_checked = True
        effective_alignment_config = alignment_config or ContextAlignmentConfig(enabled=False)
        alignment_result = ContextAlignmentGate().evaluate(
            smc_result=smc_context_result,
            crt_result=crt_result,
            config=effective_alignment_config,
        )
        alignment_allowed = bool(alignment_result.allowed)
        alignment_status = alignment_result.status
        aligned_bias = alignment_result.aligned_bias
        confidence_adjustment = float(alignment_result.confidence_adjustment)
        alignment_reasons = list(alignment_result.reasons)
        alignment_blocking_reasons = list(alignment_result.blocking_reasons)

        self._trace_step(
            tracer,
            decision_trace,
            "CONTEXT_ALIGNMENT",
            alignment_status or "UNKNOWN",
            alignment_allowed,
            reasons=list(alignment_reasons),
            blocking_reasons=list(alignment_blocking_reasons),
        )

        if not alignment_allowed:
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=[
                    *alignment_reasons,
                    *[f"SMC: {item}" for item in smc_reasons],
                    *[f"CRT: {item}" for item in crt_reasons],
                ],
                blocking_reasons=[
                    *alignment_blocking_reasons,
                    *[f"SMC: {item}" for item in smc_blocking_reasons],
                    *[f"CRT: {item}" for item in crt_blocking_reasons],
                ],
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Context-alignment blocked decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=list(alignment_reasons),
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                session_checked=True,
                session_allowed=True,
                active_session=session_result.active_session,
                session_status=session_result.status,
                session_reasons=list(session_result.reasons),
                session_blocking_reasons=list(session_result.blocking_reasons),
                news_checked=True,
                news_allowed=True,
                news_status=news_result.status,
                active_news_event=news_result.active_event,
                news_reasons=list(news_result.reasons),
                news_blocking_reasons=list(news_result.blocking_reasons),
                volatility_checked=True,
                volatility_allowed=True,
                volatility_status=volatility_result.status,
                atr=volatility_result.atr,
                last_candle_range=volatility_result.last_candle_range,
                volatility_reasons=list(volatility_result.reasons),
                volatility_blocking_reasons=list(volatility_result.blocking_reasons),
                spread_checked=True,
                spread_allowed=True,
                spread_status=spread_result.status,
                spread=spread_result.spread,
                spread_reasons=list(spread_result.reasons),
                spread_blocking_reasons=list(spread_result.blocking_reasons),
                safety_checked=True,
                safety_allowed=True,
                safety_status=safety_decision.status,
                safety_reasons=list(safety_decision.reasons),
                safety_blocking_reasons=list(safety_decision.blocking_reasons),
                safety_passed_checks=list(safety_decision.passed_checks),
                safety_failed_checks=list(safety_decision.failed_checks),
                smc_checked=smc_checked,
                smc_bias=smc_bias,
                smc_confidence=smc_confidence,
                smc_reasons=list(smc_reasons),
                smc_blocking_reasons=list(smc_blocking_reasons),
                crt_checked=crt_checked,
                crt_bias=crt_bias,
                crt_signal_type=crt_signal_type,
                crt_reasons=list(crt_reasons),
                crt_blocking_reasons=list(crt_blocking_reasons),
                alignment_checked=alignment_checked,
                alignment_allowed=alignment_allowed,
                alignment_status=alignment_status,
                aligned_bias=aligned_bias,
                confidence_adjustment=confidence_adjustment,
                alignment_reasons=list(alignment_reasons),
                alignment_blocking_reasons=list(alignment_blocking_reasons),
                ),
                tracer,
                decision_trace,
            )

        decision_context = self._build_context(
            candles,
            primary_result,
            mtf_decision,
            smc_context_result,
            crt_result,
            alignment_result,
        )
        decision_engine = DecisionEngine()
        decision_result = decision_engine.evaluate(decision_context, capital_decision, mtf_decision)
        self._trace_step(
            tracer,
            decision_trace,
            "DECISION_ENGINE",
            decision_result.action,
            bool(decision_result.allowed and decision_result.action in {"BUY", "SELL"}),
            reasons=list(getattr(decision_result, "reasons", [])),
            blocking_reasons=list(getattr(decision_result, "blocking_reasons", [])),
        )
        if decision_result.action == "NO_TRADE" or not decision_result.allowed:
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action=decision_result.action,
                executed=False,
                status="BLOCKED",
                reasons=[
                    *decision_result.reasons,
                    *[f"ALIGNMENT: {item}" for item in alignment_reasons],
                    *[f"SMC: {item}" for item in smc_reasons],
                    *[f"CRT: {item}" for item in crt_reasons],
                ],
                blocking_reasons=[
                    *decision_result.blocking_reasons,
                    *[f"ALIGNMENT: {item}" for item in alignment_blocking_reasons],
                    *[f"SMC: {item}" for item in smc_blocking_reasons],
                    *[f"CRT: {item}" for item in crt_blocking_reasons],
                ],
                confidence=decision_result.confidence,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Decision-engine blocked decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action=decision_result.action,
                trade_executed=False,
                reasons=decision_result.reasons,
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                session_checked=True,
                session_allowed=True,
                active_session=session_result.active_session,
                session_status=session_result.status,
                session_reasons=list(session_result.reasons),
                session_blocking_reasons=list(session_result.blocking_reasons),
                news_checked=True,
                news_allowed=True,
                news_status=news_result.status,
                active_news_event=news_result.active_event,
                news_reasons=list(news_result.reasons),
                news_blocking_reasons=list(news_result.blocking_reasons),
                volatility_checked=True,
                volatility_allowed=True,
                volatility_status=volatility_result.status,
                atr=volatility_result.atr,
                last_candle_range=volatility_result.last_candle_range,
                volatility_reasons=list(volatility_result.reasons),
                volatility_blocking_reasons=list(volatility_result.blocking_reasons),
                spread_checked=True,
                spread_allowed=True,
                spread_status=spread_result.status,
                spread=spread_result.spread,
                spread_reasons=list(spread_result.reasons),
                spread_blocking_reasons=list(spread_result.blocking_reasons),
                safety_checked=True,
                safety_allowed=True,
                safety_status=safety_decision.status,
                safety_reasons=list(safety_decision.reasons),
                safety_blocking_reasons=list(safety_decision.blocking_reasons),
                safety_passed_checks=list(safety_decision.passed_checks),
                safety_failed_checks=list(safety_decision.failed_checks),
                smc_checked=smc_checked,
                smc_bias=smc_bias,
                smc_confidence=smc_confidence,
                smc_reasons=list(smc_reasons),
                smc_blocking_reasons=list(smc_blocking_reasons),
                crt_checked=crt_checked,
                crt_bias=crt_bias,
                crt_signal_type=crt_signal_type,
                crt_reasons=list(crt_reasons),
                crt_blocking_reasons=list(crt_blocking_reasons),
                alignment_checked=alignment_checked,
                alignment_allowed=alignment_allowed,
                alignment_status=alignment_status,
                aligned_bias=aligned_bias,
                confidence_adjustment=confidence_adjustment,
                alignment_reasons=list(alignment_reasons),
                alignment_blocking_reasons=list(alignment_blocking_reasons),
                ),
                tracer,
                decision_trace,
            )

        entry_price = float(candles[flow_config.default_price_column].iloc[-1])
        effective_risk_config = risk_config or RiskEngineConfig(
            account_balance=float(broker_state.balance) if broker_state is not None else 10000.0
        )
        risk_plan = RiskEngine().create_plan(decision_result.action, entry_price, effective_risk_config)
        risk_reasons = list(risk_plan.reasons)
        risk_blocking_reasons = list(risk_plan.blocking_reasons)
        self._trace_step(
            tracer,
            decision_trace,
            "RISK_ENGINE",
            "RISK_ALLOWED" if risk_plan.allowed else "RISK_BLOCKED",
            bool(risk_plan.allowed),
            reasons=list(risk_reasons),
            blocking_reasons=list(risk_blocking_reasons),
        )

        if not risk_plan.allowed:
            result_reasons = ["Risk engine blocked trade", *risk_reasons, *risk_blocking_reasons]
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action=decision_result.action,
                executed=False,
                status="BLOCKED",
                reasons=[
                    *result_reasons,
                    *[f"ALIGNMENT: {item}" for item in alignment_reasons],
                    *[f"SMC: {item}" for item in smc_reasons],
                    *[f"CRT: {item}" for item in crt_reasons],
                ],
                blocking_reasons=[
                    *risk_blocking_reasons,
                    *[f"ALIGNMENT: {item}" for item in alignment_blocking_reasons],
                    *[f"SMC: {item}" for item in smc_blocking_reasons],
                    *[f"CRT: {item}" for item in crt_blocking_reasons],
                ],
                confidence=decision_result.confidence,
                price=entry_price,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            if journal is not None:
                self._trace_step(
                    tracer,
                    decision_trace,
                    "JOURNAL",
                    "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                    journal_trade_id is not None,
                    reasons=["Risk-engine blocked decision recorded"],
                    blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
                )
            return self._finalize_trace_result(
                PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action=decision_result.action,
                trade_executed=False,
                reasons=result_reasons,
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
                risk_checked=True,
                risk_allowed=False,
                risk_reasons=risk_reasons,
                risk_blocking_reasons=risk_blocking_reasons,
                stop_loss=risk_plan.stop_loss,
                take_profit=risk_plan.take_profit,
                volume=None,
                session_checked=True,
                session_allowed=True,
                active_session=session_result.active_session,
                session_status=session_result.status,
                session_reasons=list(session_result.reasons),
                session_blocking_reasons=list(session_result.blocking_reasons),
                news_checked=True,
                news_allowed=True,
                news_status=news_result.status,
                active_news_event=news_result.active_event,
                news_reasons=list(news_result.reasons),
                news_blocking_reasons=list(news_result.blocking_reasons),
                volatility_checked=True,
                volatility_allowed=True,
                volatility_status=volatility_result.status,
                atr=volatility_result.atr,
                last_candle_range=volatility_result.last_candle_range,
                volatility_reasons=list(volatility_result.reasons),
                volatility_blocking_reasons=list(volatility_result.blocking_reasons),
                spread_checked=True,
                spread_allowed=True,
                spread_status=spread_result.status,
                spread=spread_result.spread,
                spread_reasons=list(spread_result.reasons),
                spread_blocking_reasons=list(spread_result.blocking_reasons),
                safety_checked=True,
                safety_allowed=True,
                safety_status=safety_decision.status,
                safety_reasons=list(safety_decision.reasons),
                safety_blocking_reasons=list(safety_decision.blocking_reasons),
                safety_passed_checks=list(safety_decision.passed_checks),
                safety_failed_checks=list(safety_decision.failed_checks),
                smc_checked=smc_checked,
                smc_bias=smc_bias,
                smc_confidence=smc_confidence,
                smc_reasons=list(smc_reasons),
                smc_blocking_reasons=list(smc_blocking_reasons),
                crt_checked=crt_checked,
                crt_bias=crt_bias,
                crt_signal_type=crt_signal_type,
                crt_reasons=list(crt_reasons),
                crt_blocking_reasons=list(crt_blocking_reasons),
                alignment_checked=alignment_checked,
                alignment_allowed=alignment_allowed,
                alignment_status=alignment_status,
                aligned_bias=aligned_bias,
                confidence_adjustment=confidence_adjustment,
                alignment_reasons=list(alignment_reasons),
                alignment_blocking_reasons=list(alignment_blocking_reasons),
                ),
                tracer,
                decision_trace,
            )

        risk_explanation = RiskEngine().explain(risk_plan)
        trade_request = TradeRequest(
            symbol=flow_config.symbol,
            price=risk_plan.entry_price,
            volume=risk_plan.volume,
            stop_loss=risk_plan.stop_loss,
            take_profit=risk_plan.take_profit,
            reason=f"Paper flow {decision_result.action}; {risk_explanation}",
        )
        paper_broker = PaperBroker()
        trade_manager = TradeManager()
        trade_result = trade_manager.process_decision(
            decision_result,
            trade_request,
            paper_broker,
            broker_config,
            broker_state,
        )
        self._trace_step(
            tracer,
            decision_trace,
            "TRADE_MANAGER",
            trade_result.status,
            bool(trade_result.executed),
            reasons=[trade_result.reason],
            blocking_reasons=[] if trade_result.executed else [trade_result.reason],
        )
        broker_result = getattr(trade_result, "broker_result", None)
        broker_status = str(getattr(broker_result, "status", "NOT_CALLED"))
        broker_reason = str(getattr(broker_result, "reason", "Broker was not called"))
        broker_allowed = bool(getattr(broker_result, "accepted", False))
        self._trace_step(
            tracer,
            decision_trace,
            "PAPER_BROKER",
            broker_status,
            broker_allowed,
            reasons=[broker_reason],
            blocking_reasons=[] if broker_allowed else [broker_reason],
        )

        result_reasons = [
            decision_result.action,
            *decision_result.reasons,
            *risk_reasons,
            *trade_result.reason.split(";"),
        ]
        journal_trade_id = self._record_journal_entry(
            journal=journal,
            symbol=flow_config.symbol,
            action=decision_result.action,
            executed=trade_result.executed,
            status="EXECUTED" if trade_result.executed else "REJECTED",
            reasons=[
                *result_reasons,
                *[f"ALIGNMENT: {item}" for item in alignment_reasons],
                *[f"SMC: {item}" for item in smc_reasons],
                *[f"CRT: {item}" for item in crt_reasons],
            ],
            blocking_reasons=[
                *decision_result.blocking_reasons,
                *risk_blocking_reasons,
                *[f"ALIGNMENT: {item}" for item in alignment_blocking_reasons],
                *[f"SMC: {item}" for item in smc_blocking_reasons],
                *[f"CRT: {item}" for item in crt_blocking_reasons],
            ],
            confidence=decision_result.confidence,
            price=trade_request.price,
            volume=trade_request.volume,
            stop_loss=trade_request.stop_loss,
            take_profit=trade_request.take_profit,
        )
        if journal is not None:
            self._trace_step(
                tracer,
                decision_trace,
                "JOURNAL",
                "RECORDED" if journal_trade_id is not None else "NOT_RECORDED",
                journal_trade_id is not None,
                reasons=["Trade decision recorded in journal"],
                blocking_reasons=[] if journal_trade_id is not None else ["Journal entry was not recorded"],
            )

        exit_simulated = False
        exit_reason = None
        exit_price = None
        pnl = None
        final_status = "EXECUTED" if trade_result.executed else "REJECTED"

        if trade_result.executed and flow_config.simulate_exit:
            position = getattr(getattr(trade_result, "broker_result", None), "position", None)
            exit_result = ExitSimulator().simulate_exit(position, candles, flow_config.exit_simulation_config)
            exit_simulated = True
            exit_reason = exit_result.exit_reason
            exit_price = exit_result.exit_price
            pnl = exit_result.pnl
            self._trace_step(
                tracer,
                decision_trace,
                "EXIT_SIMULATOR",
                "EXITED" if exit_result.exited else "NOT_EXITED",
                bool(exit_result.exited),
                reasons=list(getattr(exit_result, "reasons", [])),
                blocking_reasons=[] if exit_result.exited else ["Exit conditions not met"],
            )
            result_reasons.append(f"Exit simulation result: {exit_result.exit_reason}")
            result_reasons.extend(exit_result.reasons)

            if exit_result.exited and exit_result.exit_price is not None and position is not None:
                close_result = paper_broker.close_position(
                    broker_state,
                    position.position_id,
                    exit_result.exit_price,
                    exit_result.exit_reason,
                )
                result_reasons.append(f"Exit simulation: {exit_result.exit_reason}")
                if close_result.accepted:
                    final_status = "CLOSED"
                    self._update_journal_exit(
                        journal=journal,
                        trade_id=journal_trade_id,
                        status="CLOSED",
                        exit_reason=exit_result.exit_reason,
                        exit_price=exit_result.exit_price,
                        pnl=exit_result.pnl,
                    )
                    if journal is not None and journal_trade_id is not None:
                        self._trace_step(
                            tracer,
                            decision_trace,
                            "JOURNAL",
                            "EXIT_UPDATED",
                            True,
                            reasons=["Journal exit was updated"],
                            blocking_reasons=[],
                        )
                else:
                    result_reasons.append(close_result.reason)

        return self._finalize_trace_result(
            PaperTradingFlowResult(
            completed=True,
            status=final_status,
            market_bias=primary_result.bias,
            decision_action=decision_result.action,
            trade_executed=trade_result.executed,
            reasons=result_reasons,
            balance=broker_state.balance if broker_state else None,
            journal_recorded=journal_trade_id is not None,
            journal_trade_id=journal_trade_id,
            session_checked=True,
            session_allowed=True,
            active_session=session_result.active_session,
            session_status=session_result.status,
            session_reasons=list(session_result.reasons),
            session_blocking_reasons=list(session_result.blocking_reasons),
            news_checked=True,
            news_allowed=True,
            news_status=news_result.status,
            active_news_event=news_result.active_event,
            news_reasons=list(news_result.reasons),
            news_blocking_reasons=list(news_result.blocking_reasons),
            volatility_checked=True,
            volatility_allowed=True,
            volatility_status=volatility_result.status,
            atr=volatility_result.atr,
            last_candle_range=volatility_result.last_candle_range,
            volatility_reasons=list(volatility_result.reasons),
            volatility_blocking_reasons=list(volatility_result.blocking_reasons),
            spread_checked=True,
            spread_allowed=True,
            spread_status=spread_result.status,
            spread=spread_result.spread,
            spread_reasons=list(spread_result.reasons),
            spread_blocking_reasons=list(spread_result.blocking_reasons),
            safety_checked=True,
            safety_allowed=True,
            safety_status=safety_decision.status,
            safety_reasons=list(safety_decision.reasons),
            safety_blocking_reasons=list(safety_decision.blocking_reasons),
            safety_passed_checks=list(safety_decision.passed_checks),
            safety_failed_checks=list(safety_decision.failed_checks),
            risk_checked=True,
            risk_allowed=True,
            risk_reasons=risk_reasons,
            risk_blocking_reasons=risk_blocking_reasons,
            stop_loss=risk_plan.stop_loss,
            take_profit=risk_plan.take_profit,
            volume=risk_plan.volume,
            exit_simulated=exit_simulated,
            exit_reason=exit_reason,
            exit_price=exit_price,
            pnl=pnl,
            smc_checked=smc_checked,
            smc_bias=smc_bias,
            smc_confidence=smc_confidence,
            smc_reasons=list(smc_reasons),
            smc_blocking_reasons=list(smc_blocking_reasons),
            crt_checked=crt_checked,
            crt_bias=crt_bias,
            crt_signal_type=crt_signal_type,
            crt_reasons=list(crt_reasons),
            crt_blocking_reasons=list(crt_blocking_reasons),
            alignment_checked=alignment_checked,
            alignment_allowed=alignment_allowed,
            alignment_status=alignment_status,
            aligned_bias=aligned_bias,
            confidence_adjustment=confidence_adjustment,
            alignment_reasons=list(alignment_reasons),
            alignment_blocking_reasons=list(alignment_blocking_reasons),
            ),
            tracer,
            decision_trace,
        )

    def explain(self, result: PaperTradingFlowResult) -> str:
        """Create a readable summary of the paper flow result."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "No reasons provided"
        balance_text = f"{result.balance:.2f}" if result.balance is not None else "N/A"
        safety_status = result.safety_status if result.safety_status is not None else "N/A"
        failed_checks = ", ".join(result.safety_failed_checks) if result.safety_failed_checks else "None"
        safety_blocks = "; ".join(result.safety_blocking_reasons) if result.safety_blocking_reasons else "None"
        return (
            f"Paper flow status: {result.status} | "
            f"Market bias: {result.market_bias} | "
            f"Decision: {result.decision_action} | "
            f"Trade executed: {result.trade_executed} | "
            f"Safety passed: {result.safety_allowed} | "
            f"Safety status: {safety_status} | "
            f"Safety failed checks: {failed_checks} | "
            f"Safety blocking reasons: {safety_blocks} | "
            f"Trace ID: {result.trace_id or 'N/A'} | "
            f"Balance: {balance_text} | "
            f"Reasons: {reasons_text}"
        )

    def _create_decision_trace(self, tracer: Optional[DecisionTracer], symbol: str) -> Optional[DecisionTrace]:
        """Create a trace when tracing is enabled."""
        if tracer is None:
            return None
        return tracer.create_trace(symbol=symbol)

    def _trace_step(
        self,
        tracer: Optional[DecisionTracer],
        trace: Optional[DecisionTrace],
        step_name: str,
        status: str,
        allowed: bool,
        reasons: Optional[List[str]] = None,
        blocking_reasons: Optional[List[str]] = None,
    ) -> None:
        """Append one safe trace step when tracing is enabled."""
        if tracer is None or trace is None:
            return
        tracer.add_step(
            trace=trace,
            step_name=step_name,
            status=status,
            allowed=allowed,
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def _finalize_trace_result(
        self,
        result: PaperTradingFlowResult,
        tracer: Optional[DecisionTracer],
        trace: Optional[DecisionTrace],
    ) -> PaperTradingFlowResult:
        """Attach final trace metadata to a result when available."""
        if tracer is None or trace is None:
            return result

        trace.final_action = result.decision_action if result.decision_action else "NO_TRADE"
        trace.final_allowed = bool(result.trade_executed and result.decision_action in {"BUY", "SELL"})

        result.trace_id = trace.trace_id
        result.trace_explanation = tracer.explain_trace(trace)
        return result

    def _record_journal_entry(
        self,
        journal: Optional[TradeJournal],
        symbol: str,
        action: str,
        executed: bool,
        status: str,
        reasons: List[str],
        blocking_reasons: List[str],
        confidence: float,
        price: Optional[float],
        volume: Optional[float],
        stop_loss: Optional[float],
        take_profit: Optional[float],
    ) -> Optional[str]:
        """Store a paper-flow decision in the journal when provided."""
        if journal is None:
            return None

        entry = TradeJournalEntry(
            trade_id=str(uuid4()),
            symbol=symbol,
            action=action,
            executed=executed,
            entry_price=price,
            volume=volume,
            stop_loss=stop_loss,
            take_profit=take_profit,
            decision_confidence=confidence,
            reasons=list(reasons),
            blocking_reasons=list(blocking_reasons),
            status=status,
            pnl=None,
        )
        journal.add_entry(entry)
        return entry.trade_id

    def _update_journal_exit(
        self,
        journal: Optional[TradeJournal],
        trade_id: Optional[str],
        status: str,
        exit_reason: str,
        exit_price: Optional[float],
        pnl: Optional[float],
    ) -> None:
        """Update the original journal entry after a simulated close."""
        if journal is None or trade_id is None:
            return

        journal.update_exit(trade_id, status, exit_reason, exit_price, pnl)

    def _build_context(
        self,
        candles: pd.DataFrame,
        analysis_result: MarketAnalysisResult,
        mtf_decision: MultiTimeframeDecision,
        smc_context_result: Optional[SMCContextResult] = None,
        crt_result: Optional[CRTResult] = None,
        alignment_result: Optional[ContextAlignmentResult] = None,
    ) -> DecisionContext:
        """Create a simple DecisionContext from the paper-flow analysis output."""
        last_close = float(candles["close"].iloc[-1])
        context = DecisionContext()
        context.market = MarketContext(price=last_close, volatility=1.0, trend=1 if analysis_result.bias == "BULLISH" else -1 if analysis_result.bias == "BEARISH" else 0)
        context.smc = SMCContext(
            bias=1 if analysis_result.bias == "BULLISH" else -1 if analysis_result.bias == "BEARISH" else 0,
            smc_bias=getattr(smc_context_result, "bias", "UNKNOWN") if smc_context_result is not None else "UNKNOWN",
            smc_confidence=float(getattr(smc_context_result, "confidence", 0.0)) if smc_context_result is not None else 0.0,
            smc_reasons=list(getattr(smc_context_result, "reasons", [])) if smc_context_result is not None else [],
            smc_blocking_reasons=list(getattr(smc_context_result, "blocking_reasons", [])) if smc_context_result is not None else [],
        )
        crt_bias = str(getattr(crt_result, "bias", "UNKNOWN") or "UNKNOWN") if crt_result is not None else "UNKNOWN"
        crt_signal_type = getattr(getattr(crt_result, "latest_signal", None), "signal_type", None) if crt_result is not None else None
        crt_reasons = list(getattr(crt_result, "reasons", [])) if crt_result is not None else []
        crt_blocking_reasons = list(getattr(crt_result, "blocking_reasons", [])) if crt_result is not None else []
        context.crt = CRTContext(
            confirmed=True,
            confidence=analysis_result.confidence / 100.0,
            crt_bias=crt_bias,
            crt_signal_type=crt_signal_type,
            crt_reasons=crt_reasons,
            crt_blocking_reasons=crt_blocking_reasons,
        )
        context.orderflow = OrderFlowContext()
        context.risk = RiskContext(equity=10000.0, max_risk_per_trade=0.01)
        context.trading_halted = False
        context.max_concurrent_trades = 1
        context.open_trades_count = 0
        context.alignment_allowed = bool(getattr(alignment_result, "allowed", True)) if alignment_result is not None else True
        context.alignment_status = getattr(alignment_result, "status", None) if alignment_result is not None else None
        context.aligned_bias = getattr(alignment_result, "aligned_bias", None) if alignment_result is not None else None
        context.alignment_confidence_adjustment = (
            float(getattr(alignment_result, "confidence_adjustment", 0.0)) if alignment_result is not None else 0.0
        )
        context.alignment_reasons = list(getattr(alignment_result, "reasons", [])) if alignment_result is not None else []
        context.alignment_blocking_reasons = (
            list(getattr(alignment_result, "blocking_reasons", [])) if alignment_result is not None else []
        )
        return context
