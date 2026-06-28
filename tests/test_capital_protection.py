"""Unit tests for the capital protection engine."""

from core.capital_protection import (
    CapitalProtectionConfig,
    CapitalProtectionEngine,
    CapitalProtectionState,
)


def make_config(**overrides):
    """Create a safe default config with simple overrides."""
    config = CapitalProtectionConfig(
        max_daily_loss=100.0,
        daily_profit_target=50.0,
        max_consecutive_losses=3,
        max_open_positions=2,
        trading_enabled=True,
        manual_pause=False,
    )
    for key, value in overrides.items():
        setattr(config, key, value)
    return config


def make_state(**overrides):
    """Create a neutral trading state with simple overrides."""
    state = CapitalProtectionState(
        realized_daily_pnl=0.0,
        consecutive_losses=0,
        open_positions=0,
        emergency_stop=False,
    )
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


def test_emergency_stop_blocks_trading():
    """Emergency stop should block all trading immediately."""
    engine = CapitalProtectionEngine()
    config = make_config()
    state = make_state(emergency_stop=True)

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert decision.status == "blocked"
    assert "Emergency stop activated" in decision.reasons


def test_trading_disabled_blocks_trading():
    """The engine should block all new trading when disabled."""
    engine = CapitalProtectionEngine()
    config = make_config(trading_enabled=False)
    state = make_state()

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert "Trading disabled" in decision.reasons


def test_manual_pause_blocks_trading():
    """A manual pause should stop new trading."""
    engine = CapitalProtectionEngine()
    config = make_config(manual_pause=True)
    state = make_state()

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert "Manual pause active" in decision.reasons


def test_daily_loss_limit_blocks_trading():
    """The engine should stop trading after the daily loss limit is reached."""
    engine = CapitalProtectionEngine()
    config = make_config(max_daily_loss=100.0)
    state = make_state(realized_daily_pnl=-100.0)

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert "Daily loss limit reached" in decision.reasons


def test_daily_profit_target_blocks_new_trades():
    """The engine should stop new trades once the daily profit target is reached."""
    engine = CapitalProtectionEngine()
    config = make_config(daily_profit_target=50.0)
    state = make_state(realized_daily_pnl=50.0)

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert "Daily profit target reached" in decision.reasons


def test_max_consecutive_losses_blocks_trading():
    """Repeated losses should trigger a protection stop."""
    engine = CapitalProtectionEngine()
    config = make_config(max_consecutive_losses=3)
    state = make_state(consecutive_losses=3)

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert "Maximum consecutive losses reached" in decision.reasons


def test_max_open_positions_blocks_new_trades():
    """The engine should block new trades when too many positions are open."""
    engine = CapitalProtectionEngine()
    config = make_config(max_open_positions=2)
    state = make_state(open_positions=2)

    decision = engine.evaluate(config, state)

    assert not decision.allowed
    assert "Maximum open positions reached" in decision.reasons


def test_allowed_trading_case():
    """Normal conditions should permit trading."""
    engine = CapitalProtectionEngine()
    config = make_config()
    state = make_state()

    decision = engine.evaluate(config, state)

    assert decision.allowed
    assert decision.status == "allowed"
    assert decision.reasons == []


def test_should_stop_trading_matches_decision():
    """The helper should align with the main evaluation result."""
    engine = CapitalProtectionEngine()
    config = make_config()
    state = make_state(emergency_stop=True)

    assert engine.should_stop_trading(config, state)


def test_explain_decision_returns_readable_summary():
    """The explanation helper should join reasons into a readable string."""
    engine = CapitalProtectionEngine()
    decision = engine.evaluate(make_config(), make_state(emergency_stop=True))

    explanation = engine.explain_decision(decision)

    assert "Emergency stop activated" in explanation
