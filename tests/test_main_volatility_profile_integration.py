from contextlib import redirect_stdout
from io import StringIO

import pandas as pd

from analysis.volatility_filter import VolatilityFilter
from config.trading_profiles import TradingProfileFactory, to_volatility_filter_config
import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def _make_candles(rows: int = 40, base_range: float = 2.0) -> pd.DataFrame:
    data: list[dict[str, float]] = []
    price = 100.0
    for _ in range(rows):
        open_price = price
        data.append(
            {
                "open": open_price,
                "high": open_price + (base_range / 2.0),
                "low": open_price - (base_range / 2.0),
                "close": open_price + 0.1,
            }
        )
        price = open_price + 0.1
    frame = pd.DataFrame(data)
    frame["time"] = pd.date_range("2026-01-01", periods=rows, freq="min")
    return frame


def test_apex_profile_creates_enabled_volatility_filter() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()
    config = to_volatility_filter_config(profile)

    assert config.enabled is True
    assert config.atr_period == 14
    assert config.min_atr == 0.5
    assert config.max_atr == 80.0
    assert config.max_last_candle_range_multiplier == 3.0


def test_spot_profile_creates_enabled_volatility_filter() -> None:
    profile = TradingProfileFactory.create_spot_gold_profile()
    config = to_volatility_filter_config(profile)

    assert config.enabled is True
    assert config.atr_period == 14
    assert config.min_atr == 0.3
    assert config.max_atr == 120.0
    assert config.max_last_candle_range_multiplier == 3.5


def test_safe_profile_blocks_volatility_safely() -> None:
    profile = TradingProfileFactory.create_safe_default_profile()
    config = to_volatility_filter_config(profile)
    result = VolatilityFilter().evaluate(_make_candles(base_range=2.0), config)

    assert config.enabled is True
    assert config.min_atr == 999999.0
    assert config.max_atr == 0.0
    assert result.allowed is False


def test_demo_mode_with_apex_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bullish" in output


def test_backtest_mode_with_apex_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Backtest" in output
    assert "Scenario: bullish" in output


def test_output_contains_volatility_filter_information() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "Volatility filter status" in output
    assert "ATR" in output
    assert "Last candle range" in output
    assert "Volatility allowed" in output


def test_safe_profile_produces_no_executed_trade() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "safe")

    assert "Trade executed or blocked: Blocked / No trade" in output
    assert "Volatility filter status" in output
    assert "Volatility allowed: False" in output
