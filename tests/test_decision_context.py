"""Unit tests for DecisionContext dataclasses.

These tests check the default conservative behavior (NO TRADE) and a
positive path where all blocking reasons are cleared.
"""
from core.decision_context import DecisionContext


def test_default_no_trade_behavior():
    """By default, DecisionContext should block trading.

    The default CRT is not confirmed and market volatility is zero, so
    the context should explain blocking reasons and `is_trade_allowed`
    should return False.
    """

    ctx = DecisionContext()

    assert not ctx.is_trade_allowed(), "Default context should not allow trading"

    reasons = ctx.explain_blocking_reasons()
    # At least CRT not confirmed and insufficient data should be present
    assert any("CRT not confirmed" in r for r in reasons)
    assert any("Insufficient market volatility" in r or "Insufficient market volatility/data" in r for r in reasons)


def test_trade_allowed_when_all_clear():
    """If CRT confirms and market/risk conditions look reasonable, allow trade."""

    ctx = DecisionContext()
    ctx.crt.confirmed = True
    ctx.crt.confidence = 0.8
    ctx.market.volatility = 0.5
    ctx.risk.equity = 10000.0
    ctx.risk.max_risk_per_trade = 0.01
    ctx.trading_halted = False
    ctx.open_trades_count = 0
    ctx.max_concurrent_trades = 1

    assert ctx.is_trade_allowed(), "Context should allow trading when conditions are clear"
    assert ctx.explain_blocking_reasons() == []
