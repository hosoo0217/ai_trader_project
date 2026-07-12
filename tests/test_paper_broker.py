"""Unit tests for the paper broker."""

from broker.paper_broker import PaperBroker, PaperBrokerConfig, PaperBrokerState


def make_config(**overrides):
    """Create a default config with optional overrides."""
    config = PaperBrokerConfig(starting_balance=10000.0, allow_buy=True, allow_sell=True, max_open_positions=1)
    for key, value in overrides.items():
        setattr(config, key, value)
    return config


def make_state(config):
    """Create a default broker state from the config."""
    return PaperBroker().create_default_state(config)


def test_default_state_balance():
    """The default state should start with the configured balance."""
    broker = PaperBroker()
    config = make_config()
    state = broker.create_default_state(config)

    assert state.balance == 10000.0
    assert state.open_positions == []
    assert state.closed_positions == []


def test_valid_buy_order_opens_position():
    """A valid BUY order should open a new position."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    result = broker.place_market_order(config, state, "EURUSD", "BUY", 1.1000, 1.0, reason="test")

    assert result.accepted
    assert result.position is not None
    assert result.position.side == "BUY"
    assert result.position.status == "OPEN"


def test_valid_sell_order_opens_position():
    """A valid SELL order should open a new position."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    result = broker.place_market_order(config, state, "EURUSD", "SELL", 1.1000, 1.0, reason="test")

    assert result.accepted
    assert result.position is not None
    assert result.position.side == "SELL"
    assert result.position.status == "OPEN"


def test_reject_invalid_side():
    """Unknown sides should be rejected."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    result = broker.place_market_order(config, state, "EURUSD", "HOLD", 1.1000, 1.0)

    assert not result.accepted
    assert result.reason == "Unknown side"


def test_reject_zero_or_negative_price():
    """Non-positive prices should be rejected."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    result = broker.place_market_order(config, state, "EURUSD", "BUY", 0.0, 1.0)

    assert not result.accepted
    assert result.reason == "Price must be positive"


def test_reject_zero_or_negative_volume():
    """Non-positive volumes should be rejected."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    result = broker.place_market_order(config, state, "EURUSD", "BUY", 1.1000, 0.0)

    assert not result.accepted
    assert result.reason == "Volume must be positive"


def test_reject_when_max_open_positions_reached():
    """The broker should reject new orders when the position limit is reached."""
    broker = PaperBroker()
    config = make_config(max_open_positions=1)
    state = make_state(config)

    broker.place_market_order(config, state, "EURUSD", "BUY", 1.1000, 1.0)
    result = broker.place_market_order(config, state, "EURUSD", "BUY", 1.1200, 1.0)

    assert not result.accepted
    assert result.reason == "Maximum open positions reached"


def test_close_buy_position_updates_balance():
    """Closing a BUY position should add profit or loss to the balance."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    order = broker.place_market_order(config, state, "EURUSD", "BUY", 1.1000, 1.0)
    result = broker.close_position(state, order.position.position_id, 1.1200, "take profit")

    assert result.accepted
    assert broker.get_balance(state) == 10000.0 + 0.02


def test_close_sell_position_updates_balance():
    """Closing a SELL position should add profit or loss to the balance."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    order = broker.place_market_order(config, state, "EURUSD", "SELL", 1.1000, 1.0)
    result = broker.close_position(state, order.position.position_id, 1.0800, "stop loss")

    assert result.accepted
    assert broker.get_balance(state) == 10000.0 + 0.02


def test_get_open_positions_returns_only_open_positions():
    """The broker should list only positions that remain open."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    first_order = broker.place_market_order(config, state, "EURUSD", "BUY", 1.1000, 1.0)
    broker.close_position(state, first_order.position.position_id, 1.1200)
    broker.place_market_order(config, state, "EURUSD", "SELL", 1.1100, 1.0)

    open_positions = broker.get_open_positions(state)

    assert len(open_positions) == 1
    assert open_positions[0].side == "SELL"


def test_close_position_applies_point_value():
    """Closing balance should use the configured monetary point value."""
    broker = PaperBroker()
    config = make_config()
    state = make_state(config)

    order = broker.place_market_order(
        config,
        state,
        "GC",
        "BUY",
        100.0,
        1.0,
    )
    result = broker.close_position(
        state,
        order.position.position_id,
        110.0,
        "take profit",
        point_value=10.0,
    )

    assert result.accepted
    assert broker.get_balance(state) == 10100.0
