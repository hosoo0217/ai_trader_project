"""Full paper trading pipeline for research and backtesting.

This module wires together the market analyzer, multi-timeframe combiner,
capital protection, decision engine, and paper broker into one safe flow.
It only simulates orders in memory and never connects to a live broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

import pandas as pd

from broker.paper_broker import PaperBroker, PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionEngine, CapitalProtectionState
from core.decision_context import DecisionContext, MarketContext, SMCContext, CRTContext, OrderFlowContext, RiskContext
from core.decision_engine import DecisionEngine, DecisionResult
from core.market_analyzer import MarketAnalysisResult, MarketAnalyzer, MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeBiasCombiner, MultiTimeframeConfig, MultiTimeframeDecision
from core.trade_manager import TradeManager, TradeRequest
from storage.trade_journal import TradeJournal, TradeJournalEntry


@dataclass
class PaperTradingFlowConfig:
    """Configuration for the paper trading flow."""

    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    default_volume: float = 1.0
    default_price_column: str = "close"


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
    ) -> PaperTradingFlowResult:
        """Run the paper flow using a single candle dataset for all timeframes."""
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
            return PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Invalid candle data"],
                balance=None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
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
            return PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Missing required candle columns"],
                balance=None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
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
            return PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["No market analysis results"],
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
            )

        primary_result = market_results.get(flow_config.timeframe) or next(iter(market_results.values()))
        if primary_result.bias == "UNKNOWN":
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
            return PaperTradingFlowResult(
                completed=False,
                status="REJECTED",
                market_bias="UNKNOWN",
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Market analysis returned UNKNOWN"],
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
            )

        mtf_combiner = MultiTimeframeBiasCombiner()
        mtf_decision = mtf_combiner.combine(market_results, mtf_config)
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
            return PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=["Multi-timeframe decision blocked trading"],
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
            )

        capital_engine = CapitalProtectionEngine()
        capital_decision = capital_engine.evaluate(capital_config, capital_state)
        if not capital_decision.allowed:
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action="NO_TRADE",
                executed=False,
                status="BLOCKED",
                reasons=capital_decision.reasons,
                blocking_reasons=capital_decision.reasons,
                confidence=0.0,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            return PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action="NO_TRADE",
                trade_executed=False,
                reasons=capital_decision.reasons,
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
            )

        decision_context = self._build_context(candles, primary_result, mtf_decision)
        decision_engine = DecisionEngine()
        decision_result = decision_engine.evaluate(decision_context, capital_decision, mtf_decision)
        if decision_result.action == "NO_TRADE" or not decision_result.allowed:
            journal_trade_id = self._record_journal_entry(
                journal=journal,
                symbol=flow_config.symbol,
                action=decision_result.action,
                executed=False,
                status="BLOCKED",
                reasons=decision_result.reasons,
                blocking_reasons=decision_result.blocking_reasons,
                confidence=decision_result.confidence,
                price=None,
                volume=None,
                stop_loss=None,
                take_profit=None,
            )
            return PaperTradingFlowResult(
                completed=True,
                status="NO_TRADE",
                market_bias=primary_result.bias,
                decision_action=decision_result.action,
                trade_executed=False,
                reasons=decision_result.reasons,
                balance=broker_state.balance if broker_state else None,
                journal_recorded=journal_trade_id is not None,
                journal_trade_id=journal_trade_id,
            )

        trade_request = TradeRequest(
            symbol=flow_config.symbol,
            price=float(candles[flow_config.default_price_column].iloc[-1]),
            volume=flow_config.default_volume,
            reason=f"Paper flow {decision_result.action}",
        )
        trade_manager = TradeManager()
        trade_result = trade_manager.process_decision(
            decision_result,
            trade_request,
            PaperBroker(),
            broker_config,
            broker_state,
        )

        journal_trade_id = self._record_journal_entry(
            journal=journal,
            symbol=flow_config.symbol,
            action=decision_result.action,
            executed=trade_result.executed,
            status="EXECUTED" if trade_result.executed else "REJECTED",
            reasons=[decision_result.action, *decision_result.reasons, *trade_result.reason.split(";")],
            blocking_reasons=decision_result.blocking_reasons,
            confidence=decision_result.confidence,
            price=trade_request.price,
            volume=trade_request.volume,
            stop_loss=trade_request.stop_loss,
            take_profit=trade_request.take_profit,
        )

        return PaperTradingFlowResult(
            completed=True,
            status="EXECUTED" if trade_result.executed else "REJECTED",
            market_bias=primary_result.bias,
            decision_action=decision_result.action,
            trade_executed=trade_result.executed,
            reasons=[decision_result.action, *decision_result.reasons, *trade_result.reason.split(";")],
            balance=broker_state.balance if broker_state else None,
            journal_recorded=journal_trade_id is not None,
            journal_trade_id=journal_trade_id,
        )

    def explain(self, result: PaperTradingFlowResult) -> str:
        """Create a readable summary of the paper flow result."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "No reasons provided"
        balance_text = f"{result.balance:.2f}" if result.balance is not None else "N/A"
        return (
            f"Paper flow status: {result.status} | "
            f"Market bias: {result.market_bias} | "
            f"Decision: {result.decision_action} | "
            f"Trade executed: {result.trade_executed} | "
            f"Balance: {balance_text} | "
            f"Reasons: {reasons_text}"
        )

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

    def _build_context(
        self,
        candles: pd.DataFrame,
        analysis_result: MarketAnalysisResult,
        mtf_decision: MultiTimeframeDecision,
    ) -> DecisionContext:
        """Create a simple DecisionContext from the paper-flow analysis output."""
        last_close = float(candles["close"].iloc[-1])
        context = DecisionContext()
        context.market = MarketContext(price=last_close, volatility=1.0, trend=1 if analysis_result.bias == "BULLISH" else -1 if analysis_result.bias == "BEARISH" else 0)
        context.smc = SMCContext(bias=1 if analysis_result.bias == "BULLISH" else -1 if analysis_result.bias == "BEARISH" else 0)
        context.crt = CRTContext(confirmed=True, confidence=analysis_result.confidence / 100.0)
        context.orderflow = OrderFlowContext()
        context.risk = RiskContext(equity=10000.0, max_risk_per_trade=0.01)
        context.trading_halted = False
        context.max_concurrent_trades = 1
        context.open_trades_count = 0
        return context
