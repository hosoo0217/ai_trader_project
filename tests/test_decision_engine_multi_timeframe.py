"""Unit tests for the decision engine with multi-timeframe integration."""

from core.capital_protection import CapitalProtectionDecision
from core.decision_context import DecisionContext
from core.decision_engine import DecisionEngine
from core.multi_timeframe import MultiTimeframeDecision


def make_context(**overrides):
    """Create a context that passes the safety checks by default."""
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


def test_capital_protection_blocks_even_when_multi_timeframe_is_buy():
    """Capital protection should remain the highest priority."""
    engine = DecisionEngine()
    context = make_context()
    capital_decision = CapitalProtectionDecision(allowed=False, reasons=["Daily loss limit reached"])
    multi_timeframe_decision = MultiTimeframeDecision(bias="BUY_BIAS", allowed=True, confidence=90.0)

    result = engine.evaluate(context, capital_decision, multi_timeframe_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed
    assert "Daily loss limit reached" in result.blocking_reasons


def test_multi_timeframe_buy_bias_produces_buy_when_safe():
    """A bullish multi-timeframe decision should produce BUY when safety checks pass."""
    engine = DecisionEngine()
    context = make_context()
    capital_decision = CapitalProtectionDecision(allowed=True)
    multi_timeframe_decision = MultiTimeframeDecision(bias="BUY_BIAS", allowed=True, confidence=90.0)

    result = engine.evaluate(context, capital_decision, multi_timeframe_decision)

    assert result.action == "BUY"
    assert result.allowed
    assert result.confidence >= 70.0


def test_multi_timeframe_sell_bias_produces_sell_when_safe():
    """A bearish multi-timeframe decision should produce SELL when safety checks pass."""
    engine = DecisionEngine()
    context = make_context(smc__bias=-1, market__trend=-1)
    capital_decision = CapitalProtectionDecision(allowed=True)
    multi_timeframe_decision = MultiTimeframeDecision(bias="SELL_BIAS", allowed=True, confidence=90.0)

    result = engine.evaluate(context, capital_decision, multi_timeframe_decision)

    assert result.action == "SELL"
    assert result.allowed


def test_multi_timeframe_wait_produces_no_trade():
    """A WAIT decision from the combiner should block the trade."""
    engine = DecisionEngine()
    context = make_context()
    capital_decision = CapitalProtectionDecision(allowed=True)
    multi_timeframe_decision = MultiTimeframeDecision(bias="WAIT", allowed=False, confidence=80.0)

    result = engine.evaluate(context, capital_decision, multi_timeframe_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed


def test_multi_timeframe_no_trade_produces_no_trade():
    """A NO_TRADE decision from the combiner should block the trade."""
    engine = DecisionEngine()
    context = make_context()
    capital_decision = CapitalProtectionDecision(allowed=True)
    multi_timeframe_decision = MultiTimeframeDecision(bias="NO_TRADE", allowed=False, confidence=80.0)

    result = engine.evaluate(context, capital_decision, multi_timeframe_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed


def test_low_confidence_produces_no_trade():
    """Low confidence should force a NO_TRADE decision."""
    engine = DecisionEngine()
    context = make_context(crt__confidence=0.6)
    capital_decision = CapitalProtectionDecision(allowed=True)
    multi_timeframe_decision = MultiTimeframeDecision(bias="BUY_BIAS", allowed=True, confidence=60.0)

    result = engine.evaluate(context, capital_decision, multi_timeframe_decision)

    assert result.action == "NO_TRADE"
    assert not result.allowed


def test_explain_returns_readable_text():
    """The explanation should summarize the final decision clearly."""
    engine = DecisionEngine()
    result = DecisionEngine().evaluate(
        make_context(),
        CapitalProtectionDecision(allowed=True),
        MultiTimeframeDecision(bias="BUY_BIAS", allowed=True, confidence=90.0),
    )

    explanation = engine.explain(result)

    assert "Final action" in explanation
    assert "BUY" in explanation
    assert "Confidence" in explanation
