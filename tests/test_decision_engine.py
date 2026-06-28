"""Unit tests for the decision engine."""

from core.capital_protection import CapitalProtectionDecision
from core.decision_context import DecisionContext
from core.decision_engine import DecisionEngine


def make_context(**overrides):
    """Create a context that is safe enough to allow a trade when needed."""
    context = DecisionContext()
    context.crt.confirmed = True
    context.crt.confidence = 0.8
    context.market.volatility = 1.0
    context.risk.equity = 10000.0
    context.risk.max_risk_per_trade = 0.01
    context.open_trades_count = 0
    context.max_concurrent_trades = 1
    context.trading_halted = False
    context.smc.bias = 1
    context.market.trend = 1

    for key, value in overrides.items():
        if "__" in key:
            parent_name, child_name = key.split("__", 1)
            parent = getattr(context, parent_name)
            setattr(parent, child_name, value)
        else:
            setattr(context, key, value)

    return context


def test_capital_protection_blocks_trade():
    """Capital protection should have the highest authority."""
    engine = DecisionEngine()
    context = make_context()
    capital_decision = CapitalProtectionDecision(allowed=False, reasons=["Daily loss limit reached"])

    result = engine.evaluate(context, capital_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed
    assert "Daily loss limit reached" in result.blocking_reasons


def test_decision_context_blocks_trade():
    """DecisionContext should block trade when its helper says no."""
    engine = DecisionEngine()
    context = make_context()
    context.crt.confirmed = False
    capital_decision = CapitalProtectionDecision(allowed=True)

    result = engine.evaluate(context, capital_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed
    assert any("DecisionContext" in reason for reason in result.blocking_reasons)


def test_low_confidence_blocks_trade():
    """Low confidence should return NO_TRADE for safety."""
    engine = DecisionEngine()
    context = make_context(crt__confidence=0.6)
    capital_decision = CapitalProtectionDecision(allowed=True)

    result = engine.evaluate(context, capital_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed
    assert result.confidence < 70.0


def test_missing_direction_returns_no_trade():
    """Neutral or missing direction should not produce a trade signal."""
    engine = DecisionEngine()
    context = make_context(smc__bias=0, market__trend=0)
    capital_decision = CapitalProtectionDecision(allowed=True)

    result = engine.evaluate(context, capital_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed


def test_valid_buy_returns_buy():
    """A safe bullish setup should return BUY."""
    engine = DecisionEngine()
    context = make_context(smc__bias=1, market__trend=1)
    capital_decision = CapitalProtectionDecision(allowed=True)

    result = engine.evaluate(context, capital_decision)

    assert result.action == "BUY"
    assert result.allowed
    assert result.confidence >= 70.0


def test_valid_sell_returns_sell():
    """A safe bearish setup should return SELL."""
    engine = DecisionEngine()
    context = make_context(smc__bias=-1, market__trend=-1)
    capital_decision = CapitalProtectionDecision(allowed=True)

    result = engine.evaluate(context, capital_decision)

    assert result.action == "SELL"
    assert result.allowed
    assert result.confidence >= 70.0


def test_explain_returns_readable_explanation():
    """Explain should turn the decision into a short human-readable summary."""
    engine = DecisionEngine()
    context = make_context()
    capital_decision = CapitalProtectionDecision(allowed=False, reasons=["Daily loss limit reached"])

    result = engine.evaluate(context, capital_decision)
    explanation = engine.explain(result)

    assert "NO_TRADE" in explanation
    assert "Daily loss limit reached" in explanation
