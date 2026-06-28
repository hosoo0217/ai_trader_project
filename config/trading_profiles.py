"""Trading profile definitions for paper trading and backtesting.

This module stores account-style presets and conversion helpers for existing
risk and protection config objects. It does not connect to any broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from analysis.session_filter import SessionFilterConfig, TradingSession
from broker.paper_broker import PaperBrokerConfig
from core.capital_protection import CapitalProtectionConfig
from risk.risk_engine import RiskEngineConfig


@dataclass
class TradingProfile:
    """Centralized account profile used by research and simulation flows."""

    profile_name: str
    account_type: str
    symbol: str
    enabled: bool
    starting_balance: float
    daily_profit_target: float
    max_daily_loss: float
    max_consecutive_losses: int
    max_open_positions: int
    risk_per_trade_percent: float
    reward_to_risk: float
    default_stop_distance: float
    min_volume: float
    max_volume: float
    point_value: float
    allow_buy: bool
    allow_sell: bool
    notes: list[str] = field(default_factory=list)


class TradingProfileFactory:
    """Factory for predefined paper/backtest-only trading profiles."""

    @staticmethod
    def create_apex_futures_profile() -> TradingProfile:
        """Create a strict futures prop-style scalping profile."""
        profile = TradingProfile(
            profile_name="Apex Futures Scalper",
            account_type="FUTURES_PROP",
            symbol="GC",
            enabled=True,
            starting_balance=50000.0,
            daily_profit_target=200.0,
            max_daily_loss=200.0,
            max_consecutive_losses=2,
            max_open_positions=1,
            risk_per_trade_percent=0.25,
            reward_to_risk=1.5,
            default_stop_distance=10.0,
            min_volume=1.0,
            max_volume=1.0,
            point_value=10.0,
            allow_buy=True,
            allow_sell=True,
            notes=[
                "Capital protection first",
                "Prop-firm style discipline",
                "Research-only configuration",
            ],
        )
        return TradingProfileFactory._sanitize_profile(profile)

    @staticmethod
    def create_spot_gold_profile() -> TradingProfile:
        """Create a controlled spot-gold profile for intraday and swing research."""
        profile = TradingProfile(
            profile_name="Spot Gold Engine",
            account_type="SPOT_GOLD",
            symbol="XAUUSD",
            enabled=True,
            starting_balance=10000.0,
            daily_profit_target=0.0,
            max_daily_loss=150.0,
            max_consecutive_losses=3,
            max_open_positions=1,
            risk_per_trade_percent=0.5,
            reward_to_risk=2.0,
            default_stop_distance=10.0,
            min_volume=0.01,
            max_volume=1.0,
            point_value=1.0,
            allow_buy=True,
            allow_sell=True,
            notes=[
                "Designed for XAUUSD simulation",
                "Supports conservative runner-style planning later",
                "Research-only configuration",
            ],
        )
        return TradingProfileFactory._sanitize_profile(profile)

    @staticmethod
    def create_safe_default_profile() -> TradingProfile:
        """Create the safest fallback profile when no account is selected."""
        profile = TradingProfile(
            profile_name="Safe Default",
            account_type="SAFE_DEFAULT",
            symbol="XAUUSD",
            enabled=False,
            starting_balance=10000.0,
            daily_profit_target=0.0,
            max_daily_loss=0.0,
            max_consecutive_losses=0,
            max_open_positions=0,
            risk_per_trade_percent=0.1,
            reward_to_risk=1.0,
            default_stop_distance=10.0,
            min_volume=0.01,
            max_volume=0.01,
            point_value=1.0,
            allow_buy=False,
            allow_sell=False,
            notes=[
                "Conservative fallback",
                "Trading disabled until profile is explicitly selected",
                "Research-only configuration",
            ],
        )
        return TradingProfileFactory._sanitize_profile(profile)

    @staticmethod
    def _sanitize_profile(profile: TradingProfile) -> TradingProfile:
        """Clamp unsafe negative values to protect paper/backtest configs."""
        profile.starting_balance = max(0.0, float(profile.starting_balance))
        profile.daily_profit_target = max(0.0, float(profile.daily_profit_target))
        profile.max_daily_loss = max(0.0, float(profile.max_daily_loss))
        profile.max_consecutive_losses = max(0, int(profile.max_consecutive_losses))
        profile.max_open_positions = max(0, int(profile.max_open_positions))
        profile.risk_per_trade_percent = max(0.0, float(profile.risk_per_trade_percent))
        profile.reward_to_risk = max(0.0, float(profile.reward_to_risk))
        profile.default_stop_distance = max(0.0, float(profile.default_stop_distance))
        profile.min_volume = max(0.0, float(profile.min_volume))
        profile.max_volume = max(0.0, float(profile.max_volume))
        profile.point_value = max(0.0, float(profile.point_value))

        if profile.max_volume < profile.min_volume:
            profile.max_volume = profile.min_volume

        return profile


def to_capital_protection_config(profile: TradingProfile) -> CapitalProtectionConfig:
    """Convert a TradingProfile into a CapitalProtectionConfig."""
    return CapitalProtectionConfig(
        max_daily_loss=max(0.0, profile.max_daily_loss),
        daily_profit_target=max(0.0, profile.daily_profit_target),
        max_consecutive_losses=max(0, profile.max_consecutive_losses),
        max_open_positions=max(0, profile.max_open_positions),
        trading_enabled=bool(profile.enabled),
        manual_pause=False,
    )


def to_risk_engine_config(profile: TradingProfile) -> RiskEngineConfig:
    """Convert a TradingProfile into a RiskEngineConfig."""
    return RiskEngineConfig(
        account_balance=max(0.0, profile.starting_balance),
        risk_per_trade_percent=max(0.0, profile.risk_per_trade_percent),
        reward_to_risk=max(0.0, profile.reward_to_risk),
        default_stop_distance=max(0.0, profile.default_stop_distance),
        min_volume=max(0.0, profile.min_volume),
        max_volume=max(0.0, profile.max_volume),
        point_value=max(0.0, profile.point_value),
    )


def to_paper_broker_config(profile: TradingProfile) -> PaperBrokerConfig:
    """Convert a TradingProfile into a PaperBrokerConfig."""
    return PaperBrokerConfig(
        starting_balance=max(0.0, profile.starting_balance),
        allow_buy=bool(profile.allow_buy and profile.enabled),
        allow_sell=bool(profile.allow_sell and profile.enabled),
        max_open_positions=max(0, profile.max_open_positions),
    )


def to_session_filter_config(profile: TradingProfile) -> SessionFilterConfig:
    """Convert a TradingProfile into a SessionFilterConfig."""
    if profile.account_type == "SAFE_DEFAULT" or not profile.enabled:
        return SessionFilterConfig(
            enabled=True,
            allowed_sessions=[
                TradingSession(name="London", start_hour_utc=7, end_hour_utc=16, enabled=False),
                TradingSession(name="New York", start_hour_utc=13, end_hour_utc=21, enabled=False),
                TradingSession(name="London New York Overlap", start_hour_utc=13, end_hour_utc=16, enabled=False),
                TradingSession(name="Asian", start_hour_utc=0, end_hour_utc=6, enabled=False),
            ],
            block_weekends=True,
            timezone_note="All session times are UTC",
        )

    return SessionFilterConfig(
        enabled=True,
        allowed_sessions=[
            TradingSession(name="London", start_hour_utc=7, end_hour_utc=16, enabled=True),
            TradingSession(name="New York", start_hour_utc=13, end_hour_utc=21, enabled=True),
            TradingSession(name="London New York Overlap", start_hour_utc=13, end_hour_utc=16, enabled=True),
            TradingSession(name="Asian", start_hour_utc=0, end_hour_utc=6, enabled=False),
        ],
        block_weekends=True,
        timezone_note="All session times are UTC",
    )
