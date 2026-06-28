"""Trade manager for routing research decisions to the paper broker.

This module is intentionally simple. It takes a decision result and a trade
request, then passes a valid BUY/SELL request to the in-memory paper broker.
It does not connect to any live broker or execute real trades.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from broker.paper_broker import PaperBroker, PaperBrokerConfig, PaperBrokerState, PaperOrderResult
from core.decision_engine import DecisionResult


@dataclass
class TradeRequest:
    """Request data for a simulated trade."""

    symbol: str
    price: float
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: str = ""


@dataclass
class TradeManagerResult:
    """Outcome of processing a trade request."""

    executed: bool
    status: str
    reason: str
    broker_result: Optional[object] = None


class TradeManager:
    """Translate a decision into a paper-broker order."""

    def process_decision(
        self,
        decision_result: DecisionResult,
        trade_request: TradeRequest,
        paper_broker: PaperBroker,
        broker_config: PaperBrokerConfig,
        broker_state: PaperBrokerState,
    ) -> TradeManagerResult:
        """Send a trade request to the paper broker when the decision allows it."""
        if decision_result is None:
            return TradeManagerResult(False, "REJECTED", "No decision provided")

        if not decision_result.allowed:
            return TradeManagerResult(False, "REJECTED", "Decision did not allow trading")

        if decision_result.action == "NO_TRADE":
            return TradeManagerResult(False, "REJECTED", "Decision was NO_TRADE")

        if trade_request is None:
            return TradeManagerResult(False, "REJECTED", "No trade request provided")

        if trade_request.price <= 0:
            return TradeManagerResult(False, "REJECTED", "Trade request price must be positive")

        if trade_request.volume <= 0:
            return TradeManagerResult(False, "REJECTED", "Trade request volume must be positive")

        if decision_result.action == "BUY":
            broker_result = paper_broker.place_market_order(
                broker_config,
                broker_state,
                trade_request.symbol,
                "BUY",
                trade_request.price,
                trade_request.volume,
                stop_loss=trade_request.stop_loss,
                take_profit=trade_request.take_profit,
                reason=trade_request.reason or "DecisionEngine BUY",
            )
            if broker_result.accepted:
                return TradeManagerResult(True, "EXECUTED", "BUY order accepted", broker_result)
            return TradeManagerResult(False, "REJECTED", broker_result.reason, broker_result)

        if decision_result.action == "SELL":
            broker_result = paper_broker.place_market_order(
                broker_config,
                broker_state,
                trade_request.symbol,
                "SELL",
                trade_request.price,
                trade_request.volume,
                stop_loss=trade_request.stop_loss,
                take_profit=trade_request.take_profit,
                reason=trade_request.reason or "DecisionEngine SELL",
            )
            if broker_result.accepted:
                return TradeManagerResult(True, "EXECUTED", "SELL order accepted", broker_result)
            return TradeManagerResult(False, "REJECTED", broker_result.reason, broker_result)

        return TradeManagerResult(False, "REJECTED", "Unknown action")

    def explain(self, result: TradeManagerResult) -> str:
        """Create a readable explanation for a trade manager outcome."""
        if result.executed:
            return f"Trade executed: {result.reason}"
        return f"Trade rejected: {result.reason}"
