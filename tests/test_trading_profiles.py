"""Unit tests for centralized trading profiles."""

from config.trading_profiles import (
    TradingProfileFactory,
    to_capital_protection_config,
    to_paper_broker_config,
    to_risk_engine_config,
)


def test_apex_profile_has_correct_account_type_and_symbol() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()

    assert profile.account_type == "FUTURES_PROP"
    assert profile.symbol == "GC"


def test_apex_profile_daily_target_is_200() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()

    assert profile.daily_profit_target == 200.0


def test_spot_profile_symbol_is_xauusd() -> None:
    profile = TradingProfileFactory.create_spot_gold_profile()

    assert profile.symbol == "XAUUSD"


def test_safe_default_profile_disables_trading() -> None:
    profile = TradingProfileFactory.create_safe_default_profile()

    assert profile.enabled is False
    assert profile.allow_buy is False
    assert profile.allow_sell is False
    assert profile.max_open_positions == 0


def test_conversion_to_capital_protection_config_works() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()
    config = to_capital_protection_config(profile)

    assert config.max_daily_loss == profile.max_daily_loss
    assert config.daily_profit_target == profile.daily_profit_target
    assert config.max_consecutive_losses == profile.max_consecutive_losses
    assert config.max_open_positions == profile.max_open_positions
    assert config.trading_enabled == profile.enabled


def test_conversion_to_risk_engine_config_works() -> None:
    profile = TradingProfileFactory.create_spot_gold_profile()
    config = to_risk_engine_config(profile)

    assert config.account_balance == profile.starting_balance
    assert config.risk_per_trade_percent == profile.risk_per_trade_percent
    assert config.reward_to_risk == profile.reward_to_risk
    assert config.default_stop_distance == profile.default_stop_distance
    assert config.min_volume == profile.min_volume
    assert config.max_volume == profile.max_volume
    assert config.point_value == profile.point_value


def test_conversion_to_paper_broker_config_works() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()
    config = to_paper_broker_config(profile)

    assert config.starting_balance == profile.starting_balance
    assert config.allow_buy == profile.allow_buy
    assert config.allow_sell == profile.allow_sell
    assert config.max_open_positions == profile.max_open_positions


def test_profiles_do_not_allow_negative_balance_or_risk() -> None:
    apex = TradingProfileFactory.create_apex_futures_profile()
    spot = TradingProfileFactory.create_spot_gold_profile()
    safe = TradingProfileFactory.create_safe_default_profile()

    for profile in [apex, spot, safe]:
        assert profile.starting_balance >= 0.0
        assert profile.max_daily_loss >= 0.0
        assert profile.risk_per_trade_percent >= 0.0
        assert profile.default_stop_distance >= 0.0
        assert profile.min_volume >= 0.0
        assert profile.max_volume >= 0.0
        assert profile.point_value >= 0.0
