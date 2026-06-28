"""Unit tests for the trade manager."""

from broker.paper_broker import PaperBroker, PaperBrokerConfig, PaperBrokerState
from core.decision_engine import DecisionResult
from core.trade_manager import TradeManager, TradeManagerResult, TradeRequest


def make_broker_state():
    """Create a fresh paper broker state for tests."""
    broker = PaperBroker()
    config = PaperBrokerConfig()
    return broker.create_default_state(config), config, broker


def test_no_trade_decision_does_not_execute():
    """A NO_TRADE decision should not send anything to the broker."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="NO_TRADE", allowed=False)
    request = TradeRequest(symbol="EURUSD", price=1.1000, volume=1.0)

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert not result.executed
    assert result.reason == "Decision did not allow trading"


def test_blocked_decision_does_not_execute():
    """A blocked decision should not send anything to the broker."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="BUY", allowed=False)
    request = TradeRequest(symbol="EURUSD", price=1.1000, volume=1.0)

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert not result.executed
    assert result.reason == "Decision did not allow trading"


def test_buy_decision_opens_paper_position():
    """A BUY decision should place a BUY order in the paper broker."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="BUY", allowed=True)
    request = TradeRequest(symbol="EURUSD", price=1.1000, volume=1.0, reason="test")

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert result.executed
    assert result.broker_result is not None
    assert len(broker_state.open_positions) == 1
    assert broker_state.open_positions[0].side == "BUY"


def test_sell_decision_opens_paper_position():
    """A SELL decision should place a SELL order in the paper broker."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="SELL", allowed=True)
    request = TradeRequest(symbol="EURUSD", price=1.1000, volume=1.0, reason="test")

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert result.executed
    assert result.broker_result is not None
    assert len(broker_state.open_positions) == 1
    assert broker_state.open_positions[0].side == "SELL"


def test_invalid_price_is_rejected():
    """A non-positive price should be rejected before sending to the broker."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="BUY", allowed=True)
    request = TradeRequest(symbol="EURUSD", price=0.0, volume=1.0)

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert not result.executed
    assert result.reason == "Trade request price must be positive"


def test_invalid_volume_is_rejected():
    """A non-positive volume should be rejected before sending to the broker."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="BUY", allowed=True)
    request = TradeRequest(symbol="EURUSD", price=1.1000, volume=0.0)

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert not result.executed
    assert result.reason == "Trade request volume must be positive"


def test_unknown_action_is_rejected():
    """An unknown action should be rejected safely."""
    broker_state, config, broker = make_broker_state()
    manager = TradeManager()
    decision = DecisionResult(action="HOLD", allowed=True)
    request = TradeRequest(symbol="EURUSD", price=1.1000, volume=1.0)

    result = manager.process_decision(decision, request, broker, config, broker_state)

    assert not result.executed
    assert result.reason == "Unknown action"


def test_explain_returns_readable_text():
    """The explanation should clearly describe the trade manager result."""
    manager = TradeManager()
    result = TradeManagerResult(True, "EXECUTED", "BUY order accepted")

    explanation = manager.explain(result)

    assert "Trade executed" in explanation
    assert "BUY order accepted" in explanation
